# SESSION LOG — Lessons Learned -- 2026-05-22 Session (BUG-037 Live Verify + BUG-038-build) — 2026-05-22

**Retrofit note:** Extracted from `ACTIVE_TASKS_HISTORY.md` on 2026-07-06 as part of the SESSION_LOG_* archetype adoption (Phase 3 retrofit Batch B). Content is verbatim from the ACTIVE_TASKS_HISTORY.md session block; the block also remains in ACTIVE_TASKS_HISTORY.md for chronological continuity.

**Source:** `ACTIVE_TASKS_HISTORY.md` (session block, extracted 2026-07-06)

---

## Lessons Learned -- 2026-05-22 Session (BUG-037 Live Verify + BUG-038-build)

| # | What We Learned | Detail | Action |
|---|-----------------|--------|--------|
| L28 | package-lock.json must NEVER be committed to this repo | Repo intentionally has no lockfile since c2eac8d (force Node 18, March 2026). 78d0fff accidentally re-added it (7954 lines), breaking every Vercel npm ci in ~8s. Fix: `git rm scopesnap-web/package-lock.json`. | Added DEC-065. |
| L29 | Vercel build failures hiding as 8-9 second Error | A broken package-lock.json causes npm ci to fail very fast. All 7 builds between 78d0fff and a908eac failed in 8-9s. Minified chunks were from pre-fix build -- no code change was live despite 6 pushes. | Always check deployment duration. Under 20s = npm ci failed. Check lockfile. |
| L30 | Module-level fmt() vs component-level const fmt | minified bundle: module-level function fmt compiled as function g(e) with no market arg. Component-level const fmt using reportMarket was absent from bundle because Vercel never rebuilt. Source code was correct all along (7736a7d). | No code action. Understanding for future debugging. |
| L31 | git show sha:path fails if file did not exist in that commit | git show 2d227ee:scopesnap-web/package-lock.json fails with 'exists on disk but not in commit'. Use git log --oneline -- path to find which commits touched the file, then restore from the right ancestor. | Use git log -- path first. |


---

## Change log

- **2026-07-06:** Extracted from ACTIVE_TASKS_HISTORY.md session block during Phase 3 retrofit (Option B).
