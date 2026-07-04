# SnapAI — Change Workflow (Staging-First)

> The canonical reference for how every code, schema, env-var, and infrastructure change reaches production.
> Codified as DEC-070. Cross-referenced from PROJECT_BRAIN.md, TECH_STACK.md, DECISIONS.md, ACTIVE_TASKS.md.
>
> **AI sessions:** read this file in full before starting any change work. Do not propose a different workflow.

---

## 1. Activation status

**ACTIVE as of 2026-05-24.** Stage 7 (Staging End-to-End QA) signed off on 2026-05-24. Staging is verified as a true mirror of production. Vercel staging deploys the `staging` branch. Full QA passes match on both environments.

This workflow is the **canonical and mandatory** path for every code, schema, env-var, and infrastructure change reaching production. The four absolute rules in Section 2 are enforced. The feature-branch → staging → main → prod loop described below is the operational workflow.

The supporting tactics from DEC-004 (git from `/tmp` clone), DEC-013 (no git stash from sandbox), and DEC-022 (Desktop Commander for git ops) remain documented practices for specific Cowork / sandbox contexts — they are no longer transitional exceptions.

---

## 2. The mental model

**Staging mirrors production by default.** Every merge to `staging` triggers an auto-deploy. Production is reached only by promoting verified files from `staging` to `main` via the `promote-to-prod.sh` script. You never edit `main` directly. You never test on production.

The cost of this discipline is one extra deploy step per change (~3 minutes). The benefit is that every production deploy has already been verified end-to-end on an environment that is byte-for-byte identical to production except for data isolation, test keys, and a visible amber banner.

**The four absolute rules** (codified in DEC-070):

1. **Never edit code directly on `main`** without going through `staging` first
2. **Never push migrations to prod** that haven't run on staging first
3. **Never add env vars to prod** without mirroring them on staging
4. **Never test on production** — testing happens on staging; production is for real users

These rules have one carve-out: the **emergency hotfix path** (Section 12). It bypasses staging but requires a documented incident reason and a mandatory follow-up sync to bring staging back in line with main within 24 hours.

---

## 3. Reference architecture (target state — active after Stage 7)

| Layer | Production | Staging |
|---|---|---|
| Houston frontend URL | https://snapai.mainnov.tech | https://staging.snapai.mainnov.tech |
| PK frontend URL | https://pk.snapai.mainnov.tech | https://pk-staging.snapai.mainnov.tech |
| Vercel default URL | (scope-snap-ai project) | https://scopesnap-web-staging.vercel.app |
| Vercel project | `scope-snap-ai` (org `mohammed-shoabs-projects-7844119e`) | `scopesnap-web-staging` |
| Vercel Production Branch | `main` | `staging` *(domain-level gitBranch="staging" set on all 3 domains — DEC-080, Stage 6 complete 2026-05-24)* |
| Backend (Railway) | scopesnap-api-production.up.railway.app | scopesnap-api-staging.up.railway.app |
| Railway service | Production service in project `0e78dd68-…` | Separate staging service in same project |
| Supabase project | `quqrvnoguofbjacrxcim` | `pqmgveqkuckbvyygsilk` (ap-northeast-1) |
| Clerk app | live keys (pk_live_…/sk_live_…) | `firm-chamois-61` test keys (pk_test_…/sk_test_…) |
| R2 bucket | scopesnap-uploads | scopesnap-uploads-staging |
| Git branch | `main` | `staging` (off `main`) |
| Banner | none | amber `StagingBanner` on authenticated routes |
| Promote script | n/a | `scripts/promote-to-prod.sh <file…>` (run from a local main checkout) |
| Keepalive cron | `keepalive-supabase-A.yml` Sundays 02:00 UTC | `keepalive-supabase-B.yml` Wednesdays 14:00 UTC |
| DNS for custom domains | Hostinger (`mshoabarabi@gmail.com`) — see DEC-066 | Hostinger (same account) |

**Auto-sync wiring** (set up in Stage 6):
- Vercel production: every push to `main` → auto-deploys to snapai.mainnov.tech + pk.snapai.mainnov.tech
- Vercel staging: every push to `staging` → auto-deploys to staging.snapai.mainnov.tech + pk-staging.snapai.mainnov.tech
- Railway production: every push to `main` → auto-deploys + runs `alembic upgrade head`
- Railway staging: every push to `staging` → auto-deploys + runs `alembic upgrade head`

---

## 4. The standard 7-step change workflow

This is the loop for every non-hotfix change. Frontend, backend, both, migration, copy tweak, anything.

### Step 1 — Branch off `staging`

```bash
# From a /tmp clone (per DEC-004 — never operate git from the NTFS workspace)
git clone https://x-token:$GH_PAT@github.com/mohammed-shoab/ScopeSnabAI /tmp/snapai_work
cd /tmp/snapai_work
git checkout staging
git pull origin staging
git checkout -b feature/<short-descriptive-name>
```

Branch naming convention:
- `feature/<name>` — new feature
- `fix/<bug-id>-<name>` — bug fix (e.g., `fix/bug-039-photo-rotation`)
- `chore/<name>` — refactor, docs, or maintenance
- `migration/<name>` — schema-only change

