# SESSION LOG — Lessons Learned — 2026-05-23 QA + Brain File Update Session — 2026-05-23

**Retrofit note:** Extracted from `ACTIVE_TASKS_HISTORY.md` on 2026-07-06 as part of the SESSION_LOG_* archetype adoption (Phase 3 retrofit Batch B). Content is verbatim from the ACTIVE_TASKS_HISTORY.md session block; the block also remains in ACTIVE_TASKS_HISTORY.md for chronological continuity.

**Source:** `ACTIVE_TASKS_HISTORY.md` (session block, extracted 2026-07-06)

---

## Lessons Learned — 2026-05-23 QA + Brain File Update Session

| # | What Went Wrong | Root Cause | How We Fixed It | WA Ref |
|---|-----------------|-----------|-----------------|--------|
| L32 | git checkout main on NTFS overwrites all Edit-tool workspace changes | `git checkout main` restores NTFS files to HEAD state, silently overwriting any changes made via Edit tool in the workspace. All 4 brain file edits were lost when the bat file ran `git checkout main` after committing to staging branch. | Re-read files fresh, re-apply changes directly on main branch, then commit. Never use `git checkout <branch>` in a bat file after making Edit-tool changes to the workspace. | WA-36 |
| L33 | git commit landed on staging branch instead of main | The Desktop Commander bat file ran `git -C REPO commit` which used the current branch (staging). Thought we were on main. Push to `origin main` showed "Everything up-to-date" because the commit was on staging. | Always `git checkout main` BEFORE making changes. Then verify with `git branch` before commit. Or better: use `git -C REPO commit` + `git -C REPO push origin main` after confirming `git -C REPO rev-parse --abbrev-ref HEAD` == main. | WA-37 |
| L34 | Cherry-pick created add/add merge conflicts on DECISIONS.md and ACTIVE_TASKS.md | Tried cherry-picking commit `1dd6331` (made on staging) onto main. Both branches had diverged significantly (staging had many separate changes). Cherry-pick computed a 3-way merge with a far ancestor as base — causing both-sides-added conflicts on every file. | Aborted with `git cherry-pick --abort`. Re-applied changes fresh directly on main. See DEC-046 (same pattern, 2026-05-21). | WA-38 |
| L35 | Desktop Commander Python multiline REPL fails after line 1 | Interactive Python REPL in Desktop Commander hangs or gives unexpected output on line 2+. Writing multiline scripts to a file via `write_file` and running them with `python C:\Temp\script.py` is reliable. | Always write Python to C:\Temp\script_name.py and run as a file. Never attempt multiline REPL interaction via interact_with_process. | WA-35 |



---

## Change log

- **2026-07-06:** Extracted from ACTIVE_TASKS_HISTORY.md session block during Phase 3 retrofit (Option B).
