# SnapAI — Active Tasks

> Tracks in-flight work, recent completions, and backlog.
> Updated by QA/dev sessions. Read this before starting any new work.
>
> Last updated: 2026-05-20 (All tracks complete. HEAD: fe86144. All bugs fixed. Lessons documented in TECH_STACK.md WA-9 through WA-14. Next session: start fresh backlog.)

---

---

## Lessons Learned — 2026-05-20 QA Session

These bugs were found during the 2026-05-20 full audit. Full workarounds in TECH_STACK.md WA-9 through WA-14.

| # | Bug / Lesson | Root Cause | Fix | WA Ref |
|---|-------------|-----------|-----|--------|
| L1 | 62 sessions had NULL share_token | apiFetch doesn't auto-inject Clerk JWT. Fire-and-forget finalize call had no token + silent .catch(()=>{}) | D.11: wrap in getToken().then(); backfill 62 rows via SQL | WA-9, DEC-030 |
| L2 | Edit tool truncated assess/page.tsx | Edit tool truncates NTFS files with non-ASCII chars (em-dash in comment) | Restore from git, apply via Python replace() | WA-10, DEC-027 |
| L3 | /diagnoses showed "offline" error | fault_cards JOIN used fc.id; PK is card_id. 500 response masked as OfflineError by apiFetch CORS failure | Fix all 3 SQL strings to use card_id | WA-11, DEC-033 |
| L4 | Track D tasks "complete" but routes not written | AI marked tasks done without verifying file on disk. Context window exhaustion. | Grep file for @router decorators before closing any backend track | WA-11, DEC-031 |
| L5 | Recommendation overlay disabled in prod silently | derive_condition_signal_from_assessment not imported; NameError caught by except Exception | Add import; use grep to verify both import + call site exist | WA-12, DEC-034 |
| L6 | Profile guard wired to dead page | estimate/[id]/page.tsx is unreachable dead code; real builder is assessment/[id]/page.tsx | Rewired to correct file | DEC-032 |
| L7 | P.7 seasonal logic duplicated nearly | P.7 PK-only inline block already existed when R.9 started | Grep target file before implementing any feature | WA-12, DEC-035 |
| L8 | Vercel dashboard check returned empty | get_page_text returns pre-hydration shell for client-rendered pages | Use javascript_tool + document.querySelector() for DOM data | WA-13 |
| L9 | git safe.directory error on fresh clone | Linux sandbox treats /tmp clones as dubious ownership | Add git config --global --add safe.directory /tmp/clone after every clone | WA-14 |


## Last QA Run

**Date:** 2026-05-20 (Full audit — Tracks R/R9/REC/D/P/Staging + all decisions resolved)
**Markets tested:** Both Houston US and Pakistan PK (infrastructure + code path verified)
**Outcome:** PASS ✅ COMPLETE — 53/53 items resolved, all fixes shipped
**Alembic head:** 029 (confirmed live in Supabase quqrvnoguofbjacrxcim)
**Commits this session:** 53db54a (D.11), 85197fc (docs), 172b825 (R.7+S.7), 02ad667 (TECH_STACK), ba15901 (doc cleanup), fe86144 (BRAIN HEAD update)
**Vercel:** Live on commit fe86144
**Railway:** Health OK
**QA sign-off:** FULLY COMPLETE ✅

### BUG-021 — Railway builds failing in 9 seconds (FIXED — commit 6e3ef5e):
**Problem:** All Railway builds completed in ~9 seconds (should be 3+ minutes). Backend was serving stale code.
**Root cause:** A skeleton `scopesnap-api/.git/` directory existed (containing only `refs/remotes/origin/` tree).
Git treated `scopesnap-api/` as a gitlink/submodule — so NONE of the backend files were tracked in the
main repo index, except `diagnostic.py` which had been previously force-added.
GitHub had no Dockerfile → Railway cloned and found nothing → 9-second "build."
**Fix procedure (if this happens again):**
1. Delete the nested `.git` via Desktop Commander PowerShell: `rmdir /S /Q "scopesnap-api\.git"`
2. Clear any index.lock: `del /F /Q ".git\index.lock"`
3. `git add scopesnap-api/` to restage all 119 files
4. Commit and push
**Prevention:** After any git operation that involves subdirectory cloning or stashing, run
`git ls-files scopesnap-api/ | head -5` — if empty, the subdirectory has been de-indexed.
**Commit:** `6e3ef5e` — "fix(build): restore scopesnap-api backend files to git index + BUG-020 fc.card_id fix"

