# SnapAI — Key Architectural Decisions

> This file records decisions made during development that have lasting impact on how the codebase works.
> Future AI sessions: read this before proposing architecture changes or writing migrations.
>
> Last updated: 2026-05-20

---

## DEC-001 — Database on Supabase, not Railway

**Decision:** All data lives in Supabase (PostgreSQL via `pooler.supabase.com`). The Railway project does NOT have a PostgreSQL service attached.

**Why:** Railway auto-created a `postgres-volume` during initial setup but it was never used. All Alembic migrations target Supabase. The Railway volume was deleted Apr 30 2026 (it was an orphaned 1MB disk).

**Impact:** `DATABASE_URL` env var on Railway points to Supabase. Never add a Railway PostgreSQL service — it would be redundant and costly.

---

## DEC-002 — Alembic migrations run automatically on Railway boot via `start.sh`

**Decision:** `start.sh` runs `alembic upgrade head` before starting Uvicorn on every Railway deploy.

**Why:** Eliminates manual migration steps; deploy = migrate + serve in one atomic operation.

**Impact:** Any new `.py` file added to `scopesnap-api/db/migrations/versions/` will run on next Railway deploy. Do NOT push a migration that is already applied to the DB — Alembic will skip it safely, but a data-changing migration run twice could corrupt data. Always check `alembic_version` table before pushing a new migration.

**Current revision:** 029 (as of 2026-05-20)

---

## DEC-003 — `input_type = 'multi'` steps use `options_jsonb`, not `reading_spec`

**Decision:** Questions with both a photo slot and a numeric reading store all input specs inside `options_jsonb` as a JSON array `[{kind, spec}, ...]`. The standalone `reading_spec` column is NULL for these rows.

**Why:** The multi-input design was chosen to allow arbitrary combinations of photo + reading + text fields in a single diagnostic step. The `options_jsonb` array was already used for `multiple_choice` options, so multi steps reuse the same column.

**Impact:** ⚠️ **CRITICAL** — Any Alembic migration that patches reading spec must target `options_jsonb` for multi steps, not `reading_spec`. Migration 014 violated this rule (patched `reading_spec` for `q4-flame-sensor`); migration 015 corrected it. See TECH_STACK.md → WA-6 for the correct SQL pattern.

**How to check before writing a migration:**
```sql
SELECT step_id, input_type, reading_spec IS NULL AS reading_spec_null
FROM diagnostic_questions
WHERE complaint_type = 'your_type';
```

---

## DEC-004 — Git operations from the Linux sandbox: use /tmp clone

**Decision:** All git commits/pushes from the sandbox must be done via a `/tmp` clone of the repo, not from the NTFS-mounted workspace.

**Why:** The workspace is an NTFS-mounted Windows drive. The Linux sandbox cannot create or delete `.git/index.lock` or `.git/HEAD.lock` on NTFS (Operation not permitted). This blocks all standard git operations AND the git plumbing fallback (hash-object → mktree → commit-tree) when HEAD.lock is also blocked.

**Impact:** Workflow for any code change that must be pushed:
1. Write file to sandbox outputs dir (`/sessions/.../outputs/`) — real Linux tmpfs
2. `git clone "https://TOKEN@github.com/ORG/REPO" /tmp/snapai_tmp`
3. `cp` from outputs to clone (never from NTFS workspace to /tmp directly if file was created there)
4. Commit and push from `/tmp/snapai_tmp`

See TECH_STACK.md → WA-5 for full command template.

---

## DEC-005 — Railway API authentication requires Clerk JWT from browser

**Decision:** The Railway backend uses Clerk JWT verification on all protected endpoints. No dev bypass token is available for external API calls.

**Why:** Clerk is the auth provider; all contractor-specific endpoints are protected.

**Impact:** When debugging via browser console, must get a JWT first:
```javascript
window.Clerk.session.getToken().then(t =>
  fetch('https://scopesnap-api-production.up.railway.app/api/...', {
    headers: {'Authorization': 'Bearer ' + t}
  })
)
```
Must be run from an authenticated tab at `snapai.mainnov.tech`. Cannot call from the sandbox (proxy blocks all outbound HTTP — see WA-2 in TECH_STACK.md).

