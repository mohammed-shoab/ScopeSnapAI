# SnapAI — Key Architectural Decisions

> This file records decisions made during development that have lasting impact on how the codebase works.
> Future AI sessions: read this before proposing architecture changes or writing migrations.
>
> Last updated: 2026-05-27 — DEC-081 through DEC-093 added (BUG numbering, promote process, Vercel team URL, single Vercel project, Next.js DOM cache, CSS text-transform innerText, StepZeroPanel JWT, OCR waterfall, A/B test localStorage, audit-before-implement, git config, CDP timeout, Clerk cross-env sessions). WA-30 through WA-47 added to TECH_STACK.md.
> Previously updated: 2026-05-24 (Stage 7 Staging E2E QA COMPLETE. DEC-070 ACTIVE. Houston full flow PASS (rpt-e198935c USD estimate), PK staging backend PASS (environment:staging, R-410A pressure-targets). | DEC-080 added — Stage 6 Vercel staging domain-level gitBranch rewire; DEC-067 marked SUPERSEDED. | Previously: DEC-071 added -- Stripe test-mode GAP from Stage 2 cost audit. | DEC-065 body added — never commit package-lock.json; DEC-066 added — stamp estimates.market at creation; merge conflict in DEC-062/063/064 resolved; DEC-063, DEC-064 added — /api/models/all response shape; pak_operating_targets is PSI table)

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

**Current revision:** 034 (as of 2026-05-24 Stage 5 parity sync)

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

---

## DEC-063 — `/api/models/all` response shape is `{models:[...]}`, not a plain array (2026-05-22)

**Date:** 2026-05-22

**Context:** During Phase 2 backend health checks, code used `Array.isArray(data)` to parse the `/api/models/all` response. This returned `false` (the response is `{"models": [...]}`, an object), causing model counts to show as 0 even though the endpoint returned 200 OK with valid data.

**Correct parse pattern:**
```javascript
const resp = await fetch(`${base}/api/models/all`, {headers: {'X-Market': 'PK'}});
const data = await resp.json();
const models = data.models || []; // NOT: Array.isArray(data) ? data : data.models
```

**Also confirmed:** `/api/brands` does NOT exist — returns 404. The only model data endpoint is `/api/models/all`.

**Impact:** Any code, test, or script that fetches brand/model data from Railway must handle the `{models:[...]}` wrapper. The existing `getBrands()` / `searchModels()` functions in `lib/modelCache.ts` handle this correctly.

---

## DEC-064 — PK PSI thresholds are in `pak_operating_targets`, not `pak_diagnostic_questions` (2026-05-22)

**Date:** 2026-05-22

**Context:** QA skill Phase 2d spec said to check `pak_diagnostic_questions` for PSI high_min thresholds. The table `pak_diagnostic_questions` does NOT exist in production Supabase — querying it returns `ERROR: relation does not exist`.

**Actual table:** `pak_operating_targets`

**Schema confirmed:**
```sql
SELECT refrigerant, ambient_c, suction_min_psi, suction_max_psi, discharge_min_psi, discharge_max_psi
FROM pak_operating_targets
ORDER BY refrigerant, ambient_c;
```

**Verified values (2026-05-22):**
- R-410A at 40°C: suction 125–145 PSI, discharge 325–370 PSI ✅
- R-32 at 40°C: suction 120–140 PSI, discharge 365–410 PSI ✅
- R-22 at 45°C: suction 78–88 PSI ✅

`suction_max_psi` is the upper normal bound — readings above this trigger a "high pressure" fault. These match QA spec requirements.

**Impact:** Any migration or data patch to PK PSI thresholds must target `pak_operating_targets`. The QA skill Phase 2d check must query `pak_operating_targets`, not `pak_diagnostic_questions`.

---

## DEC-062 — Every photo step in ServiceChecklist needs a SVC_PHOTO_SKIP_CONFIG entry (2026-05-22)

**Date:** 2026-05-22

**Problem:** `svc-4-drain` (Step 4 — Drain flush confirmation photo) had no entry in `SVC_PHOTO_SKIP_CONFIG`. A photo step with no skip config shows only the camera upload area — no skip link, no manual condition buttons. QA testers and field techs with a broken camera are completely blocked. During QA, step 4 was bypassed via a React fiber `onComplete` injection, which skipped `submitStep()` entirely and zeroed `findings`, leaving the Estimate Builder empty.

**Root cause:** SVC_PHOTO_SKIP_CONFIG in ServiceChecklist.tsx had entries for steps 1, 3, 8 but not step 4. The backend already handled `flushed`, `skipped`, and `any` branches for svc-4-drain — the fix was frontend-only.

**Fix (commit 3f09c02):** Added choice-type skip config for svc-4-drain:
- "Drain Flushed" → branch_key: flushed → adds flush_tablet finding ($12–$18) → routes to svc-5-terminals
- "Could Not Flush" → branch_key: skipped → no finding → routes to svc-5-terminals

**Rule — SVC_PHOTO_SKIP_CONFIG coverage (post 3f09c02):**
| Step | Step ID | Skip Type | Choices |
|------|---------|-----------|---------|
| 1 | svc-1-filter | choice | Dirty-Replace / Dirty-Can Clean / Looks Clean |
| 3 | svc-3-coil | choice | Heavily Blocked / Dirty / Clean |
| 4 | svc-4-drain | choice | Drain Flushed / Could Not Flush |
| 8 | svc-8-run | simple | skipped |

Steps 2, 5, 6, 7 use reading/multi input types — they always have a submit button; no skip needed.

**Checklist for any new service photo step:**
1. Add `diagnostic_questions` row with `input_type = 'photo'`
2. Add `branch_logic_jsonb` with `"skipped"` and `"any"` entries routing to next step
3. Add entry to `SVC_PHOTO_SKIP_CONFIG` in ServiceChecklist.tsx with appropriate choices
4. If step generates a finding, map the branch_key to the correct line_item_code

**Commit:** `3f09c02`
## DEC-067 — Vercel staging project deploys `main` branch, not `staging` branch (2026-05-22) — **SUPERSEDED 2026-05-24 by DEC-080**

**Date:** 2026-05-22 | **Status:** SUPERSEDED 2026-05-24 — see DEC-080

**Context:** During the staging fix session, it was discovered that the `scopesnap-web-staging` Vercel project is configured with `main` as its Production branch. The `staging` git branch was NOT linked to the Vercel staging project. All staging Vercel deployments showed source branch = `main`.

