import {
  Body,
  Controller,
  ForbiddenException,
  Get,
  Param,
  Post,
  Req,
} from '@nestjs/common';
import { ApiBearerAuth, ApiOperation, ApiTags } from '@nestjs/swagger';
import { UserRole } from '@prisma/client';
import { Request } from 'express';
import { Public } from '../../common/decorators/public.decorator';
import { Roles } from '../../common/decorators/roles.decorator';
import { AuthUser, CurrentUser } from '../../common/decorators/current-user.decorator';
import { CertificatesService } from './certificates.service';
import { BulkIssueDto, IssueManualCertificateDto } from './dto/certificate.dto';

@ApiTags('certificates')
@Controller('certificates')
export class CertificatesController {
  constructor(private readonly certificates: CertificatesService) {}

  // ── Public verification portal ──────────────────────────────────────────────

  @Public()
  @Get('verify/:identifier')
  @ApiOperation({ summary: 'Verify a certificate by ID or verification number' })
  verify(@Param('identifier') identifier: string, @Req() req: Request) {
    return this.certificates.verify(identifier, {
      ip: req.ip,
      userAgent: req.headers['user-agent'],
      method: identifier.startsWith('INF-') ? 'ID' : 'LINK',
    });
  }

  // ── Student ──────────────────────────────────────────────────────────────────

  @ApiBearerAuth()
  @Roles(UserRole.STUDENT)
  @Get('me')
  @ApiOperation({ summary: '[Student] List my earned certificates' })
  mine(@CurrentUser() user: AuthUser) {
    if (!user.studentProfileId) throw new ForbiddenException('Not a student account');
    return this.certificates.listForStudent(user.studentProfileId);
  }

  // ── Admin issuance & management ────────────────────────────────────────────────

  @ApiBearerAuth()
  @Roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)
  @Post('applications/:applicationId/issue')
  @ApiOperation({ summary: '[Admin] Auto-issue completion certificate for an application' })
  issueForApplication(@CurrentUser() user: AuthUser, @Param('applicationId') applicationId: string) {
    return this.certificates.issueForApplication(applicationId, user.id);
  }

  @ApiBearerAuth()
  @Roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)
  @Post('bulk-issue')
  @ApiOperation({ summary: '[Admin] Bulk-issue certificates for completed applications' })
  bulkIssue(@CurrentUser() user: AuthUser, @Body() dto: BulkIssueDto) {
    return this.certificates.bulkIssue(dto, user.id);
  }

  @ApiBearerAuth()
  @Roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)
  @Post('manual')
  @ApiOperation({ summary: '[Admin] Manually issue a certificate (workshop/award/etc.)' })
  manual(@CurrentUser() user: AuthUser, @Body() dto: IssueManualCertificateDto) {
    return this.certificates.issueManual(dto, user.id);
  }

  @ApiBearerAuth()
  @Roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)
  @Post(':certificateId/revoke')
  @ApiOperation({ summary: '[Admin] Revoke a certificate' })
  revoke(@Param('certificateId') certificateId: string, @Body('reason') reason: string) {
    return this.certificates.revoke(certificateId, reason ?? 'Revoked by admin');
  }
}
