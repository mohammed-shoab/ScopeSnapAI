# Canonical SnapAI Brain — READ THIS FIRST (any AI session)

**There is exactly ONE copy of each brain file. It lives at the REPOSITORY ROOT.**
Every AI session (snapai-dev, snapai-qa, snapai-* skills, ad-hoc) MUST read AND write ONLY
the root files listed below. Do not read, edit, or create brain files anywhere else.

## The canonical brain files — the ONLY real copies (repo root)

| Purpose | Canonical file (repo root) |
|---------|----------------------------|
| Project state, live URLs, infra IDs, deploy state | `PROJECT_BRAIN.md` |
| Architecture decisions (DEC-###, authoritative log) | `DECISIONS.md` |
| Active + open tasks | `ACTIVE_TASKS.md` |
| Stack, hosting, accounts, versions | `TECH_STACK.md` |
| US (Houston) vs PK market differences | `MARKET_GUIDE.md` |
| Change / staging-first / deploy / rollback workflow | `WORKFLOW.md` |
| Build log | `BUILD_LOG.md` |
| One-line current status | `STATUS.md` |

- **On disk (Drive working copy):** `C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\<FILE>.md`
- **In git:** the ROOT of `github.com/mohammed-shoab/ScopeSnapAI`, branches `main` (prod truth) and `staging` (pre-prod truth).
- History indexes live in `ACTIVE_TASKS_HISTORY.md`, `PROJECT_BRAIN_HISTORY.md`, `TECH_STACK_HISTORY.md`, `session_logs/` — those are archives, NOT the live brain.

## There are NO other copies — if you find one, it is STALE
- No brain files may exist under any subfolder: `ScopeSnapAI/`, `ProjectBrain/`, `_archive/`, `snapai-board/`, `session_logs/`, etc.
- **How to spot a stale shadow:** a second copy with a LOWER top DEC number, an OLDER "Last updated" date, or a smaller/older body than the root copy. The root copy always has the highest DEC and newest date.
- If you ever find a duplicate: do NOT read or edit it. Remove it (git-tracked → recoverable from history) and tell Shoab. Never let a session read the stale copy by accident.

## Consolidation history
- **2026-06-26 (DEC-111):** removed the first duplicate round — a nested `ScopeSnapAI/ScopeSnapAI/` shadow + `ProjectBrain/*.md` parallel copies → archived to `_archive/brain_consolidation_2026-06-26/`.
- **2026-07-14:** a nested `ScopeSnapAI/` shadow set had reappeared and drifted ~1 month stale (its `DECISIONS.md` was at DEC-096 vs root DEC-133). Removed the 5 stale duplicates — `ScopeSnapAI/DECISIONS.md`, `ScopeSnapAI/ACTIVE_TASKS.md`, `ScopeSnapAI/PROJECT_BRAIN.md`, `ScopeSnapAI/TECH_STACK.md`, `ScopeSnapAI/WORKFLOW.md`. The repo now holds exactly ONE copy of each brain file, at the root. (Removed files remain in git history if ever needed.)

## MANDATORY first step for any AI session — the Drive copy can lag prod
The Drive-synced folder is a git working copy that can be BEHIND `origin`. NEVER claim code
or brain state from it without fetching first:
```bash
cd "C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI"
git fetch origin --no-tags
git log origin/main --oneline -5          # truth for prod
git log origin/staging --oneline -5       # truth for staging
git show origin/main:DECISIONS.md | grep -m1 'DEC-'   # confirm latest DEC live on prod
```
If the working copy is behind, `git pull` (or read `git show origin/<branch>:<file>`) BEFORE
editing any brain file. See `AI_TOOLING_GOTCHAS.md` Gotcha 4 + `DECISIONS.md` DEC-111.
