import {
  BadRequestException,
  Injectable,
  Logger,
  NotFoundException,
} from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import {
  ApplicationStatus,
  Certificate,
  CertificateStatus,
  CertificateType,
} from '@prisma/client';
import { customAlphabet } from 'nanoid';
import * as QRCode from 'qrcode';
import { PrismaService } from '../../prisma/prisma.service';
import { hashContent, signHash, CertificateContent } from './certificate-hash.util';
import {
  BulkIssueDto,
  IssueManualCertificateDto,
} from './dto/certificate.dto';

const certCode = customAlphabet('ABCDEFGHIJKLMNPQRSTUVWXYZ23456789', 8);
const verifyToken = customAlphabet('abcdefghijklmnopqrstuvwxyz0123456789', 20);

@Injectable()
export class CertificatesService {
  private readonly logger = new Logger(CertificatesService.name);

  constructor(
    private readonly prisma: PrismaService,
    private readonly config: ConfigService,
  ) {}

  // ── Auto issuance (when an internship is approved as COMPLETED) ────────────────

  /**
   * Generates a certificate for a COMPLETED application. Idempotent: returns the
   * existing certificate if one was already issued. Advances the application to
   * CERTIFICATE_GENERATED.
   */
  async issueForApplication(applicationId: string, issuedByUserId: string): Promise<Certificate> {
    const application = await this.prisma.application.findUnique({
      where: { id: applicationId },
      include: {
        student: { include: { user: true } },
        internship: { include: { organization: true, domain: true } },
        certificate: true,
      },
    });
    if (!application) throw new NotFoundException('Application not found');
    if (application.certificate) return application.certificate;
    if (application.status !== ApplicationStatus.COMPLETED) {
      throw new BadRequestException('Certificate can only be issued for COMPLETED internships');
    }

    const cert = await this.persistCertificate({
      type: CertificateType.INTERNSHIP_COMPLETION,
      studentProfileId: application.studentId,
      applicationId: application.id,
      issuedByUserId,
      studentName: application.student.user.fullName,
      organizationName: application.internship.organization.companyName,
      domainName: application.internship.domain.name,
      title: `Internship Completion — ${application.internship.title}`,
      durationWeeks: application.internship.durationWeeks,
      startDate: application.startedAt,
      endDate: application.completedAt,
      grade: application.finalGrade ?? undefined,
    });

    // Move the application to its terminal state + award the "certified" badge.
    await this.prisma.application.update({
      where: { id: application.id },
      data: {
        status: ApplicationStatus.CERTIFICATE_GENERATED,
        history: {
          create: {
            fromStatus: ApplicationStatus.COMPLETED,
            toStatus: ApplicationStatus.CERTIFICATE_GENERATED,
            note: `Certificate ${cert.certificateId} issued`,
            actorId: issuedByUserId,
          },
        },
      },
    });
    await this.awardCertifiedBadge(application.studentId);

    return cert;
  }

  async bulkIssue(dto: BulkIssueDto, issuedByUserId: string) {
    const results: { applicationId: string; certificateId?: string; error?: string }[] = [];
    for (const applicationId of dto.applicationIds) {
      try {
        const cert = await this.issueForApplication(applicationId, issuedByUserId);
        results.push({ applicationId, certificateId: cert.certificateId });
      } catch (err) {
        results.push({ applicationId, error: (err as Error).message });
      }
    }
    return { issued: results.filter((r) => r.certificateId).length, results };
  }

  // ── Manual issuance (admin: workshops / bootcamps / awards) ────────────────────

  async issueManual(dto: IssueManualCertificateDto, issuedByUserId: string) {
    const student = await this.prisma.studentProfile.findUnique({
      where: { id: dto.studentProfileId },
      include: { user: true },
    });
    if (!student) throw new NotFoundException('Student not found');

    return this.persistCertificate({
      type: dto.type,
      studentProfileId: dto.studentProfileId,
      issuedByUserId,
      studentName: student.user.fullName,
      organizationName: dto.organizationName,
      domainName: dto.domainName,
      title: dto.title,
      durationWeeks: dto.durationWeeks,
      grade: dto.grade,
    });
  }

  // ── Verification portal ────────────────────────────────────────────────────────