### Step 2 — Make the change

Edit files in the `/tmp/snapai_work` clone. If an AI is making the edit, it operates entirely in `/tmp`, never touching the NTFS-mounted working copy (DEC-004).

Update brain files at the time of the change, not as an afterthought:
- New decision or workaround → add a DEC or WA entry to `DECISIONS.md` / `TECH_STACK.md`
- New bug fix → add to `ACTIVE_TASKS.md` lessons table
- Schema change → update `PROJECT_BRAIN.md` migration row
- See Section 13 for the full documentation protocol

### Step 3 — Push and open PR

```bash
git add -A
git commit -m "<type>(<scope>): <short description>"
# Examples:
#   fix(estimates): correct better-tier copy on Houston market
#   feat(diagnostic): add R-32 inverter branch for PK
#   chore(docs): update WORKFLOW.md with rollback section
git push origin feature/<name>
```

Open a PR on GitHub from `feature/<name>` → `staging`. PR description should include:
- What changed and why
- Which markets are affected (Houston, PK, both)
- Whether a migration is included
- Whether new env vars are needed
- How to verify on staging (specific URL paths and expected behavior)

If working solo, you can merge your own PR after self-review. For multi-person teams, require one approval.

### Step 4 — Merge to `staging`

Merge the PR. This triggers:
1. Vercel staging redeploys both `staging.snapai.mainnov.tech` and `pk-staging.snapai.mainnov.tech` (~2 min)
2. Railway staging redeploys (~3 min including `alembic upgrade head` if a migration was added)
3. GitHub Actions keepalive workflows continue running on schedule (no action needed)

While waiting:
- Watch Vercel deployment logs in the staging project for build errors
- Watch Railway deployment logs in the staging service for migration errors
- If either fails: investigate, push a fix to the same feature branch, re-merge

### Step 5 — Verify on staging

Open the changed flow on both staging domains where applicable:
- US change → verify on `staging.snapai.mainnov.tech`
- PK change → verify on `pk-staging.snapai.mainnov.tech`
- Both-markets change → verify on both

Use the test Clerk account (test-mode keys via `firm-chamois-61`). The amber `StagingBanner` should be visible on every authenticated route — this is your visual confirmation that you're on staging, not production.

**Verification checklist for any change:**
- The specific flow that was changed works end-to-end with the new behavior
- No regressions on adjacent flows you didn't touch
- DevTools Network shows clean requests (no 4xx/5xx errors)
- DevTools Console shows no new errors or warnings
- If a migration ran: `SELECT version_num FROM alembic_version;` on staging Supabase matches the migration head
- If env vars were added: confirm via Vercel staging Settings → Environment Variables

If verification fails: do not promote. Fix on the same feature branch, push, re-merge to staging, re-verify.

### Step 6 — Promote to production

From a local `main` checkout (NOT from the `/tmp` clone you used for feature work):

```bash
# In a fresh /tmp clone of main
git clone --branch main https://x-token:$GH_PAT@github.com/mohammed-shoab/ScopeSnapAI /tmp/snapai_main
cd /tmp/snapai_main
# Run the promote script with the exact list of files that changed
./scripts/promote-to-prod.sh scopesnap-web/components/SomeComponent.tsx scopesnap-api/api/some_endpoint.py scopesnap-api/db/migrations/versions/035_my_migration.py
```

The `promote-to-prod.sh` script (defined fully in Section 9):
1. Verifies you are on `main`
2. Fetches the latest `staging` branch
3. Copies each named file from `staging` to `main`
4. Commits with message `promote: <files> from staging to main`
5. Pushes to `origin main`

After push:
1. Vercel production redeploys `snapai.mainnov.tech` + `pk.snapai.mainnov.tech` (~2 min)
2. Railway production redeploys + runs `alembic upgrade head` (~3 min)

### Step 7 — Verify on production

Same flow as Step 5, but on the real domain:
- US change → verify on `snapai.mainnov.tech`
- PK change → verify on `pk.snapai.mainnov.tech`

Use the production-side test contractor account (live Clerk keys). NO StagingBanner should be visible — if one appears, that's BUG-031 regression, stop and investigate.

**Verification checklist for production:**
- The change is live and behaves identically to how it behaved on staging
- Production Alembic head matches what was promoted (`SELECT version_num FROM alembic_version;` on `quqrvnoguofbjacrxcim`)
- Production health endpoint returns ok: `https://scopesnap-api-production.up.railway.app/health`
- No new Sentry alerts

If verification fails on production but passed on staging, you have a real environment discrepancy — see Section 12 hotfix path, then Section 14 retrospective. This should be rare if staging is genuinely mirrored.

---

## 5. Pre-flight checklist (before opening the feature branch)

Always confirm before writing a single line of code:

1. Have I read the latest `PROJECT_BRAIN.md`, `DECISIONS.md`, `ACTIVE_TASKS.md`?
2. Do I know the current production HEAD on `main`?
3. Do I know the current production Alembic version?
4. Is staging at parity with production right now? Query both: `SELECT version_num FROM alembic_version;` on `quqrvnoguofbjacrxcim` AND `pqmgveqkuckbvyygsilk` — they must match. If they don't, fix staging FIRST (see Section 10 migration protocol).
5. Is anyone else mid-change? Check `git log staging --oneline | head -10` for recent activity, and check open PRs.
6. Does my change conflict with anything in flight? If yes, coordinate or wait.
7. Is the change US-only, PK-only, or both? Apply the rules in Section 7.4.

If any item fails: do not proceed until resolved.

---

## 6. Change-type protocols

### 6.1 Frontend-only change (TSX, TS, CSS, public assets)

Files touched: only inside `scopesnap-web/`. No backend code, no migration, no env var.

Standard 7-step workflow. Verification focus: visual correctness, console errors, Network tab cleanliness, both markets if both affected.

Common gotchas:
- **Vercel build can silently truncate** files containing emoji or non-ASCII (DEC-005) when written by Linux sandbox to NTFS. Always read blobs from git object store via `git cat-file blob <sha>` for emoji files, never the filesystem path.
- **React controlled components ignore native `.click()` events** (WA-27). Use `element[__reactPropsKey].onClick(...)` directly.
- **IndexedDB cache has 24h TTL on PK** (WA-26). After seeding new PK data, clear IndexedDB or wait 24h.
- **Vercel SSR caveat** — `javascript_tool` queries with `querySelector` for client-rendered DOM (WA-13).

### 6.2 Backend-only change (Python — API routes, services, helpers)

Files touched: only inside `scopesnap-api/`. No frontend code, no migration, no env var.

Standard 7-step workflow. Verification focus: API response shape via DevTools Network, backend logs in Railway dashboard, no 500s on adjacent endpoints.

Common gotchas:
- **`apiFetch` does NOT auto-inject Clerk JWT** (DEC-030). Every authenticated endpoint must receive `token:` argument explicitly from the frontend.
- **Markets routed via `X-Market` header** (`get_tables()` in `api/dependencies.py`). Verify both market paths if your change affects shared code.
- **`UVICORN_WORKERS = 1`** (DEC-007) — do not increase without checking Railway spend cap.
- **Estimate-tier naming inconsistency** (DEC-049) — `fault_estimate.py` uses "A"/"B"/"C", `pak_pricing_tiers` uses "good"/"better"/"best". Don't conflate.

### 6.3 Full-stack change (both frontend and backend)

Standard 7-step workflow. Sequence within a single PR:
1. Backend change first (API route, schema)
2. Frontend change second (UI calls the new API)
3. Push both as one commit OR two commits on the same branch (one PR)

Verification: backend works in isolation (curl the new endpoint via authenticated session), THEN frontend integration works.

### 6.4 Database migration (Alembic)

Files touched: a new file in `scopesnap-api/db/migrations/versions/`. Migration numbering must be the next sequential head (check `SELECT MAX(version_num) FROM alembic_version;` on both prod and staging Supabase).

Critical rules:
- **Migrations auto-run on Railway boot** via `start.sh` → `alembic upgrade head` (DEC-002). One push deploys + migrates atomically.
- **Numbering**: new migration is current head + 1 (e.g., if prod is at 034, new migration is 035).
- **Atomicity**: each migration should be self-contained and reversible if possible. Include a working `downgrade()` function.
- **Data migrations**: if the migration changes data (not just schema), test extensively on staging first — a botched data migration cannot be cleanly reverted.

Special verification on staging (Step 5):
- After merge to staging, watch Railway staging logs for `INFO  [alembic.runtime.migration] Running upgrade <prev> -> <new>, <description>`
- Query `SELECT version_num FROM alembic_version;` on `pqmgveqkuckbvyygsilk` → must show the new head
- If migration failed: Railway service will fail health check; investigate logs, fix migration file, push again

Special verification on production (Step 7):
- Same checks, but on `quqrvnoguofbjacrxcim`
- If production Alembic head doesn't match: Railway might still be deploying; wait 5 min and re-check. If still mismatched, manually inspect Railway logs.

### 6.5 Environment variable change

Vercel staging and production env vars must be kept in lockstep. Adding a new var:

1. **On staging Vercel first**: project `scopesnap-web-staging` → Settings → Environment Variables → add new var with staging-appropriate value (test keys, staging URLs)
2. **Redeploy staging** (env var changes do not auto-redeploy)
3. **Verify on staging** that the new var is being read correctly
4. **On production Vercel**: project `scope-snap-ai` → Settings → Environment Variables → add the same var with production-appropriate value (live keys, prod URLs)
5. **Redeploy production**
6. **Verify on production**

Same pattern for Railway env vars (staging service first, then production service).

**Common env vars and their values:**

| Variable | Staging value | Production value |
|---|---|---|
| `NEXT_PUBLIC_ENV` | `staging` | `production` |
| `NEXT_PUBLIC_API_URL` | `https://scopesnap-api-staging.up.railway.app` | `https://scopesnap-api-production.up.railway.app` |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | `pk_test_…` (from firm-chamois-61) | `pk_live_…` |
| `CLERK_SECRET_KEY` | `sk_test_…` | `sk_live_…` |
| `DATABASE_URL` | Supabase pooler URL for `pqmgveqkuckbvyygsilk` | Supabase pooler URL for `quqrvnoguofbjacrxcim` |
| `R2_BUCKET` | `scopesnap-uploads-staging` | `scopesnap-uploads` |

