# SnapAI AI — Tech Stack & Architecture

> **Last updated:** March 2026
> **Status:** Beta — live on Vercel + Railway

---

## Live App Locations

| Perspective | URL | Description |
|---|---|---|
| **Landing / Marketing** | https://snapai.mainnov.tech | Public homepage with waitlist form |
| **Contractor App (Sign In)** | https://snapai.mainnov.tech/dashboard | HVAC contractor dashboard — requires auth |
| **Homeowner Report** | `https://snapai.mainnov.tech/r/[slug]/[reportId]` | Public report link sent to homeowners — no auth required |
| **Backend API** | https://scopesnap-api-production.up.railway.app | FastAPI REST backend |
| **API Health Check** | https://scopesnap-api-production.up.railway.app/health | Backend uptime check |

---

## Frontend — Next.js 14 (App Router)

| Layer | Technology | Notes |
|---|---|---|
| **Framework** | Next.js 14 (App Router) | React Server Components + Client Components |
| **Language** | TypeScript | Strict mode throughout |
| **Styling** | Tailwind CSS | Custom design tokens: `brand-green`, `surface-border`, `text-secondary` etc. |
| **Auth** | Clerk | Development mode keys active — Production keys needed for open beta |
| **Deployment** | Vercel | Auto-deploys on push to `main` branch of GitHub |
| **Repo** | github.com/mohammed-shoab/SnapAIAI | Monorepo: `scopesnap-web/` + `scopesnap-api/` |

### Key Env Vars (set in Vercel)

| Variable | Purpose |
|---|---|
| `NEXT_PUBLIC_API_URL` | Points to Railway API URL |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Clerk public key (dev mode) |
| `CLERK_SECRET_KEY` | Clerk secret key (dev mode) |
| `NEXT_PUBLIC_ENV` | Set to `production` — enables Clerk middleware |
| `NEXT_TELEMETRY_DISABLED` | `1` — disables Next.js telemetry |

### Feature Flags (`lib/featureFlags.ts`)

All non-beta features are hidden behind `NEXT_PUBLIC_SHOW_*` env vars (all `false` by default). Code is present but not shown until flag is enabled.

| Flag | Feature |
|---|---|
| `NEXT_PUBLIC_SHOW_ANALYTICS` | Accuracy Tracker |
| `NEXT_PUBLIC_SHOW_PROFIT_LEAKS` | Profit Leaks widget |
| `NEXT_PUBLIC_SHOW_BENCHMARK` | BenchmarkIQ |
| `NEXT_PUBLIC_SHOW_PROPERTY_HISTORY` | Property History |
| `NEXT_PUBLIC_SHOW_EQUIPMENT` | Equipment Database + Aging Alerts |
| `NEXT_PUBLIC_SHOW_TEAM` | Technicians + Leaderboard |
| `NEXT_PUBLIC_SHOW_INTEGRATIONS` | Integrations settings |

---

## Backend — FastAPI (Python)

| Layer | Technology | Notes |
|---|---|---|
| **Framework** | FastAPI | Python 3.11+, async |
| **Database** | PostgreSQL 15 | Hosted on Railway |
| **ORM / Migrations** | SQLAlchemy + Alembic | Migration files in `scopesnap-api/db/migrations/` |
| **AI Vision** | Google Gemini 2.5 Flash | Equipment identification, condition analysis, issue detection |
| **Photo Storage** | Cloudflare R2 | S3-compatible object storage for equipment photos |
| **Email** | Resend | Transactional emails — homeowner report delivery |
| **Payments** | Stripe | Integrated (Checkout not wired for beta — feature-flagged) |
| **Deployment** | Railway | Project: `pacific-exploration` — auto-deploys from `scopesnap-api/` subdirectory |

### Key API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/api/auth/me` | Current contractor profile |
| `PATCH` | `/api/auth/me/company` | Update company profile |
| `GET` | `/api/estimates/` | List assessments |
| `POST` | `/api/estimates/` | Create assessment |
| `GET` | `/api/estimates/{id}` | Get assessment detail |
| `GET` | `/api/reports/{reportId}` | Get homeowner report (public) |
| `POST` | `/api/reports/{token}/approve` | Homeowner approves an option (public) |
| `POST` | `/api/events` | Track analytics event (rate-limited: 100/user/60s) |
| `POST` | `/api/waitlist` | Add email to waitlist |

