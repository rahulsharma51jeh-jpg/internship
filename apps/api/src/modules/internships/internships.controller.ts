import {
  Body,
  Controller,
  ForbiddenException,
  Get,
  Param,
  Patch,
  Post,
  Query,
} from '@nestjs/common';
import { ApiBearerAuth, ApiOperation, ApiTags } from '@nestjs/swagger';
import { UserRole } from '@prisma/client';
import { Public } from '../../common/decorators/public.decorator';
import { Roles } from '../../common/decorators/roles.decorator';
import { AuthUser, CurrentUser } from '../../common/decorators/current-user.decorator';
import {
  CreateInternshipDto,
  QueryInternshipDto,
  UpdateInternshipDto,
} from './dto/internship.dto';
import { InternshipsService } from './internships.service';

@ApiTags('internships')
@Controller('internships')
export class InternshipsController {
  constructor(private readonly internships: InternshipsService) {}

  // ── Public catalog ─────────────────────────────────────────────────────────

  @Public()
  @Get()
  @ApiOperation({ summary: 'Search the public internship catalog (OPEN only)' })
  search(@Query() query: QueryInternshipDto) {
    return this.internships.search(query);
  }

  @Public()
  @Get(':slug')
  @ApiOperation({ summary: 'Get internship details by slug' })
  detail(@Param('slug') slug: string) {
    return this.internships.findBySlug(slug);
  }

  // ── Organization ─────────────────────────────────────────────────────────────

  @ApiBearerAuth()
  @Roles(UserRole.ORGANIZATION)
  @Get('me/listings')
  @ApiOperation({ summary: '[Org] List my internship postings' })
  myListings(@CurrentUser() user: AuthUser, @Query() query: QueryInternshipDto) {
    return this.internships.listForOrganization(this.orgId(user), query);
  }

  @ApiBearerAuth()
  @Roles(UserRole.ORGANIZATION)
  @Post()
  @ApiOperation({ summary: '[Org] Create an internship (starts as DRAFT)' })
  create(@CurrentUser() user: AuthUser, @Body() dto: CreateInternshipDto) {
    return this.internships.create(this.orgId(user), dto);
  }

  @ApiBearerAuth()
  @Roles(UserRole.ORGANIZATION)
  @Patch(':id')
  @ApiOperation({ summary: '[Org] Update an internship' })
  update(@CurrentUser() user: AuthUser, @Param('id') id: string, @Body() dto: UpdateInternshipDto) {
    return this.internships.update(this.orgId(user), id, dto);
  }

  @ApiBearerAuth()
  @Roles(UserRole.ORGANIZATION)
  @Post(':id/submit')
  @ApiOperation({ summary: '[Org] Submit a draft for admin approval' })
  submit(@CurrentUser() user: AuthUser, @Param('id') id: string) {
    return this.internships.submitForApproval(this.orgId(user), id);
  }

  @ApiBearerAuth()
  @Roles(UserRole.ORGANIZATION)
  @Post(':id/close')
  @ApiOperation({ summary: '[Org] Close an internship' })
  close(@CurrentUser() user: AuthUser, @Param('id') id: string) {
    return this.internships.close(this.orgId(user), id);
  }

  // ── Admin approval ───────────────────────────────────────────────────────────

  @ApiBearerAuth()
  @Roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)
  @Get('admin/pending')
  @ApiOperation({ summary: '[Admin] List internships pending approval' })
  pending() {
    return this.internships.pendingApproval();
  }

  @ApiBearerAuth()
  @Roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)
  @Post(':id/approve')
  @ApiOperation({ summary: '[Admin] Approve & publish an internship' })
  approve(@CurrentUser() user: AuthUser, @Param('id') id: string) {
    return this.internships.approve(user.id, id);
  }

  @ApiBearerAuth()
  @Roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)
  @Post(':id/reject')
  @ApiOperation({ summary: '[Admin] Reject (send back to draft)' })
  reject(@Param('id') id: string) {
    return this.internships.reject(id);
  }

  private orgId(user: AuthUser): string {
    if (!user.organizationProfileId) {
      throw new ForbiddenException('Not an organization account');
    }
    return user.organizationProfileId;
  }
}