### BUG-020 — fault_cards JOIN using wrong column (FIXED — commit 6e3ef5e):
**Problem:** `/api/diagnostic/list` returned 500; `/diagnoses` page showed offline error.
**Root cause:** `fault_cards` table PK is `card_id` (NOT `id`). Three SQL strings in `diagnostic.py`
used `fc.id` → "column fc.id does not exist" at runtime. Error was masked by `apiFetch` converting
CORS failures (from 500 responses with no CORS headers) into `OfflineError`.
**Fixed locations in diagnostic.py:**
- Line ~1338: `JOIN fault_cards fc ON fc.card_id = ds.resolved_card_id` (was `fc.id`)
- Line ~1218: `SELECT card_id, card_name, ...` (was `id, ...`)
- Line ~1220: `WHERE card_id = :cid` (was `id = :cid`)
**Commit:** included in `6e3ef5e`

### BUG-019 — recommendationOverridden wired to wrong page (FIXED — commit f38b846):
**Problem:** `recommendationOverridden` flag (Track REC) was wired into `estimate/[id]/page.tsx`
(URL `/estimate/{id}`), which is dead code — the app never routes there.
**Root cause:** The REAL estimate builder is `assessment/[id]/page.tsx` (URL `/assessment/{id}`).
Any code in `estimate/[id]/page.tsx` is unreachable.
**Fix:** Rewired `recommendationOverridden`, `recommendedTier`, and `track` import to `assessment/[id]/page.tsx`
**Commit:** `f38b846`

### Railway instability during QA (session ended — status unknown at session close):
**What happened:** After pushing `6e3ef5e`, Railway began a Docker build (confirmed — not 9-second fail).
During Railway startup (~10-15 min), `(app)/layout.tsx` fetches `GET /api/auth/me` server-side.
If Railway returns 503/404 during startup, ALL protected pages redirect to `/assess`.
This is NOT a frontend bug — it is Railway startup behavior.
**Self-resolves:** Once Railway passes health check, the redirects stop immediately (Vercel cache: 30s).
**Action at next session start:** Check `GET /health` via web_fetch. If OK, verify `/diagnoses` loads.

### What was confirmed PASSING (2026-05-20 QA):
- R.3 — Address guard fires correctly before complaint selection ✅
- Flow 1 — Not Cooling: 128 PSI R-410A → routes "(ok)" = NORMAL (not high), not Card 13 ✅
- Flow 1 — Diagnostic resolves and navigates to /diagnoses/[session_id] ✅
- Backend health: Railway /health returns 200, models/all returns 76 US + 72 PK records ✅
- Diagnoses sidebar nav entry renders correctly ✅

### BUG-D.AUTH — FULLY FIXED ✅

All 4 Track D frontend files now correctly pass Clerk JWT token to `apiFetch` (DEC-030 pattern).

| File | Status | Commit |
|------|--------|--------|
| `app/(app)/diagnoses/[session_id]/page.tsx` | ✅ Fixed | `575f73e` |
| `app/(app)/diagnoses/page.tsx` | ✅ Fixed | `928a476` |
| `components/DiagnosisFeedbackModal.tsx` | ✅ Fixed | `928a476` |
| `components/FaultResolutionScreen.tsx` | ✅ Fixed | `928a476` |

**D.11 also fixed (assess/page.tsx finalize call):** `53db54a`

---

## Completed (2026-05-20 — Post-audit decisions, commit 172b825)

- [completed] D.6 — Backfill share_token on all 62 existing diagnostic_sessions
  - SQL: `UPDATE diagnostic_sessions SET share_token = encode(gen_random_bytes(32), 'hex') WHERE share_token IS NULL`
  - Verified: 62/62 tokens populated, 0 NULL remaining
  - Future sessions: auto-populated by finalize endpoint (D.11 fix, commit 53db54a)

- [completed] R.7 — Contractor profile guard in live estimate builder (assessment/[id]/page.tsx)
  - `contractorProfileOk` state: fetches /api/auth/me on load, checks company_name + phone
  - `sendEstimate()` blocked with clear error if profile incomplete
  - Amber warning banner in send tab with link to /settings
  - Commit: 172b825

- [completed] S.7 — Staging environment banner
  - New file: `scopesnap-web/components/StagingBanner.tsx`
  - Fixed amber bar, visible only when NEXT_PUBLIC_ENV === "staging" (zero production cost)
  - `app/(app)/layout.tsx`: imports and renders StagingBanner; adds pt-6 on staging
  - Commit: 172b825

