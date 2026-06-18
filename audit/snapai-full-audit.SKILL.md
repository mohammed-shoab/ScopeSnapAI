---
name: snapai-full-audit
description: >
  Comprehensive QA + security + performance audit orchestrator for the SnapAI HVAC
  diagnostic platform. Runs 24 audit steps across pre-deploy -> staging -> promote
  gate -> post-deploy phases with 3 modes (scoped, safe, full) and 10 cost mitigations.
  Delegates to community skills (Anthropic webapp-testing, GStack, Superpowers TDD)
  and local CLI tools (Semgrep, gitleaks, OWASP ZAP via Docker). Cowork-driven --
  no external API key required. Triggers: "/snapai-full-audit", "snapai full audit",
  "run full audit", "audit snapai", "snapai release audit". Default mode is `safe`.
  REQUIRES SnapAI_Audit_Framework_Setup.md prerequisites completed first.
---

# SnapAI Full Audit Skill

You are the SnapAI full-audit orchestrator. Your job: run the chosen audit mode
to completion, blocking only at Shoab confirmation gates, never silently passing
a check that didn't actually pass. You delegate execution to existing skills
where possible, run local CLI tools directly where appropriate, and orchestrate
the cost mitigations.

> **Reality note (2026-06-18):** the audit-synthetic *filtering* is implemented in
> **SDK code**, not via Sentry/PostHog dashboard inbound filters (those don't exist
> on our plans). Backend drop = env `SNAPAI_AUDIT_MODE=1` on Railway. Frontend drop =
> `sessionStorage.snapai_audit_mode='1'` (preferred) or `?audit_synthetic=1` (the URL
> param is **stripped on Clerk auth redirects**, so set the sessionStorage flag at page
> init). These filters were promoted to prod 2026-06-18 (DEC-090).

---

## Mode selection (do this FIRST)

Parse the invoking message for mode hints. Default to `safe` if ambiguous.

| User says | Mode |
|---|---|
| `/snapai-full-audit` (no mode) | safe |
| `/snapai-full-audit mode=scoped` OR "scoped audit" OR "audit this PR" | scoped |
| `/snapai-full-audit mode=safe` OR "monthly audit" OR "release audit" | safe |
| `/snapai-full-audit mode=full --confirm-i-understand-cost` OR "quarterly audit" + explicit confirm | full |

If user says `mode=full` WITHOUT `--confirm-i-understand-cost`, REFUSE and respond:
"Full mode runs unmitigated DAST + k6 stress testing. Expected cost: $3-7 extra
this Railway cycle. Confirm by re-invoking with `--confirm-i-understand-cost`
appended to your command."

State your detected mode at the top of every response: "AUDIT MODE: scoped|safe|full"

---

## Phase 0 -- Pre-flight checks (ALL MODES)

Run all 7 pre-flight checks. If any fail, ABORT and report which.

| # | Check | How to verify | Pass criterion |
|---|---|---|---|
| P1 | Railway compute cap is $15 (not $10) | Read Railway dashboard via Chrome MCP or check stored config | "$15.00" present |
| P2 | Sentry SDK filter is deployed to prod | git log on `main` OR staging behavior | backend `main.py` has `_sentry_before_send` returning None when `SNAPAI_AUDIT_MODE==1`; `sentry.client.config.ts` has `beforeSend` returning null on the audit flag |
| P3 | PostHog SDK filter is deployed to prod | git log on `main` OR staging behavior | `providers/PostHogProvider.tsx` has `before_send` returning null on the audit flag |
| P4 | Clerk audit-test users exist | Read `ScopeSnapAI/audit_test_user_credentials.env` + `.env.test` (local, gitignored) | 5 users per app. Staging = `ds.shoab+audit1..5@gmail.com`; prod = `ds.shoab+audit1,+audit12,+audit13,+audit14,+audit15@gmail.com`. Staging `userId`s present in `.env.test` |
| P5 | Docker + ZAP image cached | `docker images \| grep zap` | `ghcr.io/zaproxy/zaproxy` present (NOT the deprecated `owasp/zap2docker-stable`) |
| P6 | Semgrep + gitleaks CLI installed | `python -m semgrep --version && gitleaks version` | Both print version (semgrep runs as a Python module -- its Scripts dir is not on PATH) |
| P7 | Community skills loaded | List loaded skills | Anthropic `webapp-testing` + GStack (`qa`, `review`, `benchmark`, `canary`, `browse`) + Superpowers (`test-driven-development`, `systematic-debugging`, `brainstorming`) all present |

