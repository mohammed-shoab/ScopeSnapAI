# SnapAI — Continuation Prompt

Last updated: 2026-05-20 (All tracks complete — Q/R/R.9/REC/D/P/Staging. Full QA audit PASS. BUG-D.AUTH all 4 files fixed. D.6 share_token backfilled 62/62. R.7 profile guard live. S.7 staging banner live. Git HEAD: 02ad667. Alembic: 029.)

## Production Environment

- **App URL**: https://snapai.mainnov.tech (Houston) / https://pk.snapai.mainnov.tech (PK)
- **Frontend**: Next.js 14 deployed on Vercel (project: scope-snap-ai)
- **Backend API**: FastAPI + PostgreSQL (Railway — project: pacific-exploration)
- **Database**: Supabase PostgreSQL (NOT Railway postgres — DATABASE_URL → pooler.supabase.com)
  - Project ID: `quqrvnoguofbjacrxcim`
- **Auth**: Clerk (production keys, live)
- **Analytics**: PostHog (project 369878, token phc_A5spSAWCWKeQw9cVgVfxnmNd2f2dQjvtdwsb9PpjMbZJ)
- **Monitoring**: UptimeRobot
- **Repo**: mohammed-shoab/ScopeSnapAI (monorepo: scopesnap-web/ + scopesnap-api/)

## Staging Environment (fully operational — 2026-05-19)

- **US Staging URL**: https://staging.snapai.mainnov.tech
- **PK Staging URL**: https://pk-staging.snapai.mainnov.tech
- **Staging Backend**: https://scopesnap-api-staging.up.railway.app
- **Staging DB**: Supabase `pqmgveqkuckbvyygsilk` (ap-northeast-1) — full schema + seed data, Alembic `025`
- **Staging Auth**: Clerk staging app `firm-chamois-61` (test-mode keys)
- **Staging branch**: `staging` (off `main`; staging-specific HEAD: `980698b`)
- **Staging UI**: Amber "⚠ STAGING — not production data" banner on all pages (StagingBanner.tsx)
- **Staging secrets**: `C:\Users\dell\My Drive\Personal Claude\.staging_secrets.txt` (**never commit**)
- **Promote staging → prod**: `scripts/promote-to-prod.sh <file1> [file2 ...]` (on a local main checkout)
- **Keepalive**: `keepalive-supabase-A.yml` (Sun 02:00 UTC) + `keepalive-supabase-B.yml` (Wed 14:00 UTC), both on main, ping prod + staging
- **Healthchecks.io**: Account ds.shoab@gmail.com | Check A `https://hc-ping.com/1afa0f64-27f2-4906-97b1-b85f7abb738e` | Check B `https://hc-ping.com/2d8d3312-1a82-4223-84ba-9e021ee7f14e`

## Current Git State

- **Production HEAD**: `02ad667` — docs(TECH_STACK+BRAIN): full post-audit update (2026-05-20)
- **Staging HEAD**: `980698b` — chore(staging): migrations 020-025 + dual keepalive A/B + promote-to-prod.sh
- **Alembic revision (production)**: `029` (peak_season_surcharge_percent + seasonal_modifier_pct)
- **Alembic revision (staging)**: `025` (pak_fault_card_urdu_descriptions)
- **Active branches**: `main` (production), `staging` (staging environment)
- **Local working tree**: Clean. Use `/tmp/snapai_tmp2` (or fresh clone) for all git ops — do NOT git commit from NTFS workspace.

