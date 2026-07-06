# SESSION LOG — Previous Last QA Run — 2026-05-XX

**Retrofit note:** Extracted from `ACTIVE_TASKS_HISTORY.md` on 2026-07-06 as part of the SESSION_LOG_* archetype adoption (Phase 3 retrofit Batch B). Content is verbatim from the ACTIVE_TASKS_HISTORY.md session block; the block also remains in ACTIVE_TASKS_HISTORY.md for chronological continuity.

**Source:** `ACTIVE_TASKS_HISTORY.md` (session block, extracted 2026-07-06)

---

## Previous Last QA Run

**Date:** 2026-05-23 — Full QA + brain file updates
**Markets tested:** Both Houston US and Pakistan PK
**Outcome:** PASS ✅ — all 6 flows pass on both markets. Zero new bugs found.
**Alembic head:** 034 (unchanged)
**Git HEAD:** 19db2d1 (unchanged — no new code commits)
**Commits this session:** None — verification + documentation only
**Vercel:** Both Houston + PK serving 19db2d1 ✅
**Railway:** ACTIVE — health OK ✅
**QA sign-off:** FULLY COMPLETE ✅
**Key verifications:** All 6 flows PASS. Brain files updated with L32-L35, DEC-065/066, WA-28 through WA-37.

### Previous Last QA Run

**Date:** 2026-05-22 -- BUG-037 live verify + BUG-038-build fix
**Markets tested:** Houston (confirmed PKR on PK report rpt-701093)
**Outcome:** PASS OK -- BUG-037 confirmed live. BUG-038-build resolved.
**Alembic head:** 034 (unchanged)
**Git HEAD:** 19db2d1 -- chore: remove [MKT:] debug marker from REF line
**Commits this session:** 78d0fff (feat BUG-037+mig-033/034), 8ed9a8b (debug), 7736a7d (fix fmt), 56fb12f (debug REF), a908eac (fix build: rm lockfile), 19db2d1 (chore: rm debug)
**Key fix:** package-lock.json removed (a908eac) -- 78d0fff had added 7954-line lockfile breaking every Vercel build in ~8s. Repo has no lockfile by design (since c2eac8d). DEC-065.
**Live verification:** snapai.mainnov.tech/r/rpt-701093/rpt-701093 shows Rs.5,906 / Rs.10,969 / Rs.14,808 (PKR) -- not USD OK
**Vercel:** Both domains serving 19db2d1 OK (build time 1m 27s)
**Railway:** ACTIVE -- health OK
**QA sign-off:** FULLY COMPLETE OK
**Markets tested:** Both Houston US and Pakistan PK
**Outcome:** PASS ✅ — all 6 flows pass on both markets. Zero new bugs. Zero commits.
**Alembic head:** 032 (unchanged)
**Git HEAD:** 4db39be (unchanged — no new fixes needed)
**Commits this session:** None — verification only
**Vercel:** Both Houston + PK serving 4db39be ✅
**Railway:** ACTIVE — health OK, /health → {"status":"ok","db":"connected","environment":"production","version":"0.1.0"} ✅
**QA sign-off:** FULLY COMPLETE ✅
**Key verifications:** A.3 fault card as primary issue (reports.py c009dbb) ✅ | A.5 QR sync render (55d76f8) ✅ | PKR currency in estimate builder (₨2,025 Capacitor Failure) ✅ | PK PSI thresholds (pak_operating_targets: R-410A 125-145 at 40°C) ✅

### Previous Last QA Run

**Date:** 2026-05-22 (Full audit — both markets, all 6 flows, 3 bugs found and fixed)
**Markets tested:** Both Houston US and Pakistan PK
**Outcome:** PASS ✅ — all 6 flows pass on both markets
**Alembic head:** 032 (unchanged)
**Git HEAD:** 4db39be — "fix(BUG-036): remove dead POST /api/estimates/service call"
**Commits this session:** 0140c83 (BUG-034), 937b8c7 (BUG-035), 4db39be (BUG-036)
**Vercel:** Both Houston + PK serving 4db39be ✅
**Railway:** ACTIVE — health OK, /health → 200 ✅
**QA sign-off:** FULLY COMPLETE ✅

**Known issue (not a regression from this work):**
- BUG-031 RE-REGRESSION: Confirmed resolved 2026-05-22. NEXT_PUBLIC_ENV already set to "production" (All Environments) in Vercel. pk.snapai.mainnov.tech verified clean — no staging banner.

### Previous QA Run

**Date:** 2026-05-21 (Full audit Tracks G+TCO+F+DX — both markets + BUG-033 fix + Gree Fairy Inverter seed)
**Markets tested:** Both Houston US and Pakistan PK
**Outcome:** PASS ✅ — all 6 flows pass on both markets
**Alembic head:** 032
**Git HEAD:** 23e3019 — "fix(BUG-033): add photo skip UI to ServiceChecklist"
**Vercel:** Both Houston + PK serving 23e3019 ✅
**Railway:** ACTIVE — health OK ✅
**QA sign-off:** FULLY COMPLETE ✅

### Data Changes This Session
- **Gree Fairy Inverter** added to `pak_brands` (series index 9, type=inverter, refrigerant=R-32, 1.0T/1.5T/2.0T). Gree now has 9 series total.

### Bugs Fixed This QA Run

**BUG-033 (FIXED — commit 23e3019) — Service/Tune-Up photo skip buttons**
- **Root cause:** Service/Tune-Up flow is rendered by `ServiceChecklist.tsx`, not `DiagnosticFlow.tsx`. `PHOTO_SKIP_CONFIG` in DiagnosticFlow was never reached.
- **Fix:** Added `SVC_PHOTO_SKIP_CONFIG` + `skipExpanded` state + skip JSX directly to `ServiceChecklist.tsx`
- **Verified:** Skip buttons confirmed rendering in DOM for svc-1-filter, svc-3-coil, svc-8-run

