# SnapAI — Active Tasks

**Last updated:** 2026-09-16 (audit fixes: F6/F8 via PR #66, F2/F7 via PR #67, 180 tests green; Phase 4 checkpoint 2 FAILS - prod missing DEC-135 migration 048)
**Historical sessions:** see `ACTIVE_TASKS_HISTORY.md` (60-row session-log index at top)

---

## In Flight — 4 active workstreams (as of 2026-07-06)

| # | Workstream | Owner + Advisor | Status | Blocking on |
|---|---|---|---|---|
| 1 | **Legal cover + wordings** | Shoab + Alfred (nav) | DEC-130 v1 SHIPPED to prod 2026-07-06 | Wyoming LLC entity formation; Gate 1/2 substantiation; PK lawyer |
| 2 | **New complaint cards (Tier A)** | Shoab + Bryan (board) | ⚑ SHIPPED TO PROD 2026-07-08 (GATE D, Shoab's explicit go) — full diagnostic engine + data live on snapai-prod-use1, verified end-to-end (DEC-132). FREE BETA. | Legal Gate 1/2 substantiation is a pre-BILLING gate, NOT a code blocker; LOW-conf #25/#26 confidence upgrade pending Houston field pilot (N>=30) |
| 3 | **Brain files cleanup + future system** | Shoab + Karpathy (nav) + Rob (board) | Phase 1+2+3 executed 2026-07-06 | Path Y merge to staging + promote to prod |
| 4 | **TikTok video marketing** | Shoab + Azhan | Upcoming — not yet scoped | Owner, tools, budget TBD |

**Standing rules for active work:** DEC-070 staging→main→prod path, DEC-088 no future-tense homeowner promises, DEC-123 PK dormant, DEC-129 verify live Supabase not migrations, Card #21 PERMANENTLY EXCLUDED, ALFRED C1/C2/C3 baked into all [A!] cards. See `PROJECT_BRAIN.md` CRITICAL RULES for full list.

---

## Recent sessions (2026-06-18 onward — Bryan's exception: any session with any OPEN item stays)

## Session 2026-09-16 (later) - audit findings FIXED on staging

Prod/main untouched throughout. Staging HEAD f1ad5cd.

### Shipped

| PR | Finding | Fix | Staging |
|----|---------|-----|---------|
| #66 | **F6** PK market rendered estimates in USD | dropped the hardcoded `fmt()`; all 4 call sites now use the existing market-aware `formatCurrency()` from `lib/market.ts`. 0 hardcoded `currency:"USD"` left. | d2bf691 |
| #66 | **F8** ambient below lowest `operating_targets` row fell back to a HOT band | when the floor lookup misses, select the COLDEST configured band. Zero-row pairs (US R-32, static by design) keep the fallback dict. | d2bf691 |
| #67 | **F2** SSRF guard bypassable via HTTP redirect | `_NoRedirectHandler` + `_safe_open()`; both fetches refuse redirects. 0 bare `urlopen` left. | f1ad5cd |
| #67 | **F7** public diagnosis route trusted the spoofable X-Market header | NO migration needed: `diagnostic_sessions.company_id -> companies.market` gives a trusted source. Route now uses `tables_for_market(company_market)`; `Depends(get_tables)` REMOVED from the signature. See DEC-136. | f1ad5cd |

25 regression tests added across the two PRs; **pytest 180 pass**. F8's two
behavioural tests were red-green verified (fail on unpatched code). F2's file
fails at COLLECTION on unpatched code (ImportError on the new `_safe_open`), so
its real proof is the live-loopback test asserting a 302 is NOT followed.

### Audit gap closed

The authenticated `audit/` Playwright harness **PASSED** - first time. But it
lands on `/onboarding`, not `/dashboard` as the skill doc expects: the Clerk test
user is un-onboarded, so **new assessment / nameplate OCR / diagnostic walkthrough
/ estimate builder are STILL unexercised**. Login is proven; the product is not.
Worth onboarding the audit user so the harness reaches the real flows.

### NEW - Phase 4 promote gate: CHECKPOINT 2 FAILS

**Prod is missing the DEC-135 RLS migration.**

- staging alembic_version = **048**, prod = **047**
- `048_rls_threshold_tables_and_auto_enable_trigger.py` exists on staging
- commit `c3eb21c` (DEC-135) is **NOT an ancestor of origin/main**

Any staging->main promote must run migration 048 against prod. Until then prod
lacks the Tier A threshold-table RLS hardening.

**Documentation gap:** DEC-135 is cited by commit `c3eb21c`, by migration 048 and
by the `fix/rls-guard-dec135` branch, but **no DEC-135 entry exists in
DECISIONS.md** (highest present was DEC-134). Someone should write it up.

### F3 re-diagnosed - NOT a code defect

k6 hit `/api/health`, which touches no tables, so the 200-VU p95 failure is
Railway Hobby-plan CPU, not queries. Upgrading the plan is a spend decision, not
a fix. BUT the Supabase advisors found real scale problems that WILL bite under
authenticated load:

- **9 RLS policies re-evaluate `auth.<fn>()` / `current_setting()` per row**
  (`assessments`, `estimates`, `users`, `properties`, `pricing_rules`,
  `diagnostic_sessions`, `job_confirmations`, `photo_labels`, `reading_inputs`).
  Fix is wrapping the call as `(select auth.<fn>())`.
- 17 unindexed foreign keys; 48 unused indexes.

### Still open

| # | Finding | Status |
|---|---------|--------|
| F1 | Live Gemini key in PUBLIC git history | OPEN - Shoab accepted the risk 2026-09-16; key NOT rotated. Cannot be actioned by an agent (needs GCP console). |
| F3 | 200-VU p95 ceiling | OPEN - capacity decision + the RLS initplan work above |
| F4 | CI gitleaks is incremental, never rescans history | OPEN - needs a scheduled full-history job |
| F5 | Local `scopesnapai-web` container crash-looping | OPEN - local dev only |

### Environment notes worth keeping

- `next build` CANNOT be run on Shoab's machine: Turbopack fails to resolve
  `tailwindcss` under the machine-wide `NODE_ENV=production`. Verified it fails
  identically on UNPATCHED staging, so it is environmental, not a regression.
  CI is the only frontend build gate. `npm ci --include=dev` is required locally.
- `FaultResolutionScreen.tsx` and `diagnostic.py` are **CRLF**, unlike the
  brain files which are LF. Patch scripts must detect per-file endings.
- GitHub's "Compare & pull request" banner defaults the base to **main**. On this
  repo main IS prod. Always open PRs from an explicit `compare/staging...<branch>`
  URL and confirm the base before clicking create.

## Session 2026-09-16 - snapai-full-audit (mode=full, STAGING ONLY)

Prod/main untouched. Staging HEAD 556414c. Full report: `SnapAI_Full_Audit_2026-09-16.md`
(in the Personal Claude workspace folder, not committed to the repo).

Shipped this session:
- PR #64 merged to staging: fast-uri 3.1.2 -> 3.1.8 (lockfile-only, 3-line diff, integrity hash
  verified against npm registry). Clears Dependabot #78/#86/#87/#88/#89 and removes the only
  package regression a future staging->main promote would have introduced.

Open findings (none fixed in-loop):

| # | Finding | Severity | Where |
|---|---------|----------|-------|
| F1 | Live Gemini API key in PUBLIC git history; Clerk sk_test too. No rotation evidence. **Shoab accepted the risk 2026-09-16 - key NOT rotated.** | HIGH | `session_logs/SESSION_LOG_2026-05-21_code_audit.md` L126 |
| F2 | SSRF guard bypassable via HTTP redirect - `_is_safe_remote_url` validates the initial URL, then `urlopen` follows redirects without re-checking. DNS-rebinding window too. | MEDIUM | `scopesnap-api/services/pdf_generator.py` L441, L509 |
| F3 | Throughput knee between 50 and 200 VUs on `/api/health` (cheapest endpoint). p95 4313ms @200, 8.76% failures @500. | MEDIUM | staging infra |
| F4 | CI gitleaks is INCREMENTAL - never rescans history. Green for months while F1 sat there. | MEDIUM | `.github/workflows/gitleaks.yml` |
| F5 | Local `scopesnapai-web` container crash-looping `Restarting (254)`. Local dev only. | LOW | local docker |
| F6 | **PK market renders estimates in USD.** `fmt()` hardcodes en-US/USD; component resolves market on L140 but never passes it. 4 call sites render tier totals + line items. BUG-037 class recurrence. | HIGH (PK) | `scopesnap-web/components/FaultResolutionScreen.tsx` L131 |
| F7 | Inconsistent market trust on public routes: `reports.py` correctly uses `tables_for_market(estimate.market)`; `diagnostic.py` public route still uses the spoofable X-Market header. Root cause: only `estimates` has a `market` column. | MEDIUM | `api/diagnostic.py` L2316 vs `api/reports.py` L234 |
| F8 | Ambient below the lowest `operating_targets` row falls through to a HOT-band fallback. `ambient_c` is user-supplied with no ge/le constraint. Worst: PK R-22 has only 2 rows (35/45), so 30C falls back to the 45C band. Biases toward false `low` -> false refrigerant-leak diagnosis. | MEDIUM-HIGH | `api/diagnostic.py` L596-655, L50 |

Verified PASS this session:
- PSI assertions: R-410A 130 PSI -> `ok` (exclusive bounds, boundary value - needs a regression
  test to lock it), R-22 high_min 88, R-32 high_min 140.
- Urdu integrity: 653 Urdu runs in `lib/urdu-strings.ts`, 0 U+FFFD, real UTF-8.
- backend pytest 155 pass / 0 fail.
- ZAP active: SQLi, RCE, SSTI, XXE, cloud-metadata all PASS.

Corrections made during the audit (recorded so they are not re-litigated):
- "US R-32 has 0 operating_targets rows" is NOT a defect. PROJECT_BRAIN L84 specifies R-32 US/PK as
  a static 110-145 band and the code fallback matches. Doc, code and DB agree.
- 28 of 30 semgrep `avoid-sqlalchemy-text` ERRORs are FALSE POSITIVES. The f-strings interpolate
  only table/column identifiers sourced from `MarketTables` (frozen dataclass, 16 hardcoded
  literals); `get_tables()` uses strict equality so a hostile X-Market header cannot become a table
  name. All user values use bound params. ZAP active found no SQLi, corroborating this.

Doc staleness spotted: PROJECT_BRAIN L84 lists R-32 as US/PK static, but PK R-32 now has 5
ambient-aware DB rows (100-165 PSI) that override it. Canonical table should mark R-32 PK dynamic.

Skill-doc fix needed: `snapai-full-audit` P2 references `sentry.client.config.ts`, which does not
exist. The client Sentry filter lives in `instrumentation-client.ts` (Next 16 / Turbopack).

NOT run this session: `audit/` Playwright harness (authenticated flows), webapp-testing,
accessibility-a11y-enhanced, GStack qa/review/benchmark, quality-playbook, Phase 4 promote gate
(needs prod DB + Vercel/Railway env access), Phases 5-6. Cross-market isolation was verified by
code inspection, not by a live cross-market 404 test.

## Session 2026-07-08 — Tier A diagnostic families PROMOTED TO PROD (GATE D)

**DONE this session:**
- Executed GATE D on Shoab's explicit "do it completely till prod" go. Full Tier A build now LIVE on production (snapai-prod-use1 `zpsoprffaujswywtsgzy`).
- Two-phase code overlay (DEC-070): Phase 1 `5755dad` (backend evaluators + reading-receipt, fault_estimate cap le=26, level2 copy, migrations 046+047, 4 diagnostic components); Phase 2 `24efadf` (assess complaint entries, pushed AFTER data to avoid empty-flow window). Railway auto-ran alembic 045→046→047; Vercel deployed. Sign-in/sign-up mojibake fix `d8e60eb`.
- DB data does NOT auto-promote (separate Supabase projects) — replicated staging→prod via base64 transport + per-table md5 checksum (all matched first try): 10 threshold tables (195 rows), fault_cards 20-26, pricing_tiers card_id>=20, 17 new diagnostic_questions + 2 rewires. Prod fault_cards 19→25, dq 44→61. Method captured in DEC-132.
- Verified on prod: counts + routing integrity (0 dangling) + checksums=staging + full authenticated browser click-through (Comfort/Humidity → Clammy → Card #22 with Reading Receipt 350-402.5 CFM/ton, disclaimers, Estimate Builder $239/$478).
- POST-GATE-D PROD QA (2026-07-08, snapai-qa skill) — **QA COMPLETE / PASS**: prod backend health ok (db connected, environment=production, /api/version decoder+replace 1.2); pytest 155 passed on main; Playwright E2E CI GREEN on main (#84 Phase1 / #85 Phase2 / #86 sign-in); prod UI regression — Not Cooling core 128 PSI → NORMAL → Ductwork Leak (High Conf), no misroute to high-pressure, no crash/503; Tier A Comfort → Card #22 receipt+estimate live; StagingBanner correctly ABSENT on prod; data counts/routing/checksums = staging. No bugs found, no fixes needed.

**OPEN / follow-ups:**

| Priority | Item | Owner | Notes |
|----------|------|-------|-------|
| MEDIUM | LOW-confidence cards #25 (liquid-line) / #26 (compressor) are LIVE but carry LOW confidence pending Houston field pilot (N>=30, >=85% match). Code + feedback loop ready; confidence UPGRADE gated on real field data. | Shoab | Gap 3 — empirical, not closable by calc |
| LOW | Bryan's 2 directional refinements logged (D3 coil-drop 0.20 → prefer rated coil drop; D4 14F TXV starved-superheat treat as directional) — not blockers | Shoab + Bryan | From SnapAI_TierA_Bryan_Clinical_Review.md |
| NOTE | Legal Gate 1/2 substantiation is a pre-BILLING gate (app is FREE BETA); cards carry Alfred C1/C2/C3 disclaimers live. Not a code-deploy blocker. | Shoab + Alfred | Reconciles ACTIVE workstream 2 |

---

## Session 2026-07-08 — Bryan compendium ship (Path B) + video-marketing thread recall

**DONE this session:**
- Verified Bryan Orr HVAC compendium outputs (parallel extraction, 30 Opus subagents, 959 episodes): master compendium 1443 lines + 12 topic files 25,292 lines + 3 refreshed board refs + session log + push script + 30 raw batch JSONs — all present and correctly structured.
- Chose Path B (mirror-and-commit) over leave-in-Drive or session-log-only. Mirrored 16 files into `ScopeSnapAI/snapai-board/references/bryan-orr/`.
- Committed staging (`70b03bd` feat) + promoted to main (`47d4c37` scoped) via DEC-070. Board persona knowledge now git-versioned. DEC-131 sets the mirror-and-promote precedent for future board compendia.
- Live-tested Bryan compendium load: `@board Bryan` diagnostic-sequence test (3-ton R-410A overcharge scenario) returned episode-cited response with 4 verbatim episode IDs (`qIo_iT8msZA`, `lfuiVg8WSQ0`, `QjF4I8db1kA`, `6WlUva3hrhk`) — confirms router row 20 + skill protocol both trigger the compendium reads.
- Recalled the paused video-marketing thread — surfaced `SnapAI_Video_Marketing_Strategy_TwoDoor.md` (2026-05-22) + `SnapAI_Virality_FreeTrial_Strategy_Boards_Recommendations_2026-07-01.md` (27 voices) + Panel 5 additions (Bryan/Jenny/Zaria/Alex Su) + Nav additions (MrBeast/Reilly). Flagged honestly: Panel 5 + Reilly/MrBeast opinions on the virality strategy were NOT persisted to a follow-up doc — only their persona files exist.

**OPEN / follow-ups:**

| Priority | Item | Owner | Notes |
|----------|------|-------|-------|
| HIGH | Re-run virality-strategy question to full boards with 6 new voices (Panel 5 + MrBeast/Reilly) given DEC-130 legal shipped + Tier A app shipped + Bryan compendium loaded | Shoab + @board + @nav | Running next in this session |
| HIGH | Q7.1 from 2026-07-01 doc STILL open + blocking: current SnapAI diagnostic accuracy % across last 30 days of tester data. Karpathy's >80% threshold gates the whole dependency thesis | Shoab | Was flagged "this week" on 2026-07-01, still open a week+ later |
| MEDIUM | Q7.2–7.7 from 2026-07-01 doc still open (buyer persona for videos, named 50 shop owners target list, daily-ritual metric measurability, production pipeline architecture, value metric for pricing, first-3-videos-for-14-day-test) | Shoab | Re-evaluate after board re-ask |
| LOW | Clean up laptop-side scratch files from Bryan extraction (_extraction/*.py, HVAC_School_Transcripts/build_b28.py) | Shoab | Drive mount blocks rm; Windows-side delete needed |

Pointer to session log: `session_logs/SESSION_LOG_2026-07-08_bryan_compendium_extraction.md` (parallel session created; success criterion #10 closed today via Path B ship).

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

## Last QA Run — /snapai-qa on PRODUCTION (2026-06-17 PM)
- **Target: PROD** (snapai.mainnov.tech). Run after Brand Decoder v1.2 promote (main `f70b6276`).
- **Phase 2 backend — PASS:** `/health` ok (db connected, environme

---

## 2026-07-14 — Public /tech landing rewrite + owner data-audit door (DONE, LIVE on prod)

**Done (DEC-133):** rewrote the public `/tech` landing to the locked hero definition + trades voice; **removed the two false/legally-exposed claims** ("real field experience" / "validated against real residential split-system calls"); consolidated to one CTA "Start free ->"; added the SECONDARY owner "Own a shop?" -> "Request your free audit ->" book-a-call door; **changed `/` to RENDER `/tech` via rewrite** (200, supersedes the 308). Updated `legal-redirects.spec.ts` (Playwright caught the routing change, fixed, CI green). Staging `93da676` -> prod (main) `551330a`. QA PASS both envs (banned-string grep zero, root rewrite + owner door verified in Chrome).

**Open items:**
- [ ] Shoab: confirm the TRUE scarcity number ("first 10 techs" is a placeholder used everywhere).
- [ ] Shoab: supply the real book-a-call URL (owner CTA points at `cal.com/REPLACE-ME/snapai-audit` placeholder).
- [ ] **Alfred: final legal pass on the live copy before it is declared public-ready.**
- [ ] Privacy agreement (privacy specialist) required BEFORE any owner-audit ticket/data intake — none is built yet.


---

## 2026-07-14 — Owner data-audit funnel on /tech (CODE DONE + live prod; FUNNEL not live)

Code shipped (DEC-134): self-ID link under the hero + visually-distinct "Own a shop?" section -> external qualifying FORM_URL (placeholder). staging `290dfd4` -> prod `156e71f`. QA PASS both envs (secondary to tech CTA, no data intake on page, no banned strings, Playwright green).

**GO-LIVE BLOCKERS (Shoab):**
- [ ] Privacy attorney finalizes the **Data-Use Terms** doc (consent-checkbox link).
- [ ] Configure the **qualifying form** (Typeform/Tally/Calendly) with consent checkbox (unticked, logged) + qualify logic (ServiceTitan/Housecall Pro/Jobber/Service Fusion = FIT -> calendar; QuickBooks/Paper/Other = capture email + soft follow-up).
- [ ] Configure **scheduler** (limited slots = scarcity) + **booking-confirmation email** (invites early CSV send; not gated) + **per-shop private folder**.
- [ ] Supply real **FORM_URL** -> swap `REPLACE_WITH_FORM_URL` in tech/page.tsx.
