import {
  BadRequestException,
  Body,
  Controller,
  ForbiddenException,
  Get,
  Param,
  Patch,
  Query,
} from '@nestjs/common';
import { ApiBearerAuth, ApiOperation, ApiTags } from '@nestjs/swagger';
import { AccountStatus, UserRole } from '@prisma/client';
import { AuthUser, CurrentUser } from '../../common/decorators/current-user.decorator';
import { Roles } from '../../common/decorators/roles.decorator';
import { PaginationDto } from '../../common/dto/pagination.dto';
import { UpdateStudentProfileDto } from './dto/update-profile.dto';
import { UsersService } from './users.service';

@ApiTags('users')
@ApiBearerAuth()
@Controller('users')
export class UsersController {
  constructor(private readonly users: UsersService) {}

  @Get('me/profile')
  @ApiOperation({ summary: 'Get my student profile' })
  getMyProfile(@CurrentUser() user: AuthUser) {
    if (!user.studentProfileId) throw new ForbiddenException('Not a student account');
    return this.users.getStudentProfile(user.studentProfileId);
  }

  @Patch('me/profile')
  @ApiOperation({ summary: 'Update my student profile (recomputes completion score)' })
  updateMyProfile(@CurrentUser() user: AuthUser, @Body() dto: UpdateStudentProfileDto) {
    if (!user.studentProfileId) throw new ForbiddenException('Not a student account');
    return this.users.updateStudentProfile(user.studentProfileId, dto);
  }

  @Get('me/dashboard')
  @ApiOperation({ summary: 'Personalized student dashboard (stats + recommendations)' })
  dashboard(@CurrentUser() user: AuthUser) {
    if (!user.studentProfileId) throw new ForbiddenException('Not a student account');
    return this.users.studentDashboard(user.studentProfileId);
  }

  // ── Admin ──────────────────────────────────────────────────────────────────

  @Get()
  @Roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)
  @ApiOperation({ summary: '[Admin] List/search users' })
  list(@Query() pagination: PaginationDto) {
    return this.users.listUsers(pagination);
  }

  @Patch(':id/status')
  @Roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)
  @ApiOperation({ summary: '[Admin] Activate / suspend / ban a user' })
  setStatus(@Param('id') id: string, @Body('status') status: AccountStatus) {
    if (!Object.values(AccountStatus).includes(status)) {
      throw new BadRequestException('Invalid account status');
    }
    return this.users.setAccountStatus(id, status);
  }
}