**Critical**: never set `NEXT_PUBLIC_ENV=staging` on the production Vercel project. This is the BUG-031 footgun. See DEC-051.

### 6.6 Market-scoped change

| Scope | Frontend gating | Backend gating | DB scope |
|---|---|---|---|
| **PK only** | `if (detectMarket() === "PK") { … }` | `if tables.market == "PK": …` | Only touch `pak_*` tables |
| **US only** | `if (detectMarket() === "US") { … }` | Default (non-PK) path | Only touch standard US tables |
| **Both (universal)** | No gating | No gating | Shared tables — one migration applies to both |

See MARKET_GUIDE.md for full dual-market routing rules. The cardinal rule: **one git push deploys both markets simultaneously**. Always test the OTHER market after a change you think is single-market — it's easy to accidentally touch shared code paths.

---

## 7. The promote-to-prod.sh script

Location: `scopesnap-api/scripts/promote-to-prod.sh` (run from a local `main` checkout).

### What it does

```bash
./scripts/promote-to-prod.sh path/to/file1.tsx path/to/file2.py path/to/migration.py
```

1. Asserts current branch is `main`
2. Runs `git fetch origin staging`
3. For each named file: `git checkout origin/staging -- <file>`
4. Stages all changes: `git add <files>`
5. Commits: `promote: <files-summary> from staging to main`
6. Pushes: `git push origin main`

### What it does NOT do

- Does NOT copy env vars (Vercel/Railway env vars are managed separately — see Section 6.5)
- Does NOT copy Clerk app config, Supabase RLS policies, or any other dashboard-managed settings
- Does NOT run migrations (those run on Railway boot post-push)
- Does NOT verify the change works — that's Step 7

### When to use full-branch merge instead

For very large changes (e.g., complete track rollouts touching 50+ files), use a full merge from `staging` to `main` rather than the file-by-file script:

```bash
cd /tmp/snapai_main
git checkout main
git pull origin main
git merge origin/staging --no-ff -m "release: merge staging into main (<description>)"
git push origin main
```

Reserve full-merge for batched releases. The file-by-file promote script is the default for individual changes.

---

## 8. Migration protocol (Alembic — special handling)

Migrations have unique risk because they auto-run on Railway boot and cannot be cleanly reverted if they alter data. Treat them with extra discipline.

### Before writing a migration

1. **Query current alembic head on both environments**:
   ```sql
   -- on quqrvnoguofbjacrxcim (production)
   SELECT version_num FROM alembic_version;
   -- on pqmgveqkuckbvyygsilk (staging)
   SELECT version_num FROM alembic_version;
   ```
   These must match. If they don't, fix staging first (run any missing migrations on staging) before writing a new one.

2. **Verify your new migration number is unique**:
   ```bash
   ls scopesnap-api/db/migrations/versions/ | sort | tail -5
   ```

3. **Inspect the previous migration** to understand patterns used in this codebase (column types, naming conventions, JSONB usage).

### Writing the migration

- Use Alembic autogenerate only as a starting point. Always read and tighten the generated SQL.
- Always implement `downgrade()` — even if you never expect to use it.
- For data migrations, use `op.execute(text(...))` with raw SQL. Avoid ORM in migrations to prevent schema-version drift.
- Add a docstring at the top explaining what the migration does, what triggered it, and any rollback caveats.

### Running the migration

Standard 7-step workflow with one addition: after Step 4 (merge to staging), explicitly verify on Railway staging that the migration ran:

```bash
# Pull Railway staging logs via dashboard, look for:
# INFO  [alembic.runtime.migration] Running upgrade <prev> -> <new>, <description>
```

If you see `Running stamp` or `No upgrade required`, the migration was already applied or skipped — investigate.

### Rollback (if needed)

You cannot cleanly roll back a migration once applied to a production database without data loss risk. The options:

1. **If the migration is reversible**: write a new migration that undoes the changes. Promote through staging as usual.
2. **If the migration is data-destructive**: restore from the Supabase point-in-time backup (free tier supports daily backups for 7 days). This is a major operation — contact Shoab before doing it.
3. **Schema-only mistakes**: usually safe to write a corrective forward migration.

---

## 9. Emergency hotfix path (production-only push)

Reserved for **production outages or genuine emergencies only**. Examples that justify hotfix:
- Production health endpoint returns 500
- Critical security vulnerability with active exploitation
- Auth completely broken (no users can log in)
- Payment/estimate flow generating wrong dollar amounts

Examples that do NOT justify hotfix:
- "It's just a tiny copy change"
- "The bug only affects 5 users"
- "I'm in a hurry"
- "Staging is broken so I can't test there right now"

If you're not sure whether it's a hotfix: it isn't. Use the standard workflow.

### Hotfix protocol