### Bugs Resolved This QA Run

**BUG-031 (RESOLVED) — Staging banner on pk.snapai.mainnov.tech**
- No staging banner observed on pk.snapai.mainnov.tech as of this session
- Root cause was `NEXT_PUBLIC_ENV=staging` in Vercel production env — fixed via Vercel dashboard

### Previous QA Run

**Date:** 2026-05-21 (Track F C.1-C.4 + BUG-032 fix + full 6-flow UI check both markets)
**Markets tested:** Both Houston US and Pakistan PK
**Outcome:** PASS COMPLETE
**Alembic head:** 032
**Commits this session:** 66a772c (feat track-f-c.1/c.3/c.4), 4743a40 (fix BUG-032 approve endpoint)
**Vercel:** Both Houston + PK serving 4743a40
**Railway:** ACTIVE -- health OK on 4743a40
**QA sign-off:** FULLY COMPLETE

### Bugs Found and Fixed (Previous Run)

**BUG-032 -- Approve endpoint rejected stored tier values A/B/C (FIXED -- commit 4743a40)**
- **Problem:** Homeowner clicked Approve on report, got "selected_option must be good/better/best" -- approval silently failed
- **Root cause:** `fault_estimate.py` stores tiers as "A"/"B"/"C" in DB but `reports.py` validated against ("good","better","best") only
- **Fix:** `reports.py` line 365 expanded to accept both sets: `("good","better","best","A","B","C")`
- **Verified:** "Thank you! You selected..." confirmation screen shown live after fix

### Previous QA Run

**Date:** 2026-05-20 (Post-track-F+DX — BUG-025/026 + full 6-flow UI check both markets)
**Markets tested:** Both Houston US and Pakistan PK
**Outcome:** PASS ✅ COMPLETE
**Alembic head:** 030 (pak_diagnosis_feedback alternative_fault_id column)
**Commits this session:** 1674b4e (track-F A.1+A.3), 1ca5ed6 (track-DX group-b), d5efc36 (fix migration-030), 85c5755 (BUG-025+BUG-026)
**Vercel:** Both Houston + PK on build main-app-63c8a702126b03a3.js ✅
**Railway:** ACTIVE — "Deployment successful" on 85c5755 ✅
**QA sign-off:** FULLY COMPLETE ✅

### Bugs Found and Fixed

**BUG-025 — seasonal_modifier_pct ORM column missing (FIXED — commit 85c5755)**
- **Problem:** `seasonal_modifier_pct` passed to Estimate ORM constructor in `fault_estimate.py`
  but column was missing from the Estimate ORM class in `db/models.py`.
  SQLAlchemy 2.0 silently sets unknown kwargs as Python attributes — value is never persisted to DB.
- **Symptom:** Seasonal banner never showed even in peak months; DB column always null/default.
- **Fix:** Added `seasonal_modifier_pct: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")`
  to the Estimate class in `scopesnap-api/db/models.py` (before "Accuracy tracking" section).
- **Verified:** New estimate rpt-0494 shows `seasonal_modifier_pct=0` in DB ✅ (0 is correct for May)

**BUG-026 — handleContinue navigated to assessment_id instead of estimate_id (FIXED — commit 85c5755)**
- **Problem:** `handleContinue` in `FaultResolutionScreen.tsx` was synchronous and did
  `router.push(\`/assessment/\${data.assessment_id}\`)` — navigating to the assessment UUID, not an
  estimate UUID. `/assessment/{assessment_id}` returns 404 because it expects an estimate ID.
- **Root cause:** assessment_id != estimate_id. Estimate must be created first via
  `POST /api/estimates/fault-card`, then navigate to the returned `est.id`.
- **Fix:** Made `handleContinue` async, calls `POST /api/estimates/fault-card` first,
  then navigates to `/assessment/{est.id}`.
- **Verified:** POST /api/estimates/fault-card called ✅, navigated to /assessment/97b22e44-…
  (estimate ID, not assessment ID), rpt-0494 loaded fully with A/B/C options ✅

### Railway Incident (not a code bug)
- **Platform-wide slow builds** during this session (Railway status page confirmed).
- Build 85c5755 took ~28 minutes vs. normal ~5 minutes. Pro plan builds processed normally.
- No action required.

### Staging Banner Observation (out of scope — needs Vercel dashboard action)
- `NEXT_PUBLIC_ENV=staging` set in Vercel production config → staging banner visible on PK.
- Fix: Vercel dashboard → project → Environment Variables → set `NEXT_PUBLIC_ENV=production`
  for Production environment. NOT a code change.

### Inverter Badge Data Gap (observation)
- QA spec: "Inverter badge: select Gree Fairy Inverter — badge must appear"
- DB query on pak_brands confirms ALL 8 Gree series have `type: "non_inverter"`.
- No "Fairy Inverter" variant exists in pak_brands DB.
- Inverter badge logic exists in `StepZeroPanel.tsx` (line 691) and works correctly when
  `m.series_type === "inverter"` — but Gree has no inverter models in the seed data.
- Inverter models DO exist in the DB for: Haier, Orient, PEL, Kenwood, Samsung, LG, Mitsubishi.
- **Action item:** Test inverter badge against one of those brands (e.g., Haier "Triple Inverter").

---


---

## Change log

- **2026-07-06:** Extracted from ACTIVE_TASKS_HISTORY.md session block during Phase 3 retrofit (Option B).
