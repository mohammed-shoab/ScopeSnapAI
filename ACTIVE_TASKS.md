# SnapAI — Active Tasks

> Tracks in-flight work, recent completions, and backlog.
> Updated by QA/dev sessions. Read this before starting any new work.
>
> Last updated: 2026-05-19 (Track Q — Houston estimate engine hardening, Q.1–Q.7 complete)

---

## Last QA Run

**Date:** 2026-05-19 (Track Q — US Houston estimate engine hardening)
**Markets tested:** US only (no PK changes)
**Outcome:** PASS — Q.1 through Q.7 complete, all committed to main, Railway/Vercel deploying
**Alembic head:** 021 (migrations 020 + 021 added this session)
**Commits:** 7 hotfix commits on main (f0f13f5 → c6ef5df)
**QA sign-off:** COMPLETE (2026-05-19 Track Q)

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

## Pending / Backlog

- [ ] pak_operating_targets notes fix (R-32 label: "Typical split AC" → "Inverter split AC only")
  - **Proposed SQL (safe, no migration needed):**
    ```sql
    UPDATE pak_operating_targets
    SET notes = REPLACE(notes, 'Typical split AC', 'Inverter split AC only (R-32 PK market — all units are inverter-type)')
    WHERE refrigerant = 'R-32';
    ```
  - Awaiting Shoab approval before running

- [ ] Track R — (defined in SnapAI_Estimate_And_Diagnosis_Implementation.md, not started)
- [ ] Track REC — (defined in SnapAI_Estimate_And_Diagnosis_Implementation.md, not started)