1. **Document the incident**: open a new section in `ACTIVE_TASKS.md` under "Active Incidents" with timestamp, description, and impact estimate
2. **Hotfix from `main` directly** (the only sanctioned bypass):
   ```bash
   cd /tmp/snapai_main
   git checkout main
   git pull origin main
   # Make the fix
   git add -A
   git commit -m "hotfix: <short description> (incident: <YYYY-MM-DD-NN>)"
   git push origin main
   ```
3. **Verify on production immediately** — do not move on until the fix is live and the incident is mitigated
4. **Within 24 hours: sync staging** to match main
   ```bash
   cd /tmp/snapai_main
   git checkout staging
   git pull origin staging
   git merge origin/main -m "sync: bring staging up to main after hotfix (incident: <YYYY-MM-DD-NN>)"
   git push origin staging
   ```
5. **Write a retrospective** as a new entry in `DECISIONS.md`:
   - What broke and why
   - Why this couldn't wait for the staging cycle
   - What we missed in normal QA that let this through
   - What we will change to prevent this class of bug
6. **Update brain files** per Section 13

The 24-hour sync is non-negotiable. Staging drift from main is the single biggest risk to this workflow — it causes future changes to be tested against the wrong baseline.

---

## 10. Rollback protocol

If a verified-on-staging change still breaks production (rare but possible):

### Frontend rollback (Vercel)

- Vercel dashboard → scope-snap-ai project → Deployments → find the last good deployment → "Promote to Production"
- This is instant (~30 seconds). Code on `main` still reflects the broken version; create a `revert/` branch and promote a proper revert through staging.

### Backend rollback (Railway)

- Railway dashboard → production service → Deployments → find the last good deployment → "Redeploy"
- ~3 minutes. Same caveat: code on `main` still reflects the broken version. Revert properly through staging next.

### Schema rollback

- See Section 8 — schema rollbacks are dangerous. Write a forward-corrective migration through staging unless you absolutely must restore from backup.

### Env var rollback

- Vercel/Railway dashboard → Settings → Environment Variables → edit the variable back to its previous value → Redeploy

---

## 11. Documentation update protocol (mandatory with every change)

Every merge to `staging` and every promote to `main` must include doc updates in the same PR or commit. Brain files are the long-term memory of the project — they cannot fall out of sync with reality.

**For every change, ask:**

| If the change is… | Update… |
|---|---|
| A new architectural pattern, schema decision, or naming convention | `DECISIONS.md` — new DEC-NNN entry |
| A new workaround for a tool/infra quirk | `TECH_STACK.md` — new WA entry, top "Last updated" line |
| A bug fix | `ACTIVE_TASKS.md` — add to "Bugs Resolved" section, lesson rows if applicable |
| A new feature visible to users | `ACTIVE_TASKS.md` and `PROJECT_BRAIN.md` Track section |
| A migration | `PROJECT_BRAIN.md` migration row (new Alembic head + description) |
| An env var addition or change | `TECH_STACK.md` env var table |
| A new infra resource (Vercel project, Supabase project, etc.) | `PROJECT_BRAIN.md` Infrastructure IDs table |
| Any major learning or "what went wrong" | `ACTIVE_TASKS.md` Lessons table at bottom |

The pattern for DEC entries:

```markdown
## DEC-NNN — <one-line decision title> (<YYYY-MM-DD>)

**Date:** <YYYY-MM-DD>

**Context:** <what triggered this decision, 2-4 sentences>

**Decision:** <what we chose to do, 1-2 sentences>

**Rationale:** <why this over alternatives, 2-4 sentences>

**Rule:** <the operational rule going forward, 1-2 sentences>

**Cross-references:** DEC-NN, WA-NN if applicable
```

The pattern for WA (workaround) entries in `TECH_STACK.md`:

```markdown
**WA-NN — <one-line title> (<YYYY-MM-DD>)**
- Symptom: <observable problem>
- Root cause: <if known>
- Workaround: <the steps to apply>
- Cross-references: <DEC-NN if applicable>
```

---

## 12. AI session bootstrap

If you are an AI session starting work on this codebase, follow this bootstrap **before any code change**.

### Read order (mandatory)

1. `C:\Users\dell\My Drive\Personal Claude\ScopeSnapAI\PROJECT_BRAIN.md` — current state, IDs, deployment
2. `C:\Users\dell\My Drive\Personal Claude\ScopeSnapAI\DECISIONS.md` — DEC-001 through latest
3. `C:\Users\dell\My Drive\Personal Claude\ScopeSnapAI\TECH_STACK.md` — architecture, WA entries
4. `C:\Users\dell\My Drive\Personal Claude\ScopeSnapAI\ACTIVE_TASKS.md` — in-flight work, recent QA
5. `C:\Users\dell\My Drive\Personal Claude\ScopeSnapAI\MARKET_GUIDE.md` — dual-market routing
6. **This file** — `WORKFLOW.md`

### Confirm before starting

- Current production HEAD on `main` — `git rev-parse origin/main`
- Current staging HEAD on `staging` — `git rev-parse origin/staging`
- Current Alembic version on prod and staging — both must match (or staging must be ahead by one if a migration is in flight)
- The user's stated goal for this session — confirm in writing before code changes
- The change scope: US, PK, both
- Whether this is a hotfix or standard workflow

### Default behavior

