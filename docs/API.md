# API Reference

Base URL: `http://localhost:4000/api` · Interactive docs (Swagger): `http://localhost:4000/docs`

**Conventions**
- All responses are wrapped: `{ "success": true, "data": <payload>, "timestamp": "…" }`.
- Errors: `{ "success": false, "statusCode", "error", "message", "path", "timestamp" }`.
- Auth: send `Authorization: Bearer <accessToken>`. Routes are protected by default; `🌐` marks public routes.
- Role guards: `[ADMIN]`, `[ORG]`, `[STUDENT]`, `[MENTOR]` indicate the required role.

---

## Auth — `/auth`
| Method | Path | Access | Description |
| --- | --- | --- | --- |
| POST | `/auth/register` | 🌐 | Register a STUDENT or ORGANIZATION (privileged roles cannot be self-assigned) |
| POST | `/auth/login` | 🌐 (rate-limited 5/min) | Email + password → access & refresh tokens |
| POST | `/auth/refresh` | 🌐 | Rotate tokens using a valid refresh token |
| POST | `/auth/logout` | auth | Revoke the supplied refresh token |
| GET | `/auth/me` | auth | Current user profile (password stripped) |

## Catalog — `/catalog`
| Method | Path | Access | Description |
| --- | --- | --- | --- |
| GET | `/catalog/branches` | 🌐 | 30+ engineering branches |
| GET | `/catalog/domains` | 🌐 | 35+ domains (also grouped by category) |
| GET | `/catalog/skills` | 🌐 | Skill catalog |
| GET | `/catalog/badges` | 🌐 | Gamification badges |

## Users — `/users`
| Method | Path | Access | Description |
| --- | --- | --- | --- |
| GET | `/users/me/profile` | [STUDENT] | Get my student profile |
| PATCH | `/users/me/profile` | [STUDENT] | Update profile (recomputes completion score) |
| GET | `/users/me/dashboard` | [STUDENT] | Personalized dashboard: stats + recommendations |
| GET | `/users` | [ADMIN] | List/search users (paginated) |
| PATCH | `/users/:id/status` | [ADMIN] | Activate / suspend / ban a user |

## Internships — `/internships`
| Method | Path | Access | Description |
| --- | --- | --- | --- |
| GET | `/internships` | 🌐 | Search OPEN catalog (`domain`, `branch`, `workMode`, `minStipend`, `q`, `page`, `limit`) |
| GET | `/internships/:slug` | 🌐 | Internship detail (increments view count) |
| GET | `/internships/me/listings` | [ORG] | My postings (all statuses) |
| POST | `/internships` | [ORG] | Create internship (starts as DRAFT) |
| PATCH | `/internships/:id` | [ORG] | Update internship |
| POST | `/internships/:id/submit` | [ORG] | Submit DRAFT for admin approval |
| POST | `/internships/:id/close` | [ORG] | Close internship |
| GET | `/internships/admin/pending` | [ADMIN] | Postings awaiting approval |
| POST | `/internships/:id/approve` | [ADMIN] | Approve & publish (→ OPEN) |
| POST | `/internships/:id/reject` | [ADMIN] | Reject (→ DRAFT) |

## Applications — `/applications`
| Method | Path | Access | Description |
| --- | --- | --- | --- |
| POST | `/applications` | [STUDENT] | One-click apply (`internshipId`, optional cover letter + links) |
| GET | `/applications/me` | [STUDENT] | My applications (optional `?status=`) |
| GET | `/applications/me/:id` | [STUDENT] | One application + workspace + history |
| POST | `/applications/:id/tasks` | [STUDENT] | Submit a task/project |
| POST | `/applications/:id/attendance` | [STUDENT] | Mark attendance for a day |
| POST | `/applications/:id/weekly-report` | [STUDENT] | Submit/update a weekly report |
| GET | `/applications/org/pipeline` | [ORG] | Applicants across my internships (`?internshipId=`, `?status=`) |
| POST | `/applications/tasks/:taskId/review` | [ORG] | Review/score a task submission |
| POST | `/applications/:id/evaluate` | [ORG] | Final evaluation → COMPLETION_APPROVAL |
| POST | `/applications/:id/feedback` | [MENTOR]/[ORG] | Add mentor feedback |
| POST | `/applications/:id/transition` | auth (role-guarded) | Advance the workflow (`to`, optional `note`) |

## Certificates — `/certificates`
| Method | Path | Access | Description |
| --- | --- | --- | --- |
| GET | `/certificates/verify/:identifier` | 🌐 | Verify by certificate ID or verification number (logs the check) |
| GET | `/certificates/me` | [STUDENT] | My earned certificates |
| POST | `/certificates/applications/:applicationId/issue` | [ADMIN] | Auto-issue completion certificate |
| POST | `/certificates/bulk-issue` | [ADMIN] | Bulk-issue for completed applications |
| POST | `/certificates/manual` | [ADMIN] | Manual certificate (workshop/award/etc.) |
| POST | `/certificates/:certificateId/revoke` | [ADMIN] | Revoke a certificate |

## Analytics — `/analytics`
| Method | Path | Access | Description |
| --- | --- | --- | --- |
| GET | `/analytics/overview` | [ADMIN] | Platform KPIs: totals, placement & completion rates, top domains, status breakdown |
| GET | `/analytics/leaderboard` | 🌐 | Public XP leaderboard |

## Health — `/health`
| Method | Path | Access | Description |
| --- | --- | --- | --- |
| GET | `/health` | 🌐 | Liveness + DB connectivity probe |

---

## Example: end-to-end happy path

```bash
# 1. Login (seeded student)
curl -s -X POST localhost:4000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"student@example.com","password":"Password@123"}'

# 2. Browse the public catalog
curl -s 'localhost:4000/api/internships?domain=full-stack-development'

# 3. Apply (with the access token from step 1)
curl -s -X POST localhost:4000/api/applications \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"internshipId":"<id>","coverLetter":"Excited to contribute!"}'

# 4. Verify a certificate (public)
curl -s localhost:4000/api/certificates/verify/INF-2026-AB12CD34
```