**SUPERSEDED:** Stage 6 (2026-05-24) fixed this by setting `gitBranch: "staging"` at the domain level for all 3 staging domains via the Vercel domain PATCH API (`PATCH /api/v9/projects/{id}/domains/{domain}`). All staging domains now serve the `staging` git branch. See DEC-080 for full details.

**Historical note:** Vercel's project-level `link.productionBranch` cannot be changed via the API (schema whitelist rejects it). The domain-level `gitBranch` override achieves the same practical outcome: pushing to `staging` branch triggers new deployments that all 3 staging domains serve.

---

## DEC-068 — DNS for mainnov.tech is in Hostinger, NOT Cloudflare (2026-05-22)

**Date:** 2026-05-22

**Context:** The `.staging_secrets.txt` file contains a comment saying to add DNS records in Cloudflare (dash.cloudflare.com) for the `mainnov.tech` zone. This is WRONG. The actual DNS for `mainnov.tech` is managed in Hostinger under account `mshoabarabi@gmail.com` at `hpanel.hostinger.com`.

**Evidence:** Hostinger nameservers (`ns1.dns-parking.com` / `ns2.dns-parking.com`) are on the domain. No Cloudflare account for `ds.shoab@gmail.com` has this domain.

**CNAME records updated (2026-05-22):**
- `staging.snapai.mainnov.tech` CNAME → `e08b930de4517e81.vercel-dns-017.com` (TTL 14400)
- `pk-staging.snapai.mainnov.tech` CNAME → `e08b930de4517e81.vercel-dns-017.com` (TTL 14400)

**Old target:** `cname.vercel-dns.com` (Vercel still accepts this but recommends the new one)
**New target:** `e08b930de4517e81.vercel-dns-017.com`

**Rule:** Any future DNS changes for mainnov.tech go to Hostinger hpanel under `mshoabarabi@gmail.com`.

---

## DEC-069 — StagingBanner is RSC in app/(app)/layout.tsx — visible on authenticated routes only (2026-05-22)

**Date:** 2026-05-22

**Context:** The `StagingBanner` component is a React Server Component (no `"use client"` directive) placed in `app/(app)/layout.tsx` — the layout for authenticated/app routes. It is NOT in the root `app/layout.tsx`.

**Consequence:**
- Public pages (homepage `/`, `/sign-in`, etc.) do NOT show the staging banner
- Authenticated pages (`/assess`, `/reports`, `/settings`, etc.) DO show the banner when `NEXT_PUBLIC_ENV === "staging"`
- This is correct by design — the banner's purpose is to prevent confusion when using the app in staging mode

**Verification:** Navigating to `scopesnap-web-staging.vercel.app/assess` redirects to `/sign-in` (auth guard working). The banner appears after sign-in on any `(app)` route.

**env var reading:** Because `StagingBanner` is RSC, `process.env.NEXT_PUBLIC_ENV` is read at server runtime — NOT baked into the client JS bundle. This is why the string "staging" does NOT appear in the downloaded JS chunks (expected, not a bug).

---

## DEC-065 — Never commit `scopesnap-web/package-lock.json` (2026-05-22)

**Date:** 2026-05-22

**Problem:** Commit `78d0fff` accidentally included `scopesnap-web/package-lock.json` (7,954 lines).
This broke every Vercel build immediately — `npm ci` failed in ~8 seconds because the lockfile
was present but did not match the installed `node_modules`. Vercel showed "Error" with no detail.
Seven consecutive builds failed between `78d0fff` and `a908eac`.

**Root cause:** `package-lock.json` was generated locally and accidentally staged with `git add -A`.
The repo intentionally has NO lockfile since commit `c2eac8d` (force Node 18, March 2026).

**Fix:** `git rm scopesnap-web/package-lock.json` in commit `a908eac`. Builds resumed immediately.

**Detection signal:** Vercel build duration under 20 seconds = `npm ci` failed. Normal build = 1–2 minutes.
Check for a spurious `package-lock.json` addition in the diff whenever a build fails fast.

**Rule:** `scopesnap-web/package-lock.json` must NEVER be committed. Add it to `.gitignore` if needed.
Confirm with `git status --short | grep package-lock` before every commit. If it appears, `git rm` it.

**Impact:** DEC-065 is also in `.gitignore` — verify the .gitignore rule is present after any repo reset.

---

## DEC-066 — Stamp `estimates.market` at creation — never derive from viewer's hostname (2026-05-22)

**Date:** 2026-05-22

**Problem (BUG-037):** Pakistan estimates viewed on the Houston domain (`snapai.mainnov.tech`)
displayed USD amounts instead of PKR. Root cause: `ReportClient.tsx` had a module-level
`function fmt(n)` that called `formatCurrency(n)` with no `market` argument. `formatCurrency`
defaulted to the caller's hostname (Houston = US), so PK estimates always showed USD when
opened from any Houston URL.

**Decision:** Stamp `estimates.market` (VARCHAR(2) NOT NULL DEFAULT 'US') at the moment the
estimate is created — not at the moment it is viewed. The stored market value is the source
of truth for currency formatting in reports. The viewer's hostname is irrelevant.

**Implementation:**
- Migration 034: `ALTER TABLE estimates ADD COLUMN market VARCHAR(2) NOT NULL DEFAULT 'US'`
- `fault_estimate.py` and `diagnostic.py` both write `market = tables.market` at INSERT time
- `reports.py` returns `report.market` to the frontend
- `ReportClient.tsx`: `reportMarket = (report as any).market` (from DB, not hostname)
- `const fmt = (n: number) => formatCurrency(n, reportMarket)` — component-level, not module-level

**Rule:** ANY code that formats currency in a report or estimate display MUST read from
`report.market` (or `estimate.market`), never from `detectMarket()` at display time.
The market of an estimate is fixed at creation — it does not change when a contractor
switches contexts.

**Cross-reference:** BUG-037, migration 034, DEC-065, TECH_STACK WA-34.

---

## DEC-070 — Staging-first change workflow becomes canonical after Stage 7 sign-off (2026-05-23)

**Date:** 2026-05-23

**Context:** Through 2026-05-19 to 2026-05-22 the staging environment was set up (DEC-014) but operated as a partial mirror of production — Vercel staging tracks `main` instead of `staging` (DEC-067), the staging Supabase DB drifted from production (Alembic 025 vs prod 034), and changes have been pushed directly to `main` with verification on production. This is the opposite of what staging is for. Going forward, every change must pass through staging first, with staging maintained as a true mirror of production at all times.

**Decision:** Adopt the staging-first 7-step workflow defined in `WORKFLOW.md` as the canonical change process. The four absolute rules:

