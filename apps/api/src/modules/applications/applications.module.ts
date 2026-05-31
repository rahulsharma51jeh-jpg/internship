import { Module } from '@nestjs/common';
import { ApplicationsController } from './applications.controller';
import { ApplicationsService } from './applications.service';
import { WorkflowEngine } from './workflow.engine';

@Module({
  controllers: [ApplicationsController],
  providers: [ApplicationsService, WorkflowEngine],
  exports: [ApplicationsService, WorkflowEngine],
})
export class ApplicationsModule {}
