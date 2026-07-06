# SESSION LOG — 2026-06-20 (update) — Bug 2 (PDF 404) RESOLVED — 2026-06-20

**Retrofit note:** Extracted from `ACTIVE_TASKS_HISTORY.md` on 2026-07-06 as part of the SESSION_LOG_* archetype adoption (Phase 3 retrofit Batch B). Content is verbatim from the ACTIVE_TASKS_HISTORY.md session block; the block also remains in ACTIVE_TASKS_HISTORY.md for chronological continuity.

**Source:** `ACTIVE_TASKS_HISTORY.md` (session block, extracted 2026-07-06)

---

## 2026-06-20 (update) — Bug 2 (PDF 404) RESOLVED

Root cause: `scopesnap-api/services/pdf_generator.py` had **117 trailing NUL bytes** at EOF, so `from services.pdf_generator import generate_contractor_pdf` raised `SyntaxError: source code string cannot contain null bytes` → `_pdf_available=False` → every contractor PDF fell back to `/files/pdfs/...-unavailable.pdf` (404). The nulls were trailing padding (no code lost). Stripped them; module now imports.

- [x] **Bug 2 — PDF 404: RESOLVED.** Verified on prod: PDF generates (5.4 KB), uploads to Cloudflare R2, public URL serves a valid `%PDF-` file. Commits: staging `0cc5eb7`, main `94737c2`.
- Note: **staging** still returns a `localhost:8000` PDF URL because Railway *staging* has no `R2_*` env vars (falls back to LocalStorage). Prod has R2 configured and works. To make staging PDFs externally accessible, set `R2_ACCOUNT_ID/R2_ACCESS_KEY_ID/R2_SECRET_ACCESS_KEY/R2_BUCKET_NAME/R2_PUBLIC_URL` on the Railway staging environment (optional — staging is test data).
- Follow-up (low priority): add a friendly 503 route handler for any legacy `…-unavailable.pdf` links; consider a CI guard against NUL bytes in source files (this repo has a history of truncation/corruption — DEC-005/027).

**All 5 Estimate Builder bugs are now resolved and live on prod.**

---


---

## Change log

- **2026-07-06:** Extracted from ACTIVE_TASKS_HISTORY.md session block during Phase 3 retrofit (Option B).
