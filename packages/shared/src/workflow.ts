/**
 * Application lifecycle. The ordering here defines the canonical forward path:
 *
 *   Applied → Admin Review → Organization Review → Selected →
 *   Internship Started → Performance Evaluation → Completion Approval →
 *   Certificate Generated
 *
 * Any state can also transition to REJECTED or WITHDRAWN.
 */
export enum ApplicationStatus {
  APPLIED = 'APPLIED',
  ADMIN_REVIEW = 'ADMIN_REVIEW',
  ORG_REVIEW = 'ORG_REVIEW',
  SHORTLISTED = 'SHORTLISTED',
  UNDER_REVIEW = 'UNDER_REVIEW',
  SELECTED = 'SELECTED',
  ONGOING = 'ONGOING',
  PERFORMANCE_EVALUATION = 'PERFORMANCE_EVALUATION',
  COMPLETION_APPROVAL = 'COMPLETION_APPROVAL',
  COMPLETED = 'COMPLETED',
  CERTIFICATE_GENERATED = 'CERTIFICATE_GENERATED',
  REJECTED = 'REJECTED',
  WITHDRAWN = 'WITHDRAWN',
}

/**
 * Allowed forward/branch transitions. Used by the workflow engine to guard
 * illegal status jumps (e.g. you cannot go straight from APPLIED to COMPLETED).
 */
export const APPLICATION_TRANSITIONS: Record<ApplicationStatus, ApplicationStatus[]> = {
  [ApplicationStatus.APPLIED]: [ApplicationStatus.ADMIN_REVIEW, ApplicationStatus.REJECTED, ApplicationStatus.WITHDRAWN],
  [ApplicationStatus.ADMIN_REVIEW]: [ApplicationStatus.ORG_REVIEW, ApplicationStatus.REJECTED, ApplicationStatus.WITHDRAWN],
  [ApplicationStatus.ORG_REVIEW]: [ApplicationStatus.SHORTLISTED, ApplicationStatus.UNDER_REVIEW, ApplicationStatus.REJECTED, ApplicationStatus.WITHDRAWN],
  [ApplicationStatus.SHORTLISTED]: [ApplicationStatus.UNDER_REVIEW, ApplicationStatus.SELECTED, ApplicationStatus.REJECTED, ApplicationStatus.WITHDRAWN],
  [ApplicationStatus.UNDER_REVIEW]: [ApplicationStatus.SELECTED, ApplicationStatus.REJECTED, ApplicationStatus.WITHDRAWN],
  [ApplicationStatus.SELECTED]: [ApplicationStatus.ONGOING, ApplicationStatus.WITHDRAWN],
  [ApplicationStatus.ONGOING]: [ApplicationStatus.PERFORMANCE_EVALUATION, ApplicationStatus.WITHDRAWN],
  [ApplicationStatus.PERFORMANCE_EVALUATION]: [ApplicationStatus.COMPLETION_APPROVAL, ApplicationStatus.REJECTED],
  [ApplicationStatus.COMPLETION_APPROVAL]: [ApplicationStatus.COMPLETED, ApplicationStatus.REJECTED],
  [ApplicationStatus.COMPLETED]: [ApplicationStatus.CERTIFICATE_GENERATED],
  [ApplicationStatus.CERTIFICATE_GENERATED]: [],
  [ApplicationStatus.REJECTED]: [],
  [ApplicationStatus.WITHDRAWN]: [],
};

export function canTransition(from: ApplicationStatus, to: ApplicationStatus): boolean {
  return APPLICATION_TRANSITIONS[from]?.includes(to) ?? false;
}

export enum InternshipStatus {
  DRAFT = 'DRAFT',
  PENDING_APPROVAL = 'PENDING_APPROVAL',
  OPEN = 'OPEN',
  CLOSED = 'CLOSED',
  ARCHIVED = 'ARCHIVED',
}

export enum WorkMode {
  REMOTE = 'REMOTE',
  ONSITE = 'ONSITE',
  HYBRID = 'HYBRID',
}

export enum CertificateType {
  INTERNSHIP_COMPLETION = 'INTERNSHIP_COMPLETION',
  TRAINING = 'TRAINING',
  WORKSHOP = 'WORKSHOP',
  EXCELLENCE_AWARD = 'EXCELLENCE_AWARD',
  LETTER_OF_RECOMMENDATION = 'LETTER_OF_RECOMMENDATION',
  APPRECIATION = 'APPRECIATION',
}

export enum PerformanceGrade {
  A_PLUS = 'A_PLUS',
  A = 'A',
  B = 'B',
  C = 'C',
  PASS = 'PASS',
}
