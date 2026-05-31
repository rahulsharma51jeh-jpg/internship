import { Controller, Get, Query } from '@nestjs/common';
import { ApiBearerAuth, ApiOperation, ApiTags } from '@nestjs/swagger';
import { UserRole } from '@prisma/client';
import { Public } from '../../common/decorators/public.decorator';
import { Roles } from '../../common/decorators/roles.decorator';
import { AnalyticsService } from './analytics.service';

@ApiTags('analytics')
@Controller('analytics')
export class AnalyticsController {
  constructor(private readonly analytics: AnalyticsService) {}

  @ApiBearerAuth()
  @Roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)
  @Get('overview')
  @ApiOperation({ summary: '[Admin] Platform-wide KPIs' })
  overview() {
    return this.analytics.platformOverview();
  }

  @Public()
  @Get('leaderboard')
  @ApiOperation({ summary: 'Public XP leaderboard' })
  leaderboard(@Query('limit') limit?: string) {
    return this.analytics.leaderboard(limit ? parseInt(limit, 10) : 20);
  }
}
