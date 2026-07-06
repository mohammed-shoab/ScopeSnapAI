# SESSION LOG — Staging fix plan — 2026-05-22

**Retrofit note:** Renamed from `STAGING_FIX_PLAN.md` on 2026-07-06 as part of the SESSION_LOG_* archetype adoption (Phase 3 retrofit batch B / Option B). Content is unchanged from the original doc — only wrapped with this header + relocated to `session_logs/`.

**Original file (in _brain_backup_2026-07-06/):** `STAGING_FIX_PLAN.md`

---

# SnapAI — Staging Fix & Isolation Plan

> **Purpose:** Complete plan to fix the broken staging environment and ensure zero overlap with production.
> **Written:** 2026-05-22
> **Executed:** 2026-05-22
> **Status:** COMPLETE — all phases 1-10 executed. scopesnap-web-staging.vercel.app VALID. Custom domains pending DNS propagation (Hostinger TTL 14400s).
> **Key discovery:** DNS is in Hostinger (mshoabarabi@gmail.com), NOT Cloudflare. CNAME updated to e08b930de4517e81.vercel-dns-017.com.

---

## CRITICAL RULE — READ FIRST

**This plan makes ZERO changes to production.** Production is:
- https://snapai.mainnov.tech (Houston)
- https://pk.snapai.mainnov.tech (PK)
- https://scopesnap-api-production.up.railway.app (Railway backend)
- Supabase project `quqrvnoguofbjacrxcim` (production DB)
- Vercel project `scope-snap-ai` (production frontend)

If any action touches any of the above resources, STOP and ask the user for explicit confirmation before proceeding. The only exception is BUG-031 in Phase 2 (a production env var that is wrongly set and is causing the staging banner to appear on production — fixing it is a production fix but it is the correct and safe fix).

---

## PART A — What Should Exist (Reference Architecture)

This is the intended end state. Every item below should be completely separate from production.

### Staging Resources (all must be isolated)

| Resource | Expected Value | Notes |
|---|---|---|
| Staging frontend US | https://staging.snapai.mainnov.tech | Custom domain on staging Vercel project |
| Staging frontend PK | https://pk-staging.snapai.mainnov.tech | Custom domain on staging Vercel project |
| Staging frontend (Vercel default) | https://scopesnap-web-staging.vercel.app | Always-on default URL |
| Staging backend | https://scopesnap-api-staging.up.railway.app | Separate Railway service |
| Staging Supabase project | `pqmgveqkuckbvyygsilk` (ap-northeast-1) | Completely separate DB from production |
| Staging Clerk app | `firm-chamois-61` (test-mode keys only) | Test keys = pk_test_... / sk_test_... |
| Staging R2 bucket | `scopesnap-uploads-staging` | Separate from production R2 bucket |
| Staging git branch | `staging` on `mohammed-shoab/ScopeSnapAI` | Deploys to staging Vercel + staging Railway |

### Production Resources (NEVER TOUCH during this plan)

| Resource | Value |
|---|---|
| Production frontend US | https://snapai.mainnov.tech |
| Production frontend PK | https://pk.snapai.mainnov.tech |
| Production backend | https://scopesnap-api-production.up.railway.app |
| Production Supabase | `quqrvnoguofbjacrxcim` |
| Production Clerk app | Live keys (pk_live_... / sk_live_...) |
| Production R2 bucket | `scopesnap-uploads` (production bucket) |
| Production git branch | `main` |
| Production Vercel project | `scope-snap-ai` |

---

## PART B — Current Known Problems

Based on the audit done by the other AI, these are the confirmed issues:

| # | Problem | Severity | Affects Production? |
|---|---|---|---|
| BUG-031 | Staging banner (amber bar) is appearing on production PK site (pk.snapai.mainnov.tech) | HIGH | YES — production is showing staging UI |
| STAG-001 | Staging Vercel project is deploying from `main` branch instead of `staging` branch | HIGH | No — but it means staging code = production code, which defeats isolation |
| STAG-002 | Staging Vercel builds are failing — `npm install --legacy-peer-deps` exits with 1 | HIGH | No |
| STAG-003 | Railway staging backend returns 502 — service crashed or stopped | HIGH | No |
| STAG-004 | Custom domains `staging.snapai.mainnov.tech` and `pk-staging.snapai.mainnov.tech` are not configured on the staging Vercel project | MEDIUM | No |
| STAG-005 | No PK market accessible on staging (no pk-staging domain = no way to test PK flow on staging) | MEDIUM | No |