---

## DEC-006 — `photo_branch_map` can override numeric reading branchKey in multi steps

**Decision:** In `input_type = 'multi'` steps, if the AI photo evaluator returns `"escalate"`, the backend overrides the numeric reading's computed branchKey with `"escalate"` via the `photo_branch_map` mechanism.

**Why:** AI photo evaluation is a safety gate — if the photo shows something dangerous (e.g. burnt terminals, severe corrosion), the system should escalate regardless of the meter reading.

**Impact:** During QA/testing of reading-based routing in multi steps, skip the photo slot (leave empty). Only the numeric reading will determine branchKey when no photo is present. Injecting a synthetic/fake photo may cause the AI to return "escalate" and override the test.

---

## DEC-007 — UVICORN_WORKERS = 1 for Railway

**Decision:** Backend runs with 1 Uvicorn worker (reduced from 2 on Apr 30 2026).

**Why:** Halves memory usage. Sufficient for 50–100 concurrent users with async I/O. Cost control: Railway Hobby plan has $5/mo credit limit.

**Impact:** Do not increase UVICORN_WORKERS without checking Railway spend cap. If load exceeds 1 worker capacity, upgrade Railway plan first.

---

## DEC-008 — Frontend TypeScript strict mode, no `any` casting for branch keys

**Decision:** `classifyReading()` in `ReadingInput.tsx` uses strict string comparisons for `spec.type`. The type string in the DB must exactly match what the frontend expects.

**Known type strings and their DB values:**

| Measurement | DB `spec.type` | Frontend match |
|-------------|---------------|----------------|
| Microamps | `"microamps"` | `spec.type === "microamps"` |
| Voltage (L1-L2) | `"voltage_l1_l2"` | `spec.type === "voltage_l1_l2"` |
| Amperage (RLA) | `"amperage_rla"` | `spec.type === "amperage_rla"` |
| PSI (refrigerant) | `"psi"` | `spec.type === "psi"` |
| Capacitance (µF) | `"capacitance_uf"` | `spec.type === "capacitance_uf"` |

**Impact:** If a migration sets `spec.type` to anything not in this list, `classifyReading()` will fall through to a default `branchKey: "ok"` path, and the backend may route incorrectly. BUG #11 (voltage) and BUG #13 (microamps type mismatch) were both caused by this. Always cross-check the frontend handler before writing a migration that touches reading spec types.

---

## DEC-009 — `GET /api/diagnostic/questions/{type}` is a stripped endpoint

**Decision:** The questions list endpoint only returns: `step_id`, `step_order`, `question_text`, `input_type`. It strips `options_jsonb`, `reading_spec`, and `branch_logic_jsonb`.

**Why:** Reduces payload size; frontend only needs question text and type for the initial render. Full step data is returned in the session answer response as `next_step`.

**Impact:** Do not use this endpoint to inspect reading specs or branch logic during debugging. Use the fetch interceptor pattern (TECH_STACK.md → WA-7) to capture the actual `next_step.options` from a session answer response.

---

## DEC-010 — NTFS file writes can produce null-byte-padded files

**Decision:** When writing files to the NTFS-mounted workspace from the Linux sandbox, the Write/Edit tools can produce files with null-byte padding at the end. This corrupts TECH_STACK.md and CONTINUATION_PROMPT.md (binary file detection by grep).

**Why:** NTFS and Linux tmpfs differ in block allocation behavior. The NTFS driver may pre-allocate blocks that get filled with null bytes.

**Impact:** Before reading any .md file that may have been written by the sandbox, check for null-byte padding:
```python
with open(path, 'rb') as f:
    raw = f.read()
clean = raw.rstrip(b'\x00')
if len(clean) < len(raw):
    # File is null-padded — use clean for processing, then rewrite
```
Always write .md files using Python with explicit encoding (`'utf-8'`) and strip before appending. Both TECH_STACK.md and CONTINUATION_PROMPT.md were cleaned of null-byte padding on 2026-05-11.

---

