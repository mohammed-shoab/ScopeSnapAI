# SESSION LOG — OPEN — 2026-06-08 — PRODUCTION DATABASE MIGRATION (us-east-1) — NOT STARTED — 2026-06-08

**Retrofit note:** Extracted from `ACTIVE_TASKS_HISTORY.md` on 2026-07-06 as part of the SESSION_LOG_* archetype adoption (Phase 3 retrofit Batch B). Content is verbatim from the ACTIVE_TASKS_HISTORY.md session block; the block also remains in ACTIVE_TASKS_HISTORY.md for chronological continuity.

**Source:** `ACTIVE_TASKS_HISTORY.md` (session block, extracted 2026-07-06)

---

## OPEN — 2026-06-08 — PRODUCTION DATABASE MIGRATION (us-east-1) — NOT STARTED

Staging DB was migrated Tokyo→Virginia (us-east-1) successfully (DEC-091; details in PROJECT_BRAIN/TECH_STACK/DECISIONS). **PROD still runs on Supabase Tokyo (`scopesnap` / quqrvnoguofbjacrxcim) and must be migrated the same way** to get the ~70x DB-latency win on production. Proven recipe: take a fresh prod pg_dump → create a us-east-1 Supabase project → restore → swap Railway PROD DATABASE_URL during a low-traffic window → verify → watch Sentry 30 min. Also: add the `ix_app_events_report_viewed_short_id` index as a real Alembic migration so prod gets it. Backups for both envs are in ScopeSnapAI/backups/ (2026-06-08).


---

## Change log

- **2026-07-06:** Extracted from ACTIVE_TASKS_HISTORY.md session block during Phase 3 retrofit (Option B).
