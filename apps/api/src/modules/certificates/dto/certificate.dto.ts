import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';
import { CertificateType, PerformanceGrade } from '@prisma/client';
import { IsEnum, IsInt, IsOptional, IsString, Min } from 'class-validator';

/** Admin-issued manual certificate (workshops, bootcamps, awards, etc.). */
export class IssueManualCertificateDto {
  @ApiProperty()
  @IsString()
  studentProfileId!: string;

  @ApiProperty({ enum: CertificateType })
  @IsEnum(CertificateType)
  type!: CertificateType;

  @ApiProperty({ example: 'Generative AI Bootcamp 2026' })
  @IsString()
  title!: string;

  @ApiProperty({ example: 'Infinity Interns Academy' })
  @IsString()
  organizationName!: string;

  @ApiProperty({ example: 'Generative AI' })
  @IsString()
  domainName!: string;

  @ApiPropertyOptional()
  @IsOptional()
  @IsInt()
  @Min(1)
  durationWeeks?: number;

  @ApiPropertyOptional({ enum: PerformanceGrade })
  @IsOptional()
  @IsEnum(PerformanceGrade)
  grade?: PerformanceGrade;
}

export class BulkIssueDto {
  @ApiProperty({ type: [String], description: 'Application ids whose status is COMPLETED' })
  @IsString({ each: true })
  applicationIds!: string[];
}

export class VerifyCertificateDto {
  @ApiProperty({ description: 'Certificate ID or verification number' })
  @IsString()
  identifier!: string;
}
