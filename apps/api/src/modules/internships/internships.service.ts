import {
  ForbiddenException,
  Injectable,
  NotFoundException,
} from '@nestjs/common';
import { InternshipStatus, Prisma } from '@prisma/client';
import { customAlphabet } from 'nanoid';
import { PrismaService } from '../../prisma/prisma.service';
import { paginate } from '../../common/dto/pagination.dto';
import {
  CreateInternshipDto,
  QueryInternshipDto,
  UpdateInternshipDto,
} from './dto/internship.dto';

const slugId = customAlphabet('0123456789abcdefghijklmnopqrstuvwxyz', 6);

@Injectable()
export class InternshipsService {
  constructor(private readonly prisma: PrismaService) {}

  /** Public catalog search — only OPEN internships are visible to anonymous users. */
  async search(dto: QueryInternshipDto, includeAllStatuses = false) {
    const where: Prisma.InternshipWhereInput = {
      ...(includeAllStatuses ? {} : { status: InternshipStatus.OPEN }),
      ...(dto.status && includeAllStatuses ? { status: dto.status } : {}),
      ...(dto.domain ? { domain: { slug: dto.domain } } : {}),
      ...(dto.branch ? { branch: { slug: dto.branch } } : {}),
      ...(dto.workMode ? { workMode: dto.workMode } : {}),
      ...(dto.minStipend ? { stipendMax: { gte: dto.minStipend } } : {}),
      ...(dto.q
        ? {
            OR: [
              { title: { contains: dto.q, mode: 'insensitive' } },
              { description: { contains: dto.q, mode: 'insensitive' } },
            ],
          }
        : {}),
    };

    const [items, total] = await this.prisma.$transaction([
      this.prisma.internship.findMany({
        where,
        skip: dto.skip,
        take: dto.limit,
        orderBy: { createdAt: 'desc' },
        include: {
          organization: { select: { companyName: true, logoUrl: true, verified: true } },
          domain: true,
          branch: true,
          skills: { include: { skill: true } },
          _count: { select: { applications: true } },
        },
      }),
      this.prisma.internship.count({ where }),
    ]);

    return paginate(items, total, dto.page, dto.limit);
  }

  async findBySlug(slug: string) {
    const internship = await this.prisma.internship.findUnique({
      where: { slug },
      include: {
        organization: true,
        domain: true,
        branch: true,
        skills: { include: { skill: true } },
        tasks: true,
        _count: { select: { applications: true } },
      },
    });
    if (!internship) throw new NotFoundException('Internship not found');
    // best-effort view counter
    await this.prisma.internship.update({ where: { slug }, data: { viewsCount: { increment: 1 } } }).catch(() => undefined);
    return internship;
  }

  async create(organizationProfileId: string, dto: CreateInternshipDto) {
    const slug = `${this.slugify(dto.title)}-${slugId()}`;
    return this.prisma.internship.create({
      data: {
        slug,
        title: dto.title,
        description: dto.description,
        responsibilities: dto.responsibilities,
        eligibility: dto.eligibility,
        organizationId: organizationProfileId,
        domainId: dto.domainId,
        branchId: dto.branchId,
        workMode: dto.workMode,
        location: dto.location,
        stipendMin: dto.stipendMin,
        stipendMax: dto.stipendMax,
        durationWeeks: dto.durationWeeks,
        openings: dto.openings,
        applyByDate: dto.applyByDate ? new Date(dto.applyByDate) : undefined,
        startDate: dto.startDate ? new Date(dto.startDate) : undefined,
        status: InternshipStatus.DRAFT,
        skills: dto.skillIds?.length
          ? { create: dto.skillIds.map((skillId) => ({ skillId })) }
          : undefined,
      },
      include: { skills: { include: { skill: true } } },
    });
  }

  async update(organizationProfileId: string, id: string, dto: UpdateInternshipDto) {
    await this.assertOwner(organizationProfileId, id);
    return this.prisma.internship.update({
      where: { id },
      data: {
        title: dto.title,
        description: dto.description,
        responsibilities: dto.responsibilities,
        eligibility: dto.eligibility,
        domainId: dto.domainId,
        branchId: dto.branchId,
        workMode: dto.workMode,
        location: dto.location,
        stipendMin: dto.stipendMin,
        stipendMax: dto.stipendMax,
        durationWeeks: dto.durationWeeks,
        openings: dto.openings,
        applyByDate: dto.applyByDate ? new Date(dto.applyByDate) : undefined,
        startDate: dto.startDate ? new Date(dto.startDate) : undefined,
      },
    });
  }

  /** Organization submits a draft for admin approval. */
  async submitForApproval(organizationProfileId: string, id: string) {
    await this.assertOwner(organizationProfileId, id);
    return this.prisma.internship.update({
      where: { id },
      data: { status: InternshipStatus.PENDING_APPROVAL },
    });
  }

  async close(organizationProfileId: string, id: string) {
    await this.assertOwner(organizationProfileId, id);
    return this.prisma.internship.update({ where: { id }, data: { status: InternshipStatus.CLOSED } });
  }

  /** Listings owned by the current organization (all statuses). */
  listForOrganization(organizationProfileId: string, dto: QueryInternshipDto) {
    return this.search({ ...dto } as QueryInternshipDto, true).then(async (result) => {
      const owned = await this.prisma.internship.findMany({
        where: { organizationId: organizationProfileId },
        orderBy: { createdAt: 'desc' },
        include: { domain: true, _count: { select: { applications: true } } },
      });
      return { ...result, items: owned, meta: { ...result.meta, total: owned.length } };
    });
  }

  // ── Admin approval ───────────────────────────────────────────────────────

  pendingApproval() {
    return this.prisma.internship.findMany({
      where: { status: InternshipStatus.PENDING_APPROVAL },
      orderBy: { createdAt: 'asc' },
      include: { organization: { select: { companyName: true } }, domain: true },
    });
  }

  async approve(adminUserId: string, id: string) {
    await this.getOrThrow(id);
    return this.prisma.internship.update({
      where: { id },
      data: { status: InternshipStatus.OPEN, approvedById: adminUserId, approvedAt: new Date() },
    });
  }

  async reject(id: string) {
    await this.getOrThrow(id);
    return this.prisma.internship.update({ where: { id }, data: { status: InternshipStatus.DRAFT } });
  }

  // ── helpers ────────────────────────────────────────────────────────────────

  private async getOrThrow(id: string) {
    const internship = await this.prisma.internship.findUnique({ where: { id } });
    if (!internship) throw new NotFoundException('Internship not found');
    return internship;
  }

  private async assertOwner(organizationProfileId: string, id: string) {
    const internship = await this.getOrThrow(id);
    if (internship.organizationId !== organizationProfileId) {
      throw new ForbiddenException('You do not own this internship');
    }
    return internship;
  }

  private slugify(value: string): string {
    return value.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 60);
  }
}