## DEC-011 — Dual-market architecture: shared infra, split data by `pak_*` table prefix

**Decision:** Both the US (Houston) and Pakistan markets share one Railway backend, one
Supabase database, one Vercel deployment, and one Clerk auth instance. Market isolation is
achieved at the *query level* (Pakistan data lives in `pak_*` tables/views) rather than
at the infrastructure level (no separate backend or database per market).

**Why:** Minimises cost and operational overhead. One Railway service, one Supabase
project — no duplicate infrastructure to maintain. Market routing is pure runtime logic:
hostname → `X-Market` header → `get_tables()` → correct table names. Adding a new market
in future requires only: new `pak_XX_*` tables + a new `_XX_TABLES` constant in
`api/dependencies.py` + a new hostname in `lib/market.ts`.

**Impact — the three change scenarios:**

| Scenario | Frontend | Backend | Database |
|---|---|---|---|
| **PK only** | Gate with `detectMarket() === "PK"` | Gate with `if tables.market == "PK":` | Only touch `pak_*` tables |
| **US only** | Gate with `detectMarket() === "US"` | Default (non-PK) path | Only touch standard US tables |
| **Both (universal)** | No gate — shared code path | No gate — shared endpoint | Shared tables (`assessments`, `estimates`, etc.) — one migration applies to both |

**Key files:**
- `scopesnap-web/lib/market.ts` — `detectMarket()`, `MARKET_CONFIG`, `formatCurrency()`
- `scopesnap-api/api/dependencies.py` — `_US_TABLES`, `_PK_TABLES`, `get_tables()`
- `scopesnap-web/lib/api.ts` — injects `X-Market` header on every fetch

**Full reference:** `MARKET_GUIDE.md` — detailed guide with file lists, checklists,
DB table inventory, and example gates for all three scenarios.

---

## DEC-012 — Customer contact fields stored on Assessment row (not Property)

**Decision:** `customer_name`, `customer_phone`, and `customer_email` are stored directly
on the `assessments` table (added 2026-05-15 migration via Supabase `ALTER TABLE`).
These same fields also exist on `properties` but are written redundantly so that
phone-only assessments (PK WhatsApp flow — no address entered) have retrievable contact
data without a Property join.

**Why:** The `properties.address_line1` column is `NOT NULL`. Creating a Property for
phone-only entries (no address) violates this constraint and crashes the endpoint with a
DB error. Storing contact data on Assessment avoids the constraint entirely.

**Impact:**
- `POST /api/assessments` always writes `customer_phone/name/email` to the Assessment row
- `GET /api/estimates/{id}` reads from `Assessment.customer_*` first; falls back to
  `Property.customer_*` only if the Assessment columns are all NULL (legacy entries)
- Do NOT remove the fallback — older assessments (pre-2026-05-15) have no direct columns
- `db/models.py` → `Assessment` model has the three `Optional[str]` mapped columns
- The `assessments` table has the three VARCHAR(200/20) columns in Supabase (added via
  `ALTER TABLE assessments ADD COLUMN IF NOT EXISTS customer_phone VARCHAR(20), ...`)

---

## DEC-013 — Never use `git stash` from the Linux sandbox on NTFS-mounted repo

**Date:** 2026-05-18

**Problem:** Running `git stash` from the Linux sandbox writes a stash object using LF line endings. When the stash is later applied/dropped back onto the NTFS-mounted Windows filesystem, several frontend TypeScript/TSX files get truncated (the file content is cut off mid-function, ending with `\ No newline at end of file`). This corrupts Vercel builds with TypeScript/JSX parse errors. Affected files in the 2026-05-18 incident: `market.ts`, `assess/page.tsx`, `app/(app)/layout.tsx`, `app/r/.../ReportClient.tsx`, `LanguageToggle.tsx`, `SidebarNav.tsx`, `DiagnosticFlow.tsx`, `urdu-strings.ts`, `StepZeroPanel.tsx`, root `app/layout.tsx` — 10 files total across 4 failed Vercel deploys.

