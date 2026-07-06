# SESSION LOG — Completed — Stage 4 Staging Isolation Audit (2026-05-23) — 2026-05-23

**Retrofit note:** Extracted from `ACTIVE_TASKS_HISTORY.md` on 2026-07-06 as part of the SESSION_LOG_* archetype adoption (Phase 3 retrofit Batch B). Content is verbatim from the ACTIVE_TASKS_HISTORY.md session block; the block also remains in ACTIVE_TASKS_HISTORY.md for chronological continuity.

**Source:** `ACTIVE_TASKS_HISTORY.md` (session block, extracted 2026-07-06)

---

## Completed — Stage 4 Staging Isolation Audit (2026-05-23)

Full 8-dimension audit of staging vs production environment isolation. All dimensions PASS. 2 critical cross-contaminations found and fixed.

| Task | Description | Result | Fix Applied |
|------|-------------|--------|-------------|
| 4.1 | Vercel project isolation — env vars | CROSS-CONTAMINATION | NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY on staging was pk_live_ → corrected to pk_test_ |
| 4.2 | Railway service isolation | CROSS-CONTAMINATION | CLERK_SECRET_KEY on Railway staging was sk_live_ → replaced with sk_test_ |
| 4.3 | Supabase project isolation | PASS | prod quqrvnoguofbjacrxcim / staging pqmgveqkuckbvyygsilk — isolated |
| 4.4 | Clerk app isolation | PASS | prod=pk_live_ / staging=firm-chamois-61 (pk_test_) — separate apps |
| 4.5 | R2 bucket isolation | PASS | prod=scopesnap-uploads / staging=scopesnap-uploads-staging |
| 4.6 | Visual confirmation | CROSS-CONTAMINATION (2) | pk.snapai served pk_test_ (ISR cache) → fixed by CwjgWfNBi redeploy; staging served pk_live_ → fixed by Preview redeploy 5HJ2piG8A |
| 4.7 | Sentry environment isolation | PASS | production=8+ issues / staging=1 issue, no overlap |
| 4.8 | DNS isolation | PASS | staging e08b930de4517e81 / prod e9353dffc8a96116 — different CNAME targets |

**Key architectural fact confirmed (DEC-074):** Staging custom domains are served by Preview branch deployments of the `staging` git branch. Any env var change on the staging Vercel project MUST be followed by a staging branch Preview redeploy (not a Production env redeploy) to reach staging.snapai.mainnov.tech and pk-staging.snapai.mainnov.tech.

**Deployment IDs:** 5HJ2piG8A (staging branch Preview redeploy), CwjgWfNBi (production no-cache redeploy)

**New DEC entries:** DEC-074, DEC-075, DEC-076, DEC-077

**Git commit:** docs(stage-4): staging isolation audit complete 2026-05-23


---

## Change log

- **2026-07-06:** Extracted from ACTIVE_TASKS_HISTORY.md session block during Phase 3 retrofit (Option B).
