# SnapAI — Staging Migration Result (Tokyo → Virginia)

**Date:** 2026-06-08
**Change:** Moved the staging database from Supabase Tokyo (`ap-northeast-1`) to Supabase Virginia (`us-east-1`), co-located with the Railway backend (US East). Cost unchanged: $0 (Free/NANO).

---

## Data integrity (verified)

The new Virginia staging database is an **exact clone** of the old Tokyo staging database:
- 57 tables / 41,163 rows — **0 differences** vs source (row-by-row verified).
- Includes the full app schema (US + PK tables) **and** the complete marketing `research` schema (operator_fields 22,703, canonical_operators 4,365, etc.).
- Restored from the verified `pg_dump` backup.
- App boots clean, dashboard renders the restored data, login works.

Old Tokyo staging is paused and fully backed up — instant rollback available.

---

## The core fix: database query latency (location-independent)

This is the universal win — the per-query tax every request paid, regardless of where the user is:

| Metric | Before (Tokyo) | After (Virginia) | Improvement |
|---|---|---|---|
| `/health` (one `SELECT 1`) | ~2,000 ms | ~440 ms | **4.5×** |
| **DB query cost** (`/health` − `/`) | **~1,300 ms** | **~30–40 ms** | **~35×** |
| `/api/models/all` (real query) | ~2,200 ms | ~470 ms | **4.7×** |

The database round-trip dropped from ~1,300 ms to ~30 ms — the Tokyo ocean-crossing is gone.

---

## Real app pages (measured end-to-end)

| Page | Metric | Before | After | Improvement |
|---|---|---|---|---|
| Dashboard | TTFB | 2,462 ms | **726 ms** | 3.4× |
| Dashboard | API calls | 3,164–3,755 ms | **537–586 ms** | ~6× |
| Dashboard | Full load | 2,629 ms | **803 ms** | 3.3× |
| Diagnoses | TTFB | 2,400 ms | **659 ms** | 3.6× |
| Diagnoses | API calls | 3,199–3,204 ms | **882–1,050 ms** | ~3× |
| Pricing | TTFB | 874 ms | **613 ms** | 1.4× |
| Pricing | API call | 3,055 ms | **887 ms** | 3.4× |

**Note:** these numbers were measured from this machine's location, which adds a fixed ~400 ms network hop to *every* call (browser → Railway). For an actual Houston user sitting near Virginia, that hop is ~30–50 ms instead, so their real-world numbers will be meaningfully faster than the table above. The DB portion of the fix (~35×) applies to everyone equally.

---

## QA gate check

| Target (from plan) | Result | Pass |
|---|---|---|
| DB query < 50 ms | ~30–40 ms | ✅ |
| Authenticated page full load < 1.5 s | 0.66–0.80 s | ✅ |
| Dashboard TTFB < 600 ms (≤800 ok) | 726 ms | ✅ (within tolerance; ~400 ms is measurement-location network) |
| API data call < 400 ms (≤500 ok) | 537–586 ms dashboard | ◑ slightly over due to measurement-location network; DB portion ~30 ms |
| Functional flow works | Dashboard/diagnoses/pricing render restored data, login OK | ✅ |

---

## Current state

- **Active projects:** Tokyo prod + Virginia staging = 2, $0.
- **Tokyo staging:** paused (backed up, rollback ready).
- **Staging site:** live on the fast Virginia DB.
- **Production:** untouched, still on Tokyo (next phase, only after sign-off).

---

## Optional next polish (not required — region fix already achieved the goal)

- Raise `pool_size` 3 → 10 and drop `pool_pre_ping` in `db/database.py` (a code deploy). With the DB now co-located, pre-ping costs ~30 ms instead of ~700 ms, so the dashboard's 3 parallel calls barely contend — this is minor polish, not a necessity.

Recommendation: the staging migration is a clear success. After you're satisfied, we replicate the exact same proven steps for production.
