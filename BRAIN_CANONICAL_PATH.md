# Canonical SnapAI Brain Location

The `ScopeSnapAI/` folder at this path is the SINGLE source of truth for SnapAI brain files:

- PROJECT_BRAIN.md
- DECISIONS.md
- ACTIVE_TASKS.md
- MARKET_GUIDE.md
- TECH_STACK.md
- BUILD_LOG.md
- STATUS.md
- WORKFLOW.md

**DO NOT create copies of these files anywhere else.**

Per DEC-111, AI sessions reading the Drive-synced copy must `git fetch origin --no-tags` first to confirm vs prod.

## Brain consolidation history

Date: 2026-06-26
Action: Removed duplicate brain locations + moved to `_archive/brain_consolidation_2026-06-26/`

Previously-duplicate locations now archived:

1. **`ScopeSnapAI/ScopeSnapAI/`** — nested shadow folder containing 6 stale brain files (May 26-Jun 14, ~1 month behind canonical). Folder removed entirely after moving files to `_archive/brain_consolidation_2026-06-26/ScopeSnapAI_nested_shadow/`

2. **`ProjectBrain/PROJECT_BRAIN.md` + DECISIONS.md + ACTIVE_TASKS.md + SESSION_LOG.md** — parallel external copy with smaller line counts (May-Jun dates) than canonical. Moved to `_archive/brain_consolidation_2026-06-26/ProjectBrain_md_duplicates/`. The Python brain app (`project_brain_app.py` + configs + run_me.bat) was KEPT in `ProjectBrain/` in case still useful as a brain browser tool — but it no longer maintains duplicate brain files.

## How to verify canonical state in any future AI session

```bash
cd "C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI"
git fetch origin --no-tags
git log origin/main --oneline -5      # truth for prod
git log origin/staging --oneline -5   # truth for staging
git show origin/main:scopesnap-api/api/fault_estimate.py  # truth for any file
```

NEVER claim code state from this Drive-synced working copy without `git fetch` first. See AI_TOOLING_GOTCHAS.md Gotcha 4 + DEC-111 in DECISIONS.md.
