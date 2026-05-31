# File Structure

```
infinity-interns/
├── apps/
│   ├── api/                              # NestJS + Prisma backend
│   │   ├── prisma/
│   │   │   ├── schema.prisma             # Full database schema (single source of truth)
│   │   │   └── seed.ts                   # Branches, domains, skills, badges, demo users
│   │   ├── src/
│   │   │   ├── main.ts                   # Bootstrap: CORS, ValidationPipe, Swagger, filters
│   │   │   ├── app.module.ts             # Root module: wires features + global guards
│   │   │   ├── config/
│   │   │   │   └── configuration.ts      # Typed env config
│   │   │   ├── prisma/
│   │   │   │   ├── prisma.service.ts     # PrismaClient lifecycle
│   │   │   │   └── prisma.module.ts      # @Global Prisma module
│   │   │   ├── common/
│   │   │   │   ├── decorators/           # @Public, @Roles, @CurrentUser
│   │   │   │   ├── guards/               # JwtAuthGuard, RolesGuard
│   │   │   │   ├── filters/              # AllExceptionsFilter (incl. Prisma mapping)
│   │   │   │   ├── interceptors/         # TransformInterceptor ({success,data})
│   │   │   │   └── dto/                  # PaginationDto + paginate() helper
│   │   │   └── modules/
│   │   │       ├── health/               # Liveness + DB probe
│   │   │       ├── auth/                 # JWT auth, register/login/refresh, JwtStrategy
│   │   │       ├── catalog/              # Public branches/domains/skills/badges
│   │   │       ├── users/                # Profiles, student dashboard, admin user mgmt
│   │   │       ├── internships/          # CRUD, approval workflow, search
│   │   │       ├── applications/         # Apply + workflow.engine + workspace
│   │   │       ├── certificates/         # Issue, QR, hash, verify, revoke
│   │   │       └── analytics/            # Admin KPIs + public leaderboard
│   │   ├── tsconfig.json
│   │   ├── tsconfig.build.json           # Build-only (rootDir=src, excludes prisma)
│   │   ├── nest-cli.json
│   │   └── package.json
│   │
│   └── web/                              # Next.js (App Router) frontend
│       ├── src/
│       │   ├── app/
│       │   │   ├── layout.tsx            # Root layout + ThemeProvider (dark/light)
│       │   │   ├── globals.css           # Tailwind layers + design tokens
│       │   │   ├── page.tsx              # Landing page
│       │   │   ├── (auth)/
│       │   │   │   ├── login/page.tsx
│       │   │   │   └── register/page.tsx
│       │   │   ├── internships/page.tsx  # Catalog (SSR + API + fallback)
│       │   │   ├── dashboard/page.tsx    # Student dashboard
│       │   │   └── verify/
│       │   │       ├── page.tsx          # Verification search
│       │   │       └── [id]/page.tsx     # Verification result
│       │   ├── components/
│       │   │   ├── ui/                   # ShadCN-style primitives (button, card, badge)
│       │   │   ├── site-header.tsx / site-footer.tsx
│       │   │   ├── theme-provider.tsx / theme-toggle.tsx
│       │   │   ├── reveal.tsx            # Framer Motion scroll animation
│       │   │   └── internship-card.tsx
│       │   └── lib/
│       │       ├── api.ts                # Typed fetch client (unwraps envelope)
│       │       ├── utils.ts              # cn(), currency helpers
│       │       └── sample-data.ts        # Fallback data when API is offline
│       ├── next.config.mjs               # transpilePackages + /api rewrite
│       ├── tailwind.config.ts
│       ├── postcss.config.mjs
│       ├── tsconfig.json
│       └── package.json
│
├── packages/
│   └── shared/                           # Shared TypeScript domain model
│       └── src/
│           ├── roles.ts                  # UserRole enum
│           ├── branches.ts               # 30+ ENGINEERING_BRANCHES
│           ├── domains.ts                # 35+ INTERNSHIP_DOMAINS + categories
│           ├── workflow.ts               # ApplicationStatus + transition map
│           └── index.ts
│
├── docs/                                 # Architecture, DB, API, UI, file-structure, roadmap
├── docker-compose.yml                    # Postgres · Redis · MinIO · MailHog
├── .env.example                          # Every environment variable, documented
├── pnpm-workspace.yaml
└── package.json                          # Root scripts (dev, build, infra, prisma, seed)
```

## Conventions

- **Feature modules** in the API are self-contained (`*.module.ts`, `*.controller.ts`, `*.service.ts`, `dto/`).
- **Thin controllers, fat services** — HTTP concerns in controllers, business logic in services.
- **Shared domain values** (branches/domains/roles/workflow) live in `packages/shared` so the API and web never drift.
- **Path aliases**: API uses `@infinity/shared`; web uses `@/*` and `@infinity/shared`.
