# Database Schema

PostgreSQL via **Prisma ORM**. Source of truth: [`apps/api/prisma/schema.prisma`](../apps/api/prisma/schema.prisma).

Design principles:
- **UUID** primary keys everywhere (shard/replica friendly, non-enumerable).
- **Soft enums** mirrored in `packages/shared` so the API and web agree on values.
- **Snapshotting** on certificates (immutable record at issue time).
- **Append-only** audit (`audit_logs`) and verification (`certificate_verifications`) tables.
- **Hot-path indexes** on status/domain/branch and foreign keys.

---

## Entity-relationship overview

```
User ─1:1─ StudentProfile ─┬─< Application >─┬─ Internship >── OrganizationProfile
  │            │           │                 │      │
  │            │           │                 │      ├─< InternshipSkill >── Skill
  │            ├─< StudentSkill >── Skill     │      └─< TaskTemplate
  │            ├─< StudentBadge >── Badge     │
  │            ├─< ResumeAnalysis             ├─< ApplicationStatusEvent  (audit trail)
  │            └─< AssessmentAttempt >── Assessment
  │                                           ├─< TaskSubmission
User ─1:1─ OrganizationProfile                ├─< AttendanceRecord
User ─1:1─ Institution                        ├─< WeeklyReport
User ─1:*─ RefreshToken                       ├─< MentorFeedback >── User (mentor)
User ─1:*─ Notification                       └─1:1─ Certificate ─< CertificateVerification
User ─1:*─ AuditLog
StudentProfile ─*:1─ Branch ─< Internship >─*:1─ Domain
```

## Core tables

### Identity
| Table | Purpose | Key fields |
| --- | --- | --- |
| `users` | Account + auth + roles | `email` (unique), `passwordHash`, `roles[]`, `status`, OAuth ids |
| `refresh_tokens` | Rotating refresh tokens (hashed) | `tokenHash`, `expiresAt`, `revokedAt` |
| `student_profiles` | Student data + gamification | `branchId`, `cgpa`, `profileCompletion`, `xpPoints`, `level`, portfolio links |
| `organization_profiles` | Company data | `companyName`, `verified` |
| `institutions` | College/university accounts | `name`, `code`, `verified` |

### Taxonomy
| Table | Purpose |
| --- | --- |
| `branches` | 30+ engineering branches (`slug`, `shortCode`) |
| `domains` | 35+ internship domains (`slug`, `category`) |
| `skills` | Skill catalog |
| `student_skills` | M:N student↔skill with proficiency + `verified` |
| `internship_skills` | M:N internship↔skill (`required`) |

### Internships & applications
| Table | Purpose | Notable |
| --- | --- | --- |
| `internships` | Postings | `status` (DRAFT→PENDING_APPROVAL→OPEN→CLOSED), stipend range, `durationWeeks`, `@@index([status, domainId])` |
| `task_templates` | Reusable tasks per posting | `weekNumber`, `maxScore` |
| `applications` | Student↔internship | `status` state machine, lifecycle timestamps, `finalGrade`/`finalScore`, **unique** `(studentId, internshipId)` |
| `application_status_events` | Immutable transition log | `fromStatus`, `toStatus`, `actorId`, `note` |
| `task_submissions` | Workspace deliverables | `status` (ASSIGNED…APPROVED), `score` |
| `attendance_records` | Daily attendance | unique `(applicationId, date)` |
| `weekly_reports` | Weekly summaries | unique `(applicationId, weekNumber)` |
| `mentor_feedback` | Mentor ratings | `rating` 1-5 |

### Certificates
| Table | Purpose | Security |
| --- | --- | --- |
| `certificates` | Issued credentials | `certificateId` (e.g. `INF-2026-AB12CD34`), `verificationNumber` (unique), `contentHash` (SHA-256), `signature` (RSA), `qrPayloadUrl`, snapshotted display fields, `status` (ISSUED/REVOKED) |
| `certificate_verifications` | Append-only verification log | `method` (ID/QR/LINK), `valid`, `ip`, `userAgent` |

### AI & gamification
| Table | Purpose |
| --- | --- |
| `resume_analyses` | ATS score, skill gaps, suggestions |
| `assessments` / `assessment_attempts` | Skill tests + attempts |
| `badges` / `student_badges` | Achievement badges (XP rewards) |

### Platform infra
| Table | Purpose |
| --- | --- |
| `notifications` | In-app / email / SMS / WhatsApp messages |
| `audit_logs` | Sensitive action audit (`action`, `entity`, `entityId`, `metadata`) |

## Key enums

- `UserRole`: STUDENT · ORGANIZATION · MENTOR · INSTITUTION · ADMIN · SUPER_ADMIN
- `AccountStatus`: PENDING_VERIFICATION · ACTIVE · SUSPENDED · BANNED
- `InternshipStatus`: DRAFT · PENDING_APPROVAL · OPEN · CLOSED · ARCHIVED
- `ApplicationStatus`: APPLIED · ADMIN_REVIEW · ORG_REVIEW · SHORTLISTED · UNDER_REVIEW · SELECTED · ONGOING · PERFORMANCE_EVALUATION · COMPLETION_APPROVAL · COMPLETED · CERTIFICATE_GENERATED · REJECTED · WITHDRAWN
- `CertificateType`: INTERNSHIP_COMPLETION · TRAINING · WORKSHOP · EXCELLENCE_AWARD · LETTER_OF_RECOMMENDATION · APPRECIATION
- `PerformanceGrade`: A_PLUS · A · B · C · PASS

## Migrations & seeding

```bash
pnpm api:prisma:generate   # generate Prisma client
pnpm api:prisma:migrate    # create/apply dev migration
pnpm api:seed              # 30 branches, 35 domains, 30 skills, 5 badges, demo users
```

Demo accounts (password `Password@123`): `admin@infinityinterns.com`, `hr@technova.com`, `student@example.com`.
