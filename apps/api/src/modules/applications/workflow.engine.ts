import { BadRequestException, Injectable } from '@nestjs/common';
import { ApplicationStatus } from '@prisma/client';

/**
 * The canonical application lifecycle:
 *
 *   APPLIED → ADMIN_REVIEW → ORG_REVIEW → SHORTLISTED → UNDER_REVIEW →
 *   SELECTED → ONGOING → PERFORMANCE_EVALUATION → COMPLETION_APPROVAL →
 *   COMPLETED → CERTIFICATE_GENERATED
 *
 * Any in-flight state may also branch to REJECTED or WITHDRAWN.
 *
 * Defining transitions in one place lets the engine reject illegal jumps
 * (e.g. APPLIED → COMPLETED) and keeps the audit trail meaningful.
 */
export const TRANSITIONS: Record<ApplicationStatus, ApplicationStatus[]> = {
  APPLIED: ['ADMIN_REVIEW', 'REJECTED', 'WITHDRAWN'],
  ADMIN_REVIEW: ['ORG_REVIEW', 'REJECTED', 'WITHDRAWN'],
  ORG_REVIEW: ['SHORTLISTED', 'UNDER_REVIEW', 'REJECTED', 'WITHDRAWN'],
  SHORTLISTED: ['UNDER_REVIEW', 'SELECTED', 'REJECTED', 'WITHDRAWN'],
  UNDER_REVIEW: ['SELECTED', 'REJECTED', 'WITHDRAWN'],
  SELECTED: ['ONGOING', 'WITHDRAWN'],
  ONGOING: ['PERFORMANCE_EVALUATION', 'WITHDRAWN'],
  PERFORMANCE_EVALUATION: ['COMPLETION_APPROVAL', 'REJECTED'],
  COMPLETION_APPROVAL: ['COMPLETED', 'REJECTED'],
  COMPLETED: ['CERTIFICATE_GENERATED'],
  CERTIFICATE_GENERATED: [],
  REJECTED: [],
  WITHDRAWN: [],
};

/**
 * Which actor role is allowed to drive each transition. Used to guard that,
 * e.g., only an organization can SELECT, only an admin can move ADMIN_REVIEW on.
 */
export const TRANSITION_ACTOR: Partial<Record<ApplicationStatus, 'ADMIN' | 'ORG' | 'STUDENT' | 'SYSTEM'>> = {
  ADMIN_REVIEW: 'ADMIN',
  ORG_REVIEW: 'ADMIN',
  SHORTLISTED: 'ORG',
  UNDER_REVIEW: 'ORG',
  SELECTED: 'ORG',
  ONGOING: 'ORG',
  PERFORMANCE_EVALUATION: 'ORG',
  COMPLETION_APPROVAL: 'ORG',
  COMPLETED: 'ADMIN',
  CERTIFICATE_GENERATED: 'SYSTEM',
  WITHDRAWN: 'STUDENT',
};

@Injectable()
export class WorkflowEngine {
  canTransition(from: ApplicationStatus, to: ApplicationStatus): boolean {
    return TRANSITIONS[from]?.includes(to) ?? false;
  }

  assertTransition(from: ApplicationStatus, to: ApplicationStatus): void {
    if (!this.canTransition(from, to)) {
      throw new BadRequestException(
        `Illegal status transition: ${from} → ${to}. Allowed: [${(TRANSITIONS[from] ?? []).join(', ')}]`,
      );
    }
  }

  nextStates(from: ApplicationStatus): ApplicationStatus[] {
    return TRANSITIONS[from] ?? [];
  }
}