### Recent commit history — main (newest first)
```
02ad667 docs(TECH_STACK+BRAIN): full post-audit update
35f450c docs: all QA decisions resolved -- D.6 backfill done, R.7+S.7 shipped (172b825)
172b825 fix(R.7+S.7): contractor profile guard on sendEstimate + StagingBanner
85197fc docs: full QA audit 2026-05-20 results
53db54a fix(D.11): pass Clerk JWT token to diagnostic finalize call (DEC-030)
928a476 fix(BUG-024): diagnoses pages guard on isLoaded before getToken() + restore all web routes
fe5b02a fix(BUG-023): diagnostic list+result use pak_fault_cards directly -- bypass stale prepared statement
f82d760 fix(diagnostic): global exception handler for CORS-aware 500s + has_more/share_token in list response
575f73e fix: diagnoses detail page passes Clerk token to apiFetch
872e959 feat: add GET /api/diagnostic/result/{session_id} endpoint
6e3ef5e fix(build): restore scopesnap-api backend files to git index + BUG-020 fc.card_id fix
```

---

## Completed Tracks (all done as of 2026-05-20)

| Track | Description | Status |
|-------|-------------|--------|
| Track Q | 8 production hotfixes (Q.1–Q.7 + Q.6.5) | ✅ Complete |
| Track R | Staging environment setup (R.1–R.8) | ✅ Complete |
| Track R.9 | Seasonal modifier — global, DB-driven, both markets | ✅ Complete |
| Track REC | Recommendation engine (REC.1–REC.3, condition_signals) | ✅ Complete |
| Track D | Diagnoses screen — list, detail, feedback, share, finalize | ✅ Complete |
| Track P | PK pricing tiers — 15 cards × 3 tiers, bilingual, WhatsApp deeplinks | ✅ Complete |
| Track Staging | Staging infrastructure, keepalive, promote script | ✅ Complete |

### Track Q — Summary
8-item production hotfix lane. All items resolved and merged to main. Key: migration 021 (fault_card_descriptions), report_token (Q.6), recommendation engine merger into fault_estimate.py (Q.6.5), draft estimate refresh (Q.7).

### Track R — Summary
Full staging environment (separate Supabase, Clerk, Railway service, Vercel project). StagingBanner.tsx amber bar. Keepalive workflows. promote-to-prod.sh. R.7: contractor profile guard in assessment/[id]/page.tsx — prevents sendEstimate if company_name + phone missing.

### Track R.9 — Summary
Seasonal modifier moved from inline PK-only hardcode (P.7) to DB-driven global implementation. New columns: `peak_season_surcharge_percent` (companies table) + `seasonal_modifier_pct` (estimate_line_items). Alembic 029. Works for both markets.

### Track REC — Summary
Condition signal vocabulary (condition_signals.py). lifecycle_rules expanded to 44 rows via migration 028. `derive_condition_signal_from_assessment()` called in fault_estimate.py before lifecycle_rules lookup. Recommendation reason/source surfaced in tier response. REC.3: fix DEC-034 (missing import silently swallowed in try/except).

### Track D — Summary
Diagnoses screen fully implemented. Endpoints: GET /list, GET /result/{session_id}, POST /feedback, POST /finalize/{session_id}, GET /public/{share_token}. Frontend: /diagnoses, /diagnoses/[session_id], /d/[share_token] (public share page). FaultResolutionScreen.tsx. DiagnosisFeedbackModal.tsx. BUG-D.AUTH: all 4 files fixed (Clerk token passed explicitly — DEC-030). D.6: 62/62 share_tokens backfilled via SQL.

### Track P — Summary
PK pricing tiers: 15 fault cards × 3 tiers (Good/Better/Best) in PKR. pak_pricing_tiers table + pak_fault_card_descriptions + pak_fault_card_urdu_descriptions. WhatsApp deeplink in share page. Bilingual fault card content (English + Urdu descriptions).

---

## Architecture Notes

### Git workflow (DEC-004 — permanent)

