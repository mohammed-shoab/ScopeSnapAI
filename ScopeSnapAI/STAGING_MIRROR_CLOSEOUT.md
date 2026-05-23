# SnapAI — Staging Mirror Closeout (2026-05-24)

> Comprehensive record of the 8-stage staging-mirror effort. Covers what was broken at the
> start, what each stage fixed, what the operational state is now, and how the workflow
> works going forward. This document is a historical record — not a replacement for the
> operational brain files (PROJECT_BRAIN.md, WORKFLOW.md, DECISIONS.md, TECH_STACK.md,
> ACTIVE_TASKS.md, MARKET_GUIDE.md).

---

## 1. Starting State (2026-05-22 Baseline)

### Production

Both production URLs were live and fully functional at the start of this effort:
- https://snapai.mainnov.tech (Houston US market)
- https://pk.snapai.mainnov.tech (Pakistan market)

Backend: scopesnap-api-production.up.railway.app — healthy, environment=production.
Alembic head: 034 (migrations 001-034 applied, with 031 applied directly via Supabase MCP
rather than via Railway/Alembic chain — a drift that DEC-043 documents).
Git HEAD: 19db2d1 (Stage 1 baseline). All 6 diagnostic flows verified PASS on both markets.

### Staging (broken state)

A staging environment existed but was a partial mirror with three critical gaps:

1. Vercel staging deployed `main` branch, not `staging` branch (DEC-067). Any push to the
   staging git branch did NOT reach staging.snapai.mainnov.tech — the old production
   code was always what the staging URLs served.

2. Staging Supabase was at Alembic 025 — 9 migrations behind production (034). Schema drift
   meant staging could not reproduce production bugs or validate migrations.

3. Staging git branch HEAD was well behind main HEAD. Code and schema were both stale.

Additional discoveries during audit:
- DNS for mainnov.tech is managed in Hostinger under mshoabarabi@gmail.com, NOT Cloudflare
  as the .staging_secrets.txt comment suggested (DEC-068).
- StagingBanner is a React Server Component in app/(app)/layout.tsx — only shows on
  authenticated routes, not on the public homepage or sign-in page (DEC-069).
- Google Maps API was designed in Track F C.2 but never wired up — API key not set in
  Vercel env vars, no CSP allowances, no Service Worker passthrough.

### Change Workflow (ad-hoc state)

Changes were pushed directly to main. No staging gate. Testing happened on production.
This was acceptable during early development but became a liability as beta testers were
incoming via the LinkedIn outreach campaign (Stage 3 of the marketing plan).

---

## 2. The 8-Stage Plan

| Stage | Title                                  | Key Outcome                                            |
|-------|----------------------------------------|--------------------------------------------------------|
| 1     | Production Live-Verify                 | All tracks + recent fixes confirmed live on prod       |
| 2     | Free-Tier Cost Audit                   | $0 month-to-date confirmed, budget alerts across all services |
| 3     | Google Maps Integration                | Places autocomplete live on Houston address field      |
| 4     | Staging Isolation Audit                | Zero overlap between prod and staging — 2 critical fixes |
| 5     | Staging DB & Branch Parity             | Staging Alembic 034, staging branch = main HEAD        |
| 6     | Vercel Staging Branch Rewire           | DEC-067 superseded; staging now deploys staging branch |
| 7     | Staging End-to-End QA                  | Full E2E on staging matches production; DEC-070 activated |
| 8     | Final Doc + Meta-Retrospective         | This document                                          |

---

## 3. Per-Stage Retrospective

### Stage 1 — Production Live-Verify

Goal: confirm every feature track that had been built (Q, R, R.9, REC, D, DX, P, F, G, H)
was actually live on production with no regressions from the 2026-05-22 codebase.

What was found and fixed: Two bugs discovered during verification. BUG-040 — the Service/
Tune-Up flow completed but never created an estimate row because _generate_service_estimate()
used a raw SQLAlchemy INSERT with a Python list bound to a JSONB column without CAST(:options
AS jsonb) — SQLAlchemy silently drops it with no exception (DEC-072). BUG-041 — the amber
STAGING banner was visible on pk.snapai.mainnov.tech because NEXT_PUBLIC_ENV=staging was set
in the production Vercel project under All Environments. This was the second occurrence of
this bug (first: BUG-031, 2026-05-21) — see DEC-073 for the prevention rules.

