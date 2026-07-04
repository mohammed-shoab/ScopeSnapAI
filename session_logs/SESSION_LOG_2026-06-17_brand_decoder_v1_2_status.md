# SESSION LOG — Brand Decoder v1.2 — STATUS (2026-06-17) — 2026-06-17

**Retrofit note:** Extracted from `ACTIVE_TASKS_HISTORY.md` on 2026-07-06 as part of the SESSION_LOG_* archetype adoption (Phase 3 retrofit Batch B). Content is verbatim from the ACTIVE_TASKS_HISTORY.md session block; the block also remains in ACTIVE_TASKS_HISTORY.md for chronological continuity.

**Source:** `ACTIVE_TASKS_HISTORY.md` (session block, extracted 2026-07-06)

---

## Brand Decoder v1.2 — STATUS (2026-06-17)

**DONE on `staging` (all 7 plan stages):** serial decoder + data loader + gemini disambiguator (Stage 1, migration 039); age-handling reconciliation (Stage 2); shadow replace score + PostHog shadow eval (Stage 4); version stamping + `/api/version` + migration 040 (Stage 5); install_year audit + `age_corrected` (Stage 6); frontend 3A/3B/3C (Stage 3); glue (repair_plan recommendation_meta + correct-age endpoint); constraint-#8 refrigerant_for_year. **Tests: 94 backend pytest + 26 Playwright e2e/axe green.** UI verified live in Chrome (US). Permanent Playwright CI added (`.github/workflows/playwright-e2e.yml`, run #1 success). Staging Alembic head 040.

**WHAT'S LEFT (all owner / external — no unbuilt code):**
1. **Prod promotion — HELD for Shoab's "go".** On go: file-scoped promote `staging→main` at staging tip **`d7dbc2a8`** (incl the `re`-loader test fix + 2 new test files) (scopesnap-api decoder files + migrations 039/040 + estimates.py + the 2 new test files + scopesnap-web Stage 3 + the 2 estimate builders + StepZeroPanel + SidebarNav; **EXCLUDE `scopesnap-web/package-lock.json`** — DEC-065/099), confirm Railway prod runs `alembic upgrade head`→040, `/api/version`→1.2 on prod, then Chrome prod QA of 3A/3B/3C + the 2 fixed findings ([N] resolved, Continue=★REC) + watch Sentry/PostHog 24h. ~20-30 min.
2. **PostHog (single-project `environment`-tag setup) — STAGING DONE + LIVE-VERIFIED 2026-06-17, PROD pending promote.** ✅ Staging Railway `POSTHOG_API_KEY` set → `/api/version analytics_enabled:true`. ✅ Staging Vercel (`scopesnap-web-staging`) `NEXT_PUBLIC_POSTHOG_KEY` added (Prod+Preview) + redeployed. ✅ Prod Vercel (`scope-snap-ai`) already had the key (All Environments). ✅ `environment`-tag code on staging (`de1ec7d`). ✅ **LIVE-VERIFIED via Chrome ride-along (US + PK):** authed diagnostics run end-to-end fired PostHog events (network 204s) tagged `environment:staging` (localStorage super-property confirmed both markets). **Prod-promote runbook additions:** (a) set **`POSTHOG_API_KEY`** on the **Railway PROD environment** (`pacific-exploration` → scopesnap-api → environment **production** → Variables → New Variable → `POSTHOG_API_KEY` = `phc_…` → Deploy) — deferred because prod backend has no shadow code until promote; (b) the `environment`-tag frontend/backend code rides to prod with the promote (no separate step). Key value = the PROD PostHog project token `phc_A5spSA…` (publishable; same key for Vercel frontend + Railway backend).
3. **Stage 7 field walkthrough** — a real Houston tech runs a full staging diagnostic on their own phone (kit: `SnapAI_Stage7_Field_Walkthrough_Kit_2026-06-16.md`). Owner-scheduled. **NOTE:** assistant-driven Chrome ride-along already completed on both markets (see Stage 7 Ride-Along block below); the owner field test remains as the human-on-real-phone validation.
4. **PK interactive UI QA — ✅ DONE 2026-06-17** (Shoab logged the assistant into pk-staging Clerk). Full PK diagnostic verified live: PK brand list (Gree etc.), R-22/R-410A/R-32 refrigerant selector, Stage 3A install-year + confidence, market-appropriate diagnostic copy (soap-solution leak detect, "R-32 dominant in new PK splits, not interchangeable with R-410A"), and **PKR (₨) currency confirmed** on the estimate (₨4,725 / ₨8,775 / ₨135,000). Urdu toggle present (`اردو میں تبدیل کریں`); homeowner surfaces translated, estimate-builder is tech-side English by design.
5. **a11y backlog (separate from Stage 3):** axe surfaced PRE-EXISTING contrast debt in app chrome (sidebar nav, StepZero spec-grid `text-gray-400` labels at 2.53:1, `—` placeholder inputs at 2.22:1, "dev mode" badge). Not Brand-Decoder; track + fix later.


---

## Change log

- **2026-07-06:** Extracted from ACTIVE_TASKS_HISTORY.md session block during Phase 3 retrofit (Option B).