All git operations use `/tmp` clones (NOT the NTFS workspace). Use separate clones per branch:
```bash
# For main branch work:
git clone --branch main https://x-token:$GH_PAT@github.com/mohammed-shoab/ScopeSnapAI.git /tmp/snapai_tmp
git config --global --add safe.directory /tmp/snapai_tmp

# For staging branch work:
git clone --branch staging https://x-token:$GH_PAT@github.com/mohammed-shoab/ScopeSnapAI.git /tmp/snapai_staging
```
Token: `GH_STAGING_PAT` in `.staging_secrets.txt` (snapai-staging-deploy, repo+workflow scope).
NEVER `git stash` from sandbox on NTFS repo (DEC-013). NEVER use git plumbing from NTFS for Unicode files (truncation risk — see TECH_STACK.md WA-7).

### Desktop Commander git workflow (DEC-022 — added 2026-05-20)

When `/tmp` clone is not available or git SSH key is not configured, use Desktop Commander with bat files:
- Write bat to `C:\fixNNN.bat` (NO spaces in path — git fails on `C:\Users\dell\My Drive\...`)
- Inside bat: use `cd /d C:\Users\dell\My Drive\Personal Claude\ScopeSnapAI\scopesnap-web` (cd /d handles spaces)
- Log everything: `>> C:\fixNNN_log.txt 2>&1`
- Execute via `mcp__Desktop_Commander__start_process` with `shell: "cmd"`, path `C:\fixNNN.bat`
- Read results with `mcp__Desktop_Commander__read_file`
- ALWAYS `git stash push` before branch switches; `git stash pop` after returning
- If push rejected (remote ahead): stash → `git pull --rebase` → stash pop → push
- `interact_with_process` for interactive shells DOES NOT WORK — use single-shot bat files only
- `mcp__workspace__bash` CANNOT reach production URLs (exit code 56) — use Claude in Chrome instead
- See TECH_STACK.md WA-8 for full pattern and template

### Key DEC references (permanent rules)

| DEC | Rule |
|-----|------|
| DEC-004 | Git from /tmp clone only — never from NTFS mount |
| DEC-013 | Never `git stash` from sandbox on NTFS |
| DEC-027 | Never use Edit tool on files with non-ASCII chars (truncation) |
| DEC-028 | git fast-import to bypass corrupted index |
| DEC-029 | `companies` table has NO market column — always use X-Market header |
| DEC-030 | `apiFetch` does NOT auto-inject Clerk JWT — pass `token:` explicitly in every authenticated call |
| DEC-031 | `fault_cards` PK is `card_id`, not `id` |
| DEC-032 | Real estimate builder is `assessment/[id]/page.tsx` — `estimate/[id]/page.tsx` is dead code |
| DEC-034 | Missing imports inside try/except silently swallow NameError — always verify imports |
| DEC-035 | Grep target files before implementing — feature may be partially present |

### apiFetch token rule (DEC-030 — critical)

`apiFetch` in `lib/api.ts` does NOT auto-inject Clerk JWT. In production (non-dev), omitting `token:` means no Authorization header → 401. Dev mode uses `X-Dev-Clerk-User-Id` bypass, masking the bug.

**Correct pattern:**
```typescript
const { getToken } = useAuth();
const token = await getToken();
const data = await apiFetch<MyType>("/api/my-endpoint", { token: token ?? undefined });
```

**For fire-and-forget calls:**
```typescript
getToken().then(token => {
  apiFetch("/api/endpoint", { method: "POST", token: token ?? undefined, body: JSON.stringify({...}) })
    .catch(() => {});
}).catch(() => {});
```

### Estimate tier response shape (post-Q.6.5 + R.9)

Each tier in the `POST /api/estimates/fault-card` response includes:
```json
{
  "tier": "B",
  "recommended": true,
  "description": "...",
  "why_recommended": "...",
  "recommendation_reason": "Default capacitor recommendation",
  "recommendation_source": "card_default",
  "seasonal_modifier_pct": 0.25
}
```
`recommendation_reason` and `recommendation_source` are `null` when no lifecycle_rules match. `recommended` flag is only overridden by lifecycle_rules when `condition_signal != "default"`.

---

## Mandatory Rules

### Rule 1 — Git operations from the Linux sandbox (DEC-004 + DEC-013)