1. **Never edit code directly on `main`** without going through `staging` first
2. **Never push migrations to prod** that haven't run on staging first
3. **Never add env vars to prod** without mirroring them on staging
4. **Never test on production** — testing happens on staging; production is for real users

**Rationale:** Production is now beta-facing (5 testers incoming via LinkedIn). Every prod bug is a tester churn risk. Staging exists to absorb that risk by catching bugs against an environment that is byte-for-byte identical to production except for data isolation, test keys, and a visible amber banner. The additional cost is sleeping-mode-only on Railway (free if staging stays under $5/mo combined) and a separate Supabase project (within the 2-project free tier cap).

**Rule:** All future changes follow the 7-step workflow in `WORKFLOW.md` Section 4. Exception: emergency hotfix path (`WORKFLOW.md` Section 9) bypasses staging only for genuine production emergencies, with mandatory 24-hour follow-up sync to bring staging in line with main, plus a retrospective DEC entry explaining what slipped through normal QA.

**Activation:** ACTIVE — Stage 7 (Staging End-to-End QA) signed off 2026-05-24. This workflow is now mandatory. — at which point staging is verified to be a true mirror of production, the Vercel staging project deploys the `staging` branch, and a full QA pass on staging matches a full QA pass on production. Transitional rules (DEC-004 `/tmp` clone, DEC-013 no git stash from sandbox, DEC-022 Desktop Commander for git ops) remain in force for AI git operations — these are environment constraints, not workflow gates.

**Cross-references:**
- `C:\Users\dell\My Drive\Personal Claude\ScopeSnapAI\WORKFLOW.md` — full protocol with worked examples
- DEC-014 — staging environment architecture
- DEC-015 — dual keepalive crons (Sun + Wed)
- DEC-023 / DEC-051 — never set NEXT_PUBLIC_ENV=staging on prod
- DEC-066 — DNS in Hostinger, not Cloudflare
- DEC-067 — Vercel staging deployed main (SUPERSEDED 2026-05-24 by DEC-080)
- DEC-068 — DNS for mainnov.tech in Hostinger (account `mshoabarabi@gmail.com`)
- DEC-069 — StagingBanner is RSC, auth-only

**File created:** `C:\Users\dell\My Drive\Personal Claude\ScopeSnapAI\WORKFLOW.md` (2026-05-23)



---

## DEC-072 -- BUG-040: CAST(:options AS jsonb) required for JSONB column INSERT in raw SQLAlchemy (2026-05-23)

**Date:** 2026-05-23

**Problem:** Service/Tune-Up flow completed (`service_complete` status) but never created an estimate row. Contractor opened the assessment page and saw an empty estimate.

**Root cause:** `_generate_service_estimate()` in `api/diagnostic.py` ran a raw SQL INSERT with `:options` parameter bound to a Python list, targeting a JSONB column. SQLAlchemy with PostgreSQL requires an explicit `CAST(:options AS jsonb)` in the raw SQL string for JSONB columns. Without it, the INSERT executes and appears to succeed but the JSONB binding fails silently — no Python exception, no rollback, no row created.

**Fix:** Changed the INSERT to use `CAST(:options AS jsonb)` for the options parameter.

**Rule:** Whenever writing raw SQLAlchemy INSERT or UPDATE with parameters bound to JSONB columns, ALWAYS include `CAST(:param AS jsonb)` in the SQL string. Never rely on SQLAlchemy type inference for JSONB. Pass the value as `json.dumps(obj)` in the params dict.

**File:** `api/diagnostic.py` — `_generate_service_estimate()` function

**Detection pattern:** If an INSERT appears to run without error but no row appears, check for JSONB columns in the target table and verify CAST usage.

---

## DEC-073 -- BUG-041: NEXT_PUBLIC_ENV=staging on production Vercel is a recurring trap (2026-05-23)

**Date:** 2026-05-23

**Problem:** Amber "STAGING" banner visible on pk.snapai.mainnov.tech (BUG-041). This is a re-occurrence of BUG-031 (first found 2026-05-21, fixed 2026-05-21, re-occurred 2026-05-23).

**Root cause:** When staging environment was configured/reconfigured, `NEXT_PUBLIC_ENV=staging` was set in the production Vercel project's environment variables under "All Environments". `StagingBanner.tsx` reads `process.env.NEXT_PUBLIC_ENV === "staging"` — baked into the bundle at build time. Even a correct source tree will show the banner if this env var is wrong.

**Fix:** Set `NEXT_PUBLIC_ENV=production` in Vercel production project → Settings → Environment Variables → All Environments. Trigger a new deployment. Verify the new deployment ID appears on both domains.

**Prevention rules (CRITICAL — this bug has occurred twice):**
1. After ANY Vercel environment variable changes on ANY project, immediately open pk.snapai.mainnov.tech and check for the amber STAGING banner
2. Before triggering any new Vercel deployment, verify NEXT_PUBLIC_ENV in the PRODUCTION project is either absent or set to "production" — NEVER "staging"
3. When configuring staging project env vars, use "Preview" environment scope only — never "All Environments" which can bleed into production

**Cross-references:** DEC-051 (BUG-031 original), DEC-023 (rule: NEVER set NEXT_PUBLIC_ENV=staging on production Vercel)

---

## DEC-074 -- Stage 4 audit: Vercel staging custom domains are Preview branch deployments, not Production env builds (2026-05-23)

**Date:** 2026-05-23 (Stage 4 Staging Isolation Audit)

**Finding:** `staging.snapai.mainnov.tech` and `pk-staging.snapai.mainnov.tech` are configured as "git branch" custom domains in the `scopesnap-web-staging` Vercel project, pointing to the `staging` git branch. They are served by the **Preview** deployment of that branch -- NOT by the Production environment deployment.

**Consequence:** When NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY was corrected from pk_live_ to pk_test_ on the staging Vercel project and a "Production environment" redeploy (deployment CXM5WEJMt) was triggered, `staging.snapai.mainnov.tech` still served the old pk_live_ key. The Production redeploy built a new Production environment deployment -- which is not what staging custom domains serve.

**Fix pattern:** Deployments page → filter by branch "staging" → find latest Preview deployment → three-dot menu → Redeploy (no cache). New Preview deployment `5HJ2piG8A` was picked up by both staging custom domains. Confirmed pk_test_ on both.

**Rule:** Any env var change on `scopesnap-web-staging` that needs to reach `staging.snapai.mainnov.tech` / `pk-staging.snapai.mainnov.tech` MUST be followed by a staging branch Preview redeploy, not a Production environment redeploy.