Lessons: Railway dashboard showing Online does not mean healthy — only {"status":"ok"} from
/health counts (DEC-045). All 6 diagnostic flows (Not Cooling, Not Heating, Making Noise,
Not Dehumidifying, Leaking, Service/Tune-Up) verified PASS on both Houston and PK.

### Stage 2 — Free-Tier Cost Audit

Goal: enumerate every billable service SnapAI uses and verify the current month spend is $0
or within the free tier.

What was found: Total monthly cost confirmed at $5.00/mo (Railway flat fee only). All 15
services audited: Supabase (free tier), Railway (Hobby $5/mo), Vercel (free), Clerk (free),
Cloudflare R2 (free), Healthchecks.io (free), Sentry (free), GCP Maps ($5 credit covers it
with $300 trial running until Aug 22 2026), PostHog (free), GitHub Actions (free).

Key decision: DEC-071 — Stripe is in Railway env vars but likely in test mode. Not billed.
Budget alerts set: Supabase spend cap enabled; Railway $10 limit set.

### Stage 3 — Google Maps Integration

Goal: wire up the Google Maps Places Autocomplete on the Houston market address field
(Track F C.2 had designed it but it was never implemented).

What was found and fixed: Three separate fixes required before autocomplete worked.
(1) NEXT_PUBLIC_GOOGLE_MAPS_API_KEY added to Vercel env vars for both prod and staging.
(2) CSP headers in next.config.js lacked maps.googleapis.com and maps.gstatic.com in
script-src and connect-src — browser was blocking the Maps script (DEC-078).
(3) The SnapAI PWA Service Worker was intercepting the Maps script fetch request and
returning an opaque response that the browser refuses to execute as a script — SW needed
a passthrough rule for googleapis.com and maps.gstatic.com (DEC-079).

Surprise: The Service Worker opaque-response issue was non-obvious. The autocomplete
loaded fine with the SW unregistered but failed silently with SW active. Diagnostic proof
was confirming google.maps.places loaded successfully after unregistering the SW, then
verifying again after adding the passthrough. Code comments in next.config.js and sw.js
erroneously reference DEC-076/DEC-077 (numbers taken by Stage 4 audit) — canonical refs
are DEC-078/DEC-079.

GCP project: snapai-maps (root-matrix-497207-j4). HTTP referrer restrictions restored to
production and staging domains. Free tier: 2,500 requests/day (more than sufficient for beta).

### Stage 4 — Staging Isolation Audit

Goal: verify that staging and production are fully isolated across all 8 dimensions
(Vercel, Railway, Supabase, Clerk, R2, Visual/Domain, Sentry, DNS).

What was found and fixed: Two critical cross-contaminations discovered.
(1) The scopesnap-web-staging Vercel project had pk_live_ in NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY —
production Clerk keys on staging. This meant staging users were authenticating against the
production Clerk app. Fixed by correcting to pk_test_ and triggering a staging branch Preview
redeploy (not a Production environment build — see DEC-074 for the critical distinction).
(2) Railway staging service had sk_live_ CLERK_SECRET_KEY — the production Clerk secret key.
This allowed production user JWTs to validate against the staging backend, a security boundary
violation. Fixed by replacing with sk_test_ from the firm-chamois-61 staging app (DEC-075).

Additional finding: pk.snapai.mainnov.tech was serving pk_test_ (stale ISR/edge cache) even
though the production Vercel project had pk_live_ set. Required a no-cache production redeploy
to flush (DEC-076). Also confirmed that staging custom domains are served by Preview branch
deployments of the staging git branch, not Production environment builds — a Vercel-specific
nuance critical for future env var changes (DEC-074).

### Stage 5 — Staging DB & Branch Parity

Goal: bring staging Supabase from Alembic 025 to 034, and force-push staging git branch
to match main HEAD.

