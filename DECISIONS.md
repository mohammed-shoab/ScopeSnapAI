# SnapAI — Key Architectural Decisions

> This file records decisions made during development that have lasting impact on how the codebase works.
> Future AI sessions: read this before proposing architecture changes or writing migrations.
>
> Last updated: 2026-05-15

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

**Current revision:** 015 (as of 2026-05-11)

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
