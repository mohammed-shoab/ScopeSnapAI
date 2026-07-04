# SnapAI — Active Tasks

**Last updated:** 2026-07-06 (brain files cleanup Phase 1 — Commit 5)
**Historical sessions:** see `ACTIVE_TASKS_HISTORY.md`

---

## In Flight — 4 active workstreams (as of 2026-07-06)

| # | Workstream | Owner + Advisor | Status | Blocking on |
|---|---|---|---|---|
| 1 | **Legal cover + wordings update** | Shoab + Alfred (nav) | Audit v2 complete; remediation not yet started | TX SaaS attorney engagement; tech E&O insurance placement |
| 2 | **Adding new complaint cards** (Tier A: #20, #22, #23, #24 + Airflow sub-flow + tab J + superheat/subcool discrim) | Shoab + Bryan (board) | Bryan's 3-tier proposal drafted; not yet formally committed | Legal chat's Layer 1-4 landing (ToS deploy, in-app disclaimer) |
| 3 | **Brain files cleanup + future system** | Shoab + Karpathy (nav) + Rob (board) | Commits 1-5 executed this session; Phase 2 discipline setup pending | Approval to set up pre-commit hooks + weekly audit scheduled task |
| 4 | **TikTok video marketing** | Shoab + Azhan | Upcoming — not yet scoped | Owner, tools, budget TBD |

**Standing rules for active work:** DEC-070 staging→main→prod path, DEC-088 no future-tense homeowner promises, DEC-123 PK dormant, DEC-129 verify live Supabase not migrations, Card #21 Tier D indefinite hold. See `PROJECT_BRAIN.md` CRITICAL RULES table for full list.

---

## Recent sessions (2026-06-18 through 2026-06-29 — Bryan's exception applied: any session with any OPEN item is kept here)

## Session 2026-07-06 — Brain Files Cleanup Phase 1 + 2 (this session)

**DONE this session:**
- Phase 1 executed: 5 commits (DECISIONS.md em-dash sweep 54 headers, WORKFLOW.md Section 1 rewrite, MARKET_GUIDE.md DEC-123 banner, STATUS.md rewrite, PROJECT_BRAIN.md prune + history, TECH_STACK.md prune + history, ACTIVE_TASKS.md restructure)
- Phase 2 executed: router update (Session-start signal + 18-row routing table), pre-commit hook `.githooks/pre-commit`, weekly auto-audit scheduled task (`snapai-brain-files-weekly-audit`, Fridays 09:00 CT), WORKFLOW.md Section 16 (provenance metadata) + Section 17 (session logs)
- Phase 3 adopted (this section): SESSION_LOG_* archetype created; first log at `session_logs/SESSION_LOG_2026-07-06_brain_files_cleanup.md`

**Deep narrative:** `session_logs/SESSION_LOG_2026-07-06_brain_files_cleanup.md` — full what-worked / what-didn't / root-cause / resolution / lessons write-up.

**OPEN / follow-ups:**

| Priority | Item | Owner | Notes |
|---|---|---|---|
| HIGH | Install pre-commit hook | Shoab | `cd ScopeSnapAI && git config core.hooksPath .githooks` (~30 seconds) |
| MEDIUM | Test-fire weekly audit (approve tools) | Shoab | Sidebar → Scheduled → `snapai-brain-files-weekly-audit` → Run now |
| LOW | Phase 1.5 deep prunes | Shoab / AI | PROJECT_BRAIN 672→500, TECH_STACK 1940→500 (Bryan suggests splitting Brand Decoder), WORKFLOW 726→300 |
| LOW | Backdate SESSION_LOG_2026-07-05_deep_legal_audit.md | AI | Extract from Legal_Discussion_Verbatim_Transcript |
| LOW | Retrofit rename STAGING_MIRROR_CLOSEOUT → session log | Shoab / AI | Rob's suggestion, optional |

---

## Session 2026-06-29 (PM) — Turbopack PROMOTED TO PROD (DEC-113)

**DONE this session:**
- Promoted Turbopack to prod (scoped overlay, main `66699a05`): next.config.js (webpack()/disableLogger removed), package.json build `next build`, instrumentation-client.ts + instrumentation.ts, deleted sentry.client.config.ts. Prod already had audit work + migrations 042-044, so nothing else shipped.
- Verified prod: Vercel Turbopack build green (both projects), e2e CI green, /health ok, /api/version 1.2, §5 Sentry delivers under Turbopack (ingest 200), landing + Clerk v7 sign-in render, proxy.ts auth works, no console errors (US+PK).
- Both staging + prod now on Turbopack. Tailwind v3 retained (works under Turbopack).

**OPEN / follow-ups:**

| Priority | Item | Owner | Notes |
|----------|------|-------|-------|
| LOW (watch) | Turbopack prod bake | snapai-dev | Watch Sentry a few days for any Turbopack-specific frontend issues. |
| LOW | Resolve deliberate §5 test markers | Shoab/snapai-dev | SNAPAI-TURBOPACK-STG/PROD markers created during verification; resolve in Sentry when convenient (browser Sentry session was expired this run). |

---

## Session 2026-06-29 — Turbopack adopted on STAGING (DEC-113)

**DONE this session:**
- Adopted Turbopack on staging (PR #23, merge `a43c681`): build `next build --webpack` -> `next build`; Sentry -> `instrumentation-client.ts` + `instrumentation.ts` (deleted sentry.client.config.ts, removed disableLogger); removed next.config `webpack()` block.
- Tailwind v3.4 builds clean under Turbopack (no v4 upgrade needed). Clean build, zero warnings.
- Verified: Vercel Turbopack builds green (both projects), staging e2e CI run #65 green, local Turbopack build + e2e 34 passed, §5 Sentry delivers under Turbopack (ingest 200, nextjs/10.62.0 via instrumentation-client.ts).
- Pre-check: prod healthy after ~9-day Next 16 bake (/health ok, /api/version 1.2).

**OPEN / follow-ups:**

| Priority | Item | Owner | Notes |
|----------|------|-------|-------|
| MED | **Promote Turbopack to prod** | Shoab | Gated. Staging verified green on Turbopack; prod still `next build --webpack` until go. Separate prod promote (staging-first done). |
| LOW (watch) | Turbopack dev hot-reload | snapai-dev | Removed the dev `webpack()` polling block; if local hot-reload breaks in Docker/WSL, add top-level `watchOptions: { pollIntervalMs: 1000 }` or `next dev --webpack`. |

---

## Session 2026-06-29 -- Dependabot weekly triage + PROMOTED TO PROD

**DONE this session:**
- Weekly Dependabot triage (scheduled task `snapai-dependabot-triage`): 2 open PRs, both staging-targeted grouped minor/patch with green CI + clean mergeable_state -> MERGED both to `staging`.
  - #21 pip-minor-patch (`scopesnap-api/requirements.txt`): fastapi 0.138.0->0.138.1, boto3 1.43.34->1.43.36, alembic 1.18.4->1.18.5, weasyprint 68.0->68.1, svix 1.96.0->1.96.1.
  - #22 npm-minor-patch (`scopesnap-web`): @clerk/nextjs 7.5.7->7.5.9, posthog-js 1.391.2->1.395.0, @sentry/nextjs 10.59.0->10.62.0, autoprefixer 10.0.1->10.5.2.
- Staging QA PASS: Playwright E2E + backend pytest + gitleaks + NUL-byte all green (merge commits f1e858d / 59d15b2); /health ok, /api/version 1.2, /api/models/all US+PK 200, both staging fronts 200.
- PROMOTED TO PROD (DEC-070 file-scoped overlay): `main` 8d618fd -> **d9ae18e**, 3 files (requirements.txt, package.json, package-lock.json). Deps-only, no migration, prod-runtime-neutral.
- Prod QA PASS: main CI green on d9ae18e (Playwright E2E + pytest + gitleaks + NUL-byte); Railway prod /health ok (environment production, clean boot on bumped deps); /api/version 1.2; /api/models/all US+PK 200; both prod fronts (snapai.mainnov.tech + pk.snapai.mainnov.tech) 200.

**OPEN / follow-ups (DATED):**

| Priority | Item | Owner | Notes |
|----------|------|-------|-------|
| LOW | **Dependabot security advisory #34 (moderate)** | Shoab | GitHub flagged 1 moderate advisory on the default branch during the prod push. Pre-existing transitive, NOT from this week's bumps. Review: github.com/mohammed-shoab/ScopeSnapAI/security/dependabot/34 |
| LOW (watch) | Turbopack adoption (DEC-113) | snapai-dev | Still PLANNED; unaffected by this dep bump. |

---

## Playwright e2e CI (`playwright-e2e.yml`) — RED→GREEN + PROMOTED TO PROD — 2026-06-22 (DEC-125)

| Item | Result |
|------|--------|
| Root cause | Clerk v7 `clerkMiddleware` ran a dev-browser handshake on the dev-only `/test-harness/*` routes → 302 to the FAPI domain in the publishable key; under the e2e dummy key that domain is `clerk.example.com` (non-resolving), so every Chromium nav died `net::ERR_NAME_NOT_RESOLVED`. RED since the Next 16/React 19/Clerk v7 migration (Clerk v5 didn't do this handshake). Loopback/proxy/IPv6 were red herrings. |
| Diagnosis method | Reproduced locally on Windows with the bundled Chromium; isolated the true failing URL via `page.on('requestfailed')` (printed `https://clerk.example.com/v1/client/handshake?...`). A trivial Node server proved Chromium reaches every loopback fine. |
| Fix (3 files, prod-runtime-neutral) | `proxy.ts`: exclude `test-harness` from the middleware matcher + dev-gate strict CSP (`IS_DEV ? {} : { contentSecurityPolicy }`). `next.config.js`: `allowedDevOrigins`. `playwright.config.ts`: dropped the misdiagnosed proxy/host-resolver launch args. |
| Staging | CI run #56 (`724fdf7`) = **completed successfully, 34/34** (17 specs × 2 projects: chromium + mobile-chrome). Staging QA clean (dashboard renders through middleware, sign-in→dashboard auth redirect, Clerk under strict CSP, **zero console errors**, test-harness renders a full report). |
| Prod | Promoted `main` **`b09f155`** (file-scoped overlay per DEC-102; in prod `IS_DEV` is false so strict CSP is unchanged — only dev/test-harness routing changes). Prod QA clean (dashboard + real data, auth redirect, no new console errors). |
| Docs | DEC-125 in DECISIONS.md; TECH_STACK.md Playwright-CI section + PROJECT_BRAIN.md header + this entry all updated 2026-06-22. |
| `snapai-qa` skill | Phase 1.5 fixed (clone URL `SnapAIAI`→`ScopeSnapAI`, pnpm→npm, install `@playwright/test@1.61.0`, drop the `PLAYWRIGHT_BASE_URL_*` vars the config never read; added an "Option A = check CI status" path) + repackaged as `snapai-qa.skill` (Drive `Personal Claude/Skills/` for cross-laptop install). |
| Note | The `audit/` harness Playwright (`snapai-audit-harness`, used by `snapai-full-audit`) is a SEPARATE suite — fixing this CI does not touch it. |

**Git state:** staging `724fdf7` → main `b09f155` — PROMOTED TO PRODUCTION 2026-06-22 ✅

---

## Scope 4.13/4.14/4.15 — Copy + Signed-In Redirects + Video Embed — COMPLETE + LIVE 2026-05-27

| Check | Result |
|-------|--------|
| 4.13 Codie's copy on `/` (3 steps) | PASS — both markets, server confirmed |
| 4.13 Copy on `/tech` (eyebrow, subhead, callout, 3 steps) | PASS — both markets |
| 4.13 Copy on `/homeowner` (eyebrow removed, market scope added) | PASS — both markets |
| 4.14 Signed-in redirect on `/tech` → `/dashboard` | PASS — confirmed in browser (US staging) |
| 4.14 Signed-in redirect on `/homeowner` → `/dashboard` | PASS — confirmed in browser (US staging) |
| 4.15 `<video>` embed on `/` | PASS — both markets, YouTube gone |
| 4.15 `<video>` embed on `/tech` | PASS — both markets |
| Prod deploy — US `snapai.mainnov.tech` | PASS — Vercel Ready 2m 2s, commit 932b20e |
| Prod deploy — PK `pk.snapai.mainnov.tech` | PASS — server returning new copy, old copy gone |

**Git state:**
- `staging` branch HEAD: `f58c77e`
- `main` branch HEAD: `932b20e` — PROMOTED TO PRODUCTION 2026-05-27 ✅

---

## Session 2026-06-20 — Full release PROMOTED TO PROD + Dependabot triage (DEC-112)

**DONE this session:**
- Promoted the full staging release to PROD (main commit `5b092eb653`): Next 16/React 19/Clerk v7 migration + accumulated Brand-Decoder/audit work + migrations 037-041 (041 new to prod) + Dependabot backend bumps. File-scoped overlay incl new package-lock.json + middleware.ts->proxy.ts delete.
- Verified prod: e2e CI #32 green; Vercel prod build green; Railway backend green (alembic 041 applied, clean boot); /health ok; /api/version 1.2; Sentry v10 delivering on Next 16 prod (ingest 200); dashboard clean (resolved deliberate test markers).
- Dependabot: closed stale main-targeted #2-#6 (superseded); merged staging #7 (CI actions), #9 (pip group 18 bumps), #11 (joblib); #8 already closed; #10/#12/#13 deferred to Dependabot rebase. Backend pytest 122 passed against bumped deps.
- Vercel staging DSN confirmed set; Sentry watch clean.

**OPEN / follow-ups (DATED):**

| Priority | Item | Owner | Notes |
|----------|------|-------|-------|
| MED | **Turbopack adoption (DEC-113)** | snapai-dev | PLANNED, not started. Earliest start **2026-06-27** (after ~1wk Next16 prod bake); target **2026-06-27 -> 2026-07-11**. Prereqs: Sentry -> instrumentation-client.ts + drop disableLogger; Tailwind v3-under-Turbopack spike or v4; remove next.config webpack() block; flip to `next build`. Staging-first. |
| LOW (watch) | Next 16 prod bake | snapai-dev | Watch Sentry ~1 week post-2026-06-20 for any React 19/Clerk v7 prod regressions before starting Turbopack. |
| LOW | Dependabot rebase #10/#12/#13 | Dependabot | numpy/openpyxl/xgboost floor bumps; auto-rebase after #9/#11. |

---

## Session 2026-06-18 (PM2) — Next 16 / React 19 / Clerk v7 migration (DEC-112)

**DONE this session:**
- Migrated scopesnap-web: Next 14.2.15->16.2.9, React ^18->^19, @clerk/nextjs ^5.7.2->^7.5.3, eslint ^8->^9, eslint-config-next 16.2.9 (sentry already ^10.58.0).
- Next 16 async APIs (awaited params/headers); middleware.ts->proxy.ts + Clerk v7 `auth.protect()`; SignIn/SignUp prop renames; tsconfig baseUrl; build `next build --webpack`; globals.css `@keyframes dashRot` fix.
- Fixed React-19/Next-16 bugs: chooser-gate "16+years old" missing space (SWC trims space after `{expr}`) -> explicit `{" "}`; `useSearchParams` SSR hydration mismatch -> mounted-guards in both test harnesses.
- Fixed pre-existing staging failure: `ReportClient` now renders every tier's line items (removed `isSelected` gate) — bug-fixes-day1 e2e.
- Verified: tsc 0 errors; Vercel prod build green; e2e 34 passed; staging CI run #29 green; backend `/api/version` 1.2; Sentry v10 delivering on Next 16 staging build.
- Merged `feat/next16-react19-clerk7` -> staging (PR #14, `ba7e479`); staging deployed.
- Dependabot: closed stale main-targeted #2-#6 (superseded); merged staging-targeted #7 (CI actions), #9 (pip group, 18 backend bumps), #11 (joblib). #8 already closed (Next 16 conflict). #10/#12/#13 (numpy/openpyxl/xgboost floor bumps) deferred to Dependabot rebase (requirements.txt conflict after #9/#11).

**OPEN / follow-ups:**

| Priority | Item | Owner | Notes |
|----------|------|-------|-------|
| HIGH | Promote Next 16 / React 19 / Clerk v7 to prod | Shoab | Gated — deferred. Staging verified green; prod still Next 14 until go. |
| MED | Backend QA after pip-group merge (#9) | snapai-dev | 18 backend bumps incl fastapi 0.115->0.137, uvicorn 0.30->0.49 landed on staging — verify /health + pytest. |
| MED | Adopt Turbopack | snapai-dev | Currently `--webpack`; revisit after reconciling webpack config + Tailwind v3 postcss. |
| LOW | Dependabot rebase #10/#12/#13 | Dependabot | numpy/openpyxl/xgboost floor bumps conflicted post-#9/#11 merge; will auto-rebase. |

---

## Session 2026-06-18 (PM) — Dependabot / dependency upgrades (DEC-110)

**DONE this session:**
- ✅ Triaged the 5 open Dependabot PRs live (labels were misleading — #2/#4 were a Sentry v8→v10 MAJOR, not minor).
- ✅ Landed on staging (`550cd50`) → prod (`8541182`): `@sentry/nextjs ^8→^10.58.0`, `@opentelemetry/core 2.8.0`, `dompurify 3.4.11` (one regenerated lockfile). CI green (staging #15, prod #18).
- ✅ §5 Sentry RE-PROVEN both envs after the major bump — ingest 200, SDK 10.58.0, events tagged staging + production (`SNAPAI-WEB-2`, resolved). Dashboard clean. Prod `/api/version` still 1.2.
- ✅ `dependabot.yml` policy committed to staging (target staging, group minor+patch, ignore majors, security on) — already byte-identical on main via audit-session `6f4925a`.

**OPEN / shelved:**

| Priority | Item | Owner | Notes |
|----------|------|-------|-------|
| MEDIUM | **React 19 / Next 16 / Clerk v7 migration epic** (Dependabot #5 next 14→16, #3 @clerk/nextjs 5→7) | snapai-dev | Both fail npm install on peer conflicts — both need React 19 (we pin `react ^18`). Deliberate multi-day migration: also Turbopack-default vs our next.config webpack block, middleware→proxy, async cookies()/headers()/params, Clerk v6/7 compat. Sentry v10 (a prerequisite) already done. Prod stays on Next 14 until done. |
| LOW | **Close the 5 stale main-targeted Dependabot PRs** | Shoab / Dependabot | #2/#4/#6 superseded by the landed bumps; #5/#3 shelved (ignored by new policy). Dependabot should auto-reconcile on next run (Mon 06:00 PKT) now that main targets staging. |
| LOW | **npm audit: 7 advisories (1 crit/5 high/1 mod)** | snapai-dev | Pre-existing transitive, not introduced by this change. `audit fix --force` makes breaking changes — needs a deliberate pass. |
| LOW (watch) | **Sentry post-deploy watch** | snapai-dev | Dashboard clean immediately post-deploy; keep an eye 15–30 min for any v10-related frontend errors. |

---

## Session 2026-06-18 — Observability audit + auth fix (DEC-106–109)

**DONE this session:**
- ✅ **Backend Sentry capture fixed** — catch-all handler now calls `sentry_sdk.capture_exception` (DEC-107, `09a5a87`→prod `e4eaf1b`). Proven `SNAPAI-API-17`.
- ✅ **Frontend Sentry wired + live** — `withSentryConfig` + CSP ingest allow + `NEXT_PUBLIC_SENTRY_DSN` on staging Vercel (DEC-108, `17ae165`→prod `390d54b`). Proven `SNAPAI-WEB-1`.
- ✅ **Gmail + Sentry-dashboard error audit** — emails all map to resolved/historical; the dashboard (not the emails) surfaced 8 real unresolved issues. Lesson logged: audit the platform, not the alert emails.
- ✅ **`SNAPAI-API-Z` auth bug fixed** (undefined `logger` + duplicate-provision race) — DEC-109, staging `37faefed` → prod `d432caad`. Live both envs, prod `/health` ok + `/api/version` 1.2. Had sat unresolved since the 2026-05-23 isolation audit (~4 weeks).
- ✅ **Sentry dashboard cleaned** — all 8 then-unresolved issues Resolved (Resolve, not Archive, to keep regression detection). Dashboard now empty all projects/envs.
- ✅ **Gemini billing verified live** — balance $9.97 healthy; 429 "credits depleted" errors were historical (topped up $10 Jun 7, expires Jul 1 2027); active key `SnapAI Backend Key 2026-06` (`...y2tg`).
- ✅ **Brain files updated** — PROJECT_BRAIN banner, TECH_STACK (Sentry/Gemini/Dependabot corrections), DECISIONS (DEC-106–109), this entry.

**OPEN — Shoab-owned:**

| Priority | Item | Owner | Notes |
|----------|------|-------|-------|
| MEDIUM | **Enable Gemini auto-reload** (AI Studio → Billing → "Set up auto-reload") | Shoab | Auto-reload is OFF. When the $9.97 prepay balance depletes, OCR 429s again with no auto-refill. Payment-method change — Claude can't do it. |
| LOW | **Fix or close Dependabot bump PRs** (`next` 14→16, `js-cookie`/`@clerk`) | Shoab / snapai-dev | Preview builds fail (breaking changes) → "Failed preview deployment" emails. Benign — never touch live prod/staging. PRs can't merge until breaking changes resolved. |
| LOW (watch) | **Watch `SNAPAI-API-Z` stays quiet on Sentry** | snapai-dev | Auth fix can't be synthetically triggered (needs a real new-user Clerk login). Sentry silence on this issue is the proof-of-fix signal. |
| LOW (optional) | **Make double-provision airtight** | snapai-dev | Fix made the webhook+fallback race non-fatal; ideally only one path should provision a signup. Cleanup, not urgent. |

NOTE: the older backlog task "Enable GitHub Dependabot" is now DONE — Dependabot is active and opening PRs.

---

## Last QA Run — /snapai-qa on PRODUCTION (2026-06-17 PM)
- **Target: PROD** (snapai.mainnov.tech). Run after Brand Decoder v1.2 promote (main `f70b6276`).
- **Phase 2 backend — PASS:** `/health` ok (db connected, environment:production); `/api/version` decoder/replace/brand_data **1.2** + `analytics_enabled:true`; prod DB (`zpsoprffaujswywtsgzy`) market data intact — **58 US brands / 15 PK brands**, York+Gree present, 19 US + 16 PK fault cards, **57 brands carry serial_decodable** (migration 039 backfill on prod); PSI thresholds **R-410A PK 125-145 ✓, R-32 PK 120-140 ✓** (R-22 US 60-82 vs skill-ref 88 — minor pre-existing reference nuance, not Brand-Decoder, not a regression); alembic head **040**.
- **Phase 1 UI (US prod, logged in) — PASS:** Flow 1 Not Cooling full diagnostic → Refrigerant Leak (High Conf) → estimate **rpt-592468** USD, **Finding-1 `[N]`→"At 18 years old…" substituted**, **Finding-2 Continue="Replace Immediately ($6,480)"=★REC**; Flow 6 nameplate manual entry inline-edit works; Flow 7 env-banner **correctly ABSENT** on prod (host=snapai.mainnov.tech, no StagingBanner, frontend PostHog env=`production`). a11y SidebarNav contrast clean.
- **Phase 1.5/1.6 — PASS (cited):** Playwright/axe CI run #5 on main `f70b6276` = **success 26/26** (the workflow triggers on push to staging AND main); backend pytest **120 passed** this session (`d7dbc2a8`, after fixing the `re`-loader regression); tsc clean via CI build.
- **Phase 1 UI (PK prod) — PASS (Shoab kept prod logged in; US+PK prod SHARE the same Clerk prod app, so the session carried over — no separate PK login needed).** Fresh PK diagnostic on pk.snapai.mainnov.tech: Gree (DWP Group), 1.5-ton, **R-410A** selector, install 2008 + Sure → Not Cooling → outdoor running YES → 55 PSI → **Refrigerant Undercharge/Leak (High Conf)** with PK-specific copy (soap-solution leak detect; "R-32 dominant in new PK split ACs, not interchangeable with R-410A") → estimate **rpt-076836** in **PKR**: ₨4,725 / ₨8,775 / ₨135,000. **Finding-1 LIVE:** Full Replacement reads "**At 18 years old**, complete system replacement shifts to R-32 or R-410A…" (real age, no `[N]`). **Finding-2 LIVE:** Continue = "Replace Immediately (₨135,000)" = ★REC. PK market routing (brands/fault-cards/currency) all correct on prod.
- **BOTH MARKETS now fully verified on production.** NOT individually re-run on prod: US Flows 2-5 (Service/Tune-Up, Water Dripping, Not Turning On) — covered by staging snapai-qa-master + identical promoted build. Skill's Phase 1.5 clone recipe is stale (pnpm/`SnapAIAI`/git@ SSH/`pak_diagnostic_questions`) — used real GitHub Actions CI + Supabase prod DB instead.
- **Minor obs (non-blocking):** opening a draft estimate's PDF before "Send" returns `estimate-rpt-…-unavailable.pdf` (PDFs generate on Send, not on draft) — expected behavior, noted.
- **Bugs found: 0** on prod. **QA result: PASS — both markets verified live on production.**