What was found: Staging Supabase was missing migrations 026-034. Applied all 9 migrations
in sequence via Supabase MCP. Also discovered that pak_fault_card_descriptions and
pak_fault_card_urdu_descriptions tables do not exist in production — descriptions are
embedded in pak_fault_cards JSONB columns. 15 reference tables synced from production
(using direct psycopg2 for pak_fault_cards due to RLS blocking anon REST reads).

pak_fault_cards required direct psycopg2 connection (16 rows) because Row Level Security
blocked the standard anon key REST reads on the production Supabase. This is the only table
that needs this workaround for future re-mirror operations.

### Stage 6 — Vercel Staging Branch Rewire

Goal: fix DEC-067 — make the staging Vercel project deploy the staging git branch instead
of main.

What was found: Vercel's API does not expose link.productionBranch as a patchable field.
PATCH /api/v9/projects/{id} with productionBranch in the body returns "should NOT have
additional property" regardless of API version (v1, v7, v8, v9, v10). The Vercel UI Git
settings page also does not expose a Production Branch input for the staging project.

Solution: Set gitBranch: "staging" at the domain level for all 3 staging domains via
PATCH /api/v9/projects/{id}/domains/{domainName}. This achieves the same practical outcome —
when you push to the staging branch, all 3 staging domains rebuild and serve the new commit.

Known limitation (acceptable): The scopesnap-web-staging Vercel project still builds an
orphaned "Production environment" deployment from main pushes (link.productionBranch cannot
be changed) but since all 3 domains have gitBranch: "staging" set, those orphaned builds
are never served on any domain. The domain-level override fully controls what each staging
domain serves.

Decision recorded: DEC-080 (supersedes DEC-067).

### Stage 7 — Staging End-to-End QA

Goal: run a full diagnostic E2E flow on staging and confirm it matches production.

What was verified:
- Houston staging: full flow PASS — Not Cooling -> nameplate upload (Carrier FB4C036000) ->
  address (autocomplete loaded, pac-container confirmed) -> 45 PSI suction reading low ->
  Refrigerant Leak High Confidence -> Estimate Builder with Option A ($608), Option B ($1,013
  recommended), Option C ($1,368) all in USD with 35% markup applied. This matches production
  behavior exactly.
- Google Maps: window.google.maps.places.Autocomplete available on staging, pac-container
  instantiated (display:none is correct behavior before user types).
- Clerk keys: pk_test_ confirmed on sign-in page ("Development mode", "ScopeSnapAI Staging").
- PK staging: domain resolves, Clerk pk_test_ + Development mode confirmed (DEC-077),
  backend environment=staging + db=connected, /api/diagnostic/pk/pressure-targets returns
  correct R-410A data (suction 125-145 PSI, discharge 325-370 PSI), 74 API endpoints live.
- PK auth-gated features (PKR pricing UI, Urdu translations) require login — no test
  credentials available in .staging_secrets.txt, but all backend PK endpoints confirmed healthy.

DEC-070 activated. Staging is a true mirror of production. Workflow is mandatory.

---

## 4. Decisions Codified During This Effort

| Decision | Summary | Status |
|----------|---------|--------|
| DEC-067 | Vercel staging deployed main branch (not staging) | SUPERSEDED by DEC-080 |
| DEC-068 | DNS for mainnov.tech is in Hostinger (mshoabarabi@gmail.com), NOT Cloudflare | ACTIVE |
| DEC-069 | StagingBanner is RSC in app/(app)/layout.tsx — auth-only routes only | ACTIVE |
| DEC-070 | Staging-first 7-step change workflow | ACTIVE (Stage 7 sign-off 2026-05-24) |
| DEC-071 | Stripe in Railway env vars, likely test-mode, not billed (Stage 2 audit finding) | ACTIVE |
| DEC-072 | CAST(:options AS jsonb) required for JSONB column INSERT in raw SQLAlchemy | ACTIVE |
| DEC-073 | NEXT_PUBLIC_ENV=staging on prod Vercel is a recurring trap (2nd occurrence) | ACTIVE |
| DEC-074 | Vercel staging custom domains = Preview branch deployments, not Production env | ACTIVE |
| DEC-075 | Railway staging had sk_live_ Clerk secret key — always audit after service clone | ACTIVE |
| DEC-076 | ISR edge cache can serve stale Clerk key after env var change — verify both domains | ACTIVE |
| DEC-077 | Clerk key prefix is authoritative environment signal for all 4 SnapAI domains | ACTIVE |
| DEC-078 | CSP must include maps.googleapis.com and maps.gstatic.com | ACTIVE |
| DEC-079 | Service Worker must passthrough googleapis.com to avoid opaque-response blocking | ACTIVE |
| DEC-080 | Vercel staging domains rewired via domain-level gitBranch (supersedes DEC-067) | ACTIVE |

