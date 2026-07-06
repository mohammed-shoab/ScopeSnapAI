# SnapAI — App Speed Audit

**Date:** 2026-06-08
**Scope:** Whole-app performance, prod (`snapai.mainnov.tech` + `scopesnap-api-production.up.railway.app`)
**Method:** Live network timing from the browser, source-code review of the request path, Railway log inspection.

---

## TL;DR

The dominant bottleneck is **the database round-trip, not your code**. A single trivial `SELECT 1` against Supabase is costing **~1.4 seconds**. Every page and API call that touches the DB pays this tax, which is why the whole app feels uniformly sluggish rather than one screen being slow.

The OCR scan felt *extra* slow over the last two days for a second, now-resolved reason: with the Gemini key expired, every scan ran the full failure-retry sequence (~6s of backoff sleeps on top of 3 failed API calls). That is fixed.

Priority order: **(1) fix the DB latency, (2) warm the stack, (3) trim the frontend.** Item 1 alone should cut most screens roughly in half.

---

## What I measured (prod, live)

| Endpoint | What it does | Time |
|---|---|---|
| `GET /` | FastAPI, **no database** | ~400–630 ms |
| `GET /health` | One `SELECT 1` on Supabase | ~1,870 ms (steady) |
| `GET /api/models/all` | Real table query | ~2,200 ms |
| Landing page TTFB | Next.js SSR first byte | ~2,016 ms |
| Landing page full load | DOM + assets | ~4,055 ms |

**The key isolation:** `/health` minus `/` = **~1,400 ms spent purely on one trivial DB query.** A same-region `SELECT 1` should be 5–20 ms. Note `/health` and `/api/models/all` take basically the same time — proof the cost is fixed per-request overhead (connection + round-trip), not your query logic.

These numbers were taken while a prod redeploy was settling, so treat them as upper bounds — but the ~1.4s DB delta is location-independent (it's server-to-server, Railway→Supabase) and reproduced across every call.

---

## Root causes, in priority order

### 1. Railway → Supabase round-trip is ~700 ms each way (CRITICAL)

`db/database.py` sets `pool_pre_ping=True`, so **every** request fires a validation `SELECT 1` before its real query — two DB round-trips per request. At ~700 ms each, that's ~1.4 s before any real work happens.

The ~700 ms per round-trip itself is the real problem. Same-region Railway↔Supabase should be <50 ms. ~700 ms strongly implies **Railway (US East) and the Supabase project are in different regions**, or the free-tier pooler is latency-throttled.

**Actions (in order):**
- **Confirm the Supabase project region vs Railway's region (US East).** If they're mismatched, this is the whole ballgame — co-locating them is the single highest-leverage fix. Supabase region is in the project's dashboard → Settings → General.
- Consider dropping `pool_pre_ping=True` (halves round-trips) — but only after confirming connections are stable; pre-ping exists to dodge dead-connection errors on the free tier. Safer alternative: keep pre-ping but fix the region.
- `/health` calling `check_db_connection()` on every uptime ping means UptimeRobot/Healthchecks/Vercel-cron are each paying the full DB tax repeatedly. Consider a lightweight `/health` (no DB) plus a separate `/health/db` for deep checks.

### 2. Cold starts compound it (HIGH)

Free/hobby tiers sleep. Railway hobby + Supabase free-tier auto-pause + Vercel serverless cold start mean the *first* request after idle stacks several cold starts. Your keepalive pings (UptimeRobot, Healthchecks, Vercel cron) mitigate Supabase/Railway but each ping is now expensive (see #1). The ~2 s frontend TTFB is partly Vercel cold start, partly the SSR page making a slow backend call during render (inheriting the 1.4 s DB tax).

**Actions:** keep keepalives on; after fixing #1 they get cheap. For the frontend, make landing/marketing pages fully static (no SSR backend call) so they don't inherit DB latency.

### 3. Frontend weight (MEDIUM)

Landing page full load ~4 s. Third-party scripts are heavy on first paint: PostHog `surveys.js` (~1.2 s) and Clerk `environment` (~0.8 s). These block perceived readiness.

**Actions:** lazy-load PostHog surveys; defer Clerk on public marketing pages where auth isn't needed; confirm Next.js code-splitting isn't shipping the whole bundle on first route.

### 4. OCR retry storm — RESOLVED

`services/vision.py`: `MAX_RETRIES = 2`, exponential backoff `2 ** attempt` = 2 s then 4 s. On a *failing* key (the state you were in for ~2 days), every scan ran attempt→sleep2s→attempt→sleep4s→attempt ≈ 6 s of dead waiting plus 3 failed API calls. With the key now valid, scans are single-attempt. A healthy Gemini 2.5 Flash nameplate read is inherently ~3–8 s — that's model latency, not a bug. If you want it snappier later, `gemini-2.5-flash-lite` is faster but weaker at vision (not recommended for the core OCR).

---

## What is NOT the problem (ruled out)

- **Auth** — `api/auth.py` caches Clerk JWKS for 1 hour and verifies JWTs locally. No per-request call to Clerk. Clean.
- **Your query logic** — `/health` (no real query) and `/api/models/all` (real query) take the same time, so queries aren't the cost; the round-trip is.
- **App/Python code** — the no-DB `/` endpoint returns in ~400 ms; the app layer is fine.

---

## Recommended sequence

1. **Check Supabase region vs Railway US East.** If mismatched, migrate one to match. (Biggest win.)
2. Split `/health` into cheap (no-DB) and deep (`/health/db`) variants so keepalive pings stop paying the DB tax.
3. Re-measure. If still slow, drop `pool_pre_ping` and rely on a short `pool_recycle` instead.
4. Make public/marketing pages static (no SSR backend dependency).
5. Lazy-load PostHog + defer Clerk on public pages.

Items 1–2 are the high-leverage pair. Expect most screens to roughly halve once the DB round-trip is fixed.
