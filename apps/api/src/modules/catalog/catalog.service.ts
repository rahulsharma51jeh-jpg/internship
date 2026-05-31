import { Injectable } from '@nestjs/common';
import { PrismaService } from '../../prisma/prisma.service';

@Injectable()
export class CatalogService {
  constructor(private readonly prisma: PrismaService) {}

  branches() {
    return this.prisma.branch.findMany({ orderBy: { name: 'asc' } });
  }

  async domains() {
    const domains = await this.prisma.domain.findMany({ orderBy: { name: 'asc' } });
    // group by category for convenient UI rendering
    const grouped: Record<string, typeof domains> = {};
    for (const d of domains) {
      (grouped[d.category] ??= []).push(d);
    }
    return { all: domains, grouped };
  }

  skills() {
    return this.prisma.skill.findMany({ orderBy: { name: 'asc' } });
  }

  badges() {
    return this.prisma.badge.findMany({ orderBy: { xpReward: 'desc' } });
  }
}