- Always assume standard 7-step workflow unless the user explicitly invokes the hotfix path
- Always operate git from `/tmp` clones (DEC-004), never from the NTFS workspace
- Always read blobs from git object store for emoji-containing files (DEC-005)
- Always pass `token:` explicitly in `apiFetch` calls (DEC-030)
- Always verify live in Claude in Chrome before declaring something "done" or "deployed" (DEC-002)
- Always update brain files in the same commit as the code change (Section 11)
- Always work in the user's stated market only, unless the change is explicitly cross-market

### When in doubt

- Stop and ask Shoab
- Brutal honesty required — flag your own uncertainty openly
- Verify claims live before stating them
- If a tool fails, do not silently retry with a different approach — surface the failure first

---

## 13. What you NEVER do (the canon)

1. **Never edit code directly on `main`** — every change goes through `staging` first
2. **Never push migrations to `main`** that haven't run successfully on `staging` first
3. **Never add env vars to production Vercel/Railway** without mirroring them on staging first
4. **Never test on production** — production is for real users; testing happens on staging
5. **Never operate git from the NTFS workspace** (DEC-004) — use `/tmp` clones
6. **Never `git stash` from the Linux sandbox** on NTFS (DEC-013) — use WIP commits
7. **Never set `NEXT_PUBLIC_ENV=staging` on the production Vercel project** (DEC-051 / BUG-031)
8. **Never delete migrations** that have been applied to either environment
9. **Never commit secrets to git** — secrets live in Vercel/Railway env vars only
10. **Never use Shoab's personal LinkedIn or `shoab.*@gmail.com` accounts** for any product-side outreach or warming
11. **Never bypass the staging cycle for "small" changes** — small changes are exactly the changes most likely to slip a bug into prod
12. **Never declare something done** without a live verification screenshot or network response confirming it

---

## 14. Cross-references

| Decision | Topic | Status |
|---|---|---|
| DEC-001 | Database on Supabase, not Railway | Active |
| DEC-002 | Alembic auto-runs on Railway boot via start.sh | Active |
| DEC-004 | Git operations from `/tmp` clone only | Active |
| DEC-005 | Emoji files require git blob reads | Active |
| DEC-007 | UVICORN_WORKERS = 1 | Active |
| DEC-011 | Dual-market architecture: shared infra, split data | Active |
| DEC-012 | Customer contact on Assessment row | Active |
| DEC-013 | No `git stash` from sandbox | Active |
| DEC-014 | Staging environment architecture | Active |
| DEC-015 | Dual keepalive crons (Sun + Wed) | Active |
| DEC-022 | Desktop Commander for git ops | Active |
| DEC-023 / DEC-051 | NEXT_PUBLIC_ENV=staging never on prod | Active |
| DEC-030 | apiFetch requires explicit token: | Active |
| DEC-066 | DNS in Hostinger (NOT Cloudflare) | Active |
| DEC-067 | Vercel staging deploys main (interim) | Will be superseded in Stage 6 |
| DEC-068 | DNS for mainnov.tech in Hostinger | Active |
| DEC-069 | StagingBanner is RSC, auth-only | Active |
| **DEC-070** | **Staging-first workflow canonical** | **Active after Stage 7 sign-off** |
| MARKET_GUIDE.md | Dual-market routing rules | Active |

---

## 15. Concrete worked examples

### Example A — Tiny copy change (frontend-only)

> "Change the 'Send via WhatsApp' button label on PK to 'Send on WhatsApp'."

1. `git checkout staging && git pull && git checkout -b chore/whatsapp-button-copy`
2. Edit `scopesnap-web/lib/urdu-strings.ts` (English string only, no Urdu impact)
3. `git commit -m "chore(ui): correct WhatsApp button copy on PK"` and push
4. Open PR to `staging`, merge
5. Wait ~2 min, visit `pk-staging.snapai.mainnov.tech`, navigate to assessment view, confirm button reads "Send on WhatsApp"
6. From `/tmp/snapai_main`: `./scripts/promote-to-prod.sh scopesnap-web/lib/urdu-strings.ts`
7. Wait ~2 min, visit `pk.snapai.mainnov.tech`, confirm button reads "Send on WhatsApp"

Total time: ~10 minutes including waiting.

### Example B — Backend bug fix

> "The `/api/diagnostic/list` endpoint returns 500 when assessment has no resolved fault."

1. `git checkout staging && git pull && git checkout -b fix/bug-040-diagnostic-list-null-fault`
2. Edit `scopesnap-api/api/diagnostic.py` — add null guard around fault resolution
3. Commit, push, PR to `staging`, merge
4. Wait ~3 min for Railway redeploy
5. On `staging.snapai.mainnov.tech`, create an assessment that doesn't resolve to a fault, hit `/diagnoses` — list loads
6. From `/tmp/snapai_main`: `./scripts/promote-to-prod.sh scopesnap-api/api/diagnostic.py`
7. Wait ~3 min, verify on `snapai.mainnov.tech`
8. Update `ACTIVE_TASKS.md` with BUG-040 entry in "Bugs Resolved" section

### Example C — Migration

> "Add a new column `homeowner_signature_url` to `estimates` table."

