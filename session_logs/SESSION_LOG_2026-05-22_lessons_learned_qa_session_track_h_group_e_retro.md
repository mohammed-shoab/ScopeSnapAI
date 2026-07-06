# SESSION LOG — Lessons Learned — 2026-05-22 QA Session (Track H Group E Retro) — 2026-05-22

**Retrofit note:** Extracted from `ACTIVE_TASKS_HISTORY.md` on 2026-07-06 as part of the SESSION_LOG_* archetype adoption (Phase 3 retrofit Batch B). Content is verbatim from the ACTIVE_TASKS_HISTORY.md session block; the block also remains in ACTIVE_TASKS_HISTORY.md for chronological continuity.

**Source:** `ACTIVE_TASKS_HISTORY.md` (session block, extracted 2026-07-06)

---

## Lessons Learned — 2026-05-22 QA Session (Track H Group E Retro)

Full workarounds in PROJECT_BRAIN.md critical rules. No new DEC entries needed (architectural facts, not decisions).

| # | What We Learned | Detail | Action |
|---|-----------------|--------|--------|
| L19 | `/api/brands` does NOT exist | 404 on all attempts. Models are served at `GET /api/models/all` with X-Market header. Response is `{models:[...]}` — NOT a plain array. Always parse as `data.models`. | Updated PROJECT_BRAIN arch notes |
| L20 | `pak_diagnostic_questions` table does NOT exist in Supabase | QA spec referenced this table for PSI threshold checks. It does not exist. PK PSI thresholds live in `pak_operating_targets` (columns: refrigerant, ambient_c, suction_min_psi, suction_max_psi). | Updated PROJECT_BRAIN arch notes |
| L21 | PK model count is 73, not 72 | `GET /api/models/all` X-Market:PK returns 73 records as of 2026-05-22 (Gree Fairy Inverter was added in previous session, bumping count from 72 to 73). | Updated PROJECT_BRAIN |
| L22 | BUG-031 (staging banner) re-regression was a false alarm | Investigated 2026-05-22: NEXT_PUBLIC_ENV was already "production" (All Environments) in Vercel. pk.snapai.mainnov.tech verified clean — no staging banner. Previous session note was premature. | Always verify the live site directly before logging as open |
| L23 | Network request tracking requires early initialization | `read_network_requests` tool says "tracking starts when first called" — calling it AFTER page actions miss all prior requests. Must call it BEFORE navigating to capture API calls made during page load. | Work pattern: call read_network_requests once at session start |
| L24 | CRLF → LF conversion on Python file write | Python scripts that read NTFS files as bytes and re-write preserve content correctly but strip CRLF to LF. This is harmless for `.md` files but worth noting. All content is preserved. | No action needed |
| L25 | Flow 4 (Not Turning On) voltage question may not appear in all paths | Capacitor reading path routed directly to Capacitor Failure fault card without asking voltage. The voltage question only appears in specific branch paths. Flow 4 PASS was confirmed via fault card returned. | QA spec updated understanding |

---


---

## Change log

- **2026-07-06:** Extracted from ACTIVE_TASKS_HISTORY.md session block during Phase 3 retrofit (Option B).
