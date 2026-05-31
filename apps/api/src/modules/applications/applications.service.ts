import {
  BadRequestException,
  ForbiddenException,
  Injectable,
  NotFoundException,
} from '@nestjs/common';
import {
  Application,
  ApplicationStatus,
  Prisma,
  TaskStatus,
} from '@prisma/client';
import { PrismaService } from '../../prisma/prisma.service';
import { AuthUser } from '../../common/decorators/current-user.decorator';
import { WorkflowEngine } from './workflow.engine';
import {
  ApplyDto,
  EvaluateDto,
  MarkAttendanceDto,
  MentorFeedbackDto,
  ReviewTaskDto,
  SubmitTaskDto,
  TransitionDto,
  WeeklyReportDto,
} from './dto/application.dto';

const XP_ON_APPLY = 25;
const XP_ON_SELECTED = 100;
const XP_ON_COMPLETE = 300;

@Injectable()
export class ApplicationsService {
  constructor(
    private readonly prisma: PrismaService,
    private readonly workflow: WorkflowEngine,
  ) {}

  // ── Student: apply & track ───────────────────────────────────────────────────

  async apply(studentProfileId: string, dto: ApplyDto): Promise<Application> {
    const internship = await this.prisma.internship.findUnique({ where: { id: dto.internshipId } });
    if (!internship) throw new NotFoundException('Internship not found');
    if (internship.status !== 'OPEN') {
      throw new BadRequestException('This internship is not open for applications');
    }
    if (internship.applyByDate && internship.applyByDate < new Date()) {
      throw new BadRequestException('The application deadline has passed');
    }

    const existing = await this.prisma.application.findUnique({
      where: { studentId_internshipId: { studentId: studentProfileId, internshipId: dto.internshipId } },
    });
    if (existing) throw new BadRequestException('You have already applied to this internship');

    // Pull student portfolio defaults if not supplied in the one-click apply.
    const profile = await this.prisma.studentProfile.findUniqueOrThrow({ where: { id: studentProfileId } });

    const application = await this.prisma.$transaction(async (tx) => {
      const created = await tx.application.create({
        data: {
          studentId: studentProfileId,
          internshipId: dto.internshipId,
          status: ApplicationStatus.APPLIED,
          coverLetter: dto.coverLetter,
          resumeUrl: dto.resumeUrl ?? profile.resumeUrl,
          portfolioUrl: dto.portfolioUrl ?? profile.portfolioUrl,
          linkedinUrl: dto.linkedinUrl ?? profile.linkedinUrl,
          githubUrl: dto.githubUrl ?? profile.githubUrl,
          history: { create: { toStatus: ApplicationStatus.APPLIED, actorId: studentProfileId } },
        },
      });
      await tx.studentProfile.update({
        where: { id: studentProfileId },
        data: { xpPoints: { increment: XP_ON_APPLY } },
      });
      return created;
    });

    await this.awardBadge(studentProfileId, 'first-application');
    return application;
  }

  listForStudent(studentProfileId: string, status?: ApplicationStatus) {
    return this.prisma.application.findMany({
      where: { studentId: studentProfileId, ...(status ? { status } : {}) },
      orderBy: { appliedAt: 'desc' },
      include: {
        internship: {
          include: { organization: { select: { companyName: true, logoUrl: true } }, domain: true },
        },
        certificate: { select: { certificateId: true, pdfUrl: true } },
      },
    });
  }

  async getForStudent(studentProfileId: string, id: string) {
    const application = await this.prisma.application.findUnique({
      where: { id },
      include: {
        internship: { include: { organization: true, domain: true } },
        history: { orderBy: { createdAt: 'asc' } },
        taskSubmissions: { orderBy: { weekNumber: 'asc' } },
        attendance: { orderBy: { date: 'desc' } },
        weeklyReports: { orderBy: { weekNumber: 'asc' } },
        feedback: { orderBy: { createdAt: 'desc' } },
        certificate: true,
      },
    });
    if (!application || application.studentId !== studentProfileId) {
      throw new NotFoundException('Application not found');
    }
    return application;
  }

  // ── Organization: applicant pipeline ─────────────────────────────────────────