---

## PART C — Environment Variable Reference

This is the complete env var table for both environments. Any AI executing this plan must verify every row below during the audit phase. If a staging env var points to a production value, that is a critical overlap bug.

### Vercel — Production Project (`scope-snap-ai`)

| Variable | Expected Value | What It Does |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `https://scopesnap-api-production.up.railway.app` | Points to production Railway backend |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | `pk_live_...` (live key, starts with pk_live) | Clerk live auth |
| `CLERK_SECRET_KEY` | `sk_live_...` (live key) | Clerk live auth backend |
| `NEXT_PUBLIC_ENV` | `production` | Enables Clerk middleware; must NOT be `staging` |
| `NEXT_TELEMETRY_DISABLED` | `1` | Disables Next.js telemetry |
| Supabase keys | Points to `quqrvnoguofbjacrxcim` | Production DB |

### Vercel — Staging Project (`scopesnap-web-staging`)

| Variable | Expected Value | What It Does |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `https://scopesnap-api-staging.up.railway.app` | Must point to STAGING Railway, NOT production |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | `pk_test_...` (test key, starts with pk_test) | Clerk staging/test auth |
| `CLERK_SECRET_KEY` | `sk_test_...` (test key) | Clerk staging auth backend |
| `NEXT_PUBLIC_ENV` | `staging` | Triggers StagingBanner; treats env as dev (bypasses Edge Clerk crash) |
| `NEXT_TELEMETRY_DISABLED` | `1` | Same as production |
| Supabase keys | Must point to `pqmgveqkuckbvyygsilk` | Staging DB — NOT production |

**The critical separation test:** If `NEXT_PUBLIC_API_URL` in staging points to the production Railway URL, every staging action writes to production data. This must be verified before any staging test.

### Railway — Production Backend

| Variable | Expected Value |
|---|---|
| `DATABASE_URL` | Supabase pooler URL for project `quqrvnoguofbjacrxcim` |
| `ENVIRONMENT` | `production` |
| `RAILWAY_SERVICE_NAME` | Must clearly say production (not staging) |

### Railway — Staging Backend

| Variable | Expected Value |
|---|---|
| `DATABASE_URL` | Supabase pooler URL for project `pqmgveqkuckbvyygsilk` — NOT production |
| `ENVIRONMENT` | `staging` |
| `RAILWAY_SERVICE_NAME` | Must clearly say staging |

---

## PART D — The Fix Plan (Phase by Phase)

Execute in this exact order. Do not skip phases. Do not proceed to the next phase until the current one is fully verified.

---

### Phase 1 — Pre-Flight Audit (Read-Only, No Changes)

**Goal:** Establish ground truth before touching anything.

**1.1 — Check Railway staging service status**

Navigate to Railway dashboard → project `0e78dd68-ce72-46be-a2b1-7d3119de40a4` → find the staging service (NOT the production service `a23d5cad-d8c9-434e-a3dc-89634d8642ab`).

Record:
- Is the staging service running, crashed, or sleeping?
- What branch is it watching? (Should be `staging`, but may be `main`)
- What is the last successful deploy commit hash?
- What are the env vars set? Specifically `DATABASE_URL` and `ENVIRONMENT`.

**1.2 — Check Vercel staging project settings**

Navigate to Vercel dashboard → project `scopesnap-web-staging` (project ID `prj_vq1rWfPN9tD3k82OLFjfIxmNdULc`).

Record:
- Which git branch is it watching? (Should be `staging`)
- What is the exact npm install error in the failed build logs? (Need the full error message)
- What Node.js version is configured in project settings?
- What domains are configured? (Expect: none currently, need to add staging domains)
- What env vars are set? List all of them and their values (except sensitive ones — note those exist but are masked).

