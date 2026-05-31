import { Controller, Get } from '@nestjs/common';
import { ApiOperation, ApiTags } from '@nestjs/swagger';
import { Public } from '../../common/decorators/public.decorator';
import { CatalogService } from './catalog.service';

@ApiTags('catalog')
@Controller('catalog')
export class CatalogController {
  constructor(private readonly catalog: CatalogService) {}

  @Public()
  @Get('branches')
  @ApiOperation({ summary: 'List all engineering branches' })
  branches() {
    return this.catalog.branches();
  }

  @Public()
  @Get('domains')
  @ApiOperation({ summary: 'List all internship domains (with category grouping)' })
  domains() {
    return this.catalog.domains();
  }

  @Public()
  @Get('skills')
  @ApiOperation({ summary: 'List all skills' })
  skills() {
    return this.catalog.skills();
  }

  @Public()
  @Get('badges')
  @ApiOperation({ summary: 'List all gamification badges' })
  badges() {
    return this.catalog.badges();
  }
}
