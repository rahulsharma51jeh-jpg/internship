# UI Architecture

The web client (`apps/web`) is a **Next.js App Router** application styled with **Tailwind CSS** and **ShadCN-style** primitives, with **Framer Motion** for premium motion. It is mobile-first, supports **dark & light** modes, and is built for accessibility and fast loads.

---

## 1. Design system

### Tokens (HSL CSS variables — `globals.css`)
Theme is driven by CSS custom properties so dark/light is a single class toggle on `<html>`:

| Token | Role |
| --- | --- |
| `--background` / `--foreground` | Page surface + text |
| `--primary` / `--primary-foreground` | Brand indigo, used for CTAs and accents |
| `--accent` | Gradient partner colour (violet) |
| `--card`, `--muted`, `--secondary` | Surfaces and subtle backgrounds |
| `--border`, `--input`, `--ring` | Lines and focus rings |
| `--radius` | Global corner radius (0.75rem) |

Utilities: `.gradient-text` (brand gradient text), `.glass` (frosted header), `bg-grid-pattern` (hero grid).

### Primitives (`components/ui`)
- **Button** — `cva` variants: `default`, `outline`, `ghost`, `secondary`; sizes `sm`/`default`/`lg`/`icon`.
- **Card** — `Card`, `CardHeader`, `CardTitle`, `CardDescription`, `CardContent`, `CardFooter`.
- **Badge** — variants: `default`, `secondary`, `outline`, `success`, `warning`, `danger`.

These mirror the ShadCN UI API so the full ShadCN component set can be dropped in incrementally.

### Theming
- `next-themes` with `attribute="class"`, `defaultTheme="dark"`, `enableSystem`.
- `ThemeToggle` is hydration-safe (renders the icon only after mount).

### Motion
- `Reveal` wraps sections with a fade-and-rise on scroll (`whileInView`, `once: true`).
- Respect reduced-motion by keeping transforms subtle and short.

## 2. Rendering strategy

| Page | Strategy | Why |
| --- | --- | --- |
| `/` Landing | **Static** | Marketing content; data from `@infinity/shared` (no API call). |
| `/internships` | **Dynamic (SSR)** | Live catalog from the API; falls back to sample data if offline. |
| `/internships/[slug]` | Dynamic | Detail + apply. |
| `/verify` | Client | Search box → navigates to result. |
| `/verify/[id]` | **Dynamic (SSR)** | Server-fetches verification so QR scans load instantly with no flash. |
| `/dashboard` | Dynamic (auth) | Personalized; fed by `GET /users/me/dashboard`. |
| `(auth)/login`, `(auth)/register` | Static shells | Route group keeps auth pages chrome-free. |

The API client (`lib/api.ts`) unwraps the `{ success, data }` envelope and throws typed `ApiError`s. Server components fetch with `next: { revalidate }` for cache control.

## 3. Page map & navigation

```
/                         Landing (hero · stats · features · workflow · branches · domains · CTA)
/internships              Catalog with search + domain filter chips
/internships/[slug]       Internship detail + one-click apply
/verify                   Certificate verification search
/verify/[id]              Verification result (valid / revoked / tampered / not found)
/dashboard                Student dashboard (completion · XP · tracker · recommendations · workspace)
/login, /register         Auth (student + organization)
```

Planned sub-areas (routes scaffolded conceptually): `/dashboard/profile`, `/dashboard/workspace`, `/dashboard/portfolio`, `/org` (org dashboard), `/admin` (admin panel), `/leaderboard`, `/branches`, `/domains`.

## 4. Role-based dashboards (information architecture)

- **Student**: personalized home, profile completion meter, application status tracker, internship workspace (tasks, attendance, weekly reports, mentor feedback), digital portfolio, certificates.
- **Organization**: post/manage internships, applicant pipeline (Kanban by status), assessments, performance evaluation, completion approval.
- **Admin**: internship approval queue, student verification, certificate management (manual + bulk), analytics dashboard (KPIs, charts).

## 5. Accessibility & performance

- Semantic HTML, labelled form controls, visible focus rings (`--ring`).
- Colour contrast tuned for both themes; status communicated by text + colour (not colour alone).
- Mobile-first responsive grids; container max-width 1280px.
- `next/font` self-hosted Inter; code-split routes; first-load JS kept lean (landing ≈ 142 kB).
- Images via `next/image` (when added); CDN delivery in production.