  /**
   * Public verification by certificate ID or verification number. Recomputes the
   * content hash and compares it to the stored hash → tamper detection. Logs every
   * check to an append-only audit table.
   */
  async verify(identifier: string, meta: { ip?: string; userAgent?: string; method?: string }) {
    const cert = await this.prisma.certificate.findFirst({
      where: { OR: [{ certificateId: identifier }, { verificationNumber: identifier }] },
      include: { student: { include: { user: { select: { fullName: true } } } } },
    });

    if (!cert) {
      return { valid: false, reason: 'NOT_FOUND' as const };
    }

    const recomputed = hashContent(this.toContent(cert));
    const hashMatches = recomputed === cert.contentHash;
    const revoked = cert.status === CertificateStatus.REVOKED;
    const valid = hashMatches && !revoked;

    await this.prisma.certificateVerification.create({
      data: {
        certificateId: cert.id,
        method: meta.method ?? 'ID',
        ip: meta.ip,
        userAgent: meta.userAgent,
        valid,
      },
    });

    return {
      valid,
      reason: revoked ? ('REVOKED' as const) : hashMatches ? ('OK' as const) : ('TAMPERED' as const),
      certificate: valid
        ? {
            certificateId: cert.certificateId,
            type: cert.type,
            studentName: cert.studentName,
            organizationName: cert.organizationName,
            domainName: cert.domainName,
            title: cert.title,
            grade: cert.grade,
            durationWeeks: cert.durationWeeks,
            startDate: cert.startDate,
            endDate: cert.endDate,
            issueDate: cert.issueDate,
            verificationNumber: cert.verificationNumber,
          }
        : undefined,
    };
  }

  listForStudent(studentProfileId: string) {
    return this.prisma.certificate.findMany({
      where: { studentId: studentProfileId },
      orderBy: { issueDate: 'desc' },
    });
  }

  async getByCertificateId(certificateId: string) {
    const cert = await this.prisma.certificate.findUnique({ where: { certificateId } });
    if (!cert) throw new NotFoundException('Certificate not found');
    return cert;
  }

  async revoke(certificateId: string, reason: string) {
    await this.getByCertificateId(certificateId);
    return this.prisma.certificate.update({
      where: { certificateId },
      data: { status: CertificateStatus.REVOKED, revokedAt: new Date(), revokeReason: reason },
    });
  }

  // ── internals ────────────────────────────────────────────────────────────────

  private async persistCertificate(input: {
    type: CertificateType;
    studentProfileId: string;
    applicationId?: string;
    issuedByUserId: string;
    studentName: string;
    organizationName: string;
    domainName: string;
    title: string;
    durationWeeks?: number | null;
    startDate?: Date | null;
    endDate?: Date | null;
    grade?: string;
  }): Promise<Certificate> {
    const year = new Date().getFullYear();
    const certificateId = `INF-${year}-${certCode()}`;
    const verificationNumber = verifyToken();
    const issueDate = new Date();

    const content: CertificateContent = {
      certificateId,
      studentName: input.studentName,
      organizationName: input.organizationName,
      domainName: input.domainName,
      title: input.title,
      durationWeeks: input.durationWeeks ?? null,
      startDate: input.startDate ? input.startDate.toISOString() : null,
      endDate: input.endDate ? input.endDate.toISOString() : null,
      grade: input.grade ?? null,
      issueDate: issueDate.toISOString(),
    };

    const contentHash = hashContent(content);
    const signature = signHash(contentHash, this.config.get<string>('certificates.signingKey'));
    const verifyBaseUrl = this.config.get<string>('certificates.verifyBaseUrl') ?? 'http://localhost:3000/verify';
    const qrPayloadUrl = `${verifyBaseUrl}/${certificateId}`;

    // QR code as a data-URL — production would upload the PDF+QR to S3/R2 and
    // store the resulting object URL in pdfUrl. We keep the QR inline here.
    let qrDataUrl = qrPayloadUrl;
    try {
      qrDataUrl = await QRCode.toDataURL(qrPayloadUrl, { errorCorrectionLevel: 'M', margin: 1, width: 256 });
    } catch (err) {
      this.logger.warn(`QR generation failed, storing plain URL: ${(err as Error).message}`);
    }

    return this.prisma.certificate.create({
      data: {
        certificateId,
        type: input.type,
        status: CertificateStatus.ISSUED,
        studentId: input.studentProfileId,
        applicationId: input.applicationId,
        issuedById: input.issuedByUserId,
        studentName: input.studentName,
        organizationName: input.organizationName,
        domainName: input.domainName,
        title: input.title,
        durationWeeks: input.durationWeeks ?? undefined,
        startDate: input.startDate ?? undefined,
        endDate: input.endDate ?? undefined,
        grade: (input.grade as Certificate['grade']) ?? undefined,
        verificationNumber,
        qrPayloadUrl: qrDataUrl,
        contentHash,
        signature: signature ?? undefined,
        issueDate,
      },
    });
  }

  private toContent(cert: Certificate): CertificateContent {
    return {
      certificateId: cert.certificateId,
      studentName: cert.studentName,
      organizationName: cert.organizationName,
      domainName: cert.domainName,
      title: cert.title,
      durationWeeks: cert.durationWeeks ?? null,
      startDate: cert.startDate ? cert.startDate.toISOString() : null,
      endDate: cert.endDate ? cert.endDate.toISOString() : null,
      grade: cert.grade ?? null,
      issueDate: cert.issueDate.toISOString(),
    };
  }

  private async awardCertifiedBadge(studentProfileId: string) {
    const badge = await this.prisma.badge.findUnique({ where: { slug: 'certified' } });
    if (!badge) return;
    await this.prisma.studentBadge
      .create({ data: { studentId: studentProfileId, badgeId: badge.id } })
      .catch(() => undefined);
  }
}
