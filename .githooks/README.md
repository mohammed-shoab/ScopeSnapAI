# SnapAI Git Hooks

Pre-commit hook that enforces the mechanical brain-file rules from
`SnapAI_Brain_Files_Management_Plan_2026-07-05.md` (Phase 2b).

## Rules enforced

1. **No `Previously:` blocks in top 30 lines** of mutable-state files
   (STATUS.md rejects any; PROJECT_BRAIN.md / TECH_STACK.md allow max 1 for the "Last updated" stamp).
2. **Line-count caps** — warns (not rejects) if a file exceeds its cap:
   - STATUS.md ≤ 60 · PROJECT_BRAIN.md ≤ 500 · TECH_STACK.md ≤ 500
   - ACTIVE_TASKS.md ≤ 300 · WORKFLOW.md ≤ 300 · MARKET_GUIDE.md ≤ 300
   - DECISIONS.md + *_HISTORY.md — no cap
3. **No `diagnos*` strings in homeowner-facing files** (Alfred's Principle 3):
   - `scopesnap-web/app/homeowner/`
   - `scopesnap-web/app/d/`
   - `scopesnap-web/app/r/`
   - `scopesnap-api/templates/`

## Install

From repo root (`ScopeSnapAI/`):

```bash
git config core.hooksPath .githooks
```

Or copy to `.git/hooks/pre-commit` and `chmod +x .git/hooks/pre-commit`.

Verify with a test commit that touches STATUS.md:

```bash
echo "> Previously: test" >> STATUS.md
git add STATUS.md
git commit -m "test" # should reject
git checkout STATUS.md
```

## Bypass (emergency only)

```bash
git commit --no-verify -m "..."
```

Use only for genuine emergencies — the rules are load-bearing.

## Rule references

- Rule 1: `SnapAI_Brain_Files_Management_Plan_2026-07-05.md` Part 6, Rule 1 (session-end hygiene)
- Rule 2: same, Part 6, Rule 2 (line-count caps)
- Rule 3: `SnapAI_Legal_UI_Audit_v2_DEEP_2026-07-05.md` C5-C11 (Alfred's Principle 3 — language consistency)