**1.3 — Check Vercel production project for BUG-031**

Navigate to Vercel dashboard → project `scope-snap-ai` (NOT scopesnap-web-staging).

Record:
- What value is `NEXT_PUBLIC_ENV` set to? It must be `production`. If it is `staging` or blank, that is the cause of BUG-031.
- Are there any environment-specific overrides? Vercel allows setting different values per environment (Production / Preview / Development). Check if `NEXT_PUBLIC_ENV` has a different value set for Preview vs Production deployments.
- What does the PK market deployment specifically have for `NEXT_PUBLIC_ENV`? (Since BUG-031 only affects PK, the issue may be in a Preview override that applies to pk.snapai.mainnov.tech)

**1.4 — Check staging git branch state**

From a /tmp clone of the staging branch:
```bash
git clone --branch staging https://x-token:$GH_PAT@github.com/mohammed-shoab/ScopeSnapAI.git /tmp/snapai_staging_audit
cd /tmp/snapai_staging_audit
git log --oneline -10
cat scopesnap-web/package.json | grep '"node"'
cat scopesnap-web/.nvmrc 2>/dev/null || echo "no .nvmrc"
cat scopesnap-web/package.json | grep '"engines"' -A 5
```

Record:
- Latest commit on staging branch
- What Node.js version is specified in package.json engines or .nvmrc
- Whether staging branch has a package-lock.json that is out of sync with main

**1.5 — Verify DNS for staging domains**

Check DNS for both staging domains:
- Does `staging.snapai.mainnov.tech` have a CNAME record pointing to Vercel?
- Does `pk-staging.snapai.mainnov.tech` have a CNAME record pointing to Vercel?

If yes: the DNS exists but the Vercel project just doesn't have the domain configured (easy fix).
If no: DNS was removed and needs to be recreated in Cloudflare (or wherever the DNS is managed).

**1.6 — Record findings before proceeding**

Write a brief summary of what was found in each check. Only proceed to Phase 2 once the audit is complete and recorded.

---

### Phase 2 — Fix BUG-031 (Staging Banner on Production PK)

**Goal:** Remove the staging amber banner from the production PK site. This is the only phase that touches production.

**Why this is safe:** BUG-031 is caused by a wrong env var value on the production Vercel project. Fixing it means setting `NEXT_PUBLIC_ENV` back to `production` on the production project. This does not change any code, deploy anything, or modify the database. It only corrects a mis-set environment variable.

**2.1 — Identify the cause**

From the Phase 1.3 audit:
- If `NEXT_PUBLIC_ENV` is set to `staging` anywhere in the production Vercel project → change it to `production`.
- If `NEXT_PUBLIC_ENV` has a Preview environment override set to `staging` → remove that override (Preview env should also be `production` or blank).
- If `NEXT_PUBLIC_ENV` is already `production` everywhere, the cause is in the code (StagingBanner.tsx logic) and needs code investigation.

**2.2 — Fix the env var**

In Vercel → project `scope-snap-ai` (production):
- Environment: `NEXT_PUBLIC_ENV` = `production` for ALL environments (Production + Preview + Development)
- Save changes
- Trigger a redeploy of the production project so the new env var takes effect

**2.3 — Verify fix**

After redeploy completes:
- Visit https://pk.snapai.mainnov.tech
- Sign in
- Confirm NO amber banner appears anywhere
- Visit https://snapai.mainnov.tech (Houston)
- Sign in
- Confirm NO amber banner appears anywhere

**2.4 — Check StagingBanner.tsx placement**

The StagingBanner is currently placed in `app/(app)/layout.tsx` — it only renders on authenticated pages. Confirm it does NOT appear in `app/layout.tsx` (root layout) or `app/(public)/layout.tsx` (public pages like the landing page and homeowner report). If it is in the root layout, it would need to be moved.

---

### Phase 3 — Fix Vercel Staging Branch Wiring

**Goal:** Make staging Vercel deploy from the `staging` branch, NOT `main`.

