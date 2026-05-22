# SnapAI — Key Architectural Decisions

> This file records decisions made during development that have lasting impact on how the codebase works.
> Future AI sessions: read this before proposing architecture changes or writing migrations.
>
> Last updated: 2026-05-22 (DEC-058, DEC-059, DEC-060 added — ServiceChecklist auth, estimates INSERT, missing endpoint)

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


---

## DEC-034 — TCO data sourced from DB tables, not live calculation (Track G, 2026-05-21)

**Decision:** `five_year_comparison` data is pre-computed and stored in `card_tco_data` /
`pak_card_tco_data`, keyed on `(card_id, tier)`. It is NOT calculated at runtime from
energy prices or live repair history.

**Rationale:** Actuarial-style probability estimates require curated data (AHRI failure studies,
DOE energy data, PK load-shedding research) that cannot be derived from live signals.
Pre-computed data is auditable, reviewable by the advisory board, and version-controlled in
the JSON seed files.

**Implication:** When estimates.py calls `_enrich_tco_from_db()`, a DB miss (no TCO row for
that card/tier) returns `None` silently — FiveYearComparison renders nothing rather than
showing bad data.

---

## DEC-035 — TCO column order: C (left) -> B (center) -> A (right) (Track G, 2026-05-21)

**Decision:** FiveYearComparison renders tiers in order C, B, A — most expensive option on
the LEFT, cheapest on the right. Opposite of typical Good/Better/Best left-to-right ordering.

**Rationale:** Marcus Reed board directive. Presenting the replacement option (C) first anchors
the homeowner on the premium option and makes the middle tier (B, recommended) feel like
a reasonable save. Psychological anchoring increases B uptake.

**Implementation:** `TierCard` array is hardcoded `[C, B, A]` in FiveYearComparison.tsx.
Do not reorder without board approval.

---

## DEC-036 — PresentMode Slide4 selectedTier used as recommendedTier (Track G, 2026-05-21)

