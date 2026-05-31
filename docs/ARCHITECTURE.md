# System Architecture

Infinity Interns™ is built as a **pnpm monorepo** with a clean separation between a stateless REST API, a server-rendered web client, and shared domain types. The design favours horizontal scalability, clear aggregate boundaries, and a workflow-driven core.

---

## 1. High-level topology

```
                            ┌──────────────────────────────┐
                            │            Clients            │
                            │  Browser · Mobile · Webhooks  │
                            └───────────────┬───────────────┘
                                            │ HTTPS
                            ┌───────────────▼───────────────┐
                            │        CDN / Edge (Vercel)     │
                            │   Next.js (App Router, SSR)    │
                            │   apps/web                     │
                            └───────────────┬───────────────┘
                                            │  /api/* (REST, JSON)
                            ┌───────────────▼───────────────┐
                            │     API Gateway / Load Bal.    │
                            └───────────────┬───────────────┘
                                            │
                      ┌─────────────────────▼─────────────────────┐
                      │        NestJS API (apps/api) — stateless    │
                      │  Auth · Users · Internships · Applications  │
                      │  Certificates · Analytics · Catalog         │
                      │  Global guards: JWT → Roles → Throttle      │
                      └───┬───────────┬───────────┬───────────┬────┘
                          │           │           │           │
              ┌───────────▼──┐  ┌─────▼─────┐ ┌───▼────┐ ┌────▼─────────┐
              │ PostgreSQL   │  │  Redis    │ │  S3 /  │ │ Notification │
              │ (Prisma ORM) │  │ cache +   │ │  R2    │ │ providers    │
              │ primary +    │  │ BullMQ    │ │ object │ │ email/SMS/   │
              │ read replicas│  │ queues    │ │ store  │ │ WhatsApp     │
              └──────────────┘  └───────────┘ └────────┘ └──────────────┘
```

## 2. Components

| Component | Tech | Responsibility |
| --- | --- | --- |
| **Web** (`apps/web`) | Next.js App Router, Tailwind, ShadCN, Framer Motion | SSR pages, dashboards, public catalog, verification portal. Talks to the API over REST. |
| **API** (`apps/api`) | NestJS, Prisma | Business logic, workflow engine, certificate engine, auth, RBAC. Stateless → scales horizontally behind a load balancer. |
| **Shared** (`packages/shared`) | TypeScript | Single source of truth for branches, domains, roles, and the application-status state machine. Consumed by both apps. |
| **PostgreSQL** | Prisma ORM | System of record. UUID PKs, indexed hot paths, append-only audit + verification logs. |
| **Redis** | cache + BullMQ | Caching of hot catalog reads, rate-limit buckets, and background job queues (emails, PDF generation, AI tasks). |
| **Object storage** | AWS S3 / Cloudflare R2 | Resumes, portfolios, generated certificate PDFs. |
| **Notification providers** | SMTP / SMS / WhatsApp | Transactional and lifecycle notifications. |

## 3. Request lifecycle (API)

1. **CORS** + **Helmet-style** hardening at the edge.
2. **ValidationPipe** — DTOs validated/sanitized (`whitelist`, `forbidNonWhitelisted`).
3. **JwtAuthGuard** (global) — verifies the access token unless the route is `@Public()`.
4. **RolesGuard** (global) — enforces `@Roles(...)` metadata.
5. **ThrottlerGuard** (global) — per-IP rate limiting (login endpoints are stricter).
6. **Controller → Service → Prisma** — thin controllers, logic lives in services.
7. **TransformInterceptor** — wraps the result in `{ success, data, timestamp }`.
8. **AllExceptionsFilter** — normalizes every error (incl. Prisma codes) into one envelope.

## 4. The workflow engine (the heart of the platform)

Application state is a guarded state machine defined once in `apps/api/src/modules/applications/workflow.engine.ts`:

```
APPLIED → ADMIN_REVIEW → ORG_REVIEW → SHORTLISTED → UNDER_REVIEW →
SELECTED → ONGOING → PERFORMANCE_EVALUATION → COMPLETION_APPROVAL →
COMPLETED → CERTIFICATE_GENERATED
                         ⮑ (any in-flight state) → REJECTED | WITHDRAWN
```

- **Illegal jumps are rejected** (`assertTransition`) — e.g. you cannot go `APPLIED → COMPLETED`.
- **Actor authorization** — each transition is guarded by role (`assertActorCanDrive`): admins drive review gates, organizations drive selection/evaluation, students may only withdraw.
- **Every transition is recorded** in `ApplicationStatusEvent` (immutable audit trail) with the actor and an optional note.
- **Side effects** (XP awards, badge grants, certificate issuance) are co-located with the transition inside a DB transaction for consistency.

## 5. Certificate engine & trust model

1. On `COMPLETED`, the certificate service snapshots immutable display fields.
2. A **canonical, key-sorted serialization** is hashed with **SHA-256** → `contentHash` (anti-tamper fingerprint).
3. The hash is optionally **digitally signed** (RSA-SHA256) with a server private key.
4. A **QR code** encodes the public verification URL (`/verify/{certificateId}`).
5. Verification **recomputes the hash** and compares it → tamper detection, plus a revocation check. Every check is logged to `CertificateVerification` (append-only).
6. The model is **blockchain-ready**: `contentHash` is exactly the value you would anchor on-chain; the verification layer can be swapped to read from a smart contract without schema changes.

## 6. Scaling to millions of users

| Concern | Strategy |
| --- | --- |
| **Stateless API** | No server-side session; JWT access + rotating refresh tokens. Scale pods horizontally. |
| **Database reads** | PostgreSQL **read replicas**; Prisma can route reads. Hot catalog reads cached in Redis. |
| **Database writes** | Indexed hot paths (`@@index` on status/domain/branch); partition `audit_logs` & `certificate_verifications` by month when they grow. |
| **Heavy jobs** | PDF generation, AI analysis, bulk certificate issuance and notifications run on **BullMQ workers**, not in the request path. |
| **File delivery** | S3/R2 + CDN; signed URLs for private documents. |
| **Search** | Start with Postgres `ILIKE`/trigram; graduate to OpenSearch/Meilisearch when catalog volume demands it. |
| **Rate limiting** | Global throttler backed by Redis in production for cluster-wide buckets. |
| **Observability** | Structured logs, `/health` probe, request tracing, and metrics (OpenTelemetry-ready). |
| **Multi-region** | Stateless API + replicated Postgres + R2 (global) enables active-passive regions. |

## 7. Security posture

- **argon2** password hashing; refresh tokens stored only as SHA-256 hashes and **rotated** on use.
- **RBAC** with least privilege; privileged roles (`ADMIN`, `SUPER_ADMIN`) can never be self-assigned at registration.
- **Input validation** on every DTO; unknown fields stripped.
- **Audit trail** for sensitive actions; **append-only** verification logs.
- **Secrets** via environment variables (never committed); `.env.example` documents every key.

## 8. Environments

| Env | Web | API | DB |
| --- | --- | --- | --- |
| Local | `next dev` :3000 | `nest start --watch` :4000 | Docker Postgres/Redis/MinIO/MailHog |
| Preview | Vercel preview | Containerized API | Managed Postgres branch |
| Production | Vercel / CDN | Autoscaled containers (ECS/Fly/K8s) | Managed Postgres + replicas, Redis, R2 |
