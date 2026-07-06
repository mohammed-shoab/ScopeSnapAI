# TASK PROMPT — Handle the open Dependabot dependency PRs (staging-first, full QA, prod, docs)

> Paste this whole document into a new AI chat. It is self-contained: every fact, path, rule, and decision you need is below. Do **not** assume anything not stated here — if something contradicts what you find live, trust the **live state** and tell me.

You have **Desktop Commander** (Windows shell + file access) and **Claude in Chrome** (browser) available, plus a sandboxed Linux shell. Use them.

---

## 0. WHO YOU ARE / WHAT THIS IS

You are the senior dev for **SnapAI** — an AI HVAC diagnostic + estimate web app serving two markets: **US (Houston)** at `snapai.mainnov.tech` and **Pakistan** at `pk.snapai.mainnov.tech`. Staging mirrors are `staging.snapai.mainnov.tech` and `pk-staging.snapai.mainnov.tech`.

Your job in this session: **resolve the 5 open Dependabot dependency-update PRs correctly**, using the staging-first discipline, full QA on staging, my explicit go, then prod, then QA again, then update all the brain/docs. Nothing is to be rushed or merged blind.

**Owner:** Shoab (ds.shoab@gmail.com). I value brevity, honesty, concrete file paths + line numbers, and verifying before claiming done. If something is risky or you are unsure, say so and stop.

---

## 1. NON-NEGOTIABLE SAFETY GATES (read first, obey always)

1. **Staging-first (DEC-070).** Never edit `main` directly. Never test on production. Never push a DB migration to prod that hasn't run on staging. Always mirror env vars staging↔prod.
2. **Stop-and-confirm before any of these — list the exact change and wait for my explicit "go":**
   - Merging anything to `main` (that triggers a **production deploy**).
   - Closing or force-changing any GitHub PR.
   - Changing standing config (e.g. `.github/dependabot.yml`, auto-merge rules).
   - Anything irreversible (deleting, force-push, prod data).
3. **Never** put secrets/keys in code, logs, or PRs. Publishable keys/DSNs only if ever needed.
4. If a tool/dashboard can't be read (e.g. Railway's UI is a canvas SPA), **screenshot** it or fall back to the API — do **not** invent state.
5. Read-only research can be parallelized across subagents. **All write/commit/deploy/PR actions stay on the main thread** behind the gates above.

---

## 2. BOOTSTRAP — LOAD FULL KNOWLEDGE BEFORE DOING ANYTHING

**2a. Invoke the `snapai-dev` skill** (it bootstraps project context).