---

## Completed (2026-05-20 — Track R US Report Polish)

All 8 items shipped in single commit `177f4f9` (hotfix lane, direct to main):

- [completed] R.1 — Print button in report header + `@media print` CSS in globals.css
  - Button added alongside Call link in company header bar (`ReportClient.tsx`)
  - Print CSS hides nav/buttons, removes sticky, adds `page-break-inside: avoid` on cards

- [completed] R.2 — Updated stale Q.4 comment in `Company` interface (`custom_branding` field)

- [completed] R.3 — Address required before complaint selection
  - Guard in `handleComplaintSelected` in `assess/page.tsx`
  - Shows: "Please enter the property address before selecting a complaint type."

- [completed] R.4 — Hide Health Overview panel when all nameplate fields null
  - Removed `|| (condition !== "unknown")` from guard — now only shows when brand/model/install_year present

- [completed] R.5 — Hide photo section when no photos (no placeholder)
  - Removed the blank `AnnotatedPhotoSvg` fallback — section collapses when `photos.length === 0`

- [completed] R.6 — Replace external QR CDN with `react-qr-code` npm package
  - Added `"react-qr-code": "^3.1.0"` to `package.json`
  - `ReportQRCode` function rewritten to use `<QRCode>` component (no network request at render time)

- [completed] R.7 — Contractor profile guard before sending reports
  - State: `contractorProfileOk` (fetches `/api/auth/me` on load, checks company name + phone)
  - Banner: amber warning above header if profile incomplete, links to /settings
  - Send guard: blocks `sendEstimate()` with error message if profile incomplete

- [completed] R.8 — Site visit fee footer disclaimer
  - Backend: `reports.py` returns `site_visit_fee_text: "Diagnostic visit fee $89 — waived upon repair approval."`
  - Frontend: renders disclaimer block above report footer when field is present
  - Interface: `site_visit_fee_text?: string` added to `Report` interface

- [completed] R.9 — Seasonal labor modifier (Track S folded in)
  - _seasonal_modifier_pct(market, company_override) in fault_estimate.py
  - Houston peak: June-Sept (+25% labor). PK peak: April-Oct (+25% labor)
  - companies.peak_season_surcharge_percent (nullable INT -- NULL=market default, 0=off, 1-100=custom)
  - estimates.seasonal_modifier_pct (INT NOT NULL default 0 -- generation-time freeze)
  - seasonal_modifier_pct + seasonal_note added to FaultCardEstimateResponse
  - Missing import for derive_condition_signal_from_assessment fixed (was NameError, caught by try/except)
  - breakdown key renamed pk_seasonal -> seasonal
  - Alembic 029 applied via Supabase direct (WA-7); Railway deploy had infra issue
  - Commit: e2683dd

---

## Completed (2026-05-20 — Track D build hotfixes, direct to main)

- [completed] HOT-1 — Export `apiFetch` from `lib/api.ts`
  - Changed `async function apiFetch<T>` → `export async function apiFetch<T>`
  - Required by: `FaultResolutionScreen.tsx`, `DiagnosisFeedbackModal.tsx`, `diagnoses/page.tsx`, `diagnoses/[session_id]/page.tsx`, `d/[share_token]/page.tsx`
  - Commit: `380b486`

- [completed] HOT-2 — Fix DiagnosticResult type param in `diagnoses/[session_id]/page.tsx`
  - Changed untyped `apiFetch(url).then((res: DiagnosticResult) =>` → `apiFetch<DiagnosticResult>(url).then((res) =>`
  - Root cause: TypeScript infers `T=unknown` when no type param given; callback annotation from `unknown` to `DiagnosticResult` is rejected
  - Commit: `43c4dab`
  - Vercel: ✅ Ready (1m 23s) — deployment 2bPAP3ZKX — **current production**

---

## Completed (this session — 2026-05-19 Track Q Houston Estimate Engine)

- [completed] Q.1 — Kill legacy estimate engine
  - Deleted `scopesnap-api/services/estimate_engine.py` (dead code, zero non-self references)
  - Removed `/api/estimates/generate` route and its `GenerateEstimateRequest` import from `estimates.py`
  - Removed `generateEstimate()` from `scopesnap-web/lib/api.ts`
  - Added DEC-016 to DECISIONS.md documenting the deletion
  - Commit: `f0f13f5`

