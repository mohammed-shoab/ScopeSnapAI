# SnapAI — Active Tasks

**Last updated:** 2026-09-18 (F14 identifier-leak FIXED, suite 237 green; migration 048 applied to PROD - CP2 closed; CP3 accepted - DEC-137; promote scoped to an overlay, NOT executed)
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

## Session 2026-09-18 - F14 fixed, prod migration 048 applied, promote scoped

**F14 - raw DB identifiers in user-facing copy. FIXED (staging).**
Found by clicking through staging in a REAL browser on a Refrigerant Leak
diagnosis. The reading receipt showed the technician
`superheat_subcool_targets.target_superheat_min_f,target_superheat_max_f` as
"Compared against", and `SH above target_superheat_max_f AND SC below
target_subcool_min_f` as "why this card" - database schema on screen, and the
actual target numbers never shown at all. Sanitised in the BACKEND
(`_humanize_receipt_source` / `_humanize_receipt_why`) so web, PDF and the
homeowner report are all covered. Policy is FAIL CLOSED: a string that still
looks like an identifier after translation is dropped, not rendered.
25 new tests; suite 212 -> **237 passed**.

**Still open from the visual pass (NOT fixed, deliberately):**
- F12 - two contradictory "Confidence" values on one screen. Needs a product
  decision (relabel vs reconcile), not a unilateral code change.
- The receipt still shows "reference targets" with NO numbers for
  superheat/subcool cards. Suppressing the leak was the safe half; resolving the
  real numbers needs a lookup key that is not obviously available.
- Dashboard "Recent Assessments" renders EMPTY despite resolved diagnoses
  existing. Observed, not investigated.

**PROD change - migration 048 applied and verified (CP2 CLOSED).**
The DEC-135 RLS work was genuinely absent on prod, not just an unstamped version.
Applied to prod Supabase and verified: `tables_rls_on=10`, `trigger_armed=1`,
`evtenabled='O'`, `anon_can_exec=false`, `alembic='048'`. This is the ONLY prod
change made; prod CODE remains at `f2ba07e`.

**CP3 CLOSED as accepted - see DEC-137.** Stop re-raising it.

**Promote scoped, NOT executed.** A `git merge staging -> main` produces **11
conflicts**, not the 3 an earlier dry run reported against a much older staging
HEAD. Root cause: every main-side commit on the conflicted code files is a
`promote:` commit from `scripts/promote-to-prod.sh`, which is a scoped FILE
OVERLAY, not a merge. This repo has never done a true git merge to main, so git
is comparing two histories that were only ever copied between. **Verified safe:**
every main-only line in `diagnostic.py` (23), `pdf_generator.py` (2) and
`FaultResolutionScreen.tsx` (8) is the PRE-FIX code these patches replace - there
is zero independent main-side work in them. Use the overlay, not a merge.

---


## Session 2026-09-17 (visual) - 3 findings that only LOOKING could catch

Staging HEAD 57300dc. Prod untouched.

First visual pass of the audit: Playwright drove US staging and saved 9
screenshots to `Personal Claude/audit-screens/`, which were then actually read.
Everything else in this audit - 212 tests, ZAP active, semgrep, k6, gitleaks -
had already passed. These three were invisible to all of it, because the code
ran fine; it just told the technician the wrong thing.

| # | Finding | Status |
|---|---------|--------|
| F11 | **Staging share links pointed at PRODUCTION.** The fault screen footer read `snapai.mainnov.tech/d/159529f437...` on a STAGING page. `diagnostic.py` hardcoded the prod hosts in two places with no env awareness; CP7 had already proved a staging token 404s on prod. Now derived from `settings.frontend_url` via `_public_base_url(market)` with PK host mapping. `FRONTEND_URL` already existed on every Railway service and was simply unused. | **FIXED** |
| F13 | **Displayed band contradicted the classifier.** Receipt showed "Compared against 115-141 PSI -> WITHIN RANGE" but canonical is 115-140 normal / >=141 HIGH, and the classifier uses 140. Cause: `low_threshold` (115) is an INCLUSIVE bottom while `high_threshold` (141) is an EXCLUSIVE start-of-high - confirmed against staging `diagnostic_questions.reading_spec` (discharge is the same shape: 225/276). Band top now steps back one unit. | **FIXED** |
| F12 | **Two contradictory "Confidence" values on one screen.** Header pill `data.fault.confidence` = "High Confidence"; receipt `reading_receipt.confidence` = "MEDIUM", four lines apart. Separate backend fields that may legitimately measure different things (diagnosis vs reading quality) - but both are labelled just "Confidence", so the screen argues with itself in front of a homeowner. | **OPEN - product decision: relabel or reconcile** |

14 regression tests (`test_f11_f13_visual_findings.py`), red-green verified:
10 fail against unpatched code. Full suite **212 passed**.

**Rendered correctly** (verified by eye): dashboard, assessments list, Step Zero,
complaint grid, diagnostic tree, fault resolution, Pricing Database. STAGING
banner present, correct identity, no layout breakage. US pricing shows `$95/hr`,
`$1,400`, `$250` - the F6 fix behaving correctly on the US side.

**Also seen:** the dashboard shows "Recent Assessments" EMPTY and "Your first
assessment is 3 taps away" even though the walkthrough had resolved diagnoses.
Either assessments only surface once an estimate is finalised, or they are not
being listed. Not yet investigated.

**Lesson worth keeping:** a green suite means the code did not crash. It does not
mean the screen is right. Every finding above was a correct-looking code path
rendering a wrong number or a wrong link. Budget a visual pass in every audit.

## Session 2026-09-17 - audit close-out: F9 fixed, walkthrough real, Phase 4 scored