**Why this matters:** While staging deploys from `main`, every push to `main` (which goes to production) also triggers a staging build. Staging and production always have identical code. This defeats the entire purpose of having a separate staging environment.

**3.1 — Change the branch in Vercel**

In Vercel → project `scopesnap-web-staging`:
- Go to Settings → Git
- Change "Production Branch" from `main` to `staging`
- Save

**3.2 — Disable automatic preview deployments from main on staging**

In the same Git settings:
- Ensure that the staging Vercel project does NOT also build preview deployments from `main`.
- Only the `staging` branch should trigger builds on the `scopesnap-web-staging` project.

**3.3 — Trigger a manual redeploy from the staging branch**

After changing the branch:
- Trigger a manual redeploy of the staging Vercel project from the `staging` branch.
- Monitor the build logs — the npm install failure from STAG-002 will likely still appear.
- This is expected; Phase 4 fixes that.

---

### Phase 4 — Fix npm Build Failure on Staging Vercel

**Goal:** Make `npm install --legacy-peer-deps` succeed on the staging Vercel project.

**4.1 — Read the full build error**

From Phase 1.2, the full npm install error message was recorded. The most common causes are:

- **Node.js version mismatch**: The staging Vercel project has a Node.js version configured that is different from what `package.json` specifies. For example, Vercel defaults to Node 18 but the project uses Node 20.
- **Conflicting peer dependencies that `--legacy-peer-deps` cannot resolve**: A package in the staging branch's `package-lock.json` has a dependency that is incompatible even with `--legacy-peer-deps`.
- **package-lock.json out of sync**: The staging branch has a `package-lock.json` that was generated with a different Node.js version than what Vercel is using.

**4.2 — Fix based on cause**

**If the cause is Node.js version mismatch:**
- In Vercel → project `scopesnap-web-staging` → Settings → General → Node.js Version
- Set it to match what is in `package.json` engines field (found in Phase 1.4)
- Trigger a redeploy — the build should now pass

**If the cause is package-lock.json out of sync:**
- From the `/tmp/snapai_staging_audit` clone of the staging branch:
  ```bash
  cd /tmp/snapai_staging_audit/scopesnap-web
  rm package-lock.json
  npm install --legacy-peer-deps
  git add package-lock.json
  git commit -m "fix(staging): regenerate package-lock.json for Node compatibility"
  git push origin staging
  ```
- This regenerates the lock file with the correct Node version and pushes only to `staging` (NOT to `main`/production).

**If the cause is a conflicting package:**
- Read the full error. The error will name the specific package causing the conflict.
- The fix will be specific to that package. Do not guess — read the error first.

**4.3 — Verify build passes**

After the fix, the Vercel staging build must show a green checkmark. The build log must not contain any errors. The deployed staging URL `https://scopesnap-web-staging.vercel.app` must load the app.

---

### Phase 5 — Fix Railway Staging Backend

**Goal:** Get `https://scopesnap-api-staging.up.railway.app/health` returning `{"status":"ok","db":"connected","environment":"staging"}`.

**5.1 — Check which branch Railway staging is watching**

In Railway dashboard → staging service → Settings → Source:
- Which GitHub branch is it watching? It should be `staging`.
- If it is watching `main`, change it to `staging` and save.

**5.2 — Check the DATABASE_URL**

In Railway dashboard → staging service → Variables:
- What does `DATABASE_URL` point to? It must contain `pqmgveqkuckbvyygsilk` (the staging Supabase project ID).
- If it contains `quqrvnoguofbjacrxcim` (production Supabase ID), the staging backend is writing to production data. This is a critical overlap — fix immediately by updating `DATABASE_URL` to the staging Supabase pooler URL.
- The staging Supabase pooler URL format: `postgresql://postgres.pqmgveqkuckbvyygsilk:[PASSWORD]@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres`
- The password is in `C:\Users\dell\My Drive\Personal Claude\.staging_secrets.txt` — do NOT echo it to any log or console.

**5.3 — Check the ENVIRONMENT variable**

In Railway staging service → Variables:
- `ENVIRONMENT` should be set to `staging`.
- If missing or set to `production`, add/correct it.

**5.4 — Restart/Redeploy the staging service**

