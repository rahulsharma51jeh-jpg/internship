import {
  Body,
  Controller,
  ForbiddenException,
  Get,
  Param,
  Post,
  Query,
} from '@nestjs/common';
import { ApiBearerAuth, ApiOperation, ApiTags } from '@nestjs/swagger';
import { ApplicationStatus, UserRole } from '@prisma/client';
import { AuthUser, CurrentUser } from '../../common/decorators/current-user.decorator';
import { Roles } from '../../common/decorators/roles.decorator';
import { ApplicationsService } from './applications.service';
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

@ApiTags('applications')
@ApiBearerAuth()
@Controller('applications')
export class ApplicationsController {
  constructor(private readonly applications: ApplicationsService) {}

  // ── Student ──────────────────────────────────────────────────────────────────

  @Roles(UserRole.STUDENT)
  @Post()
  @ApiOperation({ summary: '[Student] One-click apply to an internship' })
  apply(@CurrentUser() user: AuthUser, @Body() dto: ApplyDto) {
    return this.applications.apply(this.studentId(user), dto);
  }

  @Roles(UserRole.STUDENT)
  @Get('me')
  @ApiOperation({ summary: '[Student] List my applications (optional status filter)' })
  myApplications(@CurrentUser() user: AuthUser, @Query('status') status?: ApplicationStatus) {
    return this.applications.listForStudent(this.studentId(user), status);
  }

  @Roles(UserRole.STUDENT)
  @Get('me/:id')
  @ApiOperation({ summary: '[Student] Get one application incl. workspace + history' })
  myApplication(@CurrentUser() user: AuthUser, @Param('id') id: string) {
    return this.applications.getForStudent(this.studentId(user), id);
  }

  @Roles(UserRole.STUDENT)
  @Post(':id/tasks')
  @ApiOperation({ summary: '[Student] Submit a project/task' })
  submitTask(@CurrentUser() user: AuthUser, @Param('id') id: string, @Body() dto: SubmitTaskDto) {
    return this.applications.submitTask(this.studentId(user), id, dto);
  }

  @Roles(UserRole.STUDENT)
  @Post(':id/attendance')
  @ApiOperation({ summary: '[Student] Mark attendance for a day' })
  attendance(@CurrentUser() user: AuthUser, @Param('id') id: string, @Body() dto: MarkAttendanceDto) {
    return this.applications.markAttendance(this.studentId(user), id, dto);
  }

  @Roles(UserRole.STUDENT)
  @Post(':id/weekly-report')
  @ApiOperation({ summary: '[Student] Submit / update a weekly report' })
  weeklyReport(@CurrentUser() user: AuthUser, @Param('id') id: string, @Body() dto: WeeklyReportDto) {
    return this.applications.submitWeeklyReport(this.studentId(user), id, dto);
  }

  // ── Organization pipeline ──────────────────────────────────────────────────────

  @Roles(UserRole.ORGANIZATION)
  @Get('org/pipeline')
  @ApiOperation({ summary: '[Org] Applicants across my internships' })
  pipeline(
    @CurrentUser() user: AuthUser,
    @Query('internshipId') internshipId?: string,
    @Query('status') status?: ApplicationStatus,
  ) {
    return this.applications.listForOrganization(this.orgId(user), internshipId, status);
  }

  @Roles(UserRole.ORGANIZATION)
  @Post('tasks/:taskId/review')
  @ApiOperation({ summary: '[Org] Review/score a task submission' })
  reviewTask(@CurrentUser() user: AuthUser, @Param('taskId') taskId: string, @Body() dto: ReviewTaskDto) {
    return this.applications.reviewTask(this.orgId(user), taskId, dto);
  }

  @Roles(UserRole.ORGANIZATION)
  @Post(':id/evaluate')
  @ApiOperation({ summary: '[Org] Final performance evaluation → completion approval' })
  evaluate(@CurrentUser() user: AuthUser, @Param('id') id: string, @Body() dto: EvaluateDto) {
    return this.applications.evaluate(this.orgId(user), id, dto);
  }

  // ── Mentor ───────────────────────────────────────────────────────────────────

  @Roles(UserRole.MENTOR, UserRole.ORGANIZATION)
  @Post(':id/feedback')
  @ApiOperation({ summary: '[Mentor] Add feedback to an application' })
  feedback(@CurrentUser() user: AuthUser, @Param('id') id: string, @Body() dto: MentorFeedbackDto) {
    return this.applications.addMentorFeedback(user.id, id, dto);
  }

  // ── Shared transition endpoint (role-checked inside the engine) ─────────────────

  @Post(':id/transition')
  @ApiOperation({ summary: 'Advance an application along the workflow (role-guarded)' })
  transition(@CurrentUser() user: AuthUser, @Param('id') id: string, @Body() dto: TransitionDto) {
    return this.applications.transition(user, id, dto);
  }

  // ── helpers ────────────────────────────────────────────────────────────────

  private studentId(user: AuthUser): string {
    if (!user.studentProfileId) throw new ForbiddenException('Not a student account');
    return user.studentProfileId;
  }

  private orgId(user: AuthUser): string {
    if (!user.organizationProfileId) throw new ForbiddenException('Not an organization account');
    return user.organizationProfileId;
  }
}