---

## 5. New Operational State (as of 2026-05-24)

### Production
- snapai.mainnov.tech: healthy, Alembic 034, HEAD 540e795 (main)
- pk.snapai.mainnov.tech: healthy, same deploy
- Backend: environment=production, db=connected, 74 endpoints live
- All 6 diagnostic flows PASS (verified Stage 1 and Stage 7)

### Staging
- staging.snapai.mainnov.tech: healthy, Alembic 034, serves staging git branch
- pk-staging.snapai.mainnov.tech: healthy, same staging deploy
- Backend: environment=staging, db=connected, pk-specific endpoints live
- Clerk: pk_test_ (Development mode, firm-chamois-61) — isolated from production users
- Supabase: pqmgveqkuckbvyygsilk (ap-northeast-1) — fully isolated from production data
- R2: scopesnap-uploads-staging — isolated from production uploads
- All 15 reference tables seeded from production (Stage 5)

### Workflow
Staging-first 7-step loop per WORKFLOW.md — mandatory. No more direct edits to main.
No more testing on production.

### Google Maps
Live on Houston market (staging + production). Free-tier safe ($300 GCP trial through
Aug 22 2026; 2,500 requests/day free thereafter). pac-container confirmed instantiated on
both environments.

### Total Monthly Cost
$5.00/mo (Railway Hobby flat fee only). All other services within free tier.
Budget alerts: Supabase spend cap enabled, Railway $10 limit, GCP $5 alert.

### Beta Readiness
Confirmed. Production URLs healthy, both markets functional, staging mirrors production,
workflow gates in place to protect prod from untested code.

---

## 6. How the Workflow Works Now

The 7-step staging-first loop (from WORKFLOW.md Section 4):

1. Branch off staging
   git clone --branch staging https://x-token:$GH_PAT@github.com/mohammed-shoab/ScopeSnapAI /tmp/snapai_work
   git checkout -b feature/<short-name>

2. Make the change in /tmp clone (never in the NTFS workspace per DEC-004).
   Update brain files at time of change (DEC, WA, migration rows — not as afterthought).

3. Push and open PR: git push origin feature/<name>. PR from feature branch to staging.
   PR description: what changed, which markets, migration included, env vars needed, how to verify.

4. Merge to staging. Triggers: Vercel staging redeploy (~2 min), Railway staging redeploy
   (~3 min + alembic upgrade head if migration). Watch logs for errors.

5. Verify on staging. Use staging.snapai.mainnov.tech (US) and pk-staging.snapai.mainnov.tech
   (PK). Amber StagingBanner confirms you are on staging. Run the changed flow end-to-end.
   If verification fails: fix on same feature branch, push, re-merge, re-verify. Do not promote.

6. Promote to production.
   git clone --branch main ... /tmp/snapai_main
   cd /tmp/snapai_main
   ./scripts/promote-to-prod.sh scopesnap-web/components/MyComponent.tsx ...
   This copies named files from staging to main and pushes. Triggers prod deploy.

7. Verify on production. Same flow on snapai.mainnov.tech + pk.snapai.mainnov.tech.

---

## 7. The Four Absolute Rules

From DEC-070 — these cannot be bypassed except via the emergency hotfix path (WORKFLOW.md
Section 9), which requires a documented reason and mandatory 24-hour staging re-sync.

1. Never edit code directly on main without going through staging first
2. Never push migrations to prod that have not run on staging first
3. Never add env vars to prod without mirroring them on staging first
4. Never test on production — testing happens on staging; production is for real users