### Database Tables

| Table | Purpose |
|---|---|
| `users` | Clerk-linked contractor accounts |
| `companies` | Contractor company profiles |
| `assessments` | Photo assessments + AI results |
| `reports` | Homeowner-facing reports with options |
| `properties` | Address + customer info |
| `app_events` | Analytics event log (rate-limited) |
| `waitlist_signups` | Landing page waitlist emails |

---

## Authentication Flow

```
User visits /dashboard
  └─> Next.js middleware checks NEXT_PUBLIC_ENV=production
        └─> Clerk middleware runs
              └─> Not authenticated → redirects to Clerk hosted sign-in
                    (glowing-cowbird-89.accounts.dev in dev mode)
              └─> Authenticated → proceeds to dashboard

Homeowner visits /r/[slug]/[reportId]
  └─> Middleware: path starts with /r/ → PUBLIC_PATHS → skip auth → render report
```

> ⚠️ **Beta note:** Frontend API calls currently include a `X-Dev-Clerk-User-Id: test_user_mike` dev bypass header. For multi-user beta, this needs to be replaced with proper Clerk JWT token passing from the signed-in user. Safe for single-user beta.

---

## Offline & Reliability

| Feature | Implementation |
|---|---|
| **Offline queue** | IndexedDB via `lib/offlineQueue.ts` — assessments queued if no network |
| **Event tracking** | Fire-and-forget via `lib/tracking.ts` — `sendBeacon` + 3s fetch timeout |
| **Photo fallback** | SVG placeholder rendered if HVAC photo fails to load |
| **API error states** | All pages handle loading / error / empty states gracefully |

---

## Repository Structure

```
SnapAIAI/
├── scopesnap-web/              # Next.js 14 frontend
│   ├── app/
│   │   ├── (app)/              # Auth-protected contractor app
│   │   │   ├── dashboard/      # Dashboard
│   │   │   ├── assess/         # Camera + AI assessment flow
│   │   │   ├── estimates/      # Assessment list
│   │   │   ├── estimate/[id]/  # Assessment detail
│   │   │   ├── onboarding/     # Company setup wizard
│   │   │   ├── analytics/      # Accuracy tracker (feature-flagged)
│   │   │   ├── settings/       # Company profile, pricing, privacy
│   │   │   └── billing/        # Subscription (feature-flagged)
│   │   ├── r/[slug]/[reportId] # PUBLIC homeowner report
│   │   └── page.tsx            # PUBLIC landing page
│   ├── components/
│   │   ├── SidebarNav.tsx      # Sidebar with 14 SVG icons
│   │   └── DataConfidenceLabel.tsx  # AI confidence display
│   └── lib/
│       ├── api.ts              # API_URL + OfflineError
│       ├── featureFlags.ts     # NEXT_PUBLIC_SHOW_* env vars
│       ├── offlineQueue.ts     # IndexedDB offline queue
│       └── tracking.ts         # Fire-and-forget analytics
│
├── scopesnap-api/              # FastAPI backend
│   ├── api/
│   │   ├── estimates.py        # Assessment CRUD
│   │   ├── reports.py          # Homeowner report endpoints
│   │   ├── auth.py             # Clerk user sync + company profile
│   │   └── events.py           # Analytics + waitlist (rate-limited)
│   └── db/
│       └── migrations/         # Alembic migration files
│
├── TECH_STACK.md               # This file
├── README.md                   # Project overview + links
└── SnapAI_Beta_Readiness_SignOff.docx  # Full 6-founder audit
```

---

## How to Push Updates to Live App

```bash
# From Windows Git Bash, in the SnapAIAI folder:
git add <files>
git commit -m "your message"
git push origin main
# Vercel auto-deploys in ~90 seconds
```

---

## Phase 2 Pre-Beta Checklist (Before Open Signup)

- [ ] Switch Clerk from **Development → Production** mode (required for public signups)
- [ ] Replace `DEV_HEADER` in all frontend pages with real Clerk JWT token passing
- [ ] Add Stripe Checkout wiring for payment collection
- [ ] Enable custom Clerk domain (instead of glowing-cowbird-89.accounts.dev)
