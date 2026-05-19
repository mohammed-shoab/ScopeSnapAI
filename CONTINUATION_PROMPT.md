# SnapAI — Continuation Prompt

Last updated: 2026-05-19 (Track Q complete — all 8 hotfixes + Q.6.5 merged)

## Production Environment

- **App URL**: https://snapai.mainnov.tech (Houston) / https://pk.snapai.mainnov.tech (PK)
- **Frontend**: Next.js 14 deployed on Vercel (project: scope-snap-ai)
- **Backend API**: FastAPI + PostgreSQL (Railway — project: pacific-exploration)
- **Database**: Supabase PostgreSQL (NOT Railway postgres — DATABASE_URL → pooler.supabase.com)
- **Auth**: Clerk (production keys, live)
- **Analytics**: PostHog (project 369878, token phc_A5spSAWCWKeQw9cVgVfxnmNd2f2dQjvtdwsb9PpjMbZJ)
- **Monitoring**: UptimeRobot
- **Repo**: mohammed-shoab/SnapAIAI (monorepo: scopesnap-web/ + scopesnap-api/)

## Current Git State

- **HEAD**: `f8afced` — [fix] migration 021 — rewrite with valid Python syntax
- **Alembic revision**: `021` (fault_card_descriptions — all 19 cards × 5 fields populated)
- **Branch**: `main` (single deploy branch)

### Recent commit history (newest first)
```
f8afced [fix] migration 021 — rewrite with valid Python syntax (was crashing Railway start.sh)
46dc6bc [hotfix] Q.6.5 — merge recommendation engine into fault_estimate.py response
3d1958f [docs] Track Q brain file update — ACTIVE_TASKS, PROJECT_BRAIN, DECISIONS
c6ef5df [hotfix] Q.7 — Refresh draft estimates on load with latest fault card descriptions
5bc09ed [hotfix] Q.6 — homeowner_report_url uses 32-char report_token
d51e7ab [hotfix] Q.5 — apply 19 approved fault card descriptions per tier (alembic 021)
```

---

## Track Q — COMPLETE (all 8 items)

Track Q was an 8-item production hotfix lane. All items are resolved and merged to main.

| Item | Description | Commit | Status |
|------|-------------|--------|--------|
| Q.1 | Kill legacy estimate engine (`/api/estimates/generate` deleted — DEC-016) | prior | ✅ Done |
| Q.2 | Quarantine legacy pricing_rules rows (28 rows deprecated) | prior | ✅ Done |
| Q.3 | complaint_type fallback + Sentry alert silencing | prior | ✅ Done |
| Q.4 | Remove PAID_PLANS gate on contractor branding | prior | ✅ Done |
| Q.5 | Apply 19 fault card descriptions via migration 021 | d51e7ab | ✅ Done |
| Q.6 | Switch homeowner_report_url to 32-char report_token | 5bc09ed | ✅ Done |
| Q.6.5 | Merge recommend engine into fault_estimate.py (missed in original pass) | 46dc6bc | ✅ Done |
| Q.7 | Refresh draft estimates on load with latest fault card data | c6ef5df | ✅ Done |

### Critical production issue discovered and resolved (Q.5/migration 021)

Migration `021_fault_card_descriptions.py` had a Python SyntaxError (unescaped double-quotes + em-dash characters U+2014 in string literals). `start.sh` uses `set -e`, so alembic crashing on boot kept the pre-Q.5 container running. Fix: applied data directly via Supabase MCP, advanced `alembic_version` manually to `021`, rewrote migration file using `json.dumps()`. Commit `f8afced`.

---

## Next Work: Track R (Staging Branch) + Track REC

### Track R — Staging branch setup
Before any further production hotfixes, set up a staging branch and Railway preview environment. Purpose: validate migrations and endpoints before touching production. Scope TBD in implementation doc.

### Track REC — Recommendation engine (Phase 2 of Q.6.5)
Q.6.5 wired `get_recommended_tier_internal()` into `fault_estimate.py` but hardcoded `condition_signal = "default"` (per implementation doc, deferred to REC.2). Track REC completes the lifecycle rules recommendation:
- **REC.1**: Surface `recommendation_reason` and `recommendation_source` in estimate UI (they are already returned in the API response from Q.6.5)
- **REC.2**: Wire actual `condition_signal` from diagnostic session (pitting, bearing_noise, rla_over_nameplate) into the `fault_estimate` call so age-based override logic fires

---

## Architecture Notes

### Git workflow (DEC-004 — permanent)

All git operations use `/tmp/snapai_tmp` clone (NOT the NTFS workspace):
```bash
git clone git@github.com:mohammed-shoab/SnapAIAI.git /tmp/snapai_tmp
cd /tmp/snapai_tmp
# edit files, then:
git add <files> && git commit -m "..." && git push origin main
```
NEVER `git stash` from sandbox on NTFS repo (DEC-013). NEVER use git plumbing from NTFS for Unicode files (truncation risk — see TECH_STACK.md WA-7).

### Key backend files changed in Track Q

- `scopesnap-api/api/estimates.py` — added `POST /{id}/refresh` endpoint (Q.7)
- `scopesnap-api/api/recommend.py` — added `get_recommended_tier_internal()` (Q.6.5)
- `scopesnap-api/api/fault_estimate.py` — imports + calls `get_recommended_tier_internal()`, adds `recommendation_reason`/`recommendation_source` to tier response (Q.6.5)
- `scopesnap-api/db/migrations/versions/021_fault_card_descriptions.py` — rewritten with valid Python syntax using `json.dumps()` (f8afced)
- `scopesnap-web/app/(app)/estimate/[id]/page.tsx` — on-load refresh call when status=draft (Q.7)

### Estimate tier response shape (post-Q.6.5)

Each tier in the `POST /api/estimates/fault-card` response now includes:
```json
{
  "tier": "B",
  "recommended": true,
  "description": "...",
  "why_recommended": "...",
  "recommendation_reason": "Default capacitor recommendation",
  "recommendation_source": "card_default"
}
```
`recommendation_reason` and `recommendation_source` are `null` when `get_recommended_tier_internal()` returns no match. `recommended` flag is only overridden by lifecycle_rules when `condition_signal != "default"` (preserves existing `_shou