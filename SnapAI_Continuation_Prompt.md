# SnapAI — Master Continuation Prompt
> Paste this at the start of any new Claude session.
> This replaces having to re-explain anything about the app, both markets, all architecture, all decisions, all board work, and current state.
> **Last updated: 2026-05-20 — All tracks complete (Q/R/R.9/REC/D/P/Staging). Git HEAD: `02ad667`. Alembic: `029`.**

---

## SECTION 1 — WHO I AM & WHAT WE ARE BUILDING

I am **Shoab**. We are building **ScopeSnapAI (SnapAI)** — an AI-powered HVAC diagnostic and estimating platform for field technicians. A tech opens the app on their phone, scans or enters the unit nameplate (OCR), selects a complaint (Not Cooling, Water Dripping, etc.), and the app walks them through a step-by-step diagnostic flow — collecting pressure readings, photos, and measurements — then generates a three-tier repair estimate (Good / Better / Best) and sends it to the customer.

**Two live markets, one codebase:**
- **Houston (US):** `https://snapai.mainnov.tech` — USD pricing, email delivery
- **Pakistan (PK):** `https://pk.snapai.mainnov.tech` — PKR pricing, WhatsApp delivery, phone-only customer entry (no address required)

**GitHub repo:** `mohammed-shoab/ScopeSnapAI`

---

## SECTION 2 — TECH STACK

| Layer | Technology | Notes |
|---|---|---|
| Frontend | Next.js 14 (App Router, TypeScript) | Hosted on Vercel |
| Backend | FastAPI + Python 3.11 | Hosted on Railway (1 Uvicorn worker — DEC-007) |
| Database | Supabase (PostgreSQL) | Project ID: `quqrvnoguofbjacrxcim` — NOT Railway DB |
| AI/ML | Gemini (OCR + analysis), YOLO, XGBoost | Gemini primary for photo analysis |
| Storage | Cloudflare R2 | Bucket: `scopesnap-uploads` |
| Auth | Clerk | JWT, Google SSO enabled |
| Delivery | Email (Houston) / WhatsApp API (PK) | |
| Analytics | PostHog | 8 events tracked in DiagnosticFlow |

**Key URLs:**
| Service | URL |
|---|---|
| Houston frontend | `https://snapai.mainnov.tech` |
| Pakistan frontend | `https://pk.snapai.mainnov.tech` |
| Backend (Railway) | `https://scopesnap-api-production.up.railway.app` |
| Health endpoint | `GET /health` → `{"status":"ok","db":"connected","environment":"production","version":"0.1.0"}` |
| Railway project | ID `0e78dd68-ce72-46be-a2b1-7d3119de40a4` |
| Railway service | ID `a23d5cad-d8c9-434e-a3dc-89634d8642ab` |
| Railway environment | ID `03c478ed-5720-427a-b567-d6bd2ebf3eb1` |
| Supabase project | `quqrvnoguofbjacrxcim` |
| Vercel project | `scope-snap-ai` (org: `mohammed-shoabs-projects-7844119e`) |

---

## SECTION 3 — DUAL-MARKET ARCHITECTURE (CRITICAL — READ FULLY)

**One codebase. One backend. One DB. Two live apps.**

Both markets share the same Railway service, Supabase project, Vercel deployment, and Clerk auth instance. Market isolation is at the **query level** — Pakistan data lives in `pak_*` prefixed tables.

### How market detection works (end-to-end)

**Step 1 — Frontend detects market from hostname:**
```typescript
// scopesnap-web/lib/market.ts
export function detectMarket(): Market {
  if (typeof window !== "undefined") {
    const hostname = window.location.hostname;
    if (PK_HOSTNAMES.includes(hostname) || hostname.startsWith("pk.")) {
      return "PK";
    }
  }
  return "US"; // default
}
// PK_HOSTNAMES = ["pk.snapai.mainnov.tech", "pk.snapai.app"]
```