**2b. Read + CONFIRM the brain files.** They live in `C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\`. Read all of:
- `PROJECT_BRAIN.md` — live URLs, infra IDs, current state. The top "Last updated" banner (2026-06-18) describes the most recent session (observability + auth fix). **Read that banner fully.**
- `TECH_STACK.md` — exact stack, versions, hosting, accounts. See the **"2026-06-18 — Observability + Gemini billing corrections"** section near the end (Sentry was broken→fixed; Gemini auto-reload OFF; Dependabot now active).
- `DECISIONS.md` — architecture decisions. Read **DEC-070** (staging-first), **DEC-106–109** (recent: retrospective, backend Sentry capture, frontend Sentry, auth.py fix).
- `ACTIVE_TASKS.md` — current open items. See **"Session 2026-06-18"** entry (top) for the live open list, including the Dependabot item.
- `MARKET_GUIDE.md` — US vs PK differences (refrigerants, voltage, pricing).
- `WORKFLOW.md` — the full staging-first 7-step protocol, promote/rollback/hotfix procedures.

**Use subagents to parallelize this** (see agent roster, §6). After reading, **report back to me a short confirmation**: branch model, deploy pipeline, where the helper scripts are, and the current state of the 5 PRs — so I know you actually have the knowledge before you start. **Then wait for my "proceed" once, here, before touching anything.**

---

## 3. GROUND TRUTH — REPO, BRANCHES, DEPLOY, TOOLING (bake this in)

- **GitHub repo:** `mohammed-shoab/ScopeSnapAI`. Monorepo: frontend `scopesnap-web/` (Next.js, currently **14.2.15**), backend `scopesnap-api/` (FastAPI/Python).
- **Branch → environment mapping:**
  - `staging` branch → auto-deploys to `staging.snapai.mainnov.tech` + `pk-staging.snapai.mainnov.tech` (Vercel **Preview** for the frontend; Railway **staging** env for backend).
  - `main` branch → auto-deploys to `snapai.mainnov.tech` + `pk.snapai.mainnov.tech` (Vercel **Production**; Railway **production** env). **Merging to `main` = a prod deploy.**
- **Vercel:** frontend. Prod project deploys `main`; staging is the `staging`-branch Preview. Team `mohammed-shoabs-projects-7844119e`, projects `scope-snap-ai` (prod) + `scopesnap-web-staging`.
- **Railway:** backend. Project `pacific-exploration` (id `0e78dd68-ce72-46be-a2b1-7d3119de40a4`), service `scopesnap-api` with two environments — `production` and `staging`. The Railway dashboard is a **canvas SPA**: `get_page_text` returns nothing, so **screenshot** it, and switch environments via the top-left env dropdown (it persists between visits). Health endpoints: `https://scopesnap-api-staging.up.railway.app/health` and `https://scopesnap-api-production.up.railway.app/health`; version at `/api/version` (expect decoder/replace/brand_data **1.2**). Use a `?cb=...` cache-buster.
- **Sentry:** org `mainnov`, projects `snapai-api` (backend) + `snapai-web` (frontend), env-tagged `staging`/`production`. Dashboard: `https://mainnov.sentry.io/issues/`. **Sentry was only just wired this session** — so any `@sentry/nextjs` change MUST be verified by confirming real events still deliver (see §5).
- **Git push method (IMPORTANT — the Linux sandbox CANNOT push):** use the Windows-side helper scripts in `C:\Users\Shoab\My Drive\Personal Claude\_s1_stage\`, run via **Desktop Commander** (shell is **PowerShell** — use `;` to chain, **not** `&&`). The token is pulled from the Windows git credential manager in-process (never printed). Helpers:
  - `list_prs.py` — lists open PRs + CI status + recent merges.
  - `gh_fetch.py tree <substr>` / `gh_fetch.py get <repo_path> <out>` — read files from the **staging** branch.
  - `fetch_main_file.py <repo_path> <out>` — read a file from the **main** branch.
  - `gh_commit.py <manifest.json>` — commit file(s) to a branch via the GitHub trees API. Manifest shape: `{"branch":"staging","message":"...","add":[{"local":"<abs path>","repo":"scopesnap-web/..."}]}`. Set `"branch":"main"` to commit to prod.
  - `promote_to_main.py` (dry-run by default; `--commit` to write) — file-scoped overlay staging→main. **Note:** it lists everything changed since the merge-base (can look huge — that's `git compare` three-dot semantics, not "main is stale"). For single-file or few-file promotes, prefer a targeted `gh_commit.py` with `"branch":"main"` after confirming the file's main version.
  - You may instead use your own `git`/`gh` via Desktop Commander if a local clone exists — but verify, and never force-push.
- **QA skill:** `/snapai-qa` (full app E2E cycle) and/or `snapai-qa-master` (5-layer). Use `/snapai-qa` as instructed in §4.

---

## 4. THE EXACT WORK + ORDER OF OPERATIONS

### Phase A — Triage the 5 open PRs (read-only; verify live first)
Run `list_prs.py` to refresh state (do not trust the snapshot below if it differs). **As of 2026-06-18 the 5 open PRs (all targeting `main`, all unmerged, by `dependabot[bot]`) were:**

| PR | Bump | Type | CI |
|----|------|------|----|
| **#6** | `dompurify` 3.4.8 → 3.4.11 | patch (HTML/XSS sanitizer — security-relevant) | ✅ pass |
| **#4** | `@opentelemetry/core` + `@sentry/nextjs` | minor | ✅ pass |
| **#2** | `uuid` + `@sentry/nextjs` | minor | ✅ pass |
| **#5** | `next` 14.2.15 → **16.2.9** | **MAJOR** | ❌ fail |
| **#3** | `js-cookie` + `@clerk/nextjs` | breaking | ❌ fail |

**Principles (do not deviate):**
- **Never auto-merge a major.** A major bump (Next 14→16) is a *deliberate, hand-done migration*, not a drive-by version-number change. The Dependabot PR for a major is just the broken bump — it is NOT the migration.
- **The staging branch absorbs 100% of the risk.** Prod stays on the old version the entire time. If a migration can't be made clean on staging, you **shelve it and prod is unaffected** — that's the whole point.
- Verify, don't assume. CI-green ≠ behavior-verified for things CI doesn't exercise (notably Sentry event delivery).

### Phase B — Do ALL changes on `staging` first

**B1. The 3 green PRs (#6 dompurify, #4 otel+sentry, #2 uuid+sentry):**
- These are safe minor/patch + security. Apply their dependency bumps onto the **`staging`** branch (update `scopesnap-web/package.json` + lockfile accordingly). Do them as real staging commits — do **not** merge the bot PRs into `main`.
- Because #2 and #4 bump **`@sentry/nextjs`** (which we just wired this session), you MUST verify after deploy that Sentry **still initializes and delivers events** on staging (see §5). CI passing is not enough.

**B2. PR #3 (js-cookie + @clerk/nextjs) — INVESTIGATE before deciding:**
- Pull the failing CI/build log (GitHub Actions + the Vercel preview build for that PR branch). Find the actual error. It may be a Clerk peer-dependency conflict, a minor with a breaking change, or coupling to the Next bump.
- If it's a quick, safe fix → apply on staging, QA, treat like B1.
- If it's genuinely breaking → do **not** force it; log it as a tracked ticket (see Phase F) and leave prod untouched. Report your finding and recommendation to me.

**B3. PR #5 (Next 14 → 16) — deliberate MAJOR migration on staging:**
- This is the textbook major migration. On `staging` (or a branch off staging): read Next.js 16's official **upgrade guide + breaking changes**, run the **Next codemod** (`npx @next/codemod@latest upgrade`), fix every build/type/runtime breakage, update `next.config.js` as 16 requires. Confirm `@clerk/nextjs`, `@sentry/nextjs`, and the rest are compatible with Next 16 — if a critical dep doesn't support 16 yet, that's a **shelve** signal.
- Build must go green and full QA must pass on staging. If it cannot be made clean in this session, **shelve it** (prod stays on 14), write the migration ticket (Phase F), and tell me. Do **not** promote a half-working major.
- The Dependabot PR #5 itself is the broken auto-bump — it will be discarded/closed (handled by the config change in B4 + the gate in §1).

**B4. Reconfigure `.github/dependabot.yml` (commit to `staging` for now):**
- Target the **`staging`** branch instead of `main` (so future bumps flow through staging-first, not straight to prod).
- **Group** minor + patch updates into one weekly PR (reduce noise).
- **Ignore major version updates** (`update-types: ["version-update:semver-major"]`) — this auto-closes #5 and stops Next 16 from reopening every week. Majors become manual, scheduled migrations.
- Keep **security** updates always on.
- (Optional, propose to me — don't enable unilaterally) auto-merge **patch-only** after CI is green.
- Reconfiguring standing config is a §1 gated action — show me the proposed YAML and get my go before committing it.

**B5. Commit B1 (and B2/B3 if clean) to `staging`** via `gh_commit.py` with `"branch":"staging"`. Confirm Vercel staging Preview + Railway staging redeploy succeed (screenshot Railway deploy = ACTIVE/successful; `/health` ok).

### Phase C — `/snapai-qa` on STAGING
- Run **`/snapai-qa`** targeting **staging** (US + PK). It must cover: backend health + `/api/version`, the diagnostic→estimate flow on both markets, UI smoke, Playwright/axe + backend pytest (cited), and **the Sentry event-delivery verification** from §5.
- Capture pass/fail per check. **Bugs found must be fixed on staging and re-QA'd** until green.

### Phase D — STOP. CONFIRM WITH ME.
- Report: what changed, the staging QA results, Sentry-still-works proof, which PRs are ready to promote, which are shelved/closed and why. 
- **Wait for my explicit "go" before any prod action.** Do not proceed to prod without it.

### Phase E — Promote to PROD (only after my go)
- Promote the approved staging changes to `main` (targeted `gh_commit.py` `"branch":"main"`, or `promote_to_main.py --commit` for the right file set — verify the file set first; exclude `package-lock.json`/brain docs per existing convention if using the overlay).
- Confirm Vercel **Production** + Railway **production** redeploy: screenshot Railway production env deploy = ACTIVE/"Deployment successful"; prod `/health` ok; `/api/version` still **1.2** (no regression).
- If I approved closing PRs / the dependabot.yml change, do those now (still §1-gated).

### Phase F — `/snapai-qa` on PROD + tickets
- Run **`/snapai-qa`** targeting **production** (US + PK) — same coverage as Phase C. Watch Sentry for 15–30 min post-deploy (the dashboard should stay clean; Sentry capture is live now).
- Create/append backlog tickets in `ACTIVE_TASKS.md` for anything shelved: e.g. **"Next.js 14→16 migration (deliberate, staging-first)"** and (if applicable) the Clerk/js-cookie investigation outcome.

### Phase G — UPDATE ALL DOCS (this is required, not optional)
Update, in `C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\` (use **bash heredoc append** or a Python in-place string replace via the Linux sandbox — these files are large and on a Drive-synced path that can silently truncate on naive Edit/Write; **verify line counts before/after every edit**):
- **`PROJECT_BRAIN.md`** — prepend a new dated "Last updated: <today>" banner segment summarizing what shipped (which bumps landed, Next 16 status, dependabot.yml policy change), demoting the prior banner to "Previously".
- **`TECH_STACK.md`** — update the frontend version facts (Next version if it changed; dompurify/uuid/sentry/otel versions), and the Dependabot policy (now staging-targeted, grouped, majors ignored).
- **`ACTIVE_TASKS.md`** — add a new dated session entry (done items + any shelved tickets) at the top, newest-first.
- **`DECISIONS.md`** — append a new **DEC-110** (next number after DEC-109) recording the Dependabot handling policy + the specific PR outcomes + commit SHAs (staging + prod).
- Present the updated files to me at the end.

---

## 5. SENTRY VERIFICATION (mandatory whenever `@sentry/nextjs` changes — PRs #2/#4, and after Next 16)
Sentry was non-functional until this session, so a green CI does NOT prove it still works. After the staging deploy:
1. Confirm `next.config.js` is still wrapped with `withSentryConfig` and the CSP `connect-src` still allows `https://*.ingest.us.sentry.io`.
2. Trigger a **deliberate** client-side test error on `staging.snapai.mainnov.tech` (via Chrome) and confirm a new event lands in the `snapai-web` Sentry project tagged `environment:staging`, with the ingest request returning 200.
3. Confirm `NEXT_PUBLIC_SENTRY_DSN` is still set on the staging Vercel project.
4. Do the same proof on prod after promotion (project `snapai-web`, `environment:production`). Resolve the deliberate test issues afterward.

