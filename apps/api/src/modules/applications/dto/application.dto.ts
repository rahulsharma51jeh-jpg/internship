import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';
import { ApplicationStatus, PerformanceGrade, TaskStatus } from '@prisma/client';
import {
  IsBoolean,
  IsDateString,
  IsEnum,
  IsInt,
  IsNumber,
  IsOptional,
  IsString,
  IsUrl,
  Max,
  Min,
} from 'class-validator';

export class ApplyDto {
  @ApiProperty({ description: 'Internship id to apply to' })
  @IsString()
  internshipId!: string;

  @ApiPropertyOptional()
  @IsOptional()
  @IsString()
  coverLetter?: string;

  @ApiPropertyOptional()
  @IsOptional()
  @IsUrl()
  resumeUrl?: string;

  @ApiPropertyOptional()
  @IsOptional()
  @IsUrl()
  portfolioUrl?: string;

  @ApiPropertyOptional()
  @IsOptional()
  @IsUrl()
  linkedinUrl?: string;

  @ApiPropertyOptional()
  @IsOptional()
  @IsUrl()
  githubUrl?: string;
}

export class TransitionDto {
  @ApiProperty({ enum: ApplicationStatus })
  @IsEnum(ApplicationStatus)
  to!: ApplicationStatus;

  @ApiPropertyOptional()
  @IsOptional()
  @IsString()
  note?: string;
}

export class EvaluateDto {
  @ApiProperty({ enum: PerformanceGrade })
  @IsEnum(PerformanceGrade)
  grade!: PerformanceGrade;

  @ApiProperty({ minimum: 0, maximum: 100 })
  @IsInt()
  @Min(0)
  @Max(100)
  score!: number;

  @ApiPropertyOptional()
  @IsOptional()
  @IsString()
  note?: string;
}

// ── Workspace DTOs ────────────────────────────────────────────────────────────

export class SubmitTaskDto {
  @ApiProperty()
  @IsString()
  title!: string;

  @ApiPropertyOptional()
  @IsOptional()
  @IsString()
  description?: string;

  @ApiPropertyOptional()
  @IsOptional()
  @IsUrl()
  submissionUrl?: string;

  @ApiPropertyOptional({ default: 1 })
  @IsOptional()
  @IsInt()
  @Min(1)
  weekNumber?: number;
}

export class ReviewTaskDto {
  @ApiProperty({ enum: TaskStatus })
  @IsEnum(TaskStatus)
  status!: TaskStatus;

  @ApiPropertyOptional({ minimum: 0, maximum: 100 })
  @IsOptional()
  @IsInt()
  @Min(0)
  @Max(100)
  score?: number;

  @ApiPropertyOptional()
  @IsOptional()
  @IsString()
  reviewerNote?: string;
}

export class MarkAttendanceDto {
  @ApiProperty({ example: '2026-06-01' })
  @IsDateString()
  date!: string;

  @ApiPropertyOptional({ default: true })
  @IsOptional()
  @IsBoolean()
  present?: boolean;

  @ApiPropertyOptional()
  @IsOptional()
  @IsNumber()
  @Min(0)
  @Max(24)
  hours?: number;
}

export class WeeklyReportDto {
  @ApiProperty()
  @IsInt()
  @Min(1)
  weekNumber!: number;

  @ApiProperty()
  @IsString()
  summary!: string;

  @ApiPropertyOptional()
  @IsOptional()
  @IsNumber()
  hoursLogged?: number;

  @ApiPropertyOptional()
  @IsOptional()
  @IsString()
  blockers?: string;
}

export class MentorFeedbackDto {
  @ApiProperty({ minimum: 1, maximum: 5 })
  @IsInt()
  @Min(1)
  @Max(5)
  rating!: number;

  @ApiPropertyOptional()
  @IsOptional()
  @IsString()
  comment?: string;

  @ApiPropertyOptional()
  @IsOptional()
  @IsInt()
  @Min(1)
  weekNumber?: number;
}