**DNS confirmation:** Staging custom domains CNAME target: `e08b930de4517e81.vercel-dns-017.com` (different from production `e9353dffc8a96116.vercel-dns-017.com` -- isolated at DNS level).

---

## DEC-075 -- Stage 4 audit: Railway staging had sk_live_ CLERK_SECRET_KEY (production Clerk secret key) (2026-05-23)

**Date:** 2026-05-23 (Stage 4 Staging Isolation Audit)

**Finding:** Railway staging service (`scopesnap-api-staging.up.railway.app`) had `CLERK_SECRET_KEY` set to `sk_live_...` -- the production Clerk secret key. Critical cross-contamination: staging backend was validating tokens against the production Clerk app.

**Impact:** With sk_live_ on staging, any Clerk JWT issued by the staging app (pk_test_ key) would fail validation on the staging backend. Conversely, any pk_live_ token from production would pass validation on staging -- a security boundary violation allowing production user sessions to authenticate on the staging backend.

**Fix:** Replaced with `sk_test_...` from staging Clerk app (firm-chamois-61, Development mode).

**Prevention:** After any new Railway staging service creation or cloning from production, audit ALL environment variables against the key prefix convention: sk_live_ = production only, sk_test_ = staging only. Never copy Railway env vars from production to staging without replacing all sk_live_ keys with sk_test_ equivalents.

---

## DEC-076 -- Stage 4 audit: pk.snapai.mainnov.tech served pk_test_ due to stale ISR edge cache (2026-05-23)

**Date:** 2026-05-23 (Stage 4 Staging Isolation Audit)

**Finding:** `pk.snapai.mainnov.tech` was returning `pk_test_...` as the Clerk publishable key in its HTML, despite the `scope-snap-ai` production Vercel project having `pk_live_...` in `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` for All Environments.

**Investigation (ruled out):**
- Browser cache: fresh tab showed same pk_test_ (transferSize 20,986 bytes = no cache)
- Separate Vercel project: pk.snapai.mainnov.tech is registered only in scope-snap-ai Production environment
- Code-level market detection: layout.tsx has no host-header switching, ClerkProvider has no explicit publishableKey prop
- Multiple env var values: Vercel shows single pk_live_ entry for All Environments
- PK-specific env var override: none found

**Root cause (best explanation):** Stale ISR / edge cache specific to pk.snapai.mainnov.tech's CNAME endpoint (`e9353dffc8a96116.vercel-dns-017.com`). The sibling domain `snapai.mainnov.tech` was correctly serving pk_live_ from the same Vercel project, suggesting the stale value was cached at the edge node serving that specific domain.

**Fix:** Fresh production redeploy WITHOUT build cache -- new deployment `CwjgWfNBi` (2m 54s, Production, Ready Latest, domains: snapai.mainnov.tech +3). After build, pk.snapai.mainnov.tech confirmed pk_live_.

**Lesson:** After any Vercel env var change, verify BOTH production domains independently. ISR edge cache can serve stale values on one CNAME endpoint while the other is fresh.

---

## DEC-077 -- Clerk key prefix is the authoritative environment signal for all four SnapAI domains (2026-05-23)

**Date:** 2026-05-23 (Stage 4 Staging Isolation Audit)

**Convention confirmed:**
- `pk_live_` / `sk_live_` = production Clerk app (scope-snap-ai Vercel project, Railway production service)
- `pk_test_` / `sk_test_` = staging Clerk app (firm-chamois-61, Development mode; scopesnap-web-staging Vercel project, Railway staging service)

**Note on NEXT_PUBLIC_* and render time:** `data-clerk-publishable-key` in the HTML is set by the Next.js server at request time (reflecting the NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY env var from the Vercel environment). This means it can reflect stale ISR cache values (see DEC-076) even when the Vercel project shows the correct env var. A no-cache redeploy flushes this.

**Final verified state post-Stage-4-audit (2026-05-23):**

| Domain | Clerk key prefix | Status |
|--------|-----------------|--------|
| snapai.mainnov.tech | pk_live_ | PASS |
| pk.snapai.mainnov.tech | pk_live_ | PASS (was pk_test_ pre-fix; fixed by redeploy CwjgWfNBi) |
| staging.snapai.mainnov.tech | pk_test_ | PASS (was pk_live_ pre-fix; fixed by Preview redeploy 5HJ2piG8A) |
| pk-staging.snapai.mainnov.tech | pk_test_ | PASS |

**All other Stage 4 dimensions:**
- Supabase: prod project `quqrvnoguofbjacrxcim`, staging `pqmgveqkuckbvyygsilk` -- isolated, no data overlap
- Clerk: prod app (pk_live_) vs staging app firm-chamois-61 (pk_test_) -- isolated
- R2: prod bucket `scopesnap-uploads`, staging bucket `scopesnap-uploads-staging` -- isolated
- DNS: staging CNAME `e08b930de4517e81.vercel-dns-017.com`, prod CNAME `e9353dffc8a96116.vercel-dns-017.com` -- different endpoints
- Sentry: `production` environment filter (8+ issues, SNAPAI-API-P/F/S/Y/X/W/V/T) vs `staging` filter (1 issue, SNAPAI-API-Z) -- isolated, no cross-contamination


---

## DEC-078 -- CSP must include maps.googleapis.com and maps.gstatic.com in script-src and connect-src (Stage 3 Google Maps Integration -- 2026-05-23)

**Date:** 2026-05-23 (Stage 3 Google Maps Integration)

**Context:** `HoustonAddressAutocomplete` injects a `<script src="https://maps.googleapis.com/maps/api/js?...">` tag at runtime. Without explicit CSP allowances the browser blocks the script before it executes.

**Decision:** `next.config.js` CSP headers must include:
- `script-src`: `https://maps.googleapis.com https://maps.gstatic.com`
- `connect-src`: `https://maps.googleapis.com`

**Commit:** `42e692b` (next.config.js)

**Note:** Code comment in `next.config.js` mistakenly labels this DEC-076 (that number was taken by the Stage 4 staging isolation audit). Canonical reference is DEC-078.

---

## DEC-079 -- Service Worker must passthrough maps.googleapis.com and maps.gstatic.com to avoid opaque-response blocking (Stage 3 Google Maps Integration -- 2026-05-23)

**Date:** 2026-05-23 (Stage 3 Google Maps Integration)

