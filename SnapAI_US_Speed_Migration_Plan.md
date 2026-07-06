# SnapAI — US Speed Migration Plan (Staging → QA → Prod)

**Goal:** Make the **US** site as fast as possible by eliminating the ~1,200 ms-per-query Tokyo round-trip. Move the database to the same region as the backend (US East / N. Virginia).

**Hard guardrails (your rules):**
- **Zero cost.** Stays **exactly $0/month** on the Supabase **Free plan with NANO compute**. No Pro upgrade, no paid compute, no add-ons — ever. The migration only changes *region*, not tier.
- **US only.** PK is out of scope for this work.
- **Staging first.** Nothing touches production until staging is fully migrated, QA'd, and hitting the speed targets (DEC-070).
- **I do the work; then I QA it.** You only do the steps I'm physically barred from (pasting secrets, confirming irreversible actions).

---

## Confirmed facts (from your live accounts)

| Component | Where it is now | Where it must be |
|---|---|---|
| Railway backend (`scopesnap-api`) | **US East (Virginia)** ✅ already correct | — |
| Supabase prod (`scopesnap`) | **ap-northeast-1 (Tokyo)** ❌ | **us-east-1 (N. Virginia)** |
| Supabase staging (`snapai-staging`) | **ap-northeast-1 (Tokyo)** ❌ | **us-east-1 (N. Virginia)** |
| New project cost | **$0/month** (confirmed via API) | — |

Both DBs run Postgres 17. Schema is built by **two** systems: Alembic (run by the backend on Railway boot) **and** 24 Supabase-tracked migrations. The safe way to reproduce the schema exactly is a full `pg_dump` of the source DB, not replaying migrations by hand.

**Cost guarantee:** new projects are **$0/month** (confirmed via the Supabase cost API), the same Free/NANO tier you run today. The only catch is the Free plan's **2-active-project limit** — so the plan below *juggles project slots* (pause/delete the old Tokyo project as we go) to **never exceed 2 active projects**, which keeps cost at exactly $0. We never upgrade to escape the limit.

---

## Why this is the fix

Backend (Virginia) → Database (Tokyo) → back is ~11,000 km each way. Co-locating both in Virginia drops the per-query cost from **~1,200 ms to an expected ~5–20 ms**, which cascades into every API call and every authenticated page. Railway is already in Virginia, so **only the database moves.**

---

## Target architecture (after migration)

```
Houston user ──> Vercel (US edge) ──> Railway backend (US East / Virginia)
                                            │  <5 ms, same region
                                            ▼
                                   Supabase DB (us-east-1 / Virginia)
```

---

## Cost & project-slot management (how we stay at exactly $0)

The Free plan allows **2 active projects**. We keep ≤2 active the entire time by pausing/deleting the old Tokyo project before adding each new Virginia one. Compute stays **NANO** (free) throughout. Sequence:

| Stage | Active projects (always ≤ 2) | Cost |
|---|---|---|
| Now | Tokyo-prod, Tokyo-staging | $0 |
| Pause Tokyo-staging → create Virginia-staging | Tokyo-prod, **Virginia-staging** *(Tokyo-staging paused = rollback)* | $0 |
| After staging QA passes → delete Tokyo-staging | Tokyo-prod, Virginia-staging | $0 |
| Prod cutover: temporarily delete Virginia-staging → create Virginia-prod | Tokyo-prod, **Virginia-prod** | $0 |
| After prod QA passes → delete Tokyo-prod, recreate Virginia-staging | **Virginia-prod, Virginia-staging** | $0 |

End state: both projects in Virginia, Free/NANO, **2 active, $0/month — identical cost to today.**

---

## PHASE 0 — Prep & decisions (before any change)

1. **Decision you confirm** (one question in chat): staging-data method. *Region is fixed (us-east-1, to match Railway). Compute is fixed (NANO/Free, to keep $0).*
2. I snapshot the current staging `DATABASE_URL` and code state so we can roll back instantly.
3. I verify the Free plan's active-project handling so the slot juggling above works without ever triggering a paid tier. If Supabase blocks a needed step at $0, I stop and tell you before doing anything that costs money.

---

## PHASE 1 — Staging migration (US, the real work)

**Step 1.1 — Create the new database.** I create a Supabase project `snapai-staging-use1` in **us-east-1** via the Supabase connector. *(Me. $0.)*

**Step 1.2 — Reproduce the schema.** Method depends on your Phase-0 choice:
- **Fresh rebuild (recommended for staging):** I replay the schema into the new DB and reseed reference tables (operating_targets, pricing_rules, fault_cards, etc.) from the SQL seeds in the repo. Cleanest, no password handling. *(Me, via Supabase connector + Desktop Commander.)*
- **Full copy:** `pg_dump` Tokyo → `pg_restore` Virginia, preserving all data. Runs via **Desktop Commander on your machine** (your computer can reach Supabase; the sandbox cannot). Needs the DB passwords. *(Me driving, you paste the connection strings.)*