If user invokes any mode without ALL 7 prereqs met, respond:
"Cannot run audit -- prerequisites incomplete. Failed checks: [list]. Complete
SnapAI_Audit_Framework_Setup.md before re-invoking."

---

## Phase 0.5 -- Railway cost check (ALL MODES, mitigation #9)

Before any compute-spending step, check current Railway billing cycle usage
(open https://railway.com/workspace/usage via Chrome MCP, read "Current Usage").

| Current Railway usage | Mode behavior |
|---|---|
| < $7 | All modes proceed normally |
| $7-10 | scoped: proceed. safe: proceed with warning. full: ABORT with reason. |
| $10-12 | scoped: proceed. safe: ABORT. full: ABORT. |
| > $12 | All modes ABORT -- too close to $15 cap |

State the current usage at the top of every audit run report.

---

## Phase 0.7 -- Schedule check (full mode only, mitigation #7)

For mode=full only: check current UTC time. If between 14:00-22:00 UTC
(roughly US business hours 9am-5pm Central), REFUSE and respond:
"Full mode runs heavy DAST + k6 against staging during US business hours, which
will make staging unresponsive for any active Houston tester. Schedule for
off-hours (before 14:00 UTC or after 22:00 UTC = before 8am or after 5pm
Karachi local). Re-invoke after the window opens."

scoped and safe modes have NO schedule restriction (their staging impact is minor).

---

## Phase 1 -- Pre-deploy work (varies by mode)

### Scoped mode (per-PR audit)
- Run `python -m pytest scopesnap-api/` -- invoke via bash (pytest is installed as a module; not on PATH)
- Run the **audit harness** Playwright suite (the Next.js app does NOT declare `@playwright/test`,
  so authenticated flows live in the isolated `audit/` folder):
  `cd audit && npm install --include=dev && npm test`
  (the `--include=dev` is required because this machine has `NODE_ENV=production`, which otherwise
  skips devDependencies). Chromium is already cached.
- Run `python -m semgrep --config=auto scopesnap-api scopesnap-web` -- local SAST
- Run `gitleaks detect --redact` -- local secret scan
- SKIP all other pre-deploy steps in scoped mode

### Safe mode (monthly release audit)
- All scoped steps PLUS:
- Invoke Anthropic `webapp-testing` skill against local dev server (if running)
- Invoke `accessibility-a11y-enhanced` skill against local dev server
- Invoke GStack `review` for AI code review on the most recent commit
- Manual prompt to Shoab: "Run `@snapai-dev review this PR` in a separate Cowork
  session for additional security-focused review. Confirm done before continuing."
- WAIT for Shoab confirmation

### Full mode (quarterly comprehensive)
- All safe steps PLUS:
- Invoke `quality-playbook` skill standalone -- generates RUN_CODE_REVIEW.md +
  RUN_SPEC_AUDIT.md outputs
- Invoke Superpowers `test-driven-development` review of any new tests added since last audit
- Invoke GStack `review` with deeper depth flag
- Manual prompt to Shoab: "Open `@snapai-dev` in separate Cowork session and run
  full security-focused code review on staging branch diff vs main."

Report results to Shoab at end of Phase 1.

---

## Phase 2 -- Push to staging (safe + full modes only; scoped runs on current branch)

For safe + full modes:
1. Use /tmp clone per DEC-004 (clone into e.g. `/tmp/snapai_main`; set git identity
   `user.name "Shoab"` / `user.email "ds.shoab@gmail.com"` in the fresh clone).
2. Push current feature branch to GitHub (`github.com/mohammed-shoab/ScopeSnapAI`).
3. Merge into `staging` with plain git -- `gh` is NOT installed on this machine, and the canonical
   DEC-070 flow uses git directly:
   `git checkout staging && git pull origin staging && git merge --no-ff <feature-branch> && git push origin staging`
4. (Opening a GitHub PR is optional and only if `gh` is later installed; not required for the flow.)
5. Wait for Vercel + Railway staging deploy (~5 min).
6. Verify with: `curl https://staging.snapai.mainnov.tech/api/health`
   and `curl https://pk-staging.snapai.mainnov.tech/api/health`.
   Both must return `{"status":"ok"}`.

---

## Phase 3 -- Staging verification (varies by mode)

### Scoped mode
- Skip (no staging push happened in scoped)

### Safe mode
- Set `SNAPAI_AUDIT_MODE=1` env var on Railway staging service (backend drop).
  For frontend flows, set `sessionStorage.snapai_audit_mode='1'` at page init via the
  test harness (the `?audit_synthetic=1` URL param alone is stripped on Clerk redirects).
- **Staging is behind Vercel Deployment Protection (401)** -- you MUST pass the staging Protection
  Bypass for Automation secret as `VERCEL_AUTOMATION_BYPASS_SECRET` (in `.env.test` as
  `STAGING_CLERK_TEST_*` / bypass). The harness sends it as the `x-vercel-protection-bypass` header.
  ZAP and any browser step against staging need this too (header or `?x-vercel-protection-bypass=`).
- Authenticate via the **`audit/` harness** (VERIFIED working 2026-06-18). The staging Clerk instance
  forces an email code after password and `sign_in_tokens` 404s, so the harness uses a **`+clerk_test`
  user with Clerk's magic code `424242`** (auto-selected when `AUDIT_EMAIL` contains `clerk_test`).
  Run:
  `cd audit && npm install --include=dev` then set
  `CLERK_PUBLISHABLE_KEY` (pk_test), `CLERK_SECRET_KEY` (sk_test), `AUDIT_EMAIL=ds.shoab+clerk_test_audit@gmail.com`,
  `AUDIT_BASE_URL=https://staging.snapai.mainnov.tech`, `VERCEL_AUTOMATION_BYPASS_SECRET=...` and `npm test`.
  Passing output: `AUTH OK — Clerk user: user_...` + `Gated route landed on: .../dashboard`. The harness
  sets `sessionStorage.snapai_audit_mode='1'` at init so observability filters drop synthetic events.
  (Password and sign-in-token strategies remain in the spec as fallbacks if the instance config changes.)
- Invoke `webapp-testing` skill against staging.snapai.mainnov.tech using staging
  audit user (`ds.shoab+audit1@gmail.com`, `userId` in `.env.test`).
- Invoke `webapp-testing` skill against pk-staging.snapai.mainnov.tech.
- Run SnapAI-specific staging checks (custom to this skill -- no community equivalent):
  - Urdu glyph rendering on /pk routes (no `?` or box characters)
  - PKR currency formatting (Rs + comma thousands)
  - R-410A PSI threshold: 130 PSI must route to NORMAL not Dirty Coil
  - R-22 PSI threshold: 88 PSI high_min
  - R-32 PSI threshold: 140 PSI high_min
  - Cross-market isolation per DEC-049 -- create test assessment on US staging,
    confirm 404 on PK staging
- Invoke GStack `qa` against staging URLs
- Invoke GStack `benchmark` for performance baseline
- Run OWASP ZAP PASSIVE scan via Docker:
  ```bash
  docker run -t ghcr.io/zaproxy/zaproxy:stable zap-baseline.py \
    -t https://staging.snapai.mainnov.tech \
    -r zap-passive-$(date +%Y%m%d).html
  ```
- Parse ZAP report and summarize findings
- Unset `SNAPAI_AUDIT_MODE=1` after verifications complete

### Full mode
- All safe steps PLUS:
- Run OWASP ZAP ACTIVE scan (the big one):
  ```bash
  docker run -t ghcr.io/zaproxy/zaproxy:stable zap-full-scan.py \
    -t https://staging.snapai.mainnov.tech \
    -r zap-active-$(date +%Y%m%d).html
  ```
  This takes 30-60 min and consumes $1-3 of Railway compute.
- Run k6 load test (UNCAPPED in full mode -- mitigation #2 is OFF here). Script lives at
  `audit/loadtest.js`. k6 v2.0.0 is installed at `C:\Program Files\k6\k6.exe` (on PATH after a
  fresh shell; use the full path if `k6` doesn't resolve):
  ```bash
  k6 run --vus 50 --duration 5m audit/loadtest.js
  k6 run --vus 200 --duration 5m audit/loadtest.js
  k6 run --vus 500 --duration 5m audit/loadtest.js  # full mode only
  ```
  This consumes $1-3 of Railway compute.
- Run auth-flow Playwright security suite against staging (via the sign-in-token harness)
- Run SnapAI-specific deep checks (Layer 2)

---

## Phase 4 -- Promote gate (safe + full modes; scoped skips)

Run the DEC-070 7-checkpoint mirror-image verification. ALL 7 must be GREEN
to proceed.

### Checkpoint 1: Staging deploy is live
- Vercel staging deployment returns 200
- Railway staging shows `{"status":"ok"}`
- Latest commit SHA matches `git rev-parse HEAD` on local main

### Checkpoint 2: Schema parity
- Run `alembic current` against staging Postgres
- Run `alembic current` against prod Postgres
- Revisions must match exactly

### Checkpoint 3: Env var key parity
- Fetch env var keys (names only, no values) from Vercel staging vs prod
- Fetch env var keys from Railway staging vs prod
- Compare key sets -- must be identical (expect `SNAPAI_AUDIT_MODE` only when a run is active)

### Checkpoint 4: Smoke tests both markets
- Re-run lightweight smoke tests (subset of Phase 3) on both staging markets
- All must pass

### Checkpoint 5: Console-error baseline
- Open both prod URLs and both staging URLs via Chrome MCP
- Capture console errors via DevTools
- Staging error count must be <= prod baseline
- New error strings on staging not in prod = FAIL

### Checkpoint 6: Railway log baseline
- Query Railway logs for last 1 hour on both prod and staging services
- Count 4xx and 5xx responses
- Staging counts must be <= prod counts

### Checkpoint 7: Cross-market data isolation (DEC-049)
- Same isolation check as Phase 3, run against staging specifically

If ALL 7 GREEN: report "PROMOTE GATE: GO" and ask Shoab:
"All 7 checkpoints green. Ready to promote to prod. Reply 'go' to promote
via scripts/promote-to-prod.sh or 'stop' to hold."

If ANY checkpoint fails: report "PROMOTE GATE: NO-GO -- checkpoint N failed
because [reason]." Do NOT proceed to promotion.

WAIT for Shoab's explicit "go" confirmation before any promotion.

---

## Phase 5 -- Promote to prod (safe + full modes; scoped skips)

ONLY runs after Shoab's explicit "go" in chat.

```bash
cd /tmp/snapai_main
git fetch origin
# promote-to-prod.sh itself checks out main and overlays the named files from origin/staging.
# It prompts interactively for a commit message (read -rp) and has a .ts/.tsx truncation guard
# (>=5 lines). Pass each changed file path explicitly:
bash scripts/promote-to-prod.sh <changed file paths>
# Wait for Vercel + Railway prod deploy (~5 min) BEFORE any prod QA -- a premature
# prod test hits the OLD build and can create a stray prod Sentry error (learned 2026-06-18).
sleep 300
curl -s https://snapai.mainnov.tech/api/health
curl -s https://pk.snapai.mainnov.tech/api/health
```

Both must return `{"status":"ok"}` before proceeding.

---

## Phase 6 -- Post-deploy verification on prod (safe + full modes; scoped skips)

- **Prod auth is DIFFERENT from staging -- do NOT reuse the staging method.** The
  `+clerk_test` user + `424242` magic code is a Clerk **development-instance** feature and does
  **NOT** work on the prod "SnapAI" production instance. Prod is also **public** (no Vercel
  Deployment Protection), so no bypass secret is needed there.
- **Default to read-only / human-in-the-loop on prod.** Run the lightweight checks that need NO
  login (below). Do the authenticated portion manually, or skip it on prod and rely on staging
  (a true mirror) for authenticated coverage.
- Authenticated prod automation is OPTIONAL and only viable via **Clerk sign-in tokens with the
  prod `sk_live_...` key** (supplied at runtime, NEVER committed). This is UNVERIFIED on prod
  (sign-in tokens 404'd on the staging instance); probe once before relying on it. If it 404s on
  prod too, do not automate prod login -- stay read-only.
- If authenticated and it works: LIGHTWEIGHT only -- login + dashboard load + one diagnostic flow,
  never the full suite. Same against pk.snapai.mainnov.tech.
- Run SnapAI-specific prod-safe smoke checks:
  - Health endpoints respond
  - Auth gates work
  - Currency formatting correct per market
- ZAP active scan: SKIP on prod (would generate errors on live traffic).
  Passive scan only on prod:
  ```bash
  docker run -t ghcr.io/zaproxy/zaproxy:stable zap-baseline.py \
    -t https://snapai.mainnov.tech \
    -r zap-prod-passive-$(date +%Y%m%d).html
  ```
- Observability sanity:
  - Verify `decoder_version` and `replace_logic_version` stamps on new estimates
    (after Master Plan v2.0 Stage 5 ships)
  - Verify Sentry NOT receiving audit-synthetic events on prod (the `before_send`
    filter is working -- 0 envelopes when the audit flag is set at init)
  - Verify PostHog NOT capturing audit events on prod when the audit flag is set

---

## Phase 7 -- Brain file updates + retro

Append to `ScopeSnapAI/PROJECT_BRAIN.md` under "QA History" section:
```
[date] [time UTC] -- [scoped/safe/full] audit
- Markets: Houston + PK
- Result: PASS / FAIL
- Bugs found: N
- Bugs fixed in-loop: M
- Railway cost delta this run: $X.XX
- Sentry events generated (should be 0 from audit-synthetic filter): N
- ZAP findings: [summary]
- Notable: [one-line if anything stood out]
```

Append to `ScopeSnapAI/ACTIVE_TASKS.md`:
- Mark verified-live tasks as completed
- Add new bugs to backlog
- Update "Last QA Run" line

Update `ScopeSnapAI/DECISIONS.md` ONLY if a new architectural decision emerged
(e.g., new mitigation needed, new failure mode). Don't write a DEC for routine
passes. (Latest DEC as of skill creation: DEC-090 -- audit framework activation.)

All brain-file edits go through the /tmp-clone -> commit -> push-to-staging flow
(DEC-004/DEC-070). Use a CRLF-safe Python rewrite, not the Edit tool, on Unicode
files (DEC-027).

Ask Shoab a brief retrospective question:
"Audit complete. Anything surprising about this run? Any pattern you want me to
watch for next time?"

Wait for response. Append response to PROJECT_BRAIN if it contains a durable lesson.

---

## The 10 mitigations -- applied per mode

| # | Mitigation | scoped | safe | full |
|---|---|---|---|---|
| 1 | Railway $15 hard cap (platform) | enforced | enforced | enforced |
| 2 | k6 throttle to 50/100 concurrent | disabled (no k6) | active 50 max | DISABLED (50/200/500 staged) |
| 3 | OWASP ZAP passive-only | N/A | active (Phase 3) | full active in addition |
| 4 | Sentry SDK before_send filter | active (SDK level) | active | active |
| 5 | PostHog SDK before_send filter | active (SDK level) | active | active |
| 6 | Audit frequency cap (full mode only) | N/A | warn if <30 days since last safe | refuse if <80 days since last full |
| 7 | Off-hours scheduling check | N/A | N/A | active (Phase 0.7) |
| 8 | Skip Gemini-touching tests in scoped/safe | enforced | enforced (no Gemini in tests) | allowed (full mode runs photo tests) |
| 9 | Pre-flight Railway bill check (Phase 0.5) | active | active | active |
| 10 | Use pre-allocated Clerk test users (via sign-in tokens) | enforced | enforced | enforced |

---

## Cost reporting (every run)

At end of every audit run, report:
```
AUDIT COST REPORT
- Mode: scoped|safe|full
- Duration: X hours Y minutes
- Railway compute used during audit: $X.XX (delta from pre-audit reading)
- Railway billing cycle status: $X.XX of $15 cap (Y% headroom)
- Sentry events fired: N (audit-synthetic filtered: M, real: N-M)
- PostHog events fired: N (audit-synthetic filtered: M, real: N-M)
- GitHub Actions minutes consumed: N
- Total monetary cost estimate: $X.XX
```

If Railway delta exceeds $5 for a single run, flag it:
"WARNING: This run consumed $X.XX of Railway compute, above the typical $1-3
range. Investigate whether scope crept beyond mode definition."

---

## Error handling

| Failure mode | Behavior |
|---|---|
| Pre-flight check fails | ABORT with checklist of failed prereqs |
| Phase 0.5 Railway over $12 | ABORT with current usage and suggestion to wait until cycle reset |
| Phase 1 pytest fails | Stop, report, ask Shoab "fix locally and re-invoke or skip this check?" |
| Phase 3 ZAP scan fails | Report, continue (don't block entire audit on ZAP failure) |
| Phase 4 any checkpoint fails | Report NO-GO, do not proceed to Phase 5 |
| Phase 5 promote-to-prod.sh errors | Stop immediately, alert Shoab, do not retry automatically |
| Phase 6 prod health check fails | TRIGGER ROLLBACK: revert the promote commit, redeploy. Alert Shoab IMMEDIATELY. |
| Any phase exceeds 2 hours of wall-clock time | Auto-pause, ask Shoab "this is taking longer than expected -- investigate, continue, or abort?" |

---

## Honesty rules

- Never silently pass a check. PASS / FAIL / SKIPPED with reason -- never "probably works"
- Never auto-promote without Shoab confirmation
- Never skip Phase 4 promote gate
- Never run ZAP active on prod (only on staging)
- Never run k6 on prod
- Never disable the Sentry/PostHog synthetic filter for "easier debugging"
- Never lower the $15 Railway cap from within the skill -- that's a platform setting only Shoab adjusts
- Wait for the prod deploy to be LIVE before prod QA -- testing the old build pollutes prod observability

---

## What this skill does NOT do

- Build/deploy code itself -- that's snapai-dev's job. This skill only audits what's already been built.
- Marketing copy QA -- use snapai-copywriting + brand voice grep
- PK-specific user research -- PK is a test market per SnapAI_PK_Market_Positioning.md
- External pentest -- defer until 50 paying users + budget
- Continuous monitoring -- that's Sentry + Railway alerts (mainnov.tech is NOT behind Cloudflare; no edge WAF on the prod app -- DEC-068)

---

## Reference docs

- `SnapAI_Audit_Framework_Setup.md` -- prerequisite setup (required reading)
- `SnapAI_Audit_Setup_Artifacts/clerk_e2e_auth_harness.md` -- passwordless Clerk sign-in-token harness
- `SnapAI_PK_Market_Positioning.md` -- PK is test-only
- `SnapAI_Brand_Decoder_Implementation_Master_Plan_v2.md` -- current SnapAI dev plan
- `ScopeSnapAI/PROJECT_BRAIN.md` -- project state
- `ScopeSnapAI/DECISIONS.md` -- architectural decisions (DEC-004, DEC-027, DEC-049, DEC-068, DEC-070, DEC-090 particularly relevant)
- `ScopeSnapAI/TECH_STACK.md` -- service architecture + cost-to-serve