- Click "Redeploy" on the staging Railway service.
- Wait for the deployment to complete (~3-5 minutes).
- Railway will automatically run `alembic upgrade head` via `start.sh` on boot.
- The staging Supabase DB is already at alembic head `025` — no new migrations needed at this time.

**5.5 — Verify health check**

Fetch `https://scopesnap-api-staging.up.railway.app/health`.

Expected response:
```json
{"status":"ok","db":"connected","environment":"staging","version":"0.1.0"}
```

If `environment` says `production`, the `ENVIRONMENT` env var is wrong. Fix it and redeploy.
If the response is 502, the service is still down — check Railway logs for the crash reason.

---

### Phase 6 — Restore Custom Staging Domains

**Goal:** Make `staging.snapai.mainnov.tech` and `pk-staging.snapai.mainnov.tech` resolve to the staging Vercel project.

**6.1 — Check DNS first (from Phase 1.5)**

**If DNS records exist in Cloudflare (CNAME records pointing to Vercel):**
- The DNS is fine. The problem is just that the Vercel staging project doesn't have these domains registered.
- Skip to Step 6.2.

**If DNS records do NOT exist:**
- Go to Cloudflare DNS for `mainnov.tech`.
- Add two CNAME records:
  - `staging` → `cname.vercel-dns.com` (or the Vercel CNAME target shown when you add a domain to a Vercel project)
  - `pk-staging` → `cname.vercel-dns.com`
- Proxy status: DNS only (grey cloud), NOT proxied — Vercel handles SSL.
- DNS propagation: typically 1-5 minutes with Cloudflare.

**6.2 — Add domains to Vercel staging project**

In Vercel → project `scopesnap-web-staging` → Settings → Domains:
- Add `staging.snapai.mainnov.tech`
- Add `pk-staging.snapai.mainnov.tech`
- Vercel will show a DNS verification prompt. If DNS was set correctly in Step 6.1, it will verify automatically.

**6.3 — Verify market detection for PK staging**

The app detects the market via hostname in `lib/market.ts` using `detectMarket()`. The `pk-staging.snapai.mainnov.tech` hostname must be recognized as the PK market.

Check `scopesnap-web/lib/market.ts` on the `staging` branch:
```bash
grep -n "pk-staging\|pk\." /tmp/snapai_staging_audit/scopesnap-web/lib/market.ts
```

The `detectMarket()` function should have a condition that catches `pk-staging` hostname as the PK market. The likely pattern is checking if `hostname.startsWith("pk")` or if `hostname.includes("pk")`. If the function only checks for `pk.snapai.mainnov.tech` explicitly (not a prefix check), then `pk-staging.snapai.mainnov.tech` will default to the US market.

**If market detection needs updating for staging hostnames:**
- Edit `lib/market.ts` on the `staging` branch to add `pk-staging.snapai.mainnov.tech` to the PK market hostname list.
- Commit and push to `staging` branch ONLY (not `main`).
- Trigger a staging redeploy.

**6.4 — Verify both domains load the correct market**

- Visit `https://staging.snapai.mainnov.tech` → should show Houston (US) market
- Visit `https://pk-staging.snapai.mainnov.tech` → should show PK market (Urdu sidebar, PKR currency, PK brands)

---

### Phase 7 — Full Environment Variable Audit

**Goal:** Confirm with certainty that no staging env var points to any production resource.

Run through this checklist for the staging Vercel project (`scopesnap-web-staging`):

| Check | Pass Condition | Fail Condition |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | Contains `staging.up.railway.app` | Contains `production.up.railway.app` |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Starts with `pk_test_` | Starts with `pk_live_` |
| `CLERK_SECRET_KEY` | Starts with `sk_test_` | Starts with `sk_live_` |
| `NEXT_PUBLIC_ENV` | Equals `staging` | Equals `production` or missing |
| Any Supabase URL/key | Contains `pqmgveqkuckbvyygsilk` | Contains `quqrvnoguofbjacrxcim` |

Run through this checklist for the staging Railway service:

| Check | Pass Condition | Fail Condition |
|---|---|---|
| `DATABASE_URL` | Contains `pqmgveqkuckbvyygsilk` | Contains `quqrvnoguofbjacrxcim` |
| `ENVIRONMENT` | Equals `staging` | Equals `production` or missing |
| Any Clerk key | Starts with `sk_test_` | Starts with `sk_live_` |
| Any R2 bucket reference | Contains `staging` in bucket name | Contains production bucket name |

**If any check fails:** Fix the env var immediately before proceeding. Do NOT run any tests against staging until all env vars pass.

---

### Phase 8 — Visual Labeling Verification

**Goal:** A human looking at either environment must immediately know which one they are on. No ambiguity.

**8.1 — Staging banner**

On staging (any authenticated page):
- The amber bar "⚠ STAGING — not production data" must be visible.
- It must appear on: dashboard, assess, settings, diagnoses, estimates — any page behind `app/(app)/layout.tsx`.
- It must NOT appear on: the landing page, the homeowner report (public pages).

On production (any authenticated page):
- The amber bar must NOT appear. (BUG-031 should have been fixed in Phase 2.)

**8.2 — URL labels**

Staging URLs contain `staging` or `pk-staging` in the hostname. This is sufficient visual differentiation for URLs. No additional URL-level labeling is needed.

**8.3 — Railway service naming**

In the Railway project, the two services must be clearly named:
- Production service: `scopesnap-api` or `production` — must NOT be named `staging`
- Staging service: `scopesnap-api-staging` or similar — must NOT be named `production`

If the names are confusing, rename them in Railway settings. This prevents an AI or human from accidentally redeploying the wrong service.

**8.4 — Vercel project naming**

- Production: `scope-snap-ai` — correct
- Staging: `scopesnap-web-staging` — correct

Both names are already distinct. No change needed.

---

### Phase 9 — Staging Smoke Test (End-to-End)

**Goal:** Confirm staging works end-to-end, independently of production.

Run each of these on staging only. Do NOT test production during this phase (it should already be working and this plan does not want to risk production).

**9.1 — Backend health**
- `GET https://scopesnap-api-staging.up.railway.app/health`
- Expected: `{"status":"ok","db":"connected","environment":"staging"}`

**9.2 — Frontend loads**
- Visit `https://staging.snapai.mainnov.tech`
- Confirm: landing page loads, NO staging banner on landing page
- Sign in with a staging Clerk test account
- Confirm: staging banner appears on dashboard

**9.3 — PK market on staging**
- Visit `https://pk-staging.snapai.mainnov.tech`
- Confirm: PK market (Urdu sidebar visible, PKR currency, R-32 selector)
- Confirm: staging banner visible after login

**9.4 — Basic diagnostic flow on staging**
- Start a Not Cooling diagnostic on staging
- Confirm it completes without errors
- Confirm data is written to staging Supabase (`pqmgveqkuckbvyygsilk`), NOT production Supabase (`quqrvnoguofbjacrxcim`)
- Verify in Supabase staging dashboard: new diagnostic_session row exists

**9.5 — Confirm production is untouched**
- `GET https://scopesnap-api-production.up.railway.app/health` — still returns ok
- Visit `https://snapai.mainnov.tech` — still loads, no staging banner
- Check production Supabase `quqrvnoguofbjacrxcim` — no new test rows from Phase 9 tests

---

### Phase 10 — Documentation Update

**Goal:** Update all project docs so both environments are clearly described, and the separation rules are explicit.

**10.1 — Update PROJECT_BRAIN.md**

After all fixes are confirmed, update:
- Live URLs section: staging URLs (with correct status — all ✅ Live)
- Infrastructure IDs section: confirm staging IDs are accurate
- Current Deployment State: update staging deployment table with current commits and alembic head
- QA History: add a row for this staging fix session
- Header timestamp

**10.2 — Update CONTINUATION_PROMPT.md**

Update:
- Staging Environment section: all URLs marked live, correct alembic head, correct git HEAD on staging branch
- Current Git State: update staging HEAD commit

**10.3 — Update TECH_STACK.md**