---

## 8. Lessons Learned — Future AI Sessions Must Know

The following lessons represent hard-won knowledge from the full project history and the
8-stage staging-mirror effort. Every AI session working on SnapAI must read these.

### Environment & Infrastructure

Bash sandbox cannot reach external URLs. All sandbox network is blocked. Any check that
requires hitting a live URL (Railway health, Supabase, Vercel API, GitHub API) must be done
via Claude in Chrome (javascript_tool or navigate + get_page_text). Never attempt curl or
requests.get from the sandbox — they will silently time out or fail with ECONNREFUSED.

DNS for mainnov.tech is in Hostinger, not Cloudflare. Account: mshoabarabi@gmail.com at
hpanel.hostinger.com. The comment in .staging_secrets.txt saying "add DNS in Cloudflare" is
wrong (DEC-068). CNAME target for staging domains: e08b930de4517e81.vercel-dns-017.com.

Vercel staging custom domains are served by Preview branch deployments, not Production
environment builds (DEC-074). After any env var change on scopesnap-web-staging, trigger a
staging branch Preview redeploy. A Production environment redeploy will NOT reach the staging
custom domains.

Railway showing Online does not mean the service is healthy (DEC-045). A crash-looping
process shows Online during restart attempts. Only {"status":"ok"} from /health counts.

alembic_version can be ahead of actual schema (DEC-043). A migration applied directly via
Supabase MCP stamps alembic_version without running the Alembic dependency chain. Always
verify column existence in information_schema.columns independently of the alembic_version value.

StagingBanner is RSC in app/(app)/layout.tsx — only visible on authenticated routes (DEC-069).
Never look for the staging banner on the homepage or sign-in page.

Clerk session is shared across *.mainnov.tech subdomains (DEC-047). Login on
snapai.mainnov.tech also authenticates pk.snapai.mainnov.tech. One login covers both markets.

NEXT_PUBLIC_ENV=staging on production Vercel is a recurring trap — happened twice (BUG-031,
BUG-041). After ANY Vercel env var change on ANY project, immediately verify production
NEXT_PUBLIC_ENV is absent or set to "production" (DEC-023, DEC-073).

### Git Operations

NEVER use git stash from the Linux sandbox on the NTFS-mounted repo (DEC-013). It truncates
TypeScript/TSX files due to LF/CRLF translation, causing silent corruption that only surfaces
as Vercel parse errors. Use WIP commits + git reset HEAD~1 instead.

All git operations from AI sessions must use a /tmp clone (DEC-004). The NTFS workspace
cannot have .git/index.lock created or deleted from Linux. Safe workflow: clone to /tmp,
make edits there, commit and push from /tmp. Use Desktop Commander Python subprocess for
Windows-native git operations when needed (DEC-022, DEC-050).

git config --global --add safe.directory /tmp/snapai_tmpN after every fresh clone. Without
this, git treats the directory as untrusted and refuses to operate.

Migration drift accumulates fast. After any staging re-mirror or after a Railway outage,
audit the migrations in alembic_version vs information_schema.columns. The Stage 5 gap
(Alembic 025 vs prod 034) took significant time to close. Mirror staging before starting
any new feature work.

Brain file edits from concurrent AI sessions can collide. Two sessions editing
DECISIONS.md simultaneously will clobber each other's changes. Always read brain files at
session start, make targeted replacements, verify the edit landed correctly.

### NTFS File Corruption

Never use the Edit tool on ANY file containing non-ASCII characters (DEC-027). This includes
em-dashes, arrows, emoji, box-drawing characters in .py, .ts, .tsx, .md files. The Edit tool
silently truncates the file at the non-ASCII byte. Use Python replace() scripts instead.

Python write() can silently truncate the tail of long files on NTFS (DEC-044). After any
Python write to a .py file: python3 -c "import ast; ast.parse(open(f).read()); print('OK')"
and wc -l to confirm line count. Silent truncation produces SyntaxError only at Railway startup.

### API & Frontend Patterns