**Solution:** NEVER use `git stash` from the sandbox. Instead:
1. Commit all local changes as a WIP commit: `git commit -m "wip: [description]"` before fetching/merging
2. After merge, if needed, `git reset HEAD~1` to un-commit the WIP changes
3. All git operations must use the Desktop Commander `.bat` file pattern (DEC-004 equivalent for Windows-side execution)

**Detection:** After any merge or stash operation, immediately run:
```
git diff <last-known-good-sha>..HEAD -- 'scopesnap-web/**/*.tsx' 'scopesnap-web/**/*.ts' --stat
```
Any file showing a net deletion (more `-` than `+` lines) near the end is likely truncated. Cross-check with `git show <sha>:path | wc -l` vs `wc -l path`.

**Recovery:** For each corrupted file:
1. `git show <good-sha>:<path> > <path>` to restore full content from the good commit
2. Re-apply any intentional changes on top using a Python patch script
3. Commit via Desktop Commander `.bat` and push

**Rationale:** NTFS line-ending translation (LF → CRLF) during stash restore corrupts file content when the sandbox's git and Windows git have mismatched `core.autocrlf` settings.



---

## DEC-014 -- Staging Environment Architecture (2026-05-19)

**Decision:** Full parallel staging environment before any further production changes.

**Components:**
- Separate Supabase project (`pqmgveqkuckbvyygsilk` ap-northeast-1) -- identical schema + seed data
- Separate Clerk staging app (`firm-chamois-61`) -- test-mode keys, no prod user data
- Separate Cloudflare R2 bucket (`scopesnap-uploads-staging`)
- Same Railway project, separate `staging` service watching the `staging` branch
- Same Vercel account, separate project (`scopesnap-web-staging`) watching the `staging` branch
- `StagingBanner.tsx` -- amber fixed bar on all staging pages, invisible in production
- `middleware.ts` -- `NEXT_PUBLIC_ENV=staging` treated as dev to bypass Edge Clerk crash

**Workflow:** Feature branch -> staging branch -> validate -> promote to main -> production.
**Promote script:** `scripts/promote-to-prod.sh <file1> [file2 ...]` (run from local main checkout).

---

## DEC-015 -- Keepalive workflows prevent Supabase free-tier pauses (2026-05-19)

**Decision:** Two GitHub Actions workflows ping both prod and staging Supabase on alternating days.
- `keepalive-supabase-A.yml` -- every Sunday 02:00 UTC
- `keepalive-supabase-B.yml` -- every Wednesday 14:00 UTC
- Monitored via Healthchecks.io (account ds.shoab@gmail.com)

**Impact:** Both Supabase projects remain active indefinitely without always-on paid tier.

---

## DEC-016 -- Legacy estimate engine deleted (2026-05-19)

**Decision:** `services/estimate_engine.py` deleted. `POST /api/estimates/generate` removed.

**Why:** Q.6.5 merged recommendation engine into `fault_estimate.py`, making old engine redundant.

**Impact:** All estimates flow exclusively through `POST /api/estimates/fault-card` -> `fault_estimate.py`. Never recreate the old engine.

---

## DEC-017 -- condition_signals vocabulary v1 strings are immutable (2026-05-20)

**Decision:** Existing condition_signal strings MUST NOT be renamed -- breaks lifecycle_rules backward compatibility. New signals can be added freely. See DEC-024 for full vocabulary.

---

## DEC-018 -- diagnosis_feedback table is shared (no pak_ variant) (2026-05-20)

**Decision:** Single `diagnosis_feedback` table for both markets. FK references `diagnostic_sessions.id` (already shared). Market derivable via assessment_id join for analytics.

---

## DEC-019 -- DiagnosticFlow resolved -> /diagnoses/<id>, not evidence phase (2026-05-20)

**Decision:** Fault card resolution navigates to `/diagnoses/<session_id>` (FaultResolutionScreen). Estimate still reachable from Assessments list. "Generate estimate from here" deferred to v1.5.

---

## DEC-020 -- pak_pricing_tiers table structure (2026-05-20)