Update:
- Header: note BUG-031 resolved
- Live App Locations table: add staging URLs as a separate section
- Add any new workarounds discovered during this fix (as WA-13, WA-14, etc.)

**10.4 — Update ACTIVE_TASKS.md**

- Add BUG-031 to the completed bugs list (with fix details)
- Add STAG-001 through STAG-005 as completed items
- Update "Last QA Run" to reflect this staging fix session

**10.5 — Add a SEPARATION_RULES section to PROJECT_BRAIN.md**

This is new. Add a permanent section (near the top, after Infrastructure IDs) that reads:

```
## Environment Separation Rules (permanent — do not remove)

These rules prevent production and staging from ever overlapping.

### Production-only resources (never reference these from staging)
- Supabase project: quqrvnoguofbjacrxcim
- Railway service: a23d5cad-d8c9-434e-a3dc-89634d8642ab
- Vercel project: scope-snap-ai
- Clerk keys: pk_live_* / sk_live_*
- Railway URL: scopesnap-api-production.up.railway.app

### Staging-only resources (never reference these from production)
- Supabase project: pqmgveqkuckbvyygsilk
- Railway staging URL: scopesnap-api-staging.up.railway.app
- Vercel staging project: scopesnap-web-staging / prj_vq1rWfPN9tD3k82OLFjfIxmNdULc
- Clerk keys: pk_test_* / sk_test_*
- Git branch: staging

### Separation check (run before any deploy)
1. Does NEXT_PUBLIC_API_URL in staging point to staging Railway? (must contain "staging")
2. Does DATABASE_URL in staging Railway point to staging Supabase? (must contain "pqmgveqkuckbvyygsilk")
3. Does NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY in staging start with "pk_test_"?
4. Does NEXT_PUBLIC_ENV in production say "production" (not "staging")?
5. Is staging Vercel watching the "staging" git branch (not "main")?

If any answer is No → fix before deploying.
```

---

## PART E — Phase Execution Order (Summary)

| Phase | Action | Touches Production? |
|---|---|---|
| 1 | Pre-flight audit — read only | Read-only only |
| 2 | Fix BUG-031 — correct NEXT_PUBLIC_ENV on production | YES — env var fix only, no code change |
| 3 | Fix Vercel staging branch wiring (main → staging) | No |
| 4 | Fix npm build failure on staging | No |
| 5 | Fix Railway staging backend (502 → healthy) | No |
| 6 | Restore custom staging domains | No |
| 7 | Full env var audit | No |
| 8 | Visual labeling verification | No |
| 9 | Staging smoke test | No |
| 10 | Documentation update | No |

---

## PART F — What Success Looks Like

When this plan is complete, the following must all be true simultaneously:

1. `https://snapai.mainnov.tech` — loads, NO staging banner, production data ✅
2. `https://pk.snapai.mainnov.tech` — loads, NO staging banner, production data ✅
3. `https://staging.snapai.mainnov.tech` — loads, AMBER staging banner visible after login, staging data only ✅
4. `https://pk-staging.snapai.mainnov.tech` — loads, AMBER staging banner, PK market, staging data only ✅
5. `https://scopesnap-api-staging.up.railway.app/health` — returns `{"environment":"staging"}` ✅
6. Staging Vercel deploys from `staging` branch — a push to `main` does NOT trigger staging build ✅
7. All staging env vars point to staging-only resources — verified in Phase 7 checklist ✅
8. All project docs (PROJECT_BRAIN, CONTINUATION_PROMPT, TECH_STACK, ACTIVE_TASKS) reflect the accurate state ✅

---

## PART G — Secrets Reference

The staging secrets (passwords, API tokens for staging services) are stored at:
`C:\Users\dell\My Drive\Personal Claude\.staging_secrets.txt`

⚠ This file must NEVER be committed to git.
⚠ The AI must NOT echo secret values to any log, console, or chat message.
⚠ The AI must NOT include secret values in any bat file that is also written to disk permanently.

When the AI needs a staging secret, it should read the file, use the value in-memory for the current operation, and not surface it.

---

*End of plan. Executing AI: read this entire document before starting Phase 1.*