**Context:** The SnapAI PWA Service Worker (`public/sw.js`) intercepts all fetch requests. For cross-origin `<script>` requests that fall through to the navigation handler, the SW calls `fetch(event.request)` which returns an **opaque response**. Browsers cannot execute scripts from opaque responses -- `script.onerror` fires despite an HTTP 200 from the server.

**Root cause chain:**
1. `HoustonAddressAutocomplete` injects `<script src="https://maps.googleapis.com/...">`
2. SW intercepts the script fetch (not matched by API or static-asset rules)
3. Navigation fallback calls `fetch(event.request)` -- opaque response returned
4. Browser: opaque response cannot be executed as a script -- `script.onerror` fires
5. Component: `loadError = true` -- renders `PlainInput` fallback (no autocomplete)

**Fix:** Add `maps.googleapis.com` and `maps.gstatic.com` to the third-party passthrough block in `sw.js` (alongside posthog, clerk, railway). These hostnames now get `event.respondWith(fetch(event.request)); return;` -- bypassing the opaque-response path entirely.

**Commit:** `a88c93a` (public/sw.js)

**Diagnostic proof:** Unregistering the SW via `navigator.serviceWorker.getRegistrations().then(...)` caused `google.maps.places` to load successfully (googleDefined: true, placesLoaded: true). Re-registering with the passthrough fix confirmed the same result with SW active.

**Note:** Code comment in `sw.js` mistakenly labels this DEC-077 (that number was taken by the Stage 4 staging isolation audit). Canonical reference is DEC-079.

**Future work:** `google.maps.places.Autocomplete` is deprecated for new customers as of March 1, 2025 (not discontinued -- Google shows a console warning on every load). Future migration to `google.maps.places.PlaceAutocompleteElement` required before Google discontinues the old API. No timeline announced.

**Side issue found (BUG-042):** Address field placeholder shows wrong text. Root cause: the `t()` i18n translation function is returning an error string for that key. Non-blocking -- autocomplete works correctly; placeholder only shows when field is empty.


---

## DEC-080 — Stage 6: Vercel staging domains rewired to `staging` branch via domain-level gitBranch (2026-05-24) — SUPERSEDES DEC-067

**Date:** 2026-05-24 (Stage 6 Vercel Staging Branch Rewire)

**Problem (DEC-067):** `scopesnap-web-staging` Vercel project had `main` as its Production branch. All staging Vercel deployments were sourced from `main`, not from the `staging` git branch.

**Root cause of difficulty:** Vercel's API does not expose `link.productionBranch` as a patchable field. `PATCH /api/v9/projects/{id}` with `productionBranch`, `link`, or `gitBranch` in the body returns `"should NOT have additional property"`. This applies to all API versions (v1, v7, v8, v9, v10). The Vercel UI Git settings page also does not expose a Production Branch input field in the current UI version. POST to `/link` returns 200 but does not change the branch.

**Solution:** Set `gitBranch: "staging"` at the **domain level** for all 3 staging domains via:
```
PATCH /api/v9/projects/{projectId}/domains/{domainName}
Body: { "gitBranch": "staging" }
```
Used browser-session-authenticated calls (relative URL from within vercel.com tab, `credentials: 'include'` automatic).

**Domains updated:**
| Domain | gitBranch set to |
|--------|-----------------|
| `staging.snapai.mainnov.tech` | `staging` |
| `pk-staging.snapai.mainnov.tech` | `staging` |
| `scopesnap-web-staging.vercel.app` | `staging` |

**Verification:**
- Push to `staging` branch (commit `71bc7fea`) → Vercel deployment `dpl_Gm5CkDDoFbA8CHCsM9ksETynCuFo` fired, `state=READY`, `branch=staging` ✅
- Push to `main` branch (commit `ebe82f6c`) → Production project `prj_SQgShjdRuT2cmhjgL45QMVGP8CNs` got production deploy (correct — does NOT touch staging domains) ✅
- Staging backend: `{"status":"ok","db":"connected","environment":"staging"}` ✅
- Production backend: `{"status":"ok","db":"connected","environment":"production"}` ✅

**Known limitation (acceptable):** The `scopesnap-web-staging` Vercel project STILL builds a `target: "production"` deployment from `main` pushes (because `link.productionBranch` cannot be changed). However, since all 3 domains have `gitBranch: "staging"`, those `main`-sourced builds are NOT served on any domain. They sit as orphaned Production builds. The domain-level override fully controls what each staging domain serves.

**Rule for future work:** When pushing to `staging` branch, Vercel automatically builds and deploys to all 3 staging domains. This is the intended behavior. Do NOT change the domain `gitBranch` settings back to `main` or remove them.

**Git state at Stage 6 sign-off (2026-05-24):**
- `main` HEAD: `ebe82f6cb9e7727f99ea765088d65515f6d6da93` (empty Stage 6 verification commit)
- `staging` HEAD: `71bc7fea166fa9a7526215c9475ab97b9abd8fc4` (empty Stage 6 verification commit)
- Both have one empty `--allow-empty` verification commit; no functional code changes

**Cross-references:** DEC-067 (superseded), DEC-074 (Vercel staging = Preview deployments), DEC-070 (staging-first workflow)

---

## DEC-081 — BUG numbering must be checked against git log before assigning (2026-05-27)

**Discovery:** BUG-034 was assigned to two separate bugs. The original BUG-034 is the ServiceChecklist 401 token-expiry fix (commit `0140c83`, 2026-05-22). The nameplate OCR fix was incorrectly labeled BUG-034 in commits — the canonical number is **BUG-045**.

**Rule:** Before labeling any new bug, run:
```bash
git log --oneline --all | grep -i "BUG-0" | sort
```
Take the highest number + 1. Never re-use a number. The commit message mismatch creates permanent confusion in git history and brain files.

**Cross-reference:** ACTIVE_TASKS.md — "Note on bug numbering" section under BUG-045.

---

## DEC-082 — `scripts/promote-to-prod.sh` does not exist — use manual git merge (2026-05-27)

**Discovery:** PROJECT_BRAIN.md and the DEC-070 workflow both reference `scripts/promote-to-prod.sh <files>`. This script was never created. Running it produces "No such file or directory".

**Correct manual promote process (run from /tmp clone):**
```bash
cd /tmp/snapai_tmp/scopesnap-web
git config user.email "ds.shoab@gmail.com"
git config user.name "Shoab"
git checkout main
git pull origin main          # sync before merge
git merge staging --no-ff -m "merge(prod): <description> — QA verified YYYY-MM-DD both markets"
git push origin main
```
Vercel auto-deploys `snapai.mainnov.tech` and `pk.snapai.mainnov.tech` on push to `main`.

