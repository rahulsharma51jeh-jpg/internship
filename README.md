<div align="center">

# ♾️ Infinity Interns™

### India's most comprehensive engineering internship platform

A complete ecosystem connecting **students, companies, institutions, mentors, and administrators** — discover, apply, track, complete, and earn verified internships across **30+ engineering branches** and **35+ technology domains**.

[![Built with NestJS](https://img.shields.io/badge/API-NestJS-E0234E)](https://nestjs.com)
[![Next.js](https://img.shields.io/badge/Web-Next.js-000000)](https://nextjs.org)
[![Prisma](https://img.shields.io/badge/ORM-Prisma-2D3748)](https://prisma.io)
[![PostgreSQL](https://img.shields.io/badge/DB-PostgreSQL-4169E1)](https://postgresql.org)
[![TypeScript](https://img.shields.io/badge/Lang-TypeScript-3178C6)](https://typescriptlang.org)

</div>

---

## 📦 Monorepo layout

```
infinity-interns/
├── apps/
│   ├── api/        # NestJS + Prisma backend (REST API, auth, certificates, workflow engine)
│   └── web/        # Next.js (App Router) frontend — SaaS UI, dashboards, verification portal
├── packages/
│   └── shared/     # Shared TypeScript types, enums & constants (branches, domains, roles)
├── docs/           # System architecture, DB schema, API reference, UI architecture, roadmap
├── docker-compose.yml
└── pnpm-workspace.yaml
```

## 🚀 Quick start

```bash
# 1. Install dependencies (pnpm workspace)
pnpm install

# 2. Boot infrastructure (Postgres, Redis, MinIO, MailHog)
pnpm infra:up

# 3. Configure environment
cp .env.example apps/api/.env
cp .env.example apps/web/.env.local

# 4. Set up the database
pnpm api:prisma:generate
pnpm api:prisma:migrate
pnpm api:seed            # seeds 30 branches + 35 domains + demo users

# 5. Run everything
pnpm dev                 # api on :4000, web on :3000
```

API docs (Swagger) are served at **http://localhost:4000/docs**.

## 🧱 Tech stack

| Layer            | Technology                                                            |
| ---------------- | --------------------------------------------------------------------- |
| Frontend         | Next.js (App Router), TypeScript, Tailwind CSS, ShadCN UI, Framer Motion |
| Backend          | Node.js, NestJS, REST, class-validator                                |
| Database         | PostgreSQL + Prisma ORM                                                |
| Cache / Queues   | Redis (BullMQ-ready)                                                   |
| Auth             | JWT (access + refresh), OAuth (Google, LinkedIn)                      |
| Storage          | AWS S3 / Cloudflare R2 (MinIO for local dev)                          |
| Notifications    | Email (SMTP), SMS, WhatsApp adapters                                  |
| Certificate engine | PDF generation, QR codes, SHA-256 anti-tamper hash, digital signature |

## 📚 Documentation

| Doc | Description |
| --- | --- |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture, scaling strategy, service boundaries |
| [docs/DATABASE.md](docs/DATABASE.md) | Full database schema + ER diagram |
| [docs/API.md](docs/API.md) | REST API endpoint reference |
| [docs/FILE_STRUCTURE.md](docs/FILE_STRUCTURE.md) | Annotated file/folder structure |
| [docs/UI_ARCHITECTURE.md](docs/UI_ARCHITECTURE.md) | UI architecture, design system, page map |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Feature roadmap & what is implemented vs. planned |

## 🧩 Core capabilities

- **Students** — personalized dashboard, AI recommendations, one-click apply, workspace (tasks, attendance, weekly reports), digital portfolio, verified certificates.
- **Organizations** — post internships, manage applicants, assign tasks, evaluate performance, approve completion.
- **Admins** — approval workflows, student verification, bulk/manual certificate generation, analytics.
- **Certificate engine** — auto + manual issuance, QR verification, anti-tamper hashing, blockchain-ready verification layer, public verification portal.
- **Gamification** — XP, badges, skill milestones, leaderboards.

> See [docs/ROADMAP.md](docs/ROADMAP.md) for the precise implemented-vs-planned breakdown.

## 📄 License

Proprietary — © Infinity Interns™. All rights reserved.