**Decision:** PK pricing uses dedicated `pak_pricing_tiers` table (45 rows: 15 cards x 3 tiers). Columns: `card_id`, `tier` (good/better/best), `label_en`, `label_ur`, `description_en`, `description_ur`, `parts_pkr`, `labor_pkr`, `total_pkr`.

**Why:** PKR amounts + Urdu bilingual content cannot share the US pricing_tiers table without heterogeneous currency columns and market-gated queries everywhere.

---

## DEC-021 -- pak_fault_card_descriptions + pak_fault_card_urdu_descriptions (2026-05-20)

**Decision:** Separate tables for PK fault card bilingual content. Allows independent updates to English vs Urdu without touching pak_fault_cards main data.

---

## DEC-022 -- Desktop Commander bat-file pattern for Windows-side git (2026-05-20)

**Decision:** When Linux sandbox cannot reach git (NTFS lock), use Desktop Commander .bat files on the Windows side.
- Write bat to `C:\fixNNN.bat` (no spaces in path)
- Inside bat: `cd /d "C:\Users\dell\My Drive\Personal Claude\ScopeSnapAI"`
- Log: `>> C:\fixNNN_log.txt 2>&1`
- Execute via `mcp__Desktop_Commander__start_process` with `shell: "cmd"`
- Never use interact_with_process (not interactive-capable)

---

## DEC-023 -- NEXT_PUBLIC_ENV=staging controls staging-specific behaviour (2026-05-20)

**Decision:** `NEXT_PUBLIC_ENV=staging` drives three behaviours:
1. `StagingBanner.tsx` renders amber bar
2. `middleware.ts` bypasses Clerk Edge Runtime crash
3. `app/(app)/layout.tsx` adds `pt-6` for banner height

**Never** set `NEXT_PUBLIC_ENV=staging` on the production Vercel project.


## DEC-024 -- Recommendation engine condition_signal vocabulary v1 (2026-05-20)

**Date:** 2026-05-20

**Decision:** Standard condition_signal vocabulary for lifecycle_rules lookups.
Implemented in services/condition_signals.py (Track REC.2).

| Signal | Derivation |
|---|---|
| default | No specific condition matched (fallback) |
| under_warranty | install_year within last 2 years |
| photo_confirmed_pitting | AI photo: pitting or electrical_damage in ai_issues |
| formicary_confirmed | AI photo: formicary in ai_issues |
| rla_over_nameplate | reading_inputs row with reading_type=amperage_rla and passed=false |
| recurring_clog | 2nd+ Card 5 diagnosis for same property_id in 12 months |
| attic_location | ocr_nameplate or tech_overrides location field contains "attic" |
| bearing_noise | tech_overrides.symptom contains grind/noise/bearing; or complaint_type=making_noise |
| sensor_only | card_id=11 and error_code_type contains "sensor" but not "ignitor" |

**Priority chain:** first match wins (see services/condition_signals.py _derive()).

**Vocabulary rules:**
- Vocabulary is v1 -- expected to refine after 50+ approval data points.
- New signals can be added freely.
- Existing signal strings MUST NOT be renamed -- breaks lifecycle_rules backward compatibility.
- lifecycle_rules expanded to 50 rows via migration 028 (Track REC.3).

**Impact:** fault_estimate.py calls derive_condition_signal_from_assessment() before
lifecycle_rules lookup. If derivation fails, falls back to "default" silently (try/except).


## DEC-025 -- Track D: single diagnosis_feedback table for both markets (2026-05-20)

**Date:** 2026-05-20

**Decision:** Use a single `diagnosis_feedback` table for both US and PK markets.
No `pak_diagnosis_feedback` variant.

**Rationale:** `diagnostic_sessions` is already a single shared table (no pak_ variant).
Feedback rows reference `diagnostic_sessions.id` via FK. Since the session table is shared,
the feedback table must also be shared. Market is derivable from the session's assessment_id
via join if market segmentation is needed in analytics.

**Impact:** DEC-011 shared-DB pattern applies. No market gate needed on POST /api/diagnostic/feedback.

---

## DEC-026 -- Track D: diagnosis screen replaces evidence phase for all resolutions (2026-05-20)

**Date:** 2026-05-20