**Impact:** Update any documentation that references the script. The manual process is the source of truth.

---

## DEC-083 — Vercel team URL is `mohammed-shoabs-projects-7844119e`, NOT `mohammed-shoabs-projects` (2026-05-27)

**Discovery:** Navigating to `vercel.com/mohammed-shoabs-projects/scopesnap-web/deployments` returns 404. The correct team slug includes the random suffix.

**Correct URLs:**
- Dashboard: `https://vercel.com/mohammed-shoabs-projects-7844119e`
- Deployments: `https://vercel.com/mohammed-shoabs-projects-7844119e/scopesnap-web-staging/deployments`
- Specific deploy: `https://vercel.com/mohammed-shoabs-projects-7844119e/scopesnap-web-staging/<deployId>`

**Rule:** Always use the full team slug with the `-7844119e` suffix.

---

## DEC-084 — Single Vercel project `scopesnap-web-staging` serves ALL four domains (2026-05-27)

**Discovery:** The reference to `scope-snap-ai` as the production Vercel project in PROJECT_BRAIN.md is stale. The live push of `main` branch deployed via `scopesnap-web-staging` project and confirmed `snapai.mainnov.tech` as the target domain.

**Actual setup:**
- Project: `scopesnap-web-staging` (ID: `prj_vq1rWfPN9tD3k82OLFjfIxmNdULc`)
- `main` branch → Production-env build → serves `snapai.mainnov.tech` + `pk.snapai.mainnov.tech`
- `staging` branch → domain-level gitBranch → serves `staging.snapai.mainnov.tech` + `pk-staging.snapai.mainnov.tech` + `scopesnap-web-staging.vercel.app`

**Impact:** There is ONE Vercel project for the entire frontend. Any reference to a separate `scope-snap-ai` production project is incorrect and should be updated.

---

## DEC-085 — Next.js client-side router caches component state; use fetch() for prod content verification (2026-05-27)

**Discovery:** After a Vercel deploy, navigating to a page in Chrome and checking `document.body.innerText` can return stale content from the Next.js client-side router's component cache. Even `window.location.reload(true)` does not reliably flush this. The server IS serving the new HTML, but the browser renders the cached component tree.

**Authoritative verification method for page content on prod:**
```javascript
const resp = await fetch('https://snapai.mainnov.tech/tech', { cache: 'no-store' });
const html = await resp.text();
const hasNewCopy = html.includes('Snap the nameplate in the truck');
```
A `cache: 'no-store'` fetch bypasses both browser cache and Vercel CDN edge cache and returns exactly what the server renders.

**For redirect verification (4.14):** Browser navigation IS the authoritative test. Navigate to the page and confirm `window.location.pathname === '/dashboard'`.

**Rule:** For content checks use `fetch(url, {cache:'no-store'})`. For behavior checks (redirects, auth gates) use browser navigation.

---

## DEC-086 — `innerText` returns CSS-transformed text; use `.toUpperCase()` for uppercase elements (2026-05-27)

**Discovery:** Checking `document.body.innerText.includes("Built for Houston contractors first")` returned `false` on the `/tech` page. The element renders correctly, but CSS `text-transform: uppercase` causes `innerText` to return `"BUILT FOR HOUSTON CONTRACTORS FIRST"`.

**Rule:** When checking `innerText` for strings that may be CSS-uppercased:
```javascript
body.toUpperCase().includes("BUILT FOR HOUSTON CONTRACTORS FIRST")
// OR
body.includes("Snap the nameplate") // lowercase strings are safe
```
Always check what the element actually contains via `el.innerText` before writing string checks.

---

## DEC-087 — StepZeroPanel must self-source Clerk JWT on every OCR request (BUG-045, 2026-05-27)

**Discovery (BUG-045):** The original OCR implementation passed a pre-baked JWT as a prop or called `getToken()` once at component mount. Clerk JWTs expire in 60 seconds. Any OCR attempt after token expiry silently failed with a 401.

**Fix:** StepZeroPanel calls `getToken()` immediately before each OCR API request — not once at mount, not via prop. Pattern:
```typescript
const token = await getToken();
const resp = await fetch('/api/ocr/nameplate', {
  headers: { Authorization: `Bearer ${token}`, 'X-Market': market }
});
```

**Rule (WA-9 extension):** `apiFetch` never auto-injects JWT (WA-9). For StepZeroPanel specifically: always get a fresh token inline, never cache the result of `getToken()` across requests.

---

## DEC-088 — OCR waterfall is 4-tier with field-level confidence gating (BUG-045, 2026-05-27)

**Architecture (live on main as of commit `3f06f0b`):**
- Tier 1: Gemini direct — fast, best results on clean nameplate photos
- Tier 2: Gemini with image enhancement — slower, handles dirty/angled plates
- Tier 3: DB brand lookup — matches make/model fragments to `brands` table
- Tier 4: Manual entry fallback — user types fields; photo persists as context strip

**Field-level confidence gating:** Each field (make, model, year, refrigerant) has its own confidence score. Tier 1 partial results (e.g. make=high, year=low) are supplemented by Tier 2/3 for low-confidence fields only. This avoids re-running the full waterfall when most fields are already confident.

**Note:** `brands.series` is empty for all 15 US brands. Tier 3 DB lookup is structurally correct but returns little useful data until series data is backfilled.

---

## DEC-089 — A/B test variant stored in `snap_sz_variant` localStorage key (BUG-045, 2026-05-27)

**Implementation (live as of commit `25492dc`):**
- New user sees either `"control"` or `"variant_a"` StepZero layout
- Assignment stored in `localStorage.setItem('snap_sz_variant', variant)`
- Assigned once on first StepZero view; subsequent visits read the stored value
- PostHog event: `ab_test_variant_assigned` fires on assignment with `{variant, market}` props
- Returning user localStorage path stored in `snap_sz_path`; used by Scenario D (DEC-089b)

**Rule:** Do NOT reassign the variant on subsequent visits. Read `localStorage.getItem('snap_sz_variant')` first; only assign if null.

---

## DEC-090 — Always audit existing work before implementing any fix prompt (2026-05-27)

**Discovery:** The BUG-034 fix prompt covered 15 scope items (4.1–4.15). Before writing any code, reading all 5 brain files + git log revealed that items 4.1–4.12 (BUG-045: JWT auth, Tesseract removal, 4-tier waterfall, PostHog telemetry, A/B test) were already complete and live on production. Only 4.13, 4.14, 4.15 required implementation. This pre-flight audit saved several hours of duplicate work.