**NEVER** `git add/commit/push` from the NTFS-mounted workspace in the Linux sandbox.

**Correct workflow:**
```bash
git clone "https://TOKEN@github.com/mohammed-shoab/ScopeSnapAI" /tmp/snapai_tmp
git config --global --add safe.directory /tmp/snapai_tmp
cp /sessions/.../outputs/changed_file.py /tmp/snapai_tmp/scopesnap-api/api/
cd /tmp/snapai_tmp && git add -A && git commit -m "..." && git push origin main
```

**NEVER use `git stash` from the sandbox** — it truncates TSX/TS files on NTFS (DEC-013).

### Rule 2 — Non-ASCII files (DEC-027)

**NEVER** use the `Edit` tool on any file that contains non-ASCII characters (Unicode, emoji, em-dashes, etc.), regardless of file type (.py, .ts, .tsx, .md). Use Python string replacement instead:
```python
content = open(path, 'rb').read().rstrip(b'\x00').decode('utf-8')
content = content.replace(old_str, new_str, 1)
open(path, 'w', encoding='utf-8').write(content)
```

### Rule 3 — Deploy verification (DEC-002)

A git push is NOT complete until BOTH are confirmed:
1. **Railway health:** `GET https://scopesnap-api-production.up.railway.app/health` returns `{"status":"ok","db":"connected"}`
2. **Vercel:** deployment shows "Ready" on the dashboard

Never say "done" or "deployed" after just `git push`. Sandbox cannot curl external URLs — use Chrome browser tool.

### Rule 4 — Alembic

Current migration version: **`029`**. Next migration MUST be **`030`**.
Migrations run automatically on Railway boot via `start.sh` (`alembic upgrade head`).
Check `alembic_version` table in Supabase before pushing any new migration.
**CRITICAL:** Never use em-dashes or unescaped quotes inside Python string literals in migration files. Use `json.dumps()` for data blobs. Always run `python3 -m py_compile <migration.py>` before committing.

### Rule 5 — Database is Supabase, never Railway

`DATABASE_URL` on Railway points to Supabase. There is NO Railway PostgreSQL service.

### Rule 6 — After any merge, check for NTFS file truncation

```bash
git diff <last-good-sha>..HEAD -- 'scopesnap-web/**/*.tsx' 'scopesnap-web/**/*.ts' --stat
```
Any file showing net deletion near the end is likely truncated.

### Rule 7 — NTFS null-byte padding (DEC-010)

```python
raw = open(path, 'rb').read()
clean = raw.rstrip(b'\x00')
```

---

## PSI Thresholds (verified)

| Refrigerant | Normal suction range | high_min |
|---|---|---|
| R-410A (US) | 108–144 PSI | 145 PSI |
| R-410A (PK) | 125–144 PSI | 145 PSI |
| R-22 (both) | 55–87 PSI | 88 PSI |
| R-32 (PK) | 115–139 PSI | 140 PSI |

---

## QA History

| Date | Audit | Outcome | Notes |
|------|-------|---------|-------|
| 2026-05-20 | Full QA — Tracks R/R9/REC/D/P/Staging | 48 PASS / 1 AUTO-FIX / 0 FAIL | D.6 backfill 62/62, R.7 profile guard, S.7 staging banner shipped |
| 2026-05-19 | PK SOW Addendum | PASS | BUG-015 (X-Market), BUG-016 (PK PSI routing) |
| 2026-05-18 | Houston | PASS | BUG-011 (badge), BUG-012 (electrical spec auto-fill) |
| 2026-05-15 | Houston + PK | PASS | BUG-010b rollback |
| 2026-05-11 | Houston + PK | PASS | Multiple routing bugs |

Full audit report: `C:\Users\dell\My Drive\Personal Claude\QA_Audit_Reports\QA_Audit_2026-05-20_Tracks_R_R9_REC_D_P_Staging.md`