apiFetch never auto-injects the JWT. Pass token: await getToken() explicitly on every
apiFetch call. Raw fetch() calls on public pages must manually add X-Market: detectMarket()
header to reach market-aware backend endpoints (DEC-030b).

React controlled components ignore native click/change events (WA-27). Never use
element.click() or dispatchEvent to trigger React state changes. Must call
element[__reactPropsKey].onChange() or equivalent React synthetic event handler.

CAST(:options AS jsonb) required for JSONB column INSERT in raw SQLAlchemy (DEC-072).
Without it, the INSERT appears to succeed with no error but the JSONB value is never
persisted. Always use CAST(:param AS jsonb) in the SQL string and json.dumps(obj) in params.

The estimates table has NO updated_at column (DEC-059). Any INSERT must omit it.
Estimate tiers are stored as "A"/"B"/"C" in the estimates table — not "good"/"better"/"best"
(which is pak_pricing_tiers only). These are different naming schemes; the approve endpoint
accepts both (DEC-049).

estimates.market is stamped at creation, not at view time (DEC-066). Reports must read
report.market from the DB to format currency — never call detectMarket() at display time.

### Service Worker & PWA

Service Worker must passthrough googleapis.com and maps.gstatic.com (DEC-079). Without this,
the Maps script fetch returns an opaque response that cannot be executed as a script, silently
falling back to PlainInput. Diagnostic: unregister SW -> if Maps loads, the SW is blocking it.

IndexedDB model cache has 24h TTL on PK market (WA-26). After updating pak_brands, the
browser shows stale PK models for up to 24 hours. Force-clear:
indexedDB.deleteDatabase('snapai_models_pk') + location.reload(true).

### Vercel-Specific

SSR means no client-side API fetches visible in DevTools Network on initial load (WA-33).
Use javascript_tool to call endpoints from the browser's JS context, not get_page_text,
for verifying API responses on Vercel SSR pages.

CSP must be updated for any new third-party script src (DEC-078). Google Maps required
explicit script-src and connect-src allowances.

Vercel build failing in under 20 seconds = npm ci failed, likely a spurious package-lock.json
(DEC-065). The repo intentionally has no lockfile. grep for package-lock before every commit.

### PK Market

PK models live in pak_brands JSONB series[] array, NOT in a separate equipment_models table
(DEC-057). The table pak_equipment_models does not exist. /api/brands does not exist — use
/api/models/all with X-Market: PK header. Response is {models:[...]} — parse as data.models.

PK PSI thresholds live in pak_operating_targets, NOT pak_diagnostic_questions (DEC-064).
The table pak_diagnostic_questions does not exist. PSI thresholds: R-410A suction 125-145
at 40C, R-32 suction 120-140 at 40C, R-22 suction 78-88 at 45C.

ServiceChecklist.tsx and DiagnosticFlow.tsx are separate components (DEC-056/DEC-062).
Service/Tune-Up complaint routes through ServiceChecklist — UI features in DiagnosticFlow
(photo skip UI, overrides) are silently absent for service flows unless duplicated.

---

## 9. Open Backlog at Sign-Off

### Technical Backlog
- BUG-042 (low priority): Address field placeholder shows wrong text in some conditions
  (i18n translation key returning error string). Autocomplete works correctly; placeholder
  only shows when field is empty. Non-blocking.
- google.maps.places.Autocomplete is deprecated for new GCP customers as of March 1, 2025.
  Google shows a console warning on every load. Future migration to
  google.maps.places.PlaceAutocompleteElement required before Google discontinues the old API.
  No announced discontinuation date. Track as future work.
- DEC-051 (resolved but worth monitoring): NEXT_PUBLIC_ENV=staging on production Vercel.
  This bug recurred twice. Add it to the new-session checklist permanently.
- PK auth-gated features (PKR pricing UI, Urdu translations) not tested in Stage 7 due to
  no test credentials in .staging_secrets.txt. Create a test user account in firm-chamois-61
  (Clerk staging) for future staging QA sessions.
- PostHog dashboard buildout: PostHog is in the tech stack but the analytics dashboard
  has not been built out. Deferred to Phase 2 / post-beta.