**Mandatory pre-flight for any fix/feature prompt:**
1. Read all 5 brain files
2. `git log --oneline -20` on main to see recent commits
3. Match each scope item against commits — mark DONE before touching any code
4. Only implement items not already live

**Rule:** "Already done" is always better than "done again wrong".

---

## DEC-091 — `git config user.email` + `user.name` must be set after every `/tmp` clone (2026-05-27)

**Discovery:** After cloning to `/tmp/snapai_tmp`, the first `git commit` attempt failed with "Author identity unknown". The /tmp clone starts with no user identity.

**Fix — always run immediately after clone:**
```bash
git config user.email "ds.shoab@gmail.com"
git config user.name "Shoab"
```

**Why DEC-004 doesn't cover this:** DEC-004 says use /tmp clone for all git ops. It doesn't mention that user identity must be re-set every time. Now it does.

---

## DEC-092 — CDP `javascript_tool` times out at 45s; never await >30s in a single call (2026-05-27)

**Discovery:** A polling loop using `await new Promise(r => setTimeout(r, 5000))` iterated 36 times (180s total) in a single `javascript_tool` call. CDP `Runtime.evaluate` timed out at 45 seconds, returning "renderer may be frozen or unresponsive".

**Rule:** Never put a total wait time >30s inside a single `javascript_tool` call. For waiting on Vercel builds:
1. Use `mcp__workspace__bash` with `sleep 45` (max timeout allowed)
2. Then navigate + re-check with a fresh `javascript_tool` call
3. Or poll by re-calling navigate + javascript_tool in separate tool turns

**Implication:** Vercel builds (~2min) require multiple tool call cycles with a wait between each.

---

## DEC-093 — Clerk staging and prod use separate apps; sessions are NOT shared cross-environment (2026-05-27)

**Clarification of DEC-047:** DEC-047 states "Login on snapai.mainnov.tech also logs in pk.snapai.mainnov.tech." This is correct — both production domains use the same Clerk `pk_live_` app, so one session covers both.

**But:** Staging uses a separate Clerk app (`firm-chamois-61`, `pk_test_` keys). Even though staging domains are *.mainnov.tech subdomains, the different Clerk app means different session cookies. Signing in on `staging.snapai.mainnov.tech` does NOT give a session on `snapai.mainnov.tech`, and vice versa.

**Summary:**
- US prod + PK prod: same Clerk app (`pk_live_`) → one login covers both ✅
- US staging + PK staging: same Clerk staging app (`pk_test_`) → one login covers both ✅
- Prod vs staging: DIFFERENT Clerk apps → separate sessions, no cross-env login ✅

---

## 2026-06-10 — Free automated DB backups to Cloudflare R2 (DEC-094)

### DEC-094 — Daily pg_dump of both Virginia DBs → private Cloudflare R2 bucket (2026-06-10)
**Why:** Supabase free tier keeps **0-day backup retention** and permanently deletes data after an extended pause. The GitHub Actions keepalive pings prevent the pause, but a single missed ping risked data loss. DEC-094 adds an independent, off-platform safety net at $0.

**What runs:** `.github/workflows/db-backup-r2.yml` (on `main`). Schedule `0 3 * * *` (daily 03:00 UTC) + `workflow_dispatch`. Steps: install PG17 client → `pg_dump` PROD → `pg_dump` STAGING → verify. Each dump is plain SQL (`--no-owner --no-privileges --quote-all-identifiers`), gzipped, uploaded via `aws s3 cp` (preinstalled on the runner) to bucket `snapai-db-backups` under `prod/` and `staging/` prefixes.