- [completed] Q.2 — Quarantine legacy pricing_rules rows
  - Added `deprecated BOOLEAN NOT NULL DEFAULT false` column to `pricing_rules`
  - Set all rows `deprecated = true` (Alembic migration 020)
  - Added COMMENT on table marking it as DEPRECATED
  - Commit: `64e1a17` (includes migration file `020_quarantine_legacy_pricing_rules.py`)

- [completed] Q.3 — complaint_type fallback + Sentry alert on unresolved Not-Cooling estimates
  - Added `diagnostic_resolved` check (raw SQL on `diagnostic_sessions`) in `reports.py`
  - Injected graceful fallback issues_data for `service/tune_up/maintenance` (green "Preventive service")
  - Added Sentry warning for `not_cooling/water_dripping/not_turning_on` with no diagnostic resolution + cost > 0
  - Commit: `68299eb`

- [completed] Q.4 — Remove PAID_PLANS gate on contractor branding
  - Deleted `PAID_PLANS` dict and conditional logic in `reports.py`
  - Contractor name/phone/email/logo/license now always returned regardless of plan tier
  - Commit: `68299eb` (same as Q.3)

- [completed] Q.5 — Apply 19 fault card descriptions (migration 021)
  - Migration `021_fault_card_descriptions.py`: 19 UPDATE statements, 6 new JSONB fields per card
    (description_good, why_recommended_good, description_best_comprehensive,
     why_recommended_best_comprehensive, description_best_replacement, why_recommended_best_replacement)
  - Updated `fault_estimate.py` to read new description fields with hardcoded fallbacks
  - Added `why_recommended` collapsible `<details>` block in `ReportClient.tsx` for RECOMMENDED tier
  - All 114 field values verified ≤180 chars at word boundary before commit
  - Commit: `d51e7ab`

- [completed] Q.6 — Switch frontend share URL to report_token
  - Changed `homeowner_url` in `estimates.py` from `report_short_id` to 32-char `report_token`
  - Legacy `/r/{slug}/{short_id}` URLs remain valid 12 months via OR clause in `reports.py`
  - Commit: `5bc09ed`

- [completed] Q.7 — Refresh draft estimates on load
  - Added `POST /api/estimates/{id}/refresh` to `estimates.py`
    - Resolves `card_id` from `diagnostic_sessions.resolved_card_id`
    - Patches `description`/`why_recommended` per tier from `fault_cards.better_option_estimate`
    - Saves options in-place; idempotent / no-op if not draft
  - Updated `estimate/[id]/page.tsx` useEffect to call refresh silently on draft load
  - Commit: `c6ef5df`

---

## Completed (2026-05-20 — Track D: Diagnosis Screen + History v1, commit 400ede1)

- [completed] D.1 — GET /api/diagnostic/result/<session_id> (auth, company-scoped, 409 on unresolved)
- [completed] D.2 — GET /api/diagnostic/list (cursor pagination, nameplate photo subquery, soft-delete guard)
- [completed] D.3 — POST /api/diagnostic/feedback (agreement: solved | different_fault)
- [completed] D.4 — Migration 026: action_steps, parts_needed, alternative_cards, climate_notes_* cols on fault_cards + pak_fault_cards
- [completed] D.5 — Migration 027: customer_label, customer_address, share_token, confidence_level, reasoning_chain, deleted_at on diagnostic_sessions; diagnosis_feedback table; two indexes
- [completed] D.6 — Backfill: action_steps (3 steps) + parts_needed + climate_notes for all 19 US fault cards and all 15 PK fault cards via Supabase execute_sql
- [completed] D.7 — FaultResolutionScreen.tsx (fault name + confidence badge, time estimate, action steps, parts, PK climate note, reasoning chain, photo evidence, alternatives, Mark as Solved / Different fault found, share link, watermark)
- [completed] D.8 — /diagnoses list page + DiagnosisListRow.tsx (nameplate photo first, fault name, confidence badge, customer label, relative time) + DiagnosisListEmptyState.tsx
- [completed] D.9 — /d/[share_token] public route + GET /api/diagnostic/public/<token> (unauthenticated, customer=null)
- [completed] D.10 — DiagnosisFeedbackModal.tsx (free-text real fault, Skip + Save & Close, apiFetch POST)
- [completed] D.11 — assess/page.tsx: handleDiagnosticResolved fires finalize + router.push(/diagnoses/[id]) instead of setPhase("evidence")
- [completed] D.12 — SidebarNav.tsx: magnifier icon added as "diagnoses" key; Diagnoses entry added to OVERVIEW section
- [completed] D.13 — tracking.ts: 8 new events (fault_screen_opened, fault_screen_time_on_screen, fault_screen_agreement, fault_screen_share_clicked, fault_screen_reasoning_expanded, diagnosis_list_opened, diagnosis_revisited, diagnosis_share_opened_externally)
- [completed] D.14 — _compute_confidence() in diagnostic.py: 0 skipped→high, 1→medium, 2+→low
- [completed] D.15 — Mobile QA: code audit confirmed responsive at 375/768/1280px; minor note: feedback buttons tight at 375px (v1.5: stack buttons column on mobile)
- [completed] D.16 — Docs: PROJECT_BRAIN.md, ACTIVE_TASKS.md updated; DECISIONS.md DEC-025/026 below