---

## 6. AGENT ROSTER — parallelize aggressively (10–15 subagents)
Spin up subagents for independent, read-only research and verification in parallel batches. Keep all writes/commits/deploys on the main thread. Suggested roster:

**Batch 1 — knowledge load (parallel, read-only):**
1. Agent: read + summarize `PROJECT_BRAIN.md` (focus: live IDs, current state, the 2026-06-18 banner).
2. Agent: read + summarize `TECH_STACK.md` (focus: frontend deps/versions, Sentry section, Dependabot note).
3. Agent: read + summarize `DECISIONS.md` DEC-070 + DEC-106–109.
4. Agent: read + summarize `WORKFLOW.md` (promote + rollback + hotfix steps).
5. Agent: read + summarize `ACTIVE_TASKS.md` (open items) + `MARKET_GUIDE.md` (US/PK deltas).

**Batch 2 — PR investigation (parallel, read-only):**
6. Agent: pull PR #5 (Next 16) CI + Vercel build logs; fetch Next 16 official breaking-changes/upgrade guide; produce a migration checklist + dep-compatibility matrix (Clerk, Sentry, etc. vs Next 16).
7. Agent: pull PR #3 (js-cookie + @clerk) failing build log; identify the exact error + root cause; recommend quick-fix vs shelve.
8. Agent: diff PRs #6/#4/#2 against current `package.json`/lockfile; confirm they're truly minor/patch and list the exact version deltas + any changelog security notes.
9. Agent: audit current `.github/dependabot.yml`; draft the new policy YAML (staging target, grouped minor/patch, ignore majors, security on).