**Decision:** In Slide4Value (PresentMode), `selectedTier` is passed as `recommendedTier` to
FiveYearComparison. The Option interface in PresentMode.tsx does not carry a `recommended`
boolean (the prop isn't passed through from the estimate builder).

**Rationale:** `selectedTier` in PresentMode is always the tech's recommended tier at the
point they enter Present Mode. Using it as `recommendedTier` is functionally equivalent and
avoids adding a new prop to EstimateData.


## DEC-043 -- alembic_version can be ahead of actual schema (2026-05-21)

**Date:** 2026-05-21

**Problem:** After a Railway GCP platform outage, `alembic_version` in the production DB showed
`032` but the `diagnostic_sessions.photo_skipped` column (from migration 031) did not exist.

**Root cause:** Migration 032 (Track G, `card_tco_data` tables) was applied directly via the
Supabase MCP `apply_migration` tool during a prior session. This runs the migration's DDL SQL
and stamps `alembic_version = 032` directly. It does NOT run Alembic's dependency chain —
so migration 031's `upgrade()` (which adds `photo_skipped`) was never executed.

**Rule:** NEVER assume `alembic_version = N` means all migrations <= N have been applied to the
schema. Always verify column/table existence independently:
```sql
-- Before trusting alembic_version, verify the column exists:
SELECT column_name FROM information_schema.columns
WHERE table_name = 'your_table' AND column_name = 'your_column';
```

**Fix used:** Applied 031's DDL directly via Supabase MCP:
```sql
ALTER TABLE diagnostic_sessions
  ADD COLUMN IF NOT EXISTS photo_skipped BOOLEAN NOT NULL DEFAULT false;
```
Used `IF NOT EXISTS` to make it idempotent — safe to run again.

**Impact:** After any Railway outage where builds were queued but never deployed, audit ALL
migrations in the chain between the last known-good Railway deploy and the current
`alembic_version`. Any that were applied via Supabase direct may have gaps.

---

## DEC-044 -- Python replace() write can silently truncate the end of long files (BUG-027) (2026-05-21)

**Date:** 2026-05-21

**Problem:** A Python patch script used the pattern:
```python
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace(old, new, 1)
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
```
The write succeeded with no error, but the last 2 lines of `scopesnap-api/api/reports.py`
(the closing `}` of the approve endpoint's return dict) were silently dropped. The file was
445 lines instead of the expected 447. This caused a Python SyntaxError at runtime:
`'{' was never closed` — FastAPI failed to import the reports router, crashing on startup.

**Why it's silent:** The `f.write(content)` call returns the number of bytes written, but
Python does not raise an error if the write is truncated by the OS (NTFS filesystem quirk).
The file appears valid and git commits cleanly — the SyntaxError only surfaces at runtime.

**Rules:**
1. After ANY Python write to a `.py` file, verify syntax immediately:
   ```bash
   python3 -c "import ast; ast.parse(open('path/to/file.py').read()); print('SYNTAX OK')"
   ```
2. After ANY write, verify line count matches expectation:
   ```bash
   wc -l path/to/file.py  # compare to last known good count
   ```
3. For `.tsx`/`.ts` files, check the last 10 lines:
   ```bash
   tail -10 path/to/file.tsx
   ```
4. If truncation is detected: use `git show <remote-sha>:<path>` to recover the clean file,
   then re-apply the patch.

**Recovery used:** `git show 477314b:scopesnap-api/api/reports.py > /tmp/reports_clean.py`
to recover the original, identified missing tail, used Edit tool to restore it, pushed as
`a6d4a15`.

---

## DEC-045 -- Railway "Online" dashboard status does NOT mean the service is healthy (2026-05-21)

**Date:** 2026-05-21

**Problem:** During the Railway GCP outage recovery, the Railway dashboard showed
`scopesnap-api` as "Online" while `GET /health` consistently returned 502 Bad Gateway.

**Why:** Railway's "Online" status reflects the container lifecycle state (running), not
whether the process inside is successfully handling requests. When a Python SyntaxError
prevents FastAPI from importing a router at startup, the process crash-loops. Railway
marks the container as "Online" during restart attempts, not as "Crashed".

**Rule:** ALWAYS verify health via the actual health endpoint:
```
GET https://scopesnap-api-production.up.railway.app/health
Expected: {"status":"ok","db":"connected","environment":"production","version":"0.1.0"}
```
Do NOT trust Railway dashboard status ("Online") as proof the service is healthy.
Only `{"status":"ok"}` from `/health` confirms the service is serving requests.

**Corollary:** If Railway shows "Online" but `/health` returns 502, the active deployment
has a startup crash (most likely a Python SyntaxError). Check deploy logs for the crash
traceback before attempting any other fixes.

---

## DEC-046 -- Cherry-pick fails with add/add conflicts when remote has moved ahead (2026-05-21)

**Date:** 2026-05-21

**Problem:** Tried to cherry-pick a local commit (`a0aae81`) onto `origin/main` after
remote had moved ahead by 3 commits (`477314b`). Every file had "add/add" conflicts because
git saw both sides as "adding" the file (different content). Cherry-pick aborted.

**Why:** Cherry-pick computes a 3-way merge using the cherry-pick's parent as the merge base.
When the remote has diverged significantly (especially if the same files were touched),
the merge base is a common ancestor that is far behind both sides — causing "both added" conflicts.

**Rule:** Never cherry-pick a local commit onto a remote that has moved ahead by more than
1-2 commits on the same files. Instead:
1. Pull the latest remote HEAD
2. Re-apply the changes fresh using Python `replace()` scripts directly on the remote files
3. Commit + push as a new commit on top of the latest remote HEAD

This is faster and safer than resolving cherry-pick conflicts.

---

## DEC-047 -- Clerk session is shared across *.mainnov.tech subdomains (2026-05-21)

**Date:** 2026-05-21

**Finding:** A single Clerk login on `snapai.mainnov.tech` automatically authenticates
the user on `pk.snapai.mainnov.tech` without requiring a second login. Both domains share
the same Clerk session cookie (scoped to `.mainnov.tech`).

**Impact for QA:** When testing both markets, only ONE login is needed. Navigate to
`snapai.mainnov.tech/sign-in` → log in once → then navigate to `pk.snapai.mainnov.tech` —
it will already be authenticated. The JWT tokens from `window.Clerk.session.getToken()` on
either tab are identical and accepted by the backend on both `X-Market: US` and `X-Market: PK`.

**Impact for Claude Chrome extension:** The Claude-controlled browser tab group shares cookies
across tabs within the group. Opening a PK market tab while already logged in on Houston
gives instant access — no re-login needed.

---

## DEC-048 -- Claude Chrome extension tab group resets between sessions (2026-05-21)

**Date:** 2026-05-21

**Problem:** After a context window compaction (new conversation se

---

## DEC-049 -- Estimate option tiers stored as "A"/"B"/"C" -- NOT "good"/"better"/"best" (2026-05-21)

**Date:** 2026-05-21

**Problem (BUG-032):** The homeowner report page sent `{ selected_option: "B" }` to the approve
endpoint. The approve endpoint rejected it with `422: selected_option must be 'good', 'better', or 'best'`.
The Approve button appeared to do nothing from the homeowner's perspective.

**Root cause:** Two different naming schemes exist in the codebase and were never in sync:

| Location | Tier naming |
|----------|-------------|
| `fault_estimate.py` EstimateTier | "A" / "B" / "C" (A=cheapest fix, C=replacement) |
| `pak_pricing_tiers.tier` column | "good" / "better" / "best" |
| `reports.py` approve endpoint (before fix) | "good"/"better"/"best" only -- rejected "A"/"B"/"C" |
| `ReportClient.tsx` TIER_LABELS | `{ good: "Option A", better: "Option B", best: "Option C" }` |

The `estimates` DB table stores options[].tier as "A"/"B"/"C".
`ReportClient.tsx` reads the recommended tier ("B"), sends `{ selected_option: "B" }`.
The old approve endpoint rejected "B" every time -- approval was silently broken.

**Fix:** `scopesnap-api/api/reports.py` line 365:
```python
# Before:
if body.selected_option not in ("good", "better", "best"):
# After:
if body.selected_option not in ("good", "better", "best", "A", "B", "C"):
```

**Rule:** When writing code that handles estimate option tiers:
1. The `estimates` DB table stores tiers as "A"/"B"/"C"
2. `pak_pricing_tiers.tier` uses "good"/"better"/"best" -- different system
3. The approve endpoint now accepts both -- never validate only one scheme
4. `ReportClient.tsx` TIER_LABELS is a display mapping only -- the payload uses the raw DB value

**Commit:** `4743a40`
**Verified:** "Thank you! You selected Fix + Prevent Next Failure." shown on report after approval

---

## DEC-050 -- Desktop Commander Python subprocess is the reliable git pattern for Windows (2026-05-21)

**Date:** 2026-05-21

**Problem:** Remote had moved ahead, push rejected (`fetch first`). Local had uncommitted
doc changes. Linux sandbox git is banned on NTFS (DEC-013). PowerShell semicolon commands
gave no visible output in Desktop Commander.

**Reliable workflow -- write to C:\Windows\Temp\fix_NNN.py and run via Desktop Commander:**
```python
import subprocess

repo = r"C:\Users\dell\My Drive\Personal Claude\ScopeSnapAI"

def git(cmd):
    result = subprocess.run(
        ["git"] + cmd.split(),
        cwd=repo, capture_output=True, text=True,
        encoding="utf-8", errors="replace"
    )
    print(f"git {cmd}: stdout={result.stdout!r} stderr={result.stderr!r}")
    return result

git("stash")
git("fetch origin")
git("rebase origin/main")
git("stash pop")
git("add -A")
# Note: commit message must be passed as a list element, not split
result = subprocess.run(
    ["git", "commit", "-m", "your message here"],
    cwd=repo, capture_output=True, text=True
)
print(result.stdout)
git("push origin main")
```

**Why this works:** Desktop Commander runs Python in the Windows process. Windows git can
manipulate the NTFS `.git/index` without the NTFS locking issue. The sandbox's Linux git
is what causes `index.lock` failures.

**IMPORTANT distinction from DEC-013:**
- Windows Desktop Commander Python subprocess git = SAFE (Windows git, native NTFS)
- Linux sandbox git on NTFS-mounted path = BANNED (DEC-013)

---

## DEC-051 -- BUG-031 OPEN: Staging banner visible on pk.snapai.mainnov.tech (2026-05-21)

**Date:** 2026-05-21

**Problem:** Amber "STAGING" banner appears at top of production `pk.snapai.mainnov.tech`.

**Root cause:** Vercel PRODUCTION project has `NEXT_PUBLIC_ENV=staging` set.
`StagingBanner.tsx` renders when `process.env.NEXT_PUBLIC_ENV === "staging"`.

**Fix (no code change needed -- Vercel dashboard only):**
1. Vercel dashboard -> `scope-snap-ai` project -> Settings -> Environment Variables
2. Find `NEXT_PUBLIC_ENV`
3. For Production environment: delete it OR set value to `production`
4. Trigger a new deploy

**Status:** OPEN -- awaiting Vercel dashboard action by Shoab.

**Prevention:** After any staging environment setup, immediately audit the PRODUCTION Vercel
project's environment variables to confirm `NEXT_PUBLIC_ENV` is absent or set to `production`.


---

## DEC-032 -- estimate/[id] route is dead code; real estimate builder is assessment/[id] (2026-05-20)

**Date:** 2026-05-20

**Decision:** The route `/estimate/[id]` in the Next.js app is dead code and should not be used.
The real estimate builder page is `/assessment/[id]/page.tsx`.

**Rationale:** During early development, an `/estimate/[id]` route was scaffolded.
The canonical page that renders the estimate builder UI was built at `/assessment/[id]`.
The two routes co-existed without cleanup. All navigation (from FaultResolutionScreen,
from the Assessments list, from email links) should point to `/assessment/[id]`.

**Rule:** Never link or navigate to `/estimate/<id>`. Always use `/assessment/<id>` for estimate display.

**Cross-reference:** PROJECT_BRAIN.md Critical Rules table.

---

## DEC-033 -- pak_fault_cards (and pak_fault_cards_v) use card_id as the PK business key (2026-05-20)

**Date:** 2026-05-20

**Decision:** Pakistan fault card rows use `card_id` (INTEGER) as the business key, not `id` (UUID).
All JOINs and WHERE clauses involving `pak_fault_cards` / `pak_fault_cards_v` / `fault_cards` must
reference `card_id`, not `id`.

**Rationale:** `pak_fault_cards` was seeded from `ac_data_repo_pakistan.json` where each card has
a numeric `card_id` that is the stable identifier used across `pak_card_tco_data`, `pak_pricing_tiers`,
`pak_fault_card_descriptions`, etc. The `id` UUID column is an internal row identifier and is NOT
shared across tables.

**Rule:**
```python
# CORRECT
WHERE fc.card_id = :cid
JOIN pak_card_tco_data tco ON tco.card_id = fc.card_id

# WRONG -- fc.id is a UUID that has no cross-table meaning
WHERE fc.id = :cid
```

**Cross-reference:** PROJECT_BRAIN.md Critical Rules table.

---

## DEC-052 -- Track DX: structured alternative fault card picker (DX.9) (2026-05-20)

**Date:** 2026-05-20

**Decision:** The "alternative diagnosis" UX presents a structured picker of fault card options
rather than a freeform text input. When a technician disagrees with the primary diagnosis,
they select from a short list of plausible alternative fault cards (populated from the fault_cards
table filtered by the same complaint category).

**Rationale:** Freeform text is hard to analyse and useless for improving the diagnostic model.
A structured picker creates labelled training data: (original_card_id, selected_alternative_card_id,
session context). This feeds back into future fault card probability calibration.

**Implementation:**
- `diagnosis_feedback.alternative_fault_id` (INTEGER, FK to fault_cards.card_id) — added in migration 030
- Backend: `POST /api/diagnostic/feedback` accepts `alternative_fault_id`
- Frontend: picker shows cards from same complaint category, ordered by frequency

**Cross-reference:** Migration 030, DEC-030 (migration 030_diagnosis_feedback_alternative_fault_id).

---

## DEC-053 -- Track DX: "Mark as Solved" button removed from FaultResolutionScreen (2026-05-20)

**Date:** 2026-05-20

**Decision:** The "Mark as Solved" button that previously appeared on FaultResolutionScreen
has been permanently removed. There is no replacement button or flow for marking a diagnosis
as solved in v1.

**Rationale:** PK tech feedback showed that "Mark as Solved" was never tapped. Techs use the
diagnosis screen as a live reference while working, and the concept of "solved" is ambiguous
mid-job. The button added UI clutter with zero usage. The feedback flow (alternative picker,
thumb up/down) replaces it as the primary signal of resolution quality.

**Rule:** Do NOT re-add "Mark as Solved" or any equivalent without explicit product decision.
Grep for this string before any FaultResolutionScreen edit to confirm it stays absent.

---

## DEC-054 -- Track DX: self-graduating UI thresholds (DX.12) (2026-05-20)

**Date:** 2026-05-20

**Decision:** Two UI behaviours graduate automatically based on localStorage usage counters:

1. **Repair Plan section visibility** (`snapai_diagnoses_opened_count`):
   - Sessions 1–19: all three tier cards in the Repair Plan section are expanded by default.
   - Session 20+: section collapses to a single recommended tier; user taps to expand others.
   - Threshold: 20 diagnosis screens opened (counted by `incrementDiagnosesOpened()` in
     `lib/userSessionCounter.ts`, called on FaultResolutionScreen mount).

2. **Continue button label** (`snapai_app_sessions_count`):
   - Sessions 1–3: full label "Generate Estimate & See Pricing" (hand-holding copy).
   - Session 4+: shorter label "See Estimate" (experienced-user copy).
   - Threshold: 3 app sessions (counted by `incrementSessionCount()` in
     `lib/userSessionCounter.ts`, 6-hour cooldown between increments).

**Rationale:** New techs need guidance; experienced techs find it patronising. Graduated UX
removes friction for power users without abandoning new users.

**Implementation:** `lib/userSessionCounter.ts` — localStorage only, per-device, no server sync.
Cross-device sync deferred to v1.5.

---

## DEC-055 -- Track F A.3: canonical definition of "Sent" estimate count on dashboard (2026-05-21)

**Date:** 2026-05-21

**Decision:** The "Sent" count on the contractor dashboard counts estimates where:
```sql
sent_at IS NOT NULL AND deleted_at IS NULL
```

**Rationale:** Previously, some code paths counted `status = 'sent'` and others counted
`sent_at IS NOT NULL`. The two diverged when estimates were soft-deleted (deleted_at set)
but kept `status='sent'`. The `sent_at IS NOT NULL AND deleted_at IS NULL` predicate is the
canonical definition and must be used everywhere a "Sent" count is displayed or returned.

**Rule:** Any dashboard metric, API count, or frontend display showing "Sent" estimates
MUST use the `sent_at IS NOT NULL AND deleted_at IS NULL` predicate. Never use `status='sent'`
alone as a proxy for sent count.

**Cross-reference:** Track F A.3, backend estimates.py dashboard endpoint.

---

## DEC-056 -- BUG-033: Service/Tune-Up photo skip buttons absent from deployed DOM (2026-05-21) ✅ RESOLVED

**Date:** 2026-05-21
**Status:** RESOLVED — commit `23e3019`

**Problem:** Service/Tune-Up diagnostic flow has three photo steps (svc-1-filter, svc-3-coil, svc-8-run).
Skip choice buttons (e.g. "Dirty – Replace / Dirty – Can Clean / Looks Clean") were absent from the DOM
despite `PHOTO_SKIP_CONFIG` being confirmed present in the deployed JS bundle.

**Root cause:** Service/Tune-Up flow is rendered by `ServiceChecklist.tsx`, NOT `DiagnosticFlow.tsx`.
The `PHOTO_SKIP_CONFIG` block only exists in `DiagnosticFlow.tsx` and was never reached for
`complaint_type=service`. `ServiceChecklist.tsx` rendered `<PhotoSlot>` components with no skip UI at all.

**Fix (commit 23e3019):**
- Added `SVC_PHOTO_SKIP_CONFIG` (equivalent to DiagnosticFlow's PHOTO_SKIP_CONFIG) to `ServiceChecklist.tsx`
- Added `skipExpanded` state + reset `useEffect` per step
- Added skip choice button JSX inline in the photo step render path
- No DB changes needed — `step_id` values matched config keys exactly

**Key lesson:** When a diagnostic complaint_type routes through a separate component (ServiceChecklist vs DiagnosticFlow),
any UI enhancements added to DiagnosticFlow will silently not apply to that flow. Always check which component
renders for the target complaint_type before adding skip/override UI.

**Markets affected:** Both Houston and PK (shared component, same fix)
**Cross-reference:** `ServiceChecklist.tsx`, `DiagnosticFlow.tsx`, PHOTO_SKIP_CONFIG

---

## DEC-057 — PK models are stored as JSONB series array in pak_brands, not a separate table (2026-05-21)

**Date:** 2026-05-21

**Context:** During QA, needed to verify and update Gree inverter model data. Searched for
`pak_equipment_models` table — it does not exist. The `equipment_models` table only contains
US market records (Carrier, Trane, Lennox, etc.).

**How PK models are stored:**
PK brand + model data lives in the `pak_brands` table as a JSONB column called `series`.
Each row = one brand. `series` is an array of objects:

```json
[
  {
    "name": "Fairy Inverter",
    "type": "inverter",
    "refrigerant": "R-32",
    "tonnage_data": {
      "1.0": { "capacitors": {...}, "electrical": {...} },
      "1.5": { "capacitors": {...}, "electrical": {...} },
      "2.0": { "capacitors": {...}, "electrical": {...} }
    }
  }
]
```

**How the backend serves it (`models.py`):**
`GET /api/models/all` (X-Market: PK) explodes each series entry into a synthetic model record:
```python
"series_type": s.get("type", "non_inverter"),   # drives inverter badge in StepZeroPanel
"refrigerant": s.get("refrigerant", "R-22"),
"tonnage_data": tonnage_data,                    # drives auto-fill specs per tonnage
```

**The inverter badge rule:**
`StepZeroPanel.tsx` renders `<span>Inverter</span>` badge when `m.series_type === "inverter"`.
The `series_type` field comes directly from `pak_brands.series[].type`.
Set `type: "inverter"` in the pak_brands JSONB to show the inverter badge.

**To add a new PK model series:**
```sql
UPDATE pak_brands
SET series = series || '[{
  "name": "New Model Name",
  "type": "inverter",
  "refrigerant": "R-32",
  "tonnage_data": { "1.0": {...}, "1.5": {...}, "2.0": {...} }
}]'::jsonb
WHERE id = 'brand_id_here';
```

**After updating pak_brands:**
The browser's IndexedDB model cache (TTL 24h) must be cleared before new models appear:
```js
await indexedDB.deleteDatabase('snapai_models_pk');
location.reload(true);
```

**Cross-reference:** WA-26 (IndexedDB cache), `models.py` PK market branch, `StepZeroPanel.tsx`

---

## DEC-058 — ServiceChecklist must receive a getAuthHeaders callback, not pre-baked headers (2026-05-22)

**Date:** 2026-05-22

**Problem (BUG-034):** `ServiceChecklist.tsx` originally received `authHeaders: Record<string,string>` as a prop. This token was captured once when the technician selected the complaint type. Clerk JWTs expire in 60 seconds. Any service checklist session lasting longer than 60 seconds caused every subsequent step submission to return 401 "Invalid or expired session token".

**Fix:** Changed prop to `getAuthHeaders: () => Promise<Record<string,string>>`. Each fetch call inside ServiceChecklist now calls `const headers = await getAuthHeaders()` immediately before the request.

**Rule:** Any component that makes multiple authenticated API calls over a potentially long user session MUST receive a `getAuthHeaders` callback, NOT a pre-baked headers object. This applies specifically to:
- `ServiceChecklist.tsx` (service flow, 8 steps, can take 5+ minutes)
- Any future multi-step flow with long dwell time

**Pattern:**
```typescript
// assess/page.tsx — correct
const getAuthHeaders = useCallback(async (): Promise<Record<string, string>> => {
  const market = detectMarket();
  if (IS_DEV) return { ...DEV_HEADER, "X-Market": market };
  const token = await getToken();
  return token ? { Authorization: `Bearer ${token}`, "X-Market": market } : { "X-Market": market };
}, [getToken]);

<ServiceChecklist getAuthHeaders={getAuthHeaders} ... />

// ServiceChecklist.tsx — correct
const headers = await getAuthHeaders();  // called fresh per API call
const r = await fetch(`${API_URL}/api/...`, { headers: { ...headers, "Content-Type": "application/json" } });
```

**Commit:** `0140c83`

---

## DEC-059 — estimates table has NO updated_at column — omit from all INSERTs (2026-05-22)

**Date:** 2026-05-22

**Problem (BUG-035):** `_generate_service_estimate()` in `api/diagnostic.py` included `updated_at` in its INSERT INTO estimates statement. The `estimates` table does not have an `updated_at` column. The SQL error was caught by a `try/except Exception` block and logged, but the session was still marked `service_complete`. No estimate row was created.

**Fix:** Removed `updated_at` from both the column list and VALUES in the INSERT.

**Confirmed estimates table columns (verified 2026-05-22 via information_schema):**
```
id, assessment_id, company_id, report_token, report_short_id, options, selected_option,
total_amount, deposit_amount, markup_percent, status, viewed_at, approved_at,
stripe_payment_intent_id, contractor_pdf_url, homeowner_report_url, sent_via, sent_at,
actual_cost, accuracy_score, created_at, seasonal_modifier_pct
```
**No `updated_at`. No `updated_at`. No `updated_at`.** If you need to update a row, use `SET created_at` is wrong — just omit timestamps from UPDATE clauses entirely or add the column via migration first.

**Rule:** Before inserting into `estimates`, verify the column list against `information_schema.columns` if any doubt. Never assume `updated_at` exists.

**Commit:** `937b8c7`

---

## DEC-060 — POST /api/estimates/service does NOT exist — call onComplete directly after service_step_complete (2026-05-22)

**Date:** 2026-05-22

**Problem (BUG-036):** `ServiceChecklist.tsx` had a `generateServiceEstimate()` function that POSTed to `POST /api/estimates/service`. This endpoint was never implemented on the Railway backend. The OpenAPI spec at `/openapi.json` confirms it does not exist. The 405 Method Not Allowed response caused the service checklist to show an error and never navigate away.

**How service estimates actually work:**
1. Tech submits step 8 answer (svc-8-run) via `POST /api/diagnostic/session/{id}/answer`
2. Backend `_resolve_branch()` sees `generate_estimate: true` in svc-8-run branch_logic
3. Backend calls `_generate_service_estimate(db, assessment_id, company_id)` — creates estimate row in DB
4. Backend returns `{resolved: true, service_step_complete: true}` to frontend
5. Frontend should call `onComplete()` directly — no additional API call needed
6. `handleServiceComplete` in `assess/page.tsx` ignores the result and calls `router.push(/assessment/{assessmentId})`
7. `/assessment/{id}` page fetches `GET /api/estimates/{assessment_id}` to show the estimate

**Fix:** Removed `generateServiceEstimate()` entirely. After `service_step_complete`, build a summary from `findings` state and call `onComplete()` immediately.

**Rule:** There is no POST endpoint for service estimates. The estimate is auto-generated server-side. Frontend only needs to navigate. Do not add a POST /api/estimates/service endpoint unless the service estimate response format is redesigned.

**Available estimate-related POST endpoints (as of 2026-05-22):**
- `POST /api/estimates/fault-card` — generates fault card estimate from assessment
- `POST /api/estimates/{id}/refresh` — refreshes a draft estimate
- `POST /api/estimates/{id}/documents` — generates PDF documents
- `POST /api/estimates/{id}/send` — sends estimate to homeowner

**Commit:** `4db39be`

---

## DEC-061 — Restoring NTFS files truncated by Edit tool: use git cat-file blob (2026-05-22)

**Date:** 2026-05-22

**Problem:** The Edit tool (DEC-027) truncated `api/diagnostic.py` from 1646 to 1602 lines when removing `updated_at` from an INSERT. The truncation happened even though the target string had no non-ASCII chars — the file itself does, elsewhere. SyntaxError at line 1594 confirmed the tail was missing.

**Recovery procedure:**
```bash
# Step 1 (Linux sandbox — read-only, OK on NTFS mount):
cd '/sessions/.../mnt/Personal Claude/ScopeSnapAI/scopesnap-api'
git ls-tree HEAD api/diagnostic.py
# → outputs: 100644 blob <sha>  api/diagnostic.py

git cat-file blob <sha> | wc -l
# → confirms correct line count

# Step 2: Write a Python script to the outputs dir (not NTFS):
# Script reads blob bytes from git cat-file, applies the fix via .replace(), writes to NTFS target.
# Run it via Desktop Commander (Windows Python subprocess).
```

**Recovery script pattern:**
```python
import subprocess
r = subprocess.run(["git", "cat-file", "blob", sha], cwd=repo_dir, capture_output=True)
content = r.stdout  # raw bytes from HEAD
fixed = content.replace(old_bytes, new_bytes, 1)
with open(target_path, "wb") as f:
    f.write(fixed)
# Verify:
import ast
ast.parse(fixed.decode("utf-8"))  # must not raise
```

**Rule:** If `ast.parse` or `wc -l` after a Python-script edit shows truncation: `git ls-tree HEAD <file>` → `git cat-file blob <sha>` → restore + patch in one Python script run from Desktop Commander.

**Note:** `git checkout HEAD -- <file>` fails on NTFS mount (Operation not permitted). The cat-file → Python write approach is the only reliable restore path from the Linux sandbox.


---

## DEC-062 — Every photo step in ServiceChecklist needs a SVC_PHOTO_SKIP_CONFIG entry (2026-05-22)

**Date:** 2026-05-22

**Problem:** `svc-4-drain` (Step 4 — Drain flush confirmation photo) had no entry in `SVC_PHOTO_SKIP_CONFIG` in `ServiceChecklist.tsx`. A photo input step with no skip config renders only the camera upload area. There is no alternative path — no skip link, no manual condition buttons. Result: QA testers and field technicians with a broken camera are completely blocked at step 4. The only escape was a React fiber hack that bypassed `submitStep()`, which zeroed out `findings` and left the Estimate Builder empty.

**Root cause discovery:** During QA, step 4 had to be advanced using a React fiber `onComplete` injection. This bypassed the entire `findings` accumulation in `ServiceChecklist`. The Estimate Builder showed no line items. The real fix is to add proper skip options so the normal code path runs.

**Backend already correct:** `svc-4-drain` in `diagnostic_questions.branch_logic_jsonb` already had three working branches:
- `"flushed"`: routes to svc-5-terminals + adds `flush_tablet` finding ($12–$18)
- `"skipped"`: routes to svc-5-terminals, no finding (drain flush not possible)
- `"any"`: wildcard, routes to svc-5-terminals + adds flush_tablet finding

**Frontend fix:** Added `"svc-4-drain"` to `SVC_PHOTO_SKIP_CONFIG` with `type: "choice"`:


**Rule:** Every photo step in ServiceChecklist MUST have an entry in SVC_PHOTO_SKIP_CONFIG. The current coverage (post-fix):
| Step | Step ID | Skip Type | Branches |
|------|---------|-----------|---------|
| 1 | svc-1-filter | choice | replace / dirty / clean |
| 3 | svc-3-coil | choice | heavily_blocked / dirty / clean |
| 4 | svc-4-drain | choice | flushed / skipped |
| 8 | svc-8-run | simple | skipped |

Steps 2, 5, 6, 7 are not photo steps — they use `reading` or `multi` input types, which always have explicit submit buttons.

**Checklist for adding any new service photo step:**
1. Add row to `diagnostic_questions` with `input_type = 'photo'`
2. Add branch_logic_jsonb with `"skipped"` and `"any"` entries routing to the next step
3. Add entry to `SVC_PHOTO_SKIP_CONFIG` in `ServiceChecklist.tsx` with appropriate choices
4. If step adds a service finding, map the correct `branch_key` to the `line_item_code`

**Why the drain flush photo is always completable:** Unlike diagnostic photos (filter/coil condition — tech visually assesses), the drain flush is a task the tech always performs (or decides not to). The photo is documentation only. "Drain Flushed" / "Could Not Flush" are always valid answers.

**Commit:** `3f09c02` — fix(service-checklist): add skip config for svc-4-drain