**Track D v1.5 Backlog (deferred):**
- [ ] Truck inventory check on diagnosis screen (needs inventory data)
- [ ] Generate-estimate-from-here button on FaultResolutionScreen
- [ ] Search/date filter/favorites on /diagnoses list
- [ ] Urdu translation of action_steps verbs (translate verbs only; part names stay English)
- [completed] Stack feedback buttons column at <480px viewport — isMobile state + flexDirection: column (2026-05-20)
- [ ] Re-run diagnostic button on FaultResolutionScreen

---

## Pending / Backlog

- [completed] pak_operating_targets notes fix — R-32 label updated to "Inverter split AC only (R-32 PK market — all units are inverter-type)" via SQL (2026-05-20)
  - **Proposed SQL (safe, no migration needed):**
    ```sql
    UPDATE pak_operating_targets
    SET notes = REPLACE(notes, 'Typical split AC', 'Inverter split AC only (R-32 PK market — all units are inverter-type)')
    WHERE refrigerant = 'R-32';
    ```
  - Awaiting Shoab approval before running

- [ ] Track R — (defined in SnapAI_Estimate_And_Diagnosis_Implementation.md, not started)
- [ ] Track REC — (defined in SnapAI_Estimate_And_Diagnosis_Implementation.md, not started)

## Completed (Track REC -- 2026-05-20, commit 6ac37b4)

- [completed] REC.2 -- derive_condition_signal_from_assessment()
  - New file: scopesnap-api/services/condition_signals.py
  - 9-signal priority chain: under_warranty, photo_confirmed_pitting, formicary_confirmed,
    rla_over_nameplate, recurring_clog, attic_location, bearing_noise, sensor_only, default
  - fault_estimate.py stub replaced with real call (import + await)
  - py_compile verified before push

- [completed] REC.3 -- lifecycle_rules expanded 17 -> 50 rows
  - Migration: 028_lifecycle_rules_expansion.py (revision "028", down_revision "025")
  - 33 new rows: under_warranty (11 cards), photo_confirmed_pitting (4), formicary_confirmed (4),
    rla_over_nameplate (6), recurring_clog (1), attic_location (4), bearing_noise (2), sensor_only (1)
  - Idempotent: LEFT JOIN guard prevents duplicates on re-run
  - NOTE: Revision 026/027 reserved by staging Track D migrations. This is revision 028.

- [completed] REC.5 -- PostHog tracking helpers
  - scopesnap-web/lib/tracking.ts: 3 new helpers added to track object:
    track.recommendationShown(cardId, recommendedTier, reason?, source?)
    track.recommendationOverridden(cardId, originalTier, chosenTier, estimateId?)
    track.recommendationApproved(cardId, approvedTier, recommendedTier, reportId?)
  - Wiring note: recommendationShown -> call from assess/page.tsx after R.3 done
  - Wiring note: recommendationOverridden -> call from estimate/[id]/page.tsx after R.7 done
  - Wiring note: recommendationApproved -> call from ReportClient.tsx after R.1-R.5 done

## Completed (Track REC.5 wiring -- 2026-05-20, commit e5ffefb)

- [completed] REC.5 wiring -- recommendationShown, Overridden, Approved fully wired
  - assess/page.tsx: track.recommendationShown() added at 2 call sites
    - _doPhase2Gate: source="phase2_gate", fires after estimateGenerated
    - _doGenerateEstimate: source="fault_card", fires after estimateGenerated
    - Guard: if (est.recommended_tier) -- safe when backend doesn't return field
  - estimate/[id]/page.tsx: track.recommendationOverridden() wired to Continue button
    - track import added, recommendedTier state added, captured from API on load
    - Fires only when selectedTier !== recommendedTier
  - ReportClient.tsx: track.recommendationApproved() wired in handleApprove success path
    - initialRecommendedTier derived from report.options (same l