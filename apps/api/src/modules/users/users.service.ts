import { ForbiddenException, Injectable, NotFoundException } from '@nestjs/common';
import { AccountStatus, ApplicationStatus, Prisma } from '@prisma/client';
import { PrismaService } from '../../prisma/prisma.service';
import { PaginationDto, paginate } from '../../common/dto/pagination.dto';
import { UpdateStudentProfileDto } from './dto/update-profile.dto';

/**
 * Weights used to compute a student's profile-completion score (0-100).
 * Surfaced on the dashboard as a nudge to finish the profile.
 */
const COMPLETION_WEIGHTS: Record<string, number> = {
  branchId: 15,
  collegeName: 10,
  graduationYear: 10,
  cgpa: 10,
  city: 5,
  bio: 10,
  resumeUrl: 15,
  portfolioUrl: 5,
  linkedinUrl: 10,
  githubUrl: 10,
};

@Injectable()
export class UsersService {
  constructor(private readonly prisma: PrismaService) {}

  async getStudentProfile(studentProfileId: string) {
    const profile = await this.prisma.studentProfile.findUnique({
      where: { id: studentProfileId },
      include: {
        user: { select: { fullName: true, email: true, avatarUrl: true } },
        branch: true,
        skills: { include: { skill: true } },
        badges: { include: { badge: true } },
      },
    });
    if (!profile) throw new NotFoundException('Student profile not found');
    return profile;
  }

  async updateStudentProfile(studentProfileId: string, dto: UpdateStudentProfileDto) {
    const completion = this.computeCompletion(dto);
    const updated = await this.prisma.studentProfile.update({
      where: { id: studentProfileId },
      data: { ...dto, profileCompletion: completion },
    });
    return updated;
  }

  /** Aggregated data for the personalized student dashboard. */
  async studentDashboard(studentProfileId: string) {
    const profile = await this.prisma.studentProfile.findUniqueOrThrow({
      where: { id: studentProfileId },
      include: { branch: true, skills: { include: { skill: true } } },
    });

    // groupBy is kept outside $transaction so its `_count` typing stays precise.
    const [grouped, certificates, badges] = await Promise.all([
      this.prisma.application.groupBy({
        by: ['status'],
        where: { studentId: studentProfileId },
        _count: { _all: true },
        orderBy: { status: 'asc' },
      }),
      this.prisma.certificate.count({ where: { studentId: studentProfileId } }),
      this.prisma.studentBadge.count({ where: { studentId: studentProfileId } }),
    ]);

    const byStatus = {} as Record<ApplicationStatus, number>;
    let totalApplications = 0;
    for (const row of grouped) {
      const count = row._count._all;
      byStatus[row.status] = count;
      totalApplications += count;
    }

    const recommendations = await this.recommendInternships(studentProfileId, profile.branchId);

    return {
      profile,
      stats: {
        profileCompletion: profile.profileCompletion,
        xpPoints: profile.xpPoints,
        level: profile.level,
        certificates,
        badges,
        applications: { total: totalApplications, byStatus },
      },
      recommendations,
    };
  }

  /**
   * Lightweight recommender: prioritises open internships in the student's branch,
   * newest first. (The AI recommender service can later replace this heuristic.)
   */
  private recommendInternships(studentProfileId: string, branchId: string | null) {
    void studentProfileId;
    return this.prisma.internship.findMany({
      where: { status: 'OPEN', ...(branchId ? { branchId } : {}) },
      take: 6,
      orderBy: { createdAt: 'desc' },
      include: { organization: { select: { companyName: true, logoUrl: true } }, domain: true },
    });
  }

  // ── Admin: user management ─────────────────────────────────────────────────

  async listUsers(dto: PaginationDto) {
    const where: Prisma.UserWhereInput = dto.q
      ? { OR: [{ email: { contains: dto.q, mode: 'insensitive' } }, { fullName: { contains: dto.q, mode: 'insensitive' } }] }
      : {};

    const [items, total] = await this.prisma.$transaction([
      this.prisma.user.findMany({
        where,
        skip: dto.skip,
        take: dto.limit,
        orderBy: { createdAt: 'desc' },
        select: { id: true, email: true, fullName: true, roles: true, status: true, createdAt: true },
      }),
      this.prisma.user.count({ where }),
    ]);
    return paginate(items, total, dto.page, dto.limit);
  }

  async setAccountStatus(userId: string, status: AccountStatus) {
    const user = await this.prisma.user.findUnique({ where: { id: userId } });
    if (!user) throw new NotFoundException('User not found');
    if (user.roles.includes('SUPER_ADMIN')) {
      throw new ForbiddenException('Cannot change status of a super admin');
    }
    return this.prisma.user.update({
      where: { id: userId },
      data: { status },
      select: { id: true, status: true },
    });
  }

  // ── helpers ────────────────────────────────────────────────────────────────

  private computeCompletion(dto: UpdateStudentProfileDto): number {
    let score = 0;
    for (const [field, weight] of Object.entries(COMPLETION_WEIGHTS)) {
      const value = (dto as Record<string, unknown>)[field];
      if (value !== undefined && value !== null && value !== '') {
        score += weight;
      }
    }
    return Math.min(100, score);
  }
}