Every API call in `lib/api.ts` automatically injects `"X-Market": detectMarket()` header.

**Step 2 — Backend routes by header:**
```python
# scopesnap-api/api/dependencies.py
def get_tables(x_market: Optional[str] = Header(None)) -> MarketTables:
    if x_market and x_market.strip().upper() == "PK":
        return _PK_TABLES   # pak_fault_cards_v, pak_brands, etc.
    return _US_TABLES        # fault_cards, brands, etc.
```

**Step 3 — Database: `pak_*` tables + compatibility views**

| Backend symbol | US resolves to | PK resolves to |
|---|---|---|
| `tables.fault_cards` | `fault_cards` | `pak_fault_cards_v` |
| `tables.brands` | `brands` | `pak_brands` |
| `tables.labor_rates` | `labor_rates_houston` | `pak_labor_rates_v` |
| `tables.data_defaults` | `data_defaults` | `pak_data_defaults` |
| `tables.replacement_costs` | `replacement_cost_estimates` | `pak_replacement_costs_v` |
| `tables.lifecycle_rules` | `lifecycle_rules` | `pak_lifecycle_rules_v` |
| _(pressure targets)_ | `operating_targets` | `pak_operating_targets` |

### THREE CHANGE SCENARIOS — always follow these rules

| Scenario | Frontend | Backend | DB |
|---|---|---|---|
| **PK only** | Gate with `detectMarket() === "PK"` | Gate with `if tables.market == "PK":` | Only touch `pak_*` tables |
| **US only** | Gate with `detectMarket() === "US"` | Default (non-PK) path | Only touch standard US tables |
| **Both (universal)** | No gate | No gate | Shared tables — one migration applies to both |

**ONE GIT PUSH DEPLOYS BOTH MARKETS SIMULTANEOUSLY.** Always test PK changes at `pk.snapai.mainnov.tech` and Houston changes at `snapai.mainnov.tech`.

### Two Markets at a Glance

| Attribute | Houston (US) | Pakistan (PK) |
|---|---|---|
| URL | snapai.mainnov.tech | pk.snapai.mainnov.tech |
| Currency | USD ($) | PKR (₨) |
| Language | English only | English + Urdu (RTL toggle) |
| Brands | 15 US brands (Carrier, Trane, York, Goodman…) | 15 PK brands (Gree, Haier, Dawlance, Orient…) |
| Model records | 76 | 72 |
| Refrigerants | R-410A / R-22 | R-32 / R-410A / R-22 / Not Sure |
| Delivery | Email (primary) | WhatsApp + Email |
| Customer entry | Name + address (Property table) | Name + phone only (Assessment row — see DEC-012) |
| X-Market header value | `US` | `PK` |

---

## SECTION 4 — KEY FILES

### Frontend (`scopesnap-web/`)
| File | Purpose |
|---|---|
| `lib/market.ts` | `detectMarket()`, `MARKET_CONFIG`, `formatCurrency()`, `getLanguage()` |
| `lib/api.ts` | All typed API fetch wrappers — X-Market header injection on every call |
| `lib/modelCache.ts` | Client-side model cache (`/api/models/all`), `getBrands()`, `searchModels()` |
| `lib/urdu-strings.ts` | All Urdu translation strings |
| `components/StepZeroPanel.tsx` | Nameplate entry screen — brand/model lookup, DB/Est./Edited badge logic, electrical spec auto-fill |
| `components/diagnostic/DiagnosticFlow.tsx` | Main diagnostic step renderer |
| `app/(app)/assess/page.tsx` | New assessment page — PK-gated: RefrigerantPicker, WhatsApp phone field, Ahmed Khan placeholder |
| `app/(app)/assessment/[id]/page.tsx` | Assessment view — PK-gated: WhatsApp Send button, X-Market header in `getAuthHeaders()`. R.7: contractor profile guard (company_name + phone required before sendEstimate) |
| `app/(app)/diagnoses/page.tsx` | Diagnosis history list — requires Clerk JWT (DEC-030) |
| `app/(app)/diagnoses/[session_id]/page.tsx` | Single diagnosis detail + FaultResolutionScreen |
| `app/d/[share_token]/page.tsx` | Public share page — no auth, raw fetch + X-Market header (DEC-030) |
| `components/StagingBanner.tsx` | Amber banner shown on all staging pages (NEXT_PUBLIC_ENV=staging) |
| `components/FaultResolutionScreen.tsx` | Fault card display with action steps + share/feedback buttons |
| `components/DiagnosisFeedbackModal.tsx` | Thumbs up/down feedback modal for diagnoses |