**Cloudflare R2 setup (account `0c1bfa87134c7a6688d7eaf4410bf86a`):**
- Bucket **`snapai-db-backups`** — region **ENAM** (co-located w/ Virginia us-east-1 DBs), **Standard** storage class, **public access DISABLED** (private).
- **Object Lifecycle Rule** `delete-after-14-days` → auto-deletes objects 14 days after upload (no manual cleanup).
- Scoped API token **`snapai-db-backups-rw`** — Object Read & Write, **this bucket only**, no expiry. (Least-privilege: cannot touch the app's `scopesnap-uploads` / `scopesnap-uploads-staging` buckets.)
- **Cost = $0.** Free tier is 10 GB storage / 1M Class A / 10M Class B ops / **$0 egress**. Our load: ~0.2 MB prod + ~2 MB staging per day, ~2 writes/day. Orders of magnitude inside free. (R2 does require a card-on-file to enable — already done on this account.)

**GitHub repo secrets (names only — values are secret):** `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_ENDPOINT` (=`https://0c1bfa87134c7a6688d7eaf4410bf86a.r2.cloudflarestorage.com`), `SUPABASE_DB_URL_PROD`, `SUPABASE_DB_URL_STAGING`.
- ⚠️ **Do NOT confuse with the older `CLOUDFLARE_R2_*` secrets** (CLOUDFLARE_R2_ACCESS_KEY / _SECRET_KEY / _ACCOUNT_ID / _BUCKET, added ~2 months prior) — those belong to the **app's uploads** bucket and a different token. The backup workflow uses ONLY the `R2_*` + `SUPABASE_DB_URL_*` names above.

**GOTCHAS LEARNED (cost 2 failed runs before green):**
1. **pg_dump version must be ≥ server version.** `ubuntu-latest` ships pg_dump **16**, but the Supabase server is **17.6** → `error: aborting because of server version mismatch`. Fix: `apt-get install postgresql-client-17` AND call the **explicit binary** `/usr/lib/postgresql/17/bin/pg_dump` (the `pg_wrapper` at `/usr/bin/pg_dump` still resolved to 16). Set via job env `PGDUMP`.
2. **Use the Session pooler, NOT the Transaction pooler.** First staging attempt used the Transaction-pooler string (**port 6543**, username collapsed to `postgres`) → `FATAL: password authentication failed for user "postgres"`. pg_dump needs **Session pooler** (port **5432**, username `postgres.<project-ref>`, IPv4-reachable from GitHub). Prod worked first try because it had the correct Session-pooler URL.
3. **workflow_dispatch only appears once the workflow file is on the default branch (`main`).** Pushed via git worktree from `origin/main` (then a contents-API edit for the fix) — the local working tree is a stale, dirty `staging` checkout, so never commit the backup file from there.

**VERIFIED 2026-06-10:** run `27296950101` = **success** (all 6 steps green). Bucket listing from the run: `prod/prod_20260610_1742.sql.gz` (228 KB), `prod/prod_20260610_1821.sql.gz` (228 KB), `staging/staging_20260610_1821.sql.gz` (2.1 MB). Post-change, both backends `/health` = `ok` / `db: connected` (prod `scopesnap-api-production.up.railway.app`, staging `scopesnap-api-staging.up.railway.app`) — the staging password/secret update did **not** break Railway staging.

**Restore how-to:** download the `.sql.gz` from R2 → `gunzip` → `psql "<target Session-pooler URL>" -f dump.sql`. Plain SQL, owner/privilege-stripped, so it restores cleanly into any empty DB.

**Still open (separate):** the Healthchecks "Keepalive B DOWN" alert — the two keepalive workflows still ping the **deleted Tokyo** Supabase URLs via the old `SUPABASE_PROD_URL` / `SUPABASE_STAGING_URL` secrets, so their `if: success()` heartbeat never fires. App is fine. Fix later: repoint those 4 keepalive secrets to the Virginia projects, or retire the keepalives now that R2 backups exist.

**Note:** `scopesnap-api.up.railway.app` (bare) returns a Railway "Application not found" 404 — it is **stale**. The live prod backend is **`scopesnap-api-production.up.railway.app`**.

### 2026-06-10 — Keepalive "DOWN" RESOLVED (DEC-094 follow-up)
Root cause confirmed from run logs: keepalive-supabase-B failed with `curl: (6) Could not resolve host: quqrvnoguofbjacrxcim.supabase.co` — the 4 keepalive secrets still pointed at the **deleted Tokyo** projects, so the ping failed and the `if: success()` Healthchecks heartbeat never fired → DOWN.

**Fix:** repointed all 4 keepalive secrets to the Virginia (us-east-1) projects (values fetched via Supabase MCP; updated through the GitHub Secrets API with libsodium sealed-box encryption — the anon keys are publishable/public):
- `SUPABASE_PROD_URL`    = `https://zpsoprffaujswywtsgzy.supabase.co` (snapai-prod-use1)
- `SUPABASE_STAGING_URL` = `https://kikhhnanuwzocwcpzutr.supabase.co` (snapai-staging-use1)
- `SUPABASE_PROD_ANON_KEY` / `SUPABASE_STAGING_ANON_KEY` = each project's legacy anon JWT.

**Verified 2026-06-10:** manually dispatched both keepalive-supabase-A and -B → both **success**; steps Ping production / Ping staging / Heartbeat(Healthchecks.io) all green. Both Healthchecks checks flip DOWN→UP. Twice-weekly schedule restored (A = Sun 02:00 UTC, B = Wed 14:00 UTC).

Note: keepalive is now somewhat redundant with the daily R2 backup (which pg_dumps both DBs daily = stronger DB-activity keepalive), but it's kept for the independent Healthchecks "did the scheduled job run" monitor.
## DEC-095 — Audit remediation batch 2: authed market trust, strict-CSP nonce, report-link hardening, SRI accepted (2026-06-21)

Closes the remaining open items from the full-audit deep review (items #3-#7),
implemented and verified on staging (branch audit/remediation-batch-2 -> staging).

- **#4 Authenticated market trust (High).** Market for AUTHENTICATED requests was
  resolved from the spoofable `X-Market` header, letting a logged-in company pull
  the other market's pricing/reference tables into its own estimate. Fix: new
  trusted `companies.market` column (migration 043), stamped at provision time
  from the request host; `AuthContext.market`; new `get_company_tables` dependency
  resolving tables from the company's own market. 13 authenticated call sites
  flipped off the header (assessments, diagnostic x6, error_code x2, estimates,
  fault_estimate, recommend, ocr). Public/unauthed routes (`get_public_diagnosis`,
  `get_public_report`, model seeding) intentionally still use the header. Backfill:
  existing rows default 'US'; verified staging = 4 companies, all US, 0 PK, so no
  PK company mis-resolves. ACTION on prod promote: confirm/backfill any PK company
  (`UPDATE companies SET market='PK' WHERE ...`) before flipping prod.
- **#5/#9 Strict-CSP nonce (Med).** Replaced the static `script-src 'unsafe-inline'`
  CSP with Clerk v7 strict CSP: `clerkMiddleware` now runs on every request with
  `contentSecurityPolicy.strict` (per-request nonce + `'strict-dynamic'`), exposed
  via `x-nonce`; `<ClerkProvider dynamic>`; nonce on the inline SW script; static
  CSP removed from next.config.js (Clerk is the single CSP source). `'unsafe-eval'`
  kept (Google Maps) and `style-src 'unsafe-inline'` kept (Clerk/Maps). NOTE: the
  literal `'unsafe-inline'` token remains in script-src as Clerk's deliberate
  legacy-browser fallback, but is IGNORED by modern browsers because
  `'strict-dynamic'` is present (the Google-recommended backwards-compatible strict
  CSP). Verified on staging: header carries strict-dynamic+nonce (single source),
  auth harness PASS (Clerk login->dashboard), public report renders, Google Maps is
  bundle-injected via createElement+appendChild so strict-dynamic trusts it via
  propagation.
- **#6 Report-link hardening (Low).** New report links now emit the strong 32-char
  `report_token` instead of the guessable `rpt-####` short id (3 email fallbacks);
  short-id lookup stays resolvable so existing customer links keep working.
  Rate-limiting (DEC from batch 1) remains the brute-force mitigation. Changing the
  public URL scheme to invalidate old short-id links is deferred as a product call.
- **#3 SRI (Low) — ACCEPTED, not pursued.** No stable non-experimental path on
  Next.js 16; `experimental.sri` has a known CDN integrity-mismatch bug
  (vercel/next.js#91633) that broke Clerk at runtime here and was reverted. The
  strict-dynamic+nonce CSP (#5) covers the same script-injection threat class.
- **#7 Brain-doc divergence — RECONCILED.** Root cause was CRLF-vs-LF noise (now
  fixed by `.gitattributes *.md text eol=lf`). `ScopeSnapAI/DECISIONS.md` and
  `ScopeSnapAI/TECH_STACK.md` (main was a clean superset) adopted from main on
  staging; both `PROJECT_BRAIN.md` files (bidirectional divergence) were unioned
  losslessly (heading-count verified, both sides' unique sections preserved).
  Next free decision number after this entry is DEC-096.

Verification: backend py_compile + app import + 145/145 pytest pass; migration 043
live on staging DB (head=043); frontend tsc 0 errors; auth harness PASS; CSP header
+ Maps loader checked in-browser. Not yet promoted to prod (staging-only this round).