### Feature Backlog (Post-Beta Phase 2)
- "Generate estimate from here" button on FaultResolutionScreen — deferred to v1.5 (DEC-019)
- Cross-device sync for userSessionCounter.ts localStorage data — deferred to v1.5 (DEC-054)
- ONBOARDING.md for new contributors — not yet written
- Railway staging sleep-mode optimization (keep staging under $5/mo combined cost)
- Emergency hotfix path (WORKFLOW.md Section 9) has never been exercised — the first real
  hotfix will be a learning moment; ensure the retrospective DEC entry is written

### Marketing Backlog
- LinkedIn outreach to Houston HVAC contractors (5 beta testers targeted via 12-week plan)
- Quora content strategy (30 answers x 5 repurposed assets = 150 touchpoints)
- HVAC podcast pitch (Bryan Orr, Gary McCreadie — highest leverage single move per marketing plan)
- PK market outreach via WhatsApp HVAC contractor groups (Karachi, Lahore, Multan)

---

## 10. What This Document Is NOT

- Not a replacement for PROJECT_BRAIN.md, WORKFLOW.md, DECISIONS.md, TECH_STACK.md,
  ACTIVE_TASKS.md, MARKET_GUIDE.md — those remain the operational reference files.
  This is a historical record of the staging-mirror effort only.

- Not a guide for new contributors. That would be a separate ONBOARDING.md document
  covering environment setup, first-deploy walkthrough, and common debugging patterns.

- Not the future product roadmap. The roadmap lives in the marketing master plan and
  the phase-2 feature backlog tracked in ACTIVE_TASKS.md.

- Not current operational state. This document was accurate at sign-off (2026-05-24) but
  will become stale as the project evolves. For current state, always read PROJECT_BRAIN.md.

---

## Sign-Off

**Stage 8 complete — Project Closing — 2026-05-24**

All 8 stages signed off. DEC-070 staging-first workflow OPERATIONAL (activated Stage 7,
verified end-to-end during the full staging QA pass).

Production: snapai.mainnov.tech + pk.snapai.mainnov.tech — healthy, Alembic 034.
Staging: staging.snapai.mainnov.tech + pk-staging.snapai.mainnov.tech — true mirror.
Main HEAD: 540e795b20eadba81734d0a978fed7384f93befa
Staging HEAD: d9bad2cfb2dd85c74e20bb2dd68897d019c4af29
Google Maps: live on Houston, free-tier safe ($300 GCP trial through Aug 22 2026).
Total monthly cost: $5.00/mo (Railway flat fee only), budget alerts on all services.
Brain files internally consistent (Stage 8 consistency audit complete — see Section below).
STAGING_MIRROR_CLOSEOUT.md written (this file).

Future workflow: per WORKFLOW.md. Branch off staging, verify on staging, promote-to-prod.sh.
No more direct edits to main. No more testing on production.

---

## Appendix: Stage 8 Consistency Audit Findings

Items verified clean (no contradictions found):

- PROJECT_BRAIN.md "Vercel staging deploys" note — updated from "main branch" to
  "staging branch via domain-level gitBranch (DEC-080)" in Stage 7 brain file commit.
- DEC-070 Activation — updated from "becomes mandatory after Stage 7" to "ACTIVE 2026-05-24".
- DEC-067 — marked SUPERSEDED 2026-05-24 by DEC-080 in DECISIONS.md header and body.
- WORKFLOW.md Section 1 (Activation status) — updated from "not yet operational" to
  "ACTIVE as of Stage 7 sign-off (2026-05-24)".
- ACTIVE_TASKS.md — Stage 7 sign-off block added at top with all verification checks.
- DEC-002 notes "Current revision: 029" — this is stale (current is 034). Noted here;
  low-priority fix since DEC-002 is about the Railway auto-run mechanism, not the head value.
- All four absolute rules (DEC-070) are consistently stated across WORKFLOW.md, PROJECT_BRAIN.md,
  TECH_STACK.md, and ACTIVE_TASKS.md.
- Clerk key convention (DEC-077) consistent across all files.
- DNS location (Hostinger, DEC-068) consistent across all files.