### Backend (`scopesnap-api/`)
| File | Purpose |
|---|---|
| `api/diagnostic.py` | All diagnostic session logic, PSI routing, fault card return |
| `api/dependencies.py` | `get_tables()` — `_US_TABLES` / `_PK_TABLES` constants |
| `api/assessments.py` | Assessment CRUD + `customer_phone/name/email` storage on Assessment row |
| `api/estimates.py` | Estimate generation — reads `Assessment.customer_*` first, falls back to `Property.customer_*` |
| `db/migrations/versions/` | Alembic migrations — current head: `029` (peak_season_surcharge_percent + seasonal_modifier_pct — applied 2026-05-20 via Supabase direct, WA-7 pattern) |
| `services/condition_signals.py` | `derive_condition_signal_from_assessment()` — condition_signal vocabulary for lifecycle_rules lookups |
| `scripts/load_repo_pakistan.py` | Loads `pak_*` tables from `ac_data_repo_pakistan.json` |

---

## SECTION 5 — MANDATORY RULES (NEVER SKIP)

### Rule 1 — Git operations from the Linux sandbox (DEC-004 + DEC-013)

**NEVER** `git add/commit/push` from the NTFS-mounted workspace in the Linux sandbox. The sandbox cannot write `.git/index.lock` on NTFS.

**Correct workflow:**
```bash
# 1. Write files to Linux tmpfs (sandbox outputs dir)
# 2. Clone the repo fresh
git clone "https://TOKEN@github.com/mohammed-shoab/ScopeSnapAI" /tmp/snapai_tmp
# 3. Copy changed files from outputs to clone
cp /sessions/.../outputs/changed_file.py /tmp/snapai_tmp/scopesnap-api/api/
# 4. Commit and push from /tmp/snapai_tmp
cd /tmp/snapai_tmp && git add -A && git commit -m "..." && git push origin main
```

**NEVER use `git stash` from the sandbox** — it truncates TSX/TS files on NTFS (DEC-013). Use WIP commits instead.

### Rule 2 — Emoji files (DEC-005 / legacy note)

Files containing emoji (✅ ⚠️ 🔧 📸) cannot be safely read from the NTFS mount during git blob construction. Use `git cat-file blob <sha>` to read them from git objects instead:
```python
r = subprocess.run(['git','cat-file','blob', BLOB_SHA], capture_output=True)
content_bytes = r.stdout  # clean UTF-8
```

### Rule 3 — Deploy verification (DEC-002)

A git push is NOT complete until BOTH are confirmed:
1. **Railway health:** `GET https://scopesnap-api-production.up.railway.app/health` returns `{"status":"ok","db":"connected"}`
2. **Vercel:** deployment shows "Ready" on the dashboard

Never say "done" or "deployed" after just `git push`. Check both. Sandbox cannot curl external URLs — use the Chrome browser tool to visit the health endpoint.

### Rule 4 — Alembic

Current migration version: **`029`**. Next migration MUST be **`030`**.
Migrations run automatically on Railway boot via `start.sh` (`alembic upgrade head`).
Check `alembic_version` table in Supabase before pushing any new migration.
**CRITICAL:** Never use em-dashes or unescaped quotes inside Python string literals in migration files. Use `json.dumps()` for data blobs. Always run `python3 -m py_compile <migration.py>` before committing. See TECH_STACK.md WA-7 for the Supabase-direct apply pattern.

