import { Injectable } from '@nestjs/common';
import { ApplicationStatus } from '@prisma/client';
import { PrismaService } from '../../prisma/prisma.service';

@Injectable()
export class AnalyticsService {
  constructor(private readonly prisma: PrismaService) {}

  /** Platform-wide KPIs for the admin analytics dashboard. */
  async platformOverview() {
    const [
      totalStudents,
      totalOrganizations,
      activeInternships,
      totalApplications,
      completed,
      certificates,
      selected,
    ] = await this.prisma.$transaction([
      this.prisma.studentProfile.count(),
      this.prisma.organizationProfile.count(),
      this.prisma.internship.count({ where: { status: 'OPEN' } }),
      this.prisma.application.count(),
      this.prisma.application.count({
        where: { status: { in: [ApplicationStatus.COMPLETED, ApplicationStatus.CERTIFICATE_GENERATED] } },
      }),
      this.prisma.certificate.count(),
      this.prisma.application.count({
        where: {
          status: {
            in: [
              ApplicationStatus.SELECTED,
              ApplicationStatus.ONGOING,
              ApplicationStatus.PERFORMANCE_EVALUATION,
              ApplicationStatus.COMPLETION_APPROVAL,
              ApplicationStatus.COMPLETED,
              ApplicationStatus.CERTIFICATE_GENERATED,
            ],
          },
        },
      }),
    ]);

    // groupBy kept outside $transaction so `_count` typing stays precise.
    const [byStatus, topDomains] = await Promise.all([
      this.prisma.application.groupBy({
        by: ['status'],
        _count: { _all: true },
        orderBy: { status: 'asc' },
      }),
      this.prisma.internship.groupBy({
        by: ['domainId'],
        _count: { _all: true },
        orderBy: { _count: { domainId: 'desc' } },
        take: 8,
      }),
    ]);

    // Resolve domain names for the top-domains chart.
    const domainIds = topDomains.map((d) => d.domainId);
    const domains = await this.prisma.domain.findMany({ where: { id: { in: domainIds } } });
    const domainMap = new Map(domains.map((d) => [d.id, d.name]));

    return {
      totals: {
        students: totalStudents,
        organizations: totalOrganizations,
        activeInternships,
        applications: totalApplications,
        certificates,
      },
      rates: {
        placementRate: totalApplications ? +((selected / totalApplications) * 100).toFixed(1) : 0,
        completionRate: selected ? +((completed / selected) * 100).toFixed(1) : 0,
      },
      applicationsByStatus: Object.fromEntries(byStatus.map((r) => [r.status, r._count._all])),
      topDomains: topDomains.map((d) => ({
        domain: domainMap.get(d.domainId) ?? 'Unknown',
        internships: d._count._all,
      })),
    };
  }

  /** Public leaderboard for the gamification system. */
  leaderboard(limit = 20) {
    return this.prisma.studentProfile.findMany({
      take: limit,
      orderBy: [{ xpPoints: 'desc' }, { level: 'desc' }],
      select: {
        id: true,
        xpPoints: true,
        level: true,
        collegeName: true,
        user: { select: { fullName: true, avatarUrl: true } },
        branch: { select: { name: true, shortCode: true } },
        _count: { select: { certificates: true, badges: true } },
      },
    });
  }
}