**Decision:** When DiagnosticFlow resolves to a fault card, the app navigates directly to
`/diagnoses/<session_id>` (FaultResolutionScreen) instead of the old evidence → estimate flow.

**Rationale:** PK tech feedback: "I bought this for the estimate, but the diagnostic is what I use."
The diagnosis screen is the product hero. Estimate generation is available from the assessment page
but is no longer the forced next step after a diagnostic resolution.

**Wiring:** `handleDiagnosticResolved` in `assess/page.tsx` fires:
1. Fire-and-forget `POST /api/diagnostic/finalize/<session_id>` (idempotent, sets customer_label + share_token)
2. `router.push('/diagnoses/<session_id>')`

**Deferral:** The "Generate estimate from here" button on FaultResolutionScreen is deferred to v1.5.
Techs can still navigate to the estimate via Assessments list if needed.

**Impact:** The old `setPhase("evidence")` call is removed. Evidence/photo collection phase still
exists for non-diagnostic-resolved assessments (e.g., service/tune_up) but is no longer reached
from the diagnostic resolution path.


## DEC-027 -- NTFS truncation affects ALL files with Unicode, not just emoji-containing TSX (2026-05-20)

**Date:** 2026-05-20

**Problem:** During Track D QA, the Edit tool was used to replace a section of
`scopesnap-api/api/diagnostic.py`. The file contained Unicode box-drawing characters
in section header comments (e.g. `# -- D.9: GET /public/{share_token} --------`).
The Edit tool truncated the file at approximately 80 characters per line, cutting off
lines mid-sentence and producing a file that was 1565 lines instead of the expected 1578+.
Python's `ast.parse()` reported a SyntaxError at the truncation point.

**DEC-010 only covered null-byte padding; DEC-013 only covered git stash.
This is a new failure mode: the Edit tool itself truncates on NTFS for any file with
non-ASCII characters, regardless of whether it's TSX, TS, or PY.**

**Rule extension:**
> NEVER use the `Edit` tool on ANY file that contains non-ASCII characters
> (Unicode, emoji, box-drawing, em-dashes, etc.), regardless of file type.
> This includes `.py`, `.ts`, `.tsx`, `.md` files.

**Safe write patterns for files with Unicode:**
1. Python append script: `with open(path, 'a') as f: f.write(content)` — bypasses Edit
2. `git fast-import` plumbing — bypasses index and Edit tool entirely
3. Desktop Commander `write_file` in chunks of ≤30 lines — use for full rewrites

**Detection after any Edit on a Unicode-containing file:**
```bash
python3 -c "import ast; ast.parse(open('file.py').read()); print('OK')"
wc -l file.py  # compare to expected line count
```

**Recovery used in this incident:**
1. `git show <remote-sha>:<path> > /tmp/file_clean.py` — extract clean remote version
2. Append new content via Python script (no Edit tool)
3. `git hash-object -w <file>` + `git fast-import` to commit without using index

---

## DEC-028 -- git index corruption recovery: use git fast-import to bypass index (2026-05-20)

**Date:** 2026-05-20

**Problem:** Multiple sequential `git read-tree`, `git update-index`, and `git stash`
operations in the Linux sandbox against an NTFS-mounted repo caused the `.git/index`
file to become corrupted (`error: bad signature 0x00000000 / fatal: index file corrupt`).
Once corrupted, even `rm -f .git/index && git read-tree HEAD` only worked transiently --
the next git operation would corrupt it again. `git stash`, `git add`, `git checkout -- .`
all failed.

**Root cause:** Concurrent lock file creation races between sandbox git and Windows git
(VS Code, shell, etc.) on the NTFS mount. The `.git/index.lock` being left behind by
a timed-out bash call caused subsequent operations to write to a stale/partially-written
index file.

**Recovery pattern (2026-05-20 incident):**
```bash
# 1. Hash the target file(s) directly into the object store (bypasses index)
HASH=$(git hash-object -w path/to/file.py)

# 2. Build the commit via fast-import (no index needed)
git fast-import --quiet << EOF
commit refs/heads/main
author Claude Bot <claude@anthropic.com> $(date +%s) +0000
committer Claude Bot <claude@anthropic.com> $(date +%s) +0000
data <byte-length-of-message>
<commit message>
from <parent-sha>
M 100644 <blob-hash> path/to/file.py
EOF

# 3. Push normally
git push origin main
```