1. `git checkout staging && git pull && git checkout -b migration/035-homeowner-signature`
2. Write migration `scopesnap-api/db/migrations/versions/035_homeowner_signature_url.py`:
   - `upgrade()`: `op.add_column('estimates', sa.Column('homeowner_signature_url', sa.String(), nullable=True))`
   - `downgrade()`: `op.drop_column('estimates', 'homeowner_signature_url')`
3. Commit, push, PR to `staging`, merge
4. Wait ~3 min for Railway staging redeploy + alembic upgrade
5. Verify: `SELECT version_num FROM alembic_version;` on staging Supabase → `035`
6. Verify: `\d estimates` shows the new column
7. From `/tmp/snapai_main`: `./scripts/promote-to-prod.sh scopesnap-api/db/migrations/versions/035_homeowner_signature_url.py`
8. Wait ~3 min, verify `version_num = 035` on production Supabase, column exists
9. Update `PROJECT_BRAIN.md` Alembic row: `035 (homeowner_signature_url) | Applied | <date>`

### Example D — Hotfix

> "Production reports endpoint returning 500 across all reports. Found root cause: missing import in `reports.py` after recent merge."

1. Document incident in `ACTIVE_TASKS.md` "Active Incidents" → `INCIDENT-2026-05-23-01`
2. From `/tmp/snapai_main`: `git checkout main`
3. Edit `scopesnap-api/api/reports.py` — add missing `from datetime import datetime`
4. `git commit -m "hotfix: missing datetime import in reports.py (incident: 2026-05-23-01)"`
5. `git push origin main`
6. Wait ~3 min, hit any production `/r/{slug}/{reportId}` URL — confirm 200
7. Within 24h: `git checkout staging && git merge origin/main && git push origin staging`
8. Write retrospective DEC entry: why staging tests passed but prod failed (likely answer: this file was edited directly on main by some earlier process — exactly the kind of thing this workflow prevents going forward)

---

## 16. Maintenance of this document

WORKFLOW.md itself follows the standard workflow. Updates to this file:

