# SESSION LOG — Lessons Learned — 2026-05-20 QA Session — 2026-05-20

**Retrofit note:** Extracted from `ACTIVE_TASKS_HISTORY.md` on 2026-07-06 as part of the SESSION_LOG_* archetype adoption (Phase 3 retrofit Batch B). Content is verbatim from the ACTIVE_TASKS_HISTORY.md session block; the block also remains in ACTIVE_TASKS_HISTORY.md for chronological continuity.

**Source:** `ACTIVE_TASKS_HISTORY.md` (session block, extracted 2026-07-06)

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



---

## Change log

- **2026-07-06:** Extracted from ACTIVE_TASKS_HISTORY.md session block during Phase 3 retrofit (Option B).