  async listForOrganization(organizationProfileId: string, internshipId?: string, status?: ApplicationStatus) {
    const where: Prisma.ApplicationWhereInput = {
      internship: { organizationId: organizationProfileId },
      ...(internshipId ? { internshipId } : {}),
      ...(status ? { status } : {}),
    };
    return this.prisma.application.findMany({
      where,
      orderBy: { appliedAt: 'desc' },
      include: {
        student: {
          include: {
            user: { select: { fullName: true, email: true, avatarUrl: true } },
            branch: true,
            skills: { include: { skill: true } },
          },
        },
        internship: { select: { title: true, slug: true } },
      },
    });
  }

  // ── Workflow transitions ──────────────────────────────────────────────────────

  async transition(actor: AuthUser, id: string, dto: TransitionDto) {
    const application = await this.prisma.application.findUnique({
      where: { id },
      include: { internship: true },
    });
    if (!application) throw new NotFoundException('Application not found');

    this.assertActorCanDrive(actor, application, dto.to);
    this.workflow.assertTransition(application.status, dto.to);

    const timestamps = this.timestampsForStatus(dto.to);

    const updated = await this.prisma.$transaction(async (tx) => {
      const result = await tx.application.update({
        where: { id },
        data: {
          status: dto.to,
          ...timestamps,
          ...(dto.to === ApplicationStatus.REJECTED ? { rejectionNote: dto.note } : {}),
          history: {
            create: { fromStatus: application.status, toStatus: dto.to, note: dto.note, actorId: actor.id },
          },
        },
      });

      if (dto.to === ApplicationStatus.SELECTED) {
        await tx.studentProfile.update({
          where: { id: application.studentId },
          data: { xpPoints: { increment: XP_ON_SELECTED } },
        });
      }
      if (dto.to === ApplicationStatus.COMPLETED) {
        await tx.studentProfile.update({
          where: { id: application.studentId },
          data: { xpPoints: { increment: XP_ON_COMPLETE } },
        });
      }
      return result;
    });

    if (dto.to === ApplicationStatus.ONGOING) await this.awardBadge(application.studentId, 'first-internship');
    return updated;
  }

  /** Org records the final performance evaluation, advancing to completion approval. */
  async evaluate(organizationProfileId: string, id: string, dto: EvaluateDto) {
    const application = await this.prisma.application.findUnique({
      where: { id },
      include: { internship: true },
    });
    if (!application) throw new NotFoundException('Application not found');
    if (application.internship.organizationId !== organizationProfileId) {
      throw new ForbiddenException('Not your applicant');
    }
    this.workflow.assertTransition(application.status, ApplicationStatus.COMPLETION_APPROVAL);

    return this.prisma.application.update({
      where: { id },
      data: {
        finalGrade: dto.grade,
        finalScore: dto.score,
        status: ApplicationStatus.COMPLETION_APPROVAL,
        history: {
          create: {
            fromStatus: application.status,
            toStatus: ApplicationStatus.COMPLETION_APPROVAL,
            note: dto.note ?? `Graded ${dto.grade} (${dto.score}/100)`,
            actorId: organizationProfileId,
          },
        },
      },
    });
  }

  // ── Workspace: tasks, attendance, reports, feedback ───────────────────────────

  async submitTask(studentProfileId: string, applicationId: string, dto: SubmitTaskDto) {
    await this.assertStudentOwnsActive(studentProfileId, applicationId);
    return this.prisma.taskSubmission.create({
      data: {
        applicationId,
        title: dto.title,
        description: dto.description,
        submissionUrl: dto.submissionUrl,
        weekNumber: dto.weekNumber ?? 1,
        status: TaskStatus.SUBMITTED,
        submittedAt: new Date(),
      },
    });
  }

  async reviewTask(organizationProfileId: string, taskId: string, dto: ReviewTaskDto) {
    const task = await this.prisma.taskSubmission.findUnique({
      where: { id: taskId },
      include: { application: { include: { internship: true } } },
    });
    if (!task) throw new NotFoundException('Task not found');
    if (task.application.internship.organizationId !== organizationProfileId) {
      throw new ForbiddenException('Not your applicant');
    }
    return this.prisma.taskSubmission.update({
      where: { id: taskId },
      data: { status: dto.status, score: dto.score, reviewerNote: dto.reviewerNote, reviewedAt: new Date() },
    });
  }