### Rule 5 — Database is Supabase, never Railway

`DATABASE_URL` on Railway points to Supabase. There is NO Railway PostgreSQL service. SQL patches always go to the Supabase SQL editor.

### Rule 6 — After any merge, check for NTFS file truncation

```bash
git diff <last-good-sha>..HEAD -- 'scopesnap-web/**/*.tsx' 'scopesnap-web/**/*.ts' --stat
```
Any file showing net deletion near the end is likely truncated. Restore with `git show <good-sha>:<path> > <path>`.

### Rule 7 — NTFS null-byte padding (DEC-010)

Files written to NTFS by the Linux sandbox may have null bytes at the end. Strip before processing:
```python
raw = open(path, 'rb').read()
clean = raw.rstrip(b'\x00')
```

---

## SECTION 6 — PSI THRESHOLDS (CURRENT, VERIFIED)

| Refrigerant | Normal suction range | high_min |
|---|---|---|
| R-410A (US) | 108–144 PSI | 145 PSI |
| R-410A (PK) | 125–144 PSI | 145 PSI |
| R-22 (both) | 55–87 PSI | 88 PSI |
| R-32 (PK) | 115–139 PSI | 140 PSI |

**Verified test case (Houston 2026-05-18):** 128 PSI R-410A → NORMAL ✅
**Verified test case (PK 2026-05-19):** 130 PSI R-410A → discharge PSI step (not Card 13) ✅

---

## SECTION 7 — CURRENT DEPLOYMENT STATE (2026-05-19)

| Layer | Commit | Status |
|---|---|---|
| Vercel (both domains) | `02ad667` | Production Live ✅ |
| Railway backend | `02ad667` | Health OK ✅ |
| Alembic migration | `029` (peak_season_surcharge_percent + seasonal_modifier_pct) | Applied via Supabase direct |
| `pak_data_defaults` | 1 row (market=PK) | Seeded |
| `pak_operating_targets` | PK PSI thresholds + R-32 (5 rows, 30-50C ambient) | Seeded |
| `pak_pricing_tiers` | 45 rows (15 cards × 3 tiers) | Seeded (Track P) |
| `lifecycle_rules` | 44 rows (expanded via migration 028) | Seeded (Track REC.3) |
| `diagnostic_sessions.share_token` | 62/62 non-null | Backfilled 2026-05-20 (D.6) |

**Recent commits (newest first):**
- `02ad667` — docs(TECH_STACK+BRAIN): full post-audit update (2026-05-20)
- `35f450c` — docs: all QA decisions resolved — D.6 backfill done, R.7+S.7 shipped
- `172b825` — fix(R.7+S.7): contractor profile guard on sendEstimate + StagingBanner
- `53db54a` — fix(D.11): pass Clerk JWT token to diagnostic finalize call
- `928a476` — fix(BUG-024): diagnoses pages guard on isLoaded before getToken()
- `fe5b02a` — fix(BUG-023): diagnostic list+result use pak_fault_cards directly
- `f82d760` — fix(diagnostic): CORS-aware 500s + has_more/share_token in list response

---

## SECTION 8 — COMPLETE DECISIONS LOG (DEC-001 to DEC-013)

