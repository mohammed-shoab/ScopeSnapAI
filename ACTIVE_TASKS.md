# SnapAI — Active Tasks

**Last updated:** 2026-09-18 PM (**PROMOTED TO PROD** f2ba07e -> 18a1c3e, all CI + deploys green, Dependabot 28 -> 9 with 0 critical; prod click-through confirms F13/F14/CP7 live; NEW F15-F18; PKR unverifiable - zero PK companies exist)
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

## Session 2026-09-18 (PM) - PROMOTED TO PROD + post-deploy click-through

**PROMOTE EXECUTED.** Shoab's explicit go. `f2ba07e -> 18a1c3e`, DEC-070 scoped
overlay of 24 files (NOT a git merge - see the 2026-09-18 AM entry for why).
Verified live: main CI all green (backend pytest, Playwright E2E, gitleaks,
NUL-byte, RLS guard); Railway prod deployment ACTIVE + "Deployment successful",
which also proves `alembic upgrade head` resolved revision 048; both Vercel
projects rebuilt green.

**The urgent reason it had to go now.** Migration 048 had been applied to the prod
DATABASE while the migration FILE existed only on staging. `start.sh` runs
`alembic upgrade head` under `set -e`, so the NEXT backend deploy would have died
with "Can't locate revision identified by '048'". Prod was healthy but one deploy
away from a failed boot. Closed by shipping the file.

**Dependabot on the default branch: 28 -> 9. All 4 CRITICAL cleared** (next
16.2.12 -> 16.3.4). Also cleared sharp, nanoid, fast-uri, browserslist, dompurify
and the stale postcss 8.4.31. REMAINING 9 (staging is equally behind, not
regressions): js-yaml x2, brace-expansion x4, fflate, weasyprint x2 - one
weasyprint advisory has NO patched version.

**PROD VERIFIED BY HAND IN CHROME (US).** Full walk: sign-in -> dashboard -> new
assessment -> Step Zero manual (Carrier 24ACC6, auto-filled specs, 2015, Mild) ->
Not Cooling -> 55 PSI (classified low) -> SH 25 / SC 3 -> **Refrigerant Leak** ->
estimate builder (3 tiers, correct USD) -> Generate Documents (PDF + report link)
-> homeowner report -> Diagnoses list -> Pricing Rules.

  - **F14 CONFIRMED FIXED ON PROD.** Receipt now reads "Superheat above the target
    superheat maximum and subcool below the target subcool minimum". API confirms
    `target_source: null` - the identifier pointer is SUPPRESSED, i.e. the
    fail-closed policy behaving as designed. Zero schema anywhere in the UI, the
    homeowner report or the JSON payload.
  - **F13 CONFIRMED FIXED ON PROD** - question copy reads "115-140", not 115-141.
  - **CP7 PASS ON PROD (live proof of F7/DEC-136).** Public diagnostic route
    returns a byte-identical 1342-byte body under X-Market of none/US/PK/ZZ and a
    SQL-injection string. NOTE: the first attempt used the REPORT token and got a
    33-byte 404 - a VACUOUS pass. Caught it because 33 bytes was too short. Always
    sanity-check that the endpoint returns real data before trusting an
    equality-based security test.
  - F12 still present on prod, now proven at the DATA layer: `fault.confidence:
    "high"` vs `reading_receipt.confidence: "Medium"` in one payload.
  - Receipt still has `target_low: null, target_high: null` - the known follow-up.
  - "Recent Assessments" renders POPULATED on prod, so the empty list seen on
    staging was a data artifact, NOT a code bug. Earlier note corrected.

**NEW FINDINGS (prod, none caused by the promote)**
  F15  PK Urdu i18n, TWO defects, customer-facing. First visual confirmation of
       Urdu mode ever (pk-staging auth nav had always timed out). RTL layout flip
       itself works correctly.
       (a) BIDI: hero subtitle renders "seconds - AI-powered - three options, one
           recommendation 90" - the leading "90" is displaced to the END under
           RTL. String is also untranslated.
       (b) "LAST 5 ASSESSMENTS" left in English while its own child labels are
           translated - a missed translation key, not a missing locale.
  F16  PROD-ONLY pricing data defect. `pricing_rules`: prod has 28 rows vs
       staging 14, every national default duplicated EXACTLY twice, and the UI
       renders both copies. Separately - and true in BOTH envs - every row is
       `deprecated = true` yet still rendered to the user as "National Defaults",
       so the endpoint is not filtering on `deprecated`. Pre-existing; nothing in
       the promote seeds pricing data.
  F17  React #418 hydration mismatch on the PUBLIC homeowner report page.
  F18  Homeowner report `<title>` renders "HVAC Report - - Shoab DS's HVAC" - an
       empty segment with a doubled dash when no customer name is set.

**PKR / F6 IS NOT VERIFIABLE, IN EITHER ENVIRONMENT.** `companies` holds 17 rows
on prod and 4 on staging - **all market='US', zero PK companies anywhere.** There
is no PK tenant capable of producing a PK estimate, so the PKR branch of the F6
fix has never been exercised end-to-end and cannot be until a PK company exists.
Any earlier "PKR verified" note means unit/data level, NOT a live UI estimate.
This also means the PK production front-end is live with zero tenants, and that a
US company viewing the PK host correctly still sees USD (DEC-136: market comes
from the record owner, not the host).

**PROD DB STATE** alembic 048, RLS on 56 tables, `rls_auto_enable_trg` armed
(evtenabled='O'), anon EXECUTE revoked. NOTE: the trigger is named
`rls_auto_enable_trg`, NOT `rls_auto_enable` - a verification query using the
bare name returns 0 and looks like a regression. It is not.

---


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