**Key insight:** `git fast-import` creates commits from blob hashes without touching
`.git/index` at all. It is the safest way to push file changes when the index is broken.

**Prevention:**
- Never run multiple git operations in rapid succession against the NTFS-mounted repo
- Remove `.git/index.lock` before every git command: `rm -f .git/index.lock`
- Prefer `git fast-import` for all pushes in this environment (avoids stash, add, commit cycle)

---

## DEC-029 -- companies table has NO market column; market routing is always header-based (2026-05-20)

**Date:** 2026-05-20

**Problem:** During Track D implementation, `GET /api/diagnostic/public/{share_token}`
was written to determine market by querying `SELECT market FROM companies WHERE id = :cid`.
This column does not exist and would have caused a 500 at runtime.

**Rule:** The `companies` table has NO `market` column. Market is ALWAYS determined by:
- **Frontend:** `detectMarket()` in `lib/market.ts` (hostname-based: `pk.*` → PK, else US)
- **Backend:** `X-Market` HTTP header → `get_tables()` in `api/dependencies.py`
- **Never:** A column on the companies/users/assessments tables

**Correct pattern for market-aware backend endpoints:**
```python
@router.get("/some-endpoint")
async def my_endpoint(
    tables: MarketTables = Depends(get_tables),  # reads X-Market header
    ...
):
    fc_table = tables.fault_cards   # "fault_cards" or "pak_fault_cards"
    market = tables.market          # "US" or "PK"
```

**For unauthenticated endpoints** (no Clerk JWT): still add `get_tables` dependency.
The `X-Market` header must be sent by the client. See DEC-030.

---

## DEC-030b -- Raw fetch() calls on public pages must explicitly send X-Market header (2026-05-20)

**Date:** 2026-05-20

**Problem:** Authenticated API calls use `apiFetch()` from `lib/api.ts`, which
auto-injects `X-Market: detectMarket()` on every request. However, the public share
page `/d/[share_token]` uses a raw `fetch()` call (no Clerk auth headers needed).
Raw `fetch()` does NOT auto-inject X-Market, so the backend `get_tables()` defaults
to US market for all public share requests, including PK URLs.

**Fix applied (commit 6314219):**
```typescript
// Public page -- no apiFetch, but still send X-Market
fetch(`${API_URL}/api/diagnostic/public/${share_token}`, {
  headers: { "X-Market": detectMarket() },
})
```

**Rule:** Any `fetch()` call (raw, not apiFetch) that hits a market-aware endpoint
MUST manually add `headers: { "X-Market": detectMarket() }`.

**Pattern to search for potential violations:**
```bash
grep -rn "fetch(" scopesnap-web/ | grep -v "apiFetch\|node_modules" | grep "/api/"
```
Each result should either use `apiFetch` or explicitly pass `X-Market`.

---

## DEC-031 -- QA must verify code on disk, not just task list status (2026-05-20)

**Date:** 2026-05-20

**Problem:** Track D tasks D.1-D.9 were marked [completed] in ACTIVE_TASKS.md.
But QA-4 (backend code audit via grep) revealed that 4 of the 5 new backend endpoints
were missing from the actual file. The parallel session had added only
`GET /result/{session_id}` (commits 872e959 + 575f73e). The remaining 4 routes --
`GET /list`, `POST /feedback`, `POST /finalize/{session_id}`, `GET /public/{share_token}` --
were never written to `diagnostic.py`.

**Root cause:** Task completion was tracked optimistically (the AI declared tasks done
before verifying the file on disk). Context window limits in long sessions mean the AI
may lose track of whether it actually wrote something vs. only planned to write it.