**Step 1.3 — Tune the connection pool.** I edit `db/database.py`: raise `pool_size` 3 → 10, and drop `pool_pre_ping` (it was doubling every round-trip; far less needed at <20 ms). *(Me, code edit on a `staging` branch.)*

**Step 1.4 — Point staging at the new DB.** Swap `DATABASE_URL` on **scopesnap-api-staging** in Railway to the new us-east-1 pooler URL. The connection string contains a password, so **you paste it** (same as the Gemini key). I open the field and walk you to it. *(You paste, I verify.)*

**Step 1.5 — Deploy & boot-check.** Railway redeploys; I confirm `/health` returns `{"db":"connected","environment":"staging"}` and Alembic ran clean. *(Me.)*

---

## PHASE 2 — Staging QA (must pass before prod)

I re-run the **exact** measurements from today's report against staging and compare to targets:

| Stage | Before (Tokyo) | **Target (Virginia)** | Pass if |
|---|---|---|---|
| DB query (`/health` − `/`) | ~1,300 ms | **< 50 ms** | ≤ 50 ms |
| API data call (dashboard) | 3,055–3,755 ms | **< 400 ms** | ≤ 500 ms |
| Dashboard TTFB | 2,462 ms | **< 600 ms** | ≤ 800 ms |
| Authenticated page full load | 1.3–2.8 s | **< 1.5 s** | ≤ 1.5 s |

Plus a **functional** pass: I click through dashboard, assessments, diagnoses, pricing, and run a full nameplate-scan → diagnosis → estimate flow on staging to confirm nothing broke in the move. If any gate fails, I diagnose and fix before we go near prod. *(Me. Reported back with the same number tables.)*

---

## PHASE 3 — Production migration (only after Phase 2 passes)

Same shape as Phase 1, with one difference: **prod data is real**, so we use the full `pg_dump`/`pg_restore` copy (preserving assessments, reports, users), not a fresh reseed.

1. To stay at ≤2 active projects ($0), I first delete the now-validated Virginia-staging, then create `snapai-use1` in **us-east-1** (Virginia-staging is recreated at the end). *(Me.)*
2. Full data copy Tokyo → Virginia via Desktop Commander. *(Me driving, you paste connection strings.)*
3. Promote the pool-tuning code to `main` via your promote-to-prod script. *(Me.)*
4. You swap prod `DATABASE_URL` to the new us-east-1 DB. *(You paste, I verify.)*
5. I watch the redeploy, confirm health, and watch Sentry for 30 min.

**Cutover note:** to avoid losing assessments created between dump and switch, we either do this in a low-traffic window or briefly pause writes. I'll flag the exact moment.

---

## PHASE 4 — Production QA & sign-off

I re-measure prod against the same targets, run the functional flow, watch Sentry 30 min, and update PROJECT_BRAIN / TECH_STACK / DECISIONS with the new region, the pool change, and a DEC entry. *(Me.)*

---

## Who does what

| Step | Owner |
|---|---|
| Create us-east-1 projects | **Me** (Supabase connector) |
| Schema + data migration | **Me** (connector + Desktop Commander on your machine) |
| Code: pool tuning | **Me** (staging branch → promote) |
| Paste new `DATABASE_URL` into Railway | **You** (it's a secret; I can't enter credentials) |
| Paste DB connection strings for dump/restore | **You** (secrets) |
| All measurement, QA, deploy-watch, brain updates | **Me** |
| Approve irreversible prod cutover | **You** |

---

## Rollback (at every phase)

The old Tokyo databases stay untouched and running the whole time. If anything fails, we revert `DATABASE_URL` to the original Tokyo string (I keep it saved) and redeploy — back to the prior state in ~3 minutes. Nothing is deleted until you sign off that the new setup is stable.

---

## Risks & mitigations

- **Free-tier 2-project limit** → handled by the slot-juggling sequence above (pause/delete old before adding new); we never exceed 2 active, so we never trigger a paid tier. If any step would cost money, I stop and ask first.
- **Sandbox can't reach Supabase** → data copy runs via Desktop Commander on your machine, which can.
- **Two migration systems** → full `pg_dump` reproduces the exact schema regardless of which tool built it.
- **Dump/restore needs DB passwords** → you paste; I never store or echo them.
- **Data drift during prod cutover** → low-traffic window or brief write pause.

---

## What I need from you to start

1. Approve the plan.
2. Answer the 1 decision I'll ask in chat (staging-data method). Region (us-east-1) and tier (NANO/Free, $0) are already fixed.
3. Be available for ~3 short credential-paste moments (new `DATABASE_URL`, and connection strings for the data copy).

Once approved, I start at Phase 1 Step 1.1 and report after each step.
