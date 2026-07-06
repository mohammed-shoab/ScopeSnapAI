# SESSION LOG — Change Workflow Reference (added 2026-05-23 — DEC-070) — 2026-05-23

**Retrofit note:** Extracted from `ACTIVE_TASKS_HISTORY.md` on 2026-07-06 as part of the SESSION_LOG_* archetype adoption (Phase 3 retrofit Batch B). Content is verbatim from the ACTIVE_TASKS_HISTORY.md session block; the block also remains in ACTIVE_TASKS_HISTORY.md for chronological continuity.

**Source:** `ACTIVE_TASKS_HISTORY.md` (session block, extracted 2026-07-06)

---

## Change Workflow Reference (added 2026-05-23 — DEC-070)

All change work follows the staging-first workflow defined in `WORKFLOW.md`. The four absolute rules:

1. Never edit code directly on `main` without going through `staging` first
2. Never push migrations to prod that haven't run on staging first
3. Never add env vars to prod without mirroring them on staging
4. Never test on production — testing happens on staging

DEC-070 is now ACTIVE (Stage 7 signed off 2026-05-24). Hotfix path defined in `WORKFLOW.md` Section 9.

---

---


---

## Change log

- **2026-07-06:** Extracted from ACTIVE_TASKS_HISTORY.md session block during Phase 3 retrofit (Option B).
