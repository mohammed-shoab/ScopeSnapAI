# SESSION LOG — ✅ PROD PROMOTION COMPLETE — 2026-06-17 (main tip `f70b6276`) — 2026-06-17

**Retrofit note:** Extracted from `ACTIVE_TASKS_HISTORY.md` on 2026-07-06 as part of the SESSION_LOG_* archetype adoption (Phase 3 retrofit Batch B). Content is verbatim from the ACTIVE_TASKS_HISTORY.md session block; the block also remains in ACTIVE_TASKS_HISTORY.md for chronological continuity.

**Source:** `ACTIVE_TASKS_HISTORY.md` (session block, extracted 2026-07-06)

---

## ✅ PROD PROMOTION COMPLETE — 2026-06-17 (main tip `f70b6276`)

Shoab gave the "go". Promoted `staging → main` and verified prod live.

- **Promote method:** file-scoped overlay of staging's blobs onto main's tree (60 files) via GitHub trees API, base_tree=main so main-only files preserved. **Excluded** `package-lock.json` (main already has its verified deterministic lock — DEC supersedes old "no lock" note; package.json unchanged) + 2 root brain docs. Pre-flight verified the divergence was safe: main was ahead 15 / behind 31; the only direct-on-main hotfixes (`public/sw.js`, `vercel.json`) were byte-identical to staging, so no revert risk. New main commit `f70b6276`.
- **Prod backend (Railway `pacific-exploration` → production):** deploy ACTIVE + successful. `/api/version` → decoder/replace/brand_data **1.2**; `/health` ok, `environment:production`, db connected. **Prod DB alembic head = `040`** (confirmed via Supabase prod `zpsoprffaujswywtsgzy`; migration 040 columns `decoder_version`/`replace_logic_version` present on `assessments`). Under `start.sh` `set -e`, the new code serving = migrations 039+040 passed.
- **Prod frontend (Vercel):** Playwright E2E CI run #5 on `main` @ f70b6276 = **success** (build clean + 26 e2e/axe pass) → Vercel prod build is green. Playwright now runs on every push to BOTH staging and main.
- **PostHog on prod:** **DONE.** Set `POSTHOG_API_KEY` (publishable phc_ key) on Railway prod env → redeployed → `/api/version analytics_enabled:true` (verified with a cache-buster; plain polls were returning a CACHED old-container response — note for future). `ENVIRONMENT=production` already set (so backend events tag `environment:production`). Frontend PostHog key already on prod Vercel + env-tag code now deployed.
- **Live prod-UI QA — ✅ DONE (Shoab kept prod logged in; Google SSO passthrough).** Fresh prod diagnostic: Carrier, 3-ton, install **2008** + **Sure** → Not Cooling → outdoor running YES → 55 PSI → Refrigerant Leak (High Conf) → estimate **rpt-592468** (`snapai.mainnov.tech`, USD). **Finding #1 confirmed LIVE on prod:** Full Replacement ★REC reads **"At 18 years old, complete system replacement eliminates near-term repair risk and reduces electricity costs by 30-40%. New 10-year manufacturer warranty included."** (real age substituted, no `[N]`). **Finding #2 confirmed:** Continue button = **"Continue with Replace Immediately ($6,480)"** (= ★REC tier). **a11y:** SidebarNav contrast rendering clean on prod.
- **Frontend PostHog env tag — ✅ CONFIRMED on prod:** localStorage `ph_phc_…_posthog.environment = "production"`, so `NEXT_PUBLIC_ENV=production` is set on prod Vercel and frontend events tag `environment:production`. Same publishable key as backend (single-project split-by-environment design working end-to-end).
- **PROD PROMOTION FULLY VERIFIED — nothing left to build, deploy, or QA.** Remaining items are optional/owner-only: full quality-playbook engine (separate run), Stage 7 human field test (real tech on real phone), and passive 24h Sentry/PostHog monitoring.


---

## Change log

- **2026-07-06:** Extracted from ACTIVE_TASKS_HISTORY.md session block during Phase 3 retrofit (Option B).