| # | Decision | Rule |
|---|---|---|
| DEC-001 | Database on Supabase, not Railway | `DATABASE_URL` points to Supabase. Never add Railway PostgreSQL. |
| DEC-002 | Alembic auto-runs on Railway boot | `start.sh` runs `alembic upgrade head`. Never push a migration already applied. |
| DEC-003 | `multi` steps use `options_jsonb`, not `reading_spec` | Migrations patching reading spec for multi steps must target `options_jsonb`. |
| DEC-004 | Git from sandbox via `/tmp` clone | Cannot write `.git/` lock files on NTFS. Clone to `/tmp`, commit and push from there. |
| DEC-005 | Railway auth = Clerk JWT from browser | No dev bypass token. Get JWT via `window.Clerk.session.getToken()` from authenticated tab. |
| DEC-006 | `photo_branch_map` overrides numeric reading in multi steps | AI photo "escalate" overrides meter reading's branchKey. Skip photo slot during pure reading QA. |
| DEC-007 | UVICORN_WORKERS = 1 | Halves Railway memory. Do not increase without checking $5/mo spend cap. |
| DEC-008 | Frontend TypeScript strict — `spec.type` strings must match exactly | `classifyReading()` matches exact strings: `"psi"`, `"microamps"`, `"voltage_l1_l2"`, `"amperage_rla"`, `"capacitance_uf"`. Wrong type silently routes to "ok". |
| DEC-009 | `GET /api/diagnostic/questions/{type}` strips spec data | Only returns `step_id`, `step_order`, `question_text`, `input_type`. Use fetch interceptor to inspect full `next_step` data. |
| DEC-010 | NTFS null-byte file padding | Files written by Linux sandbox to NTFS may have null bytes appended. Always `rstrip(b'\x00')` before processing `.md` or `.json` files. |
| DEC-011 | Dual-market = shared infra, split data by `pak_*` prefix | One Railway + one Supabase + one Vercel. Market isolation is runtime query-level, not infrastructure-level. |
| DEC-012 | Customer contact stored on Assessment row (not Property) | `properties.address_line1` is NOT NULL — PK phone-only entries cannot create a Property. Store `customer_name/phone/email` on `assessments` row directly. |
| DEC-013 | Never `git stash` from Linux sandbox | Stash truncates TSX/TS files on NTFS. Use WIP commits instead. Recovery: `git show <good-sha>:<path> > <path>`. |
| DEC-016 | Legacy estimate engine deleted (2026-05-19) | `services/estimate_engine.py` deleted, `POST /api/estimates/generate` removed, `generateEstimate()` removed. All estimates now flow through `POST /api/estimates/fault-card` → `fault_estimate.py` only. |
| DEC-017–023 | Staging infra, condition_signals, diagnoses screen (2026-05-19–20) | See DECISIONS.md for full entries |
| DEC-024 | condition_signal vocabulary v1 | 9 signals; first match wins; must not rename existing strings |
| DEC-025 | `diagnosis_feedback` table — single shared table (no pak_ variant) | FK to diagnostic_sessions which is already shared |
| DEC-026 | DiagnosticFlow resolves → /diagnoses/<id> (not evidence phase) | Estimate still reachable from Assessments list |
| DEC-027 | Edit tool truncates ALL files with non-ASCII, not just emoji TSX | Use Python replace() for any Unicode-containing file |
| DEC-028 | git fast-import bypasses corrupted .git/index entirely | Preferred pattern for NTFS repos |
| DEC-029 | companies table has NO market column | Market always via X-Market header → get_tables() |
| DEC-030 | apiFetch does NOT auto-inject Clerk JWT | Pass `token: await getToken()` in every authenticated call |
| DEC-031 | fault_cards PK is card_id, never id | JOIN on fc.card_id; SELECT card_id |
| DEC-032 | estimate/[id]/page.tsx is dead code | Real builder is assessment/[id]/page.tsx |
| DEC-034 | Missing imports inside try/except silently swallow NameError | Verify import exists AND resolves at startup |
| DEC-035 | Grep target files before implementing any feature | Feature may be partially present already |

---

## SECTION 9 — NAMEPLATE SCREEN (STEP ZERO) — JOBS-STYLE DESIGN

This was a major board and architectural decision. Summary:

