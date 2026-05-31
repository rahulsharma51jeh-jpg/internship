# Roadmap — Implemented vs. Planned

This document is an honest map of what is **fully implemented and runnable today** versus what is **scaffolded or planned**. The foundation is production-grade; the remaining items extend it along the documented architecture without schema changes.

---

## ✅ Implemented & validated (compiles, builds, typechecks)

### Backend (NestJS + Prisma)
- **Auth**: register (student/org), login, JWT access + **rotating refresh tokens** (hashed), logout, `/auth/me`. argon2 hashing. Privileged-role self-assignment blocked.
- **RBAC**: global `JwtAuthGuard` + `RolesGuard`, `@Public`/`@Roles`/`@CurrentUser` decorators.
- **Catalog**: branches, domains (grouped), skills, badges.
- **Users**: student profile CRUD with computed completion score, **personalized dashboard** aggregation + recommendations, admin user list + suspend/ban.
- **Internships**: create/update/close, **admin approval workflow**, public search with filters, slug generation, view counter.
- **Applications**: one-click apply (dedupe + portfolio defaults), **guarded workflow state machine** with actor-role checks and an immutable status-event audit trail, organization applicant pipeline, performance evaluation, and a full **workspace** (task submissions, attendance, weekly reports, mentor feedback). XP + badge side effects.
- **Certificates**: auto + manual + bulk issuance, `INF-YYYY-XXXXXXXX` ids, QR codes, **SHA-256 anti-tamper hash**, optional RSA signature, **verification with tamper detection**, append-only verification log, revocation.
- **Analytics**: platform KPIs (placement/completion rates, top domains, status breakdown), public XP leaderboard.
- **Platform**: consistent response/error envelopes, global rate limiting, `/health` probe, Swagger/OpenAPI at `/docs`.
- **Data**: complete Prisma schema (27 models) + seed (30 branches, 35 domains, 30 skills, 5 badges, demo users + sample internship).

### Frontend (Next.js)
- Landing page (hero, stats, features, workflow, all 30 branches + 35 domains, CTA) with dark/light + motion.
- Internship catalog (SSR, API-backed, filters, graceful offline fallback).
- Certificate **verification portal** (search + SSR result with valid/revoked/tampered/not-found states).
- Student dashboard (completion meter, XP/level, application tracker, recommendations, workspace entry).
- Auth pages (student + organization), ShadCN-style design system, typed API client.

### Tooling
- pnpm monorepo, shared domain package, Docker Compose (Postgres/Redis/MinIO/MailHog), env reference, root scripts.

## 🟡 Scaffolded / partial (clear next step)
- **Internship detail + apply page** (`/internships/[slug]`) — API endpoint exists; UI page to be added.
- **Org & Admin dashboards UI** — API endpoints exist; build the React views (applicant Kanban, approval queue, analytics charts).
- **Auth wiring on web** — forms post to the documented endpoints; add client actions + token storage/refresh + protected routes.
- **PDF certificate rendering** — hash/QR/verification done; add a PDF template (e.g. `@react-pdf` or Puppeteer) and upload to S3/R2, storing `pdfUrl`.

## 🔮 Planned (architecture supports without breaking changes)
- **AI suite**: resume ATS analyzer, skill-gap analysis, career recommender, skill assessments, interview simulator. (`resume_analyses`, `assessments`, `assessment_attempts` tables already exist; back them with an AI worker.)
- **OAuth**: Google + LinkedIn login (fields + config present; add Passport strategies).
- **Notifications**: email/SMS/WhatsApp delivery via BullMQ workers (`notifications` table + provider config present).
- **Object storage uploads**: signed-URL upload flow for resumes/portfolios/certificate PDFs.
- **Blockchain anchoring**: anchor `contentHash` on-chain and read it back in the verification layer.
- **Gamification depth**: domain/institution rankings, skill milestones, richer leaderboards.
- **Search**: graduate from Postgres `ILIKE` to OpenSearch/Meilisearch.
- **Observability**: OpenTelemetry tracing, metrics, dashboards; read-replica routing.

## Suggested delivery sequence
1. Wire web auth + protected routes; build internship detail/apply page.
2. Org applicant pipeline + admin approval/analytics UIs.
3. Certificate PDF rendering + S3/R2 uploads.
4. Notification workers (email first).
5. AI resume analyzer + recommendations (highest perceived value).
6. OAuth, then blockchain anchoring + advanced search.