Prod/main untouched. Staging HEAD a8ffa3a.

### Shipped

| PR | What | Staging |
|----|------|---------|
| #70 | **F9** non-UUID path param caused an unhandled 500. 7 `{estimate_id}` params typed `UUID` (5 estimates.py, 2 payments.py) + a narrow `DBAPIError`->400 handler in main.py covering the 18 `assessment_id`/`session_id` params still typed `str`. 18 tests, red-green (11 fail unpatched). Suite: **198 passed**. | 61b694f |
| #71 | The assessment -> diagnosis walkthrough, for real. | a8ffa3a |

### F9 - why it hid

Sentry **SNAPAI-API-1A**: `GET /api/estimates/new` -> `DataError: invalid UUID
'new'`. It hid because the old flow test asserted against **`/assessment/new`
(singular), which is not a route** - Next matched `[id]` with `id="new"`, the
page rendered "Loading estimate...", the test went GREEN, and the backend 500'd
underneath. Real entry: **`/assessments/new`** -> `/assess`. A render check is
not a behaviour check; the walkthrough now asserts state transitions and fails
on ANY 5xx.

### Walkthrough now genuinely works

`/assessments/new` -> `/assess` -> Step Zero via **manual tab** -> "Not Cooling"
-> question tree -> resolved **"Ductwork Leak | High Confidence"**, 0x 5xx.
Determinism via `localStorage.snap_sz_path="manual"` - the app's OWN A/B key,
not a backdoor. Asserts PROGRESS (>=1 step), not resolution: a first-option
answerer should not be trusted to navigate a clinical decision tree.

### CORRECTION - Step Zero is NOT a hard photo gate

An earlier entry claimed a nameplate photo was mandatory. **Wrong** -
StepZeroPanel has a photo|manual tab pair; manual's "Confirm & Continue" calls
`onConfirm` directly.

### NEW - F10 (LOW): dead `onSkip` prop

`components/StepZeroPanel.tsx` declares `onSkip` (L68) and destructures it
(L114) but **never invokes it**. `app/(app)/assess/page.tsx:462` wires
`onSkip={() => setPhase("complaint")}` - a handler that can never fire. Either
restore a skip affordance or delete the prop. Not a blocker: the manual tab
works.

### Phase 4 promote gate - SCORED

| # | Checkpoint | Result |
|---|------------|--------|
| 1 | Staging deploy live | **PASS** |
| 2 | Schema parity | **FAIL** - staging alembic 048, prod 047. Migration `048_rls_threshold_tables_and_auto_enable_trigger.py` is on staging; `c3eb21c` (DEC-135) is NOT an ancestor of main. A promote MUST run 048 on prod. |
| 3 | Env-var key parity | **CLOSED - ACCEPTED (DEC-137)** - `CRON_SECRET` is set on PROD (fails closed, verified) and deliberately NOT set on staging. Shoab's decision 2026-09-18. Staging-only exposure, not a promote blocker. CP3 must score this PASS-with-note from now on. Missing on PROD would still be a real FAIL. |
| 4 | Smoke both markets | **PASS** - all 4 surfaces HTTP 200, len 2437 |
| 5 | Console-error baseline | **PASS** - NOVEL=0 both markets; staging 26 vs prod 33 |
| 6 | Railway log baseline | **NOT MEANINGFUL** - ZAP active + k6 500 VUs deliberately generated thousands of errors on staging the same day. Needs a quiet window. |
| 7 | Cross-market isolation | **PASS** - live proof of F7: no header / `X-Market: US` / forged `X-Market: PK` / SQL-injection string in the header all return byte-identical results (HTTP 200, len=996, card 'Refrigerant Leak'). Staging token 404s on prod; bogus token 404s. |

### Observability - filter NOT working on staging

`SNAPAI_AUDIT_MODE` is **not set on the Railway staging service** (confirmed in
Variables). That is why SNAPAI-API-1A reached Sentry - `_sentry_before_send`
never engaged. **The audit polluted Sentry**, exactly what mitigation #4 exists
to prevent. Set it before the next run.

### STILL NOT VERIFIED - F6 PKR rendering

F6 (PR #66) is verified only by code reading + CI. A Playwright check to sign in
on **pk-staging** and assert the rendered currency got as far as auth
(`PK hostname: pk-staging...`) but **authenticated PK nav times out**
(`net::ERR_ABORTED`, then 30s, across 4 retries). Spec NOT committed - it does
not pass. Nobody has SEEN PK render its own symbol. Treat F6 as
fixed-in-code, unproven-on-screen. Check pk-staging perf / Clerk cross-domain
handoff on that hostname.

### Open findings

| # | Finding | Severity |
|---|---------|----------|
| F1 | Live Gemini key in PUBLIC git history - risk ACCEPTED by Shoab, key NOT rotated | HIGH |
| F3 | 200-VU p95 ceiling (Hobby plan, not a code defect) + **9 RLS policies re-evaluating `auth.<fn>()` per row** + 17 unindexed FKs | MEDIUM |
| F4 | CI gitleaks is incremental - never rescans history | MEDIUM |
| F5 | Local `scopesnapai-web` container crash-looping | LOW |
| F10 | Dead `onSkip` prop | LOW |
| - | ~~`CRON_SECRET` missing on staging~~ CLOSED - accepted, DEC-137 | - |
| - | `SNAPAI_AUDIT_MODE` not set on Railway staging | MEDIUM |
| - | prod missing migration 048 (DEC-135) | MEDIUM |
### Never run: `webapp-testing`, `accessibility-a11y-enhanced`, GStack
`qa`/`benchmark`/`review`, `quality-playbook`. No human clicked through the site
in a visible browser - all UI coverage is headless Playwright.

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