**7 fields only** (3 removed permanently — Serial#, Factory Charge, Voltage nameplate — never used in diagnostic routing):
- Tonnage, Refrigerant, RLA, LRA, CAP µF, MCA, MOCP

**Visual treatment (board decision — see Section 10):**
- Auto-filled from DB: soft grey background + **"DB"** badge (calm, not shouting)
- Inferred from LRA correlation: grey + **"Est."** badge
- DB null: white background, blank, cursor invitation
- Single tap → inline edit, no modal, no drawer
- Badge changes from "DB" → **"✏ Edited"** (orange) on override
- No bulk-clear button
- `spec_source` tracked per field: `"database"` / `"nameplate_override"` / `"nameplate_entry"`
- Model # = read-only reference chip (not editable, not used in routing)

**Currently implemented (as of 2026-05-18 BUG-012 fix):**
- Electrical spec auto-fill works via `ELECTRICAL_SPECS_BY_TONNAGE` static lookup in `StepZeroPanel.tsx`
- Badge logic (DB / Est. / ✏ Edited) implemented and verified live
- File: `scopesnap-web/components/StepZeroPanel.tsx`

---

## SECTION 10 — BOARD DECISIONS (SnapAI Advisory Board)

The SnapAI advisory board (@board) is convened for major product and architecture decisions. All board sessions are documented here.

### Board Decision: Editable spec fields (Jobs-style)

**Question asked:** Should auto-filled spec fields still be visible and editable even when the app fills them from the database?

**Board consensus (unanimous):**
Yes. The tech in the field may find a discrepancy on the actual nameplate. The app should:
- Show all 7 spec fields visibly (never hide)
- Auto-filled fields appear dim/grey with a "DB" badge — confident but not shouting
- Single tap to edit inline — no modal, no drawer
- Override logs as `spec_source: "nameplate_override"` for data quality tracking
- No bulk-clear button (would destroy useful data quality signals)

This is the **Jobs principle**: the app shows what it knows quietly, and the tech corrects anything wrong with a single tap.

### Board Decision: Cap µF inference for new Houston series

**Context:** Four new HVAC series were added. Heil and Coleman are different corporate families — never clone values between them.

**Corporate family rule (CRITICAL — never violate):**
| Brand | Corporate Owner |
|---|---|
| York, Coleman, Luxaire | Johnson Controls (JCI) |
| Heil, Tempstar, Comfortmaker, Arcoaire | ICP / Carrier Global |

Cap µF for 3 series inferred by LRA correlation (public spec sheets inaccessible for exact values):

| Series | 1.5T | 2.0T | 2.5T | 3.0T | 3.5T | 4.0T | 5.0T |
|---|---|---|---|---|---|---|---|
| Heil QuietComfort | 35 µF | 35 µF | 35 µF | 40 µF | 45 µF | 45 µF | 50 µF |
| Coleman Echelon (recip 1.5–3.5T) | 45 µF | 45 µF | 50 µF | 55 µF | 60 µF | — | — |
| Coleman Echelon (scroll 4–5T) | — | — | — | — | — | 45 µF | 50 µF |
| Coleman Echelon Deluxe | — | 35 µF | — | 45 µF | — | 55 µF | 60 µF |
| Heil QCD | null | null | — | null | — | null | null |

Inferred values: `source: "inferred_by_lra_correlation"`, UI badge: `"Est."` (not `"DB"`). Fan µF = 5 µF across all.
Heil QCD: electrical data NOT available (page 33 of ICP doc inaccessible). `data_status: "pending"`. Cannot infer without LRA. Do not populate — show "data pending — enter manually."

---

## SECTION 11 — PAKISTAN-SPECIFIC TECHNICAL DATA

### PK Context
- Voltage: 220–240V / 50Hz / single phase
- Summer ambient: 35–52°C (Karachi, Lahore, Multan, Jacobabad)
- Dominant unit: wall-mounted split (indoor + outdoor)
- Standard residential tonnages: **1.0T, 1.5T, 2.0T only**
- 2.5T is NOT standard residential — show commercial warning banner
- ~90–95% non-inverter units use capillary tube metering
- Currency: PKR (₨)
- 15 brands, 72 series in database

### PK Charging Targets (verified)
| Refrigerant | Metering | Target SH | Notes |
|---|---|---|---|
| R-22 capillary (95% of units) | Capillary | 5°C/9°F at 35°C ambient; 3°C/5°F at 45°C ambient | Decrease 1°C per 5°C above 35°C |
| R-22 TXV (premium Daikin, Mitsubishi, Panasonic) | TXV | Subcooling 5°C/9°F primary | |
| R-410A (Gree GWC, Haier HSU) | Likely TXV/piston | Subcooling 5°C/9°F primary | |
| R-32 | Inverter only | No fixed-speed R-32 in Pakistan | All inverter — separate diagnostic path |

### PK Fault Pressure Signatures (verified PSI thresholds)
**R-22 at 35°C:**
- Low charge: suction <60 PSI / discharge <230 PSI
- Dirty condenser: discharge >300 PSI
- Overcharge: suction >78 PSI / discharge >300 PSI / subcooling >10°C
- Dirty evaporator: suction <62 PSI / delta-T >14°C

**Pakistan-specific diagnostic notes:**
- Voltage fluctuations (180–240V in some cities) — verify voltage before diagnosing electrical faults
- Adulterated R-22 cylinders common — if pressure/performance doesn't match expected, suspect refrigerant quality
- Extreme ambient (45–52°C) causes baseline discharge to read high naturally — do not misdiagnose as dirty condenser without confirming ambient temp

### PK Electrical Defaults (verified — source: ZamZam HVAC + ACHR News)
| Tonnage | Comp µF | Indoor fan µF | Outdoor fan µF | RLA | LRA | MCA | MOCP |
|---|---|---|---|---|---|---|---|
| 1.0T | 20 µF | 1.2 µF | 2.5 µF | 6.0A | 36A | 8.0A | 15A |
| 1.5T | 30 µF | 1.5 µF | 2.5 µF | 9.5A | 55A | 12.5A | 20A |
| 2.0T | 40 µF | 2.0 µF | 3.5 µF | 13.0A | 76A | 16.5A | 25A |

---

## SECTION 12 — QA HISTORY

| Date | Markets | Outcome | Bugs Fixed |
|---|---|---|---|
| 2026-05-20 | Full QA — Tracks R/R9/REC/D/P/Staging | PASS ✅ | 48 PASS / 1 AUTO-FIX. D.6 backfill (62/62 share_tokens), R.7 profile guard, S.7 staging banner shipped |
| 2026-05-19 | PK (SOW Addendum) | PASS ✅ | BUG-015 (X-Market header), BUG-016 (PK PSI routing); A-2/A-4/A-5 verified; B-1/C-3 seeded |
| 2026-05-18 | Houston | PASS ✅ | BUG-011 (badge logic), BUG-012 (electrical spec auto-fill), DEC-013 CRLF truncation recovery (10 files) |
| 2026-05-15 | Houston + PK | PASS | BUG-010b (`_complete_service_session` rollback) |
| 2026-05-11 | Houston + PK | PASS | Multiple routing bugs, photo policy, inverter flag |

**Bug details (most recent):**

**BUG-016** (fixed `01082c6`): PK market — 130 PSI R-410A suction (normal range) was routing to US Card 13 (Dirty Coil). Root cause: `pak_diagnostic_questions` table does not exist; PK was falling through to US question tree. Fix: PK-gated intercept in `diagnostic.py` after `_pk_evaluate_pressure` returns "ok" for suction — routes to discharge PSI step instead.

**BUG-015** (fixed `0ce93a8`): PK market — all diagnostic API calls missing `X-Market: PK` header (hitting US tables). Root cause: `getAuthHeaders()` in `assessment/[id]/page.tsx` omitted `"X-Market": detectMarket()`. Fix: added the header.

**BUG-012** (fixed `6a8eecb`): Electrical spec fields blank after model selection. Fix: `ELECTRICAL_SPECS_BY_TONNAGE` static lookup table added to `StepZeroPanel.tsx`.

**BUG-011** (fixed `817f712`): DB badge never flipped to "✏ Edited" on manual override. Fix: `editedManualFields: Set<string>` state tracking in `StepZeroPanel.tsx`.

---

## SECTION 13 — COMPLETED TRACKS + PENDING BACKLOG (as of 2026-05-20)

### All Tracks — COMPLETE ✅

| Track | Status | Notes |
|-------|--------|-------|
| Track Q (Q.1–Q.7 + Q.6.5) | ✅ Complete | 8 production hotfixes, recommendation engine, draft refresh |
| Track R (R.1–R.8) | ✅ Complete | Staging env, keepalive, promote script, contractor profile guard (R.7) |
| Track R.9 | ✅ Complete | DB-driven seasonal modifier, both markets, alembic 029 |
| Track REC (REC.1–REC.3) | ✅ Complete | condition_signals.py, lifecycle_rules 44 rows, DEC-034 import fix |
| Track D (D.1–D.15) | ✅ Complete | Diagnoses screen, 5 endpoints, BUG-D.AUTH all fixed, D.6 backfill |
| Track P | ✅ Complete | PK pricing tiers 45 rows, bilingual descriptions, WhatsApp deeplink |
| Track Staging | ✅ Complete | StagingBanner.tsx, dual keepalive, promote-to-prod.sh |

### Remaining Backlog / Future Tracks

- **Houston SOW Tasks 2–9**: Water Dripping 404, Contactor crash, Service/Tune-Up 503, Phase 2 PSI routing, photo policy, inverter flag, diagnostic event logging, brand escape path
- **PK SOW gaps**: A-1 (electrical spec auto-fill from `pak_brands` JSONB), A-3 (Send via WhatsApp button) — A-2/A-4/A-5 complete
- **Heil QCD data**: RLA, LRA, Cap µF, MCA, MOCP pending. `data_status: "pending"` in app. Needs ICP TechAssist portal or AHRI database.
- **Tech debt**: Per-unit electrical specs in `equipment_models` for real "DB" badge vs "Est."
- **Diagnoses → Estimate flow**: "Generate estimate from here" button on FaultResolutionScreen deferred to v1.5 (DEC-026)

---

## SECTION 14 — ALL FILES & LOCATIONS

**Primary working folder:** `C:\Users\Shoab\My Drive\Personal Claude\`
(Google Drive — syncs to both laptops. All new files go here.)

### Documentation files
| File | Purpose |
|---|---|
| `SnapAI_SOW_AI.md` | Houston SOW — AI developer brief (9 tasks, cap µF tables, Jobs-style spec fields) |
| `SnapAI_SOW_Human.docx` | Houston SOW — human-readable formatted version |
| `SnapAI_PK_SOW_Addendum.md` | Pakistan addendum v1.1 — AI developer brief (verified charging targets, fault signatures, defaults) |
| `SnapAI_PK_SOW_Human_v2.docx` | Pakistan addendum — human-readable formatted version |
| `SnapAI_Continuation_Prompt.md` | This file — paste at start of every new session |

### Data files
| File | Purpose |
|---|---|
| `pakistan_hvac_gap_data.json` | Verified PK charging targets, fault signatures, electrical defaults |
| `ac_data_repo_pakistan_v4.json` | Full PK brand/series database (needed for A-1 seeding) |
| `hvac_verified_specs.json` | Verified Heil/Coleman Houston electrical specs (source for Task 0 data) |

### Skills
| File | Purpose |
|---|---|
| `snapai-qa.skill` | QA skill — install by double-clicking. Runs full 8-phase blocking QA: U