**Batch 3 — verification (parallel, after each deploy):**
10. Agent: staging backend health + `/api/version` + data-routing checks (US + PK).
11. Agent: staging Sentry event-delivery proof (per §5).
12. Agent: Playwright/axe + backend pytest status (cite CI runs).
13. Agent (post-prod): prod health + `/api/version` + Sentry-quiet watch.

**Batch 4 — docs (parallel drafting, main thread commits):**
14. Agent: draft the `PROJECT_BRAIN.md` + `ACTIVE_TASKS.md` updates.
15. Agent: draft the `TECH_STACK.md` + `DECISIONS.md` (DEC-110) updates.

Use a final **verification subagent** to independently re-check that prod `/health`, `/api/version`, and the Sentry dashboard are all clean before you declare done.

---

## 7. DEFINITION OF DONE
- Approved safe bumps live on **both** staging and prod; `/api/version` still 1.2; both markets functional; Sentry verified delivering on both envs and dashboard clean.
- Next 16 either fully migrated + QA-passed + promoted, **or** cleanly shelved with prod untouched and a tracked migration ticket.
- PR #3 resolved or ticketed with a clear root-cause finding.
- `.github/dependabot.yml` updated to the agreed policy (with my go), breaking-major PRs auto-closed.
- `PROJECT_BRAIN.md`, `TECH_STACK.md`, `ACTIVE_TASKS.md`, `DECISIONS.md` (DEC-110) all updated, line-count-verified, and presented.
- A final honest summary: what shipped, what was shelved and why, commit SHAs (staging + prod), and any remaining watch items.

**Remember:** report honestly, verify before claiming done, and never skip the Phase D confirmation gate before prod.
