import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';
import { Type } from 'class-transformer';
import {
  IsArray,
  IsDateString,
  IsEnum,
  IsInt,
  IsOptional,
  IsString,
  Min,
  MinLength,
} from 'class-validator';
import { WorkMode, InternshipStatus } from '@prisma/client';
import { PaginationDto } from '../../../common/dto/pagination.dto';

export class CreateInternshipDto {
  @ApiProperty({ example: 'Full Stack Developer Intern' })
  @IsString()
  @MinLength(4)
  title!: string;

  @ApiProperty()
  @IsString()
  @MinLength(20)
  description!: string;

  @ApiPropertyOptional()
  @IsOptional()
  @IsString()
  responsibilities?: string;

  @ApiPropertyOptional()
  @IsOptional()
  @IsString()
  eligibility?: string;

  @ApiProperty({ description: 'Domain id (from /catalog/domains)' })
  @IsString()
  domainId!: string;

  @ApiPropertyOptional({ description: 'Branch id (from /catalog/branches)' })
  @IsOptional()
  @IsString()
  branchId?: string;

  @ApiPropertyOptional({ enum: WorkMode, default: WorkMode.REMOTE })
  @IsOptional()
  @IsEnum(WorkMode)
  workMode?: WorkMode;

  @ApiPropertyOptional()
  @IsOptional()
  @IsString()
  location?: string;

  @ApiPropertyOptional({ example: 15000 })
  @IsOptional()
  @IsInt()
  @Min(0)
  stipendMin?: number;

  @ApiPropertyOptional({ example: 25000 })
  @IsOptional()
  @IsInt()
  @Min(0)
  stipendMax?: number;

  @ApiPropertyOptional({ default: 8 })
  @IsOptional()
  @IsInt()
  @Min(1)
  durationWeeks?: number;

  @ApiPropertyOptional({ default: 1 })
  @IsOptional()
  @IsInt()
  @Min(1)
  openings?: number;

  @ApiPropertyOptional()
  @IsOptional()
  @IsDateString()
  applyByDate?: string;

  @ApiPropertyOptional()
  @IsOptional()
  @IsDateString()
  startDate?: string;

  @ApiPropertyOptional({ type: [String], description: 'Skill ids' })
  @IsOptional()
  @IsArray()
  @IsString({ each: true })
  skillIds?: string[];
}

export class UpdateInternshipDto extends CreateInternshipDto {}

export class QueryInternshipDto extends PaginationDto {
  @ApiPropertyOptional()
  @IsOptional()
  @IsString()
  domain?: string; // domain slug

  @ApiPropertyOptional()
  @IsOptional()
  @IsString()
  branch?: string; // branch slug

  @ApiPropertyOptional({ enum: WorkMode })
  @IsOptional()
  @IsEnum(WorkMode)
  workMode?: WorkMode;

  @ApiPropertyOptional({ enum: InternshipStatus })
  @IsOptional()
  @IsEnum(InternshipStatus)
  status?: InternshipStatus;

  @ApiPropertyOptional({ description: 'Minimum monthly stipend (INR)' })
  @IsOptional()
  @Type(() => Number)
  @IsInt()
  @Min(0)
  minStipend?: number;
}
