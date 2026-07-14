# SnapAI — start here (canonical entry)

**Read `PROJECT_BRAIN.md` first**, then `DECISIONS.md`, `TECH_STACK.md`, `MARKET_GUIDE.md`, `ACTIVE_TASKS.md`, `WORKFLOW.md` — all at the **repo root**. These are the ONE canonical brain.

- There are **no other copies**. Any brain file under a subfolder (`ScopeSnapAI/`, `ProjectBrain/`, `_archive/`, session folders) is a **stale shadow — ignore it**. Full directory + how to spot a shadow: `BRAIN_CANONICAL_PATH.md`.
- **ALWAYS `git fetch origin --no-tags` before trusting any brain/code state** — the Drive-synced working copy can lag prod. Truth = `origin/main` (prod) and `origin/staging` (pre-prod).
- Staging-first workflow: never edit `main` directly (DEC-070). All changes go staging → QA → promote to main.

Repo: `github.com/mohammed-shoab/ScopeSnapAI`. Prod: snapai.mainnov.tech (US) + pk.snapai.mainnov.tech (PK, dormant).