  async markAttendance(studentProfileId: string, applicationId: string, dto: MarkAttendanceDto) {
    await this.assertStudentOwnsActive(studentProfileId, applicationId);
    const date = new Date(dto.date);
    return this.prisma.attendanceRecord.upsert({
      where: { applicationId_date: { applicationId, date } },
      update: { present: dto.present ?? true, hours: dto.hours },
      create: { applicationId, date, present: dto.present ?? true, hours: dto.hours },
    });
  }

  async submitWeeklyReport(studentProfileId: string, applicationId: string, dto: WeeklyReportDto) {
    await this.assertStudentOwnsActive(studentProfileId, applicationId);
    return this.prisma.weeklyReport.upsert({
      where: { applicationId_weekNumber: { applicationId, weekNumber: dto.weekNumber } },
      update: { summary: dto.summary, hoursLogged: dto.hoursLogged, blockers: dto.blockers },
      create: {
        applicationId,
        weekNumber: dto.weekNumber,
        summary: dto.summary,
        hoursLogged: dto.hoursLogged,
        blockers: dto.blockers,
      },
    });
  }

  async addMentorFeedback(mentorUserId: string, applicationId: string, dto: MentorFeedbackDto) {
    const application = await this.prisma.application.findUnique({ where: { id: applicationId } });
    if (!application) throw new NotFoundException('Application not found');
    return this.prisma.mentorFeedback.create({
      data: {
        applicationId,
        mentorId: mentorUserId,
        rating: dto.rating,
        comment: dto.comment,
        weekNumber: dto.weekNumber,
      },
    });
  }

  // ── helpers ────────────────────────────────────────────────────────────────

  private timestampsForStatus(status: ApplicationStatus): Partial<Prisma.ApplicationUpdateInput> {
    switch (status) {
      case ApplicationStatus.SELECTED:
        return { selectedAt: new Date() };
      case ApplicationStatus.ONGOING:
        return { startedAt: new Date() };
      case ApplicationStatus.COMPLETED:
        return { completedAt: new Date() };
      case ApplicationStatus.REJECTED:
        return { rejectedAt: new Date() };
      default:
        return {};
    }
  }

  private assertActorCanDrive(actor: AuthUser, application: Application & { internship: { organizationId: string } }, to: ApplicationStatus) {
    const isAdmin = actor.roles.some((r) => r === 'ADMIN' || r === 'SUPER_ADMIN');
    const isOrgOwner = actor.organizationProfileId === application.internship.organizationId;
    const isStudentOwner = actor.studentProfileId === application.studentId;

    // Students may only withdraw their own application.
    if (to === ApplicationStatus.WITHDRAWN) {
      if (!isStudentOwner && !isAdmin) throw new ForbiddenException('Only the applicant can withdraw');
      return;
    }
    // Admin-only transitions.
    const adminOnly: ApplicationStatus[] = [
      ApplicationStatus.ADMIN_REVIEW,
      ApplicationStatus.ORG_REVIEW,
      ApplicationStatus.COMPLETED,
    ];
    if (adminOnly.includes(to)) {
      if (!isAdmin) throw new ForbiddenException('Admin action required');
      return;
    }
    // Org-driven transitions.
    if (!isOrgOwner && !isAdmin) {
      throw new ForbiddenException('Organization action required');
    }
  }

  private async assertStudentOwnsActive(studentProfileId: string, applicationId: string) {
    const application = await this.prisma.application.findUnique({ where: { id: applicationId } });
    if (!application || application.studentId !== studentProfileId) {
      throw new NotFoundException('Application not found');
    }
    const activeStates: ApplicationStatus[] = [
      ApplicationStatus.SELECTED,
      ApplicationStatus.ONGOING,
      ApplicationStatus.PERFORMANCE_EVALUATION,
    ];
    if (!activeStates.includes(application.status)) {
      throw new BadRequestException('Workspace is only available for active internships');
    }
    return application;
  }

  private async awardBadge(studentProfileId: string, badgeSlug: string) {
    const badge = await this.prisma.badge.findUnique({ where: { slug: badgeSlug } });
    if (!badge) return;
    await this.prisma.studentBadge
      .create({ data: { studentId: studentProfileId, badgeId: badge.id } })
      .catch(() => undefined); // ignore duplicates
  }
}
