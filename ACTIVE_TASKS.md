# SnapAI — Active Tasks

> Tracks in-flight work, recent completions, and backlog.
> Updated by QA/dev sessions. Read this before starting any new work.
>
> Last updated: 2026-05-18 (electrical spec auto-fill — commit 6a8eecb)

---

## Last QA Run

**Date:** 2026-05-18
**Markets tested:** Houston (snapai.mainnov.tech)
**Outcome:** PASS — all Houston flows verified including re-run of Flow 1 post BUG-012 fix; all Phase 2 backend checks passed
**Bugs fixed:** 7 (BUG-011 badge + 5 CRLF stash truncations + BUG-012 electrical spec auto-fill)
**Final commit:** `6a8eecb` — Production Current Ready on Vercel
**QA sign-off:** COMPLETE (2026-05-18)

---

## Completed (this session)

- [completed] BUG-012: Electrical spec fields (RLA/LRA/MCA/MOCP/Cap) were blank after selecting brand/model from DB
  - Root cause: `applyModelRecord` only filled brand/series/tonnage/refrigerant; no electrical spec lookup existed
  - Fix: Added `ELECTRICAL_SPECS_BY_TONNAGE` static lookup table (midpoints from ac_data_repo.json) to `StepZeroPanel.tsx`; `applyModelRecord` now populates rla/lra/mca/mocp/capacitor_uf from table when fields are null
  - Badge change: rla/lra/mca/mocp badge changed from "db" to "est" (values are reference estimates, not per-unit DB records)
  - File: `scopesnap-web/components/StepZeroPanel.tsx`
  - Commit: `6a8eecb`
  - Verified live: York LX → 3.5T → RLA=16.2, LRA=86, Cap=50/5 MFD, MCA=22.5, MOCP=35 ✓

- [completed] BUG-011: DB badge never changed to "✏ Edited" when tech edited a DB-filled nameplate field
  - Fix: added `editedManualFields: Set<string>` state to `StepZeroPanel.tsx`; badge flips orange on edit, green resets on new model apply
  - File: `scopesnap-web/components/StepZeroPanel.tsx`
  - Commit: `817f712`

- [completed] Fix CRLF stash corruption in 10 frontend files
  - Root cause: `git stash` from Linux sandbox onto NTFS mount truncates TSX/TS files (see DEC-013)
  - Files restored from `e1db2ac`: `market.ts`, `assess/page.tsx`, `app/(app)/layout.tsx`, `ReportClient.tsx`, `LanguageToggle.tsx`, `SidebarNav.tsx`, `DiagnosticFlow.tsx`, `urdu-strings.ts`, root `app/layout.tsx`, `StepZeroPanel.tsx` (patched)
  - Commits: `55e4c3a`, `eb7fb93`, `51796d5`, `817f712`

---

## In Progress

- None currently.

---

## Backlog

- [ ] PK market full QA run (Flows 1–6 + Flow 5 PK-specific) — not tested this session (Houston-only scope)
- [ ] Add DEC-013 guard to QA checklist: after any merge, run `git diff <sha> --stat` on all TS/TSX files before pushing
- [ ] Consider uploading actual per-unit electrical specs to `equipment_models` table so DB badge (not Est.) can show when real data exists
- [ ] Update QA skill doc: `/api/series?brand=york` endpoint does not exist — actual Supabase connectivity is proven via `/api/models/all`

---

## Known Issues

- None currently in production (all verified in QA 2026-05-18).