1. Branch off staging
2. Edit `ScopeSnapAI/WORKFLOW.md`
3. PR to staging, merge
4. (No staging verification needed — this is doc only, doesn't affect deploys)
5. Promote to main via the script
6. Update `Last updated` line at top with date and one-line summary of change

The only exception: corrections that are factually wrong (e.g., wrong project ID) — those are doc hotfixes and can be edited directly on `main` with the same incident documentation as code hotfixes.

---

*Last updated: 2026-05-23 — initial draft establishing staging-first workflow as DEC-070. Activates after Stage 7 sign-off.*

---

## 16. Brain-file provenance metadata (added 2026-07-06 — brain files cleanup Phase 2d)

**Rule:** Every substantive entry (rule, fact, claim, threshold) in a brain file carries a small YAML metadata block above it, so the weekly auto-audit can detect stale content mechanically.

### Format

```yaml
---
added: 2026-07-06
last_verified: 2026-07-06
source: DEC-129
---
```

Three fields, all required:
- **`added:`** — ISO date the entry was first written into the brain file
- **`last_verified:`** — ISO date the entry was last confirmed against live state (Supabase, prod app, git log, etc.)
- **`source:`** — canonical reference — a DEC number, a user rule date, a legal chat citation, or a URL

### Where to apply

- **STATUS.md open blockers** — each blocker line gets metadata (added / last_verified / owner)
- **PROJECT_BRAIN.md CRITICAL RULES table** — each row carries the source column (already done); add `last_verified` in a footnote when confirmed
- **DECISIONS.md** — each DEC-XXX already carries an implicit `added:` in the header date; add `last_verified:` when re-checking
- **TECH_STACK.md** — each infrastructure claim (Alembic head, service URL, brand data version) carries metadata
- **MARKET_GUIDE.md** — market status banners carry metadata

### Where NOT to apply

- **Header text** (titles, section titles) — no metadata needed
- **Prose narrative** — no metadata (this is why prose is limited to top-of-file current-state paragraphs)
- **Historical archive files (`*_HISTORY.md`)** — no metadata (frozen archives, never re-verified)

### Staleness triggers (weekly auto-audit checks)

- `last_verified` > 60 days old → flag as WARNING
- `last_verified` > 180 days old → flag as VIOLATION
- No `last_verified` at all → flag as MISSING_METADATA warning

### Example: an entry with metadata

```markdown
---
added: 2026-07-05
last_verified: 2026-07-05
source: Legal chat 2026-07-05, Alfred (nav)
---
**Card #21 Heat Exchanger + Combustion Safety Check = Tier D indefinite hold** — six gates must clear (insurance rider, ToS rewrite, homeowner report language, threshold recalibration, PE engineering review, full audit trail). No CO / HX / combustion safety in scope until then.
```

### Enforcement

The weekly auto-audit (`snapai-brain-files-weekly-audit` scheduled task, Fridays 09:00 CT) checks provenance metadata coverage and staleness. Missing or stale metadata generates a report entry — not a hard block. Provenance is the audit's earliest-warning signal that a rule may be drifting away from reality.

### Reference

Full plan: `SnapAI_Brain_Files_Management_Plan_2026-07-05.md` Part 6 Rule 4 (provenance metadata).

---

## 17. Session Learnings Log — the SESSION_LOG_* archetype (added 2026-07-06 — brain files cleanup Phase 3)

**Rule:** Every substantive session that produces retrospective content — root causes traced, hypotheses tried, failures learned from — writes a dedicated `SESSION_LOG_YYYY-MM-DD_<topic>.md` file. This is the deep-narrative counterpart to the short brain-file summaries.

### Location + Naming

**Folder:** `ScopeSnapAI/session_logs/`

**Filename:** `SESSION_LOG_YYYY-MM-DD_<snake_case_topic>.md`

Examples:
- `SESSION_LOG_2026-07-06_brain_files_cleanup.md`
- `SESSION_LOG_2026-07-05_deep_legal_audit.md`
- `SESSION_LOG_2026-06-20_scoring_overhaul.md` (Omni pattern)

### Standard sections (template)

Every session log includes:

1. **Metadata header** — duration, participants, related workstream, related files (with computer:// URLs)
2. **Context** — what we started with (2-3 sentences)
3. **Goal** — what we tried to accomplish (1-2 sentences)
4. **What we tried** — chronological hypotheses with worked/failed/partial results
5. **What worked** — specific things that stuck
6. **What DIDN'T work** — dead ends, wrong assumptions, false paths (highest-value section per Bryan Orr)
7. **Root causes** — analytical write-up of why the failed attempts failed
8. **Resolution** — the final approach that worked (specific enough to replicate)
9. **Lessons for next time** — actionable, not vague
10. **Follow-up items** — checkboxes with owner + rough effort
11. **References** — related DECs, brain files, plan docs, audit docs
12. **Change log** — session-log-level change history

### When to create one (the "future-you" test)

**Create a session log when:**
- Substantive debug/fix (something was broken; you tried multiple things before finding root cause)
- Non-trivial build (new subsystem, major refactor, migration)
- Multi-hour session with clear before/after state
- Ad-hoc closeout / audit / plan doc worthy of preservation

**Skip when:**
- Simple one-line fix
- Straightforward planned work with no surprises
- Pure discussion / strategic planning session (goes in ACTIVE_TASKS session block or a plan doc)
- Session where nothing worked and no learning surfaced

**Rough test:** *"If I forgot this in 3 months, would future me want the story?"* Yes → session log. No → skip.

### How this connects to the other brain files

**Loose coupling:**

- **ACTIVE_TASKS.md session block** stays short (DONE + OPEN + a one-line pointer to the session log)
- **DECISIONS.md** — if a session log surfaced a decision, the DEC references the log as source
- **PROJECT_BRAIN.md CRITICAL RULES** — if a lesson became a rule, the rule references the session log
- **STATUS.md** milestones — short entry with a pointer to the session log

Result: brain files stay small and load fast; deep narrative lives in rarely-opened session logs.

### Archetype rules

- **Immutable append-only** — like DECISIONS.md, never rewritten
- **No line cap** — grows as needed; queried, not scanned
- **Provenance metadata not required at entry level** — the file itself is a dated snapshot; whole-file metadata in the top-of-file section suffices

### Session-end update ritual (analyze + propose, do NOT ask questions)

When Shoab says *"update the brain files"* or at end of a substantive session:

1. The AI analyzes what happened in the session against the routing table in `SnapAI_Project_Instructions.md` Section 7.
2. The AI presents ONE consolidated proposal: *"I'll update these files with these changes: [file 1] — [summary]. [file 2] — [summary]. ... Say yes to write all, or flag exceptions."*
3. Shoab replies "yes" or flags specific items.
4. AI executes in one pass. Reports result.

**Do NOT ask a series of yes/no questions.** The AI already knows what each file is for (see Section 7 routing table). Analyze once, propose once, execute once.

**Only exception where asking is OK:** when the session log topic isn't obvious (mixed workstreams), the AI proposes 1-3 candidate filenames and lets Shoab pick.

### Retroactive session log candidates (Rob's suggestion)

Existing docs that are basically session logs and could be renamed with zero content change:
- `STAGING_MIRROR_CLOSEOUT.md` → `session_logs/SESSION_LOG_2026-05-24_staging_mirror_closeout.md`
- `STAGING_FIX_PLAN.md` → `session_logs/SESSION_LOG_2026-05-22_staging_fix_plan.md`
- `AUDIT_FINDINGS_DETAILED.md` / `AUDIT_REPORT_Phase3_QA.md` / `CODE_AUDIT_REPORT.md` → date-tag each and move to session_logs/

Optional retrofit — not required for the pattern to work forward.

### Reference

Full plan: `SnapAI_Brain_Files_Management_Plan_2026-07-05.md`.
First instance: `session_logs/SESSION_LOG_2026-07-06_brain_files_cleanup.md`.
Omni pattern reference: `Claude Omni/SESSION_LOG_2026-06-20_scoring_overhaul.md`, `SESSION_LOG_2026-06-21_phase1_frontend.md`, `SESSION_LOG_2026-06-21_phase2A_2B.md`.