**Mandatory QA checklist for any backend track:**
```bash
# Count @router. decorators in target file
grep -c "@router\." scopesnap-api/api/diagnostic.py

# Verify each expected route exists
grep "@router\." scopesnap-api/api/diagnostic.py | grep -E "result|list|feedback|finalize|public"

# Syntax check
python3 -c "import ast; ast.parse(open('scopesnap-api/api/diagnostic.py').read()); print('OK')"

# Confirm file wasn't truncated
wc -l scopesnap-api/api/diagnostic.py
```

**Rule:** Before marking any backend track complete, always grep the actual file for
every route that was supposed to be added. Task list status alone is not sufficient proof.
---

## DEC-036 -- SQLAlchemy 2.0 silently drops ORM constructor kwargs for unmapped columns (2026-05-20)

**Date:** 2026-05-20

**Problem:** `fault_estimate.py` passed `seasonal_modifier_pct=seasonal_pct_int` to the
`Estimate(...)` ORM constructor. The column existed in the database (added by migration 029)
but was NOT defined in the `Estimate` ORM class in `db/models.py`.

SQLAlchemy 2.0 with `DeclarativeBase` silently sets unknown constructor kwargs as plain Python
attributes on the instance — no error, no warning. The value is **never persisted to the database**.
The column always received its `server_default` of 0, regardless of what Python passed.

**Discovery:** Noticed the seasonal banner never appeared in peak months. Traced to
`seasonal_modifier_pct` always being 0 in DB. Compared `fault_estimate.py` constructor call
against `db/models.py` Estimate class definition — column was absent from ORM.

**Fix:** Added to `Estimate` class in `db/models.py`:
```python
# R.9 seasonal labour surcharge captured at generation time (migration 029)
seasonal_modifier_pct: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
```

**Rule for future migrations:** Any time a new column is added via Alembic migration AND
the column value is set in Python code (not purely a server_default), the corresponding
`Mapped[type] = mapped_column(...)` line MUST be added to the ORM class in `db/models.py`.

**Verification pattern after any new column + ORM work:**
```python
# After creating a test record, query the column immediately:
result = db.execute(text("SELECT seasonal_modifier_pct FROM estimates WHERE id = :id"), {"id": est.id})
print(result.scalar())  # Must NOT be server_default if Python passed a value
```

---

## DEC-037 -- FaultResolutionScreen.handleContinue must be async and create estimate before navigating (2026-05-20)

**Date:** 2026-05-20

**Problem:** `handleContinue` in `FaultResolutionScreen.tsx` was synchronous and navigated to
`/assessment/${data.assessment_id}`. This is wrong for two reasons:
1. `assessment_id` is the diagnostic assessment UUID — NOT an estimate UUID.
2. The `/assessment/[id]` page expects an **estimate** ID (from the `estimates` table).
Navigating to an assessment_id caused a 404 on the estimate builder page.

**Root cause:** The function was written before the diagnoses flow was refactored. After the
DX track refactor, assessments no longer auto-create estimates — the estimate must be explicitly
created by calling `POST /api/estimates/fault-card`.

**Fix:** Made `handleContinue` async:
```typescript
async function handleContinue() {
  if (!data.assessment_id || navigating) return;
  setNavigating(true);
  // ... track event ...
  try {
    const token = await getToken();
    const est = await apiFetch<{ id: string }>("/api/estimates/fault-card", {
      method: "POST",
      token: token ?? undefined,
      body: JSON.stringify({
        card_id: data.fault.card_id,
        assessment_id: data.assessment_id,
      }),
    });
    if (!est.id) throw new Error("No estimate ID");
    router.push(`/assessment/${est.id}`);  // est.id = estimate UUID
  } catch (err) {
    console.error("Estimate creation failed:", err);
    setNavigating(false);
  }
}
```

**Rule:** Any button that "continues to estimate" from a diagnosis result MUST:
1. Call `POST /api/estimates/fault-card` with `{card_id, assessment_id}`
2. Use the returned `est.id` (estimate UUID) for navigation
3. Never use `data.assessment_id` or `data.session_id` as the route parameter

**Verified live:** rpt-0494 created and loaded correctly after fix. Navigation went to
`/assessment/97b22e44-c121-4e21-92e6-0d3a158b4e95` (estimate ID). ✅
