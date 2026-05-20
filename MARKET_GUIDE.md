# SnapAI — Dual-Market Architecture Guide

> **READ THIS FIRST** in every new session.
> SnapAI runs as two separate live apps — one for Houston (US) and one for Pakistan (PK).
> Last updated: 2026-05-20

---

## The Two Apps at a Glance

| Attribute | 🇺🇸 Houston (US) | 🇵🇰 Pakistan (PK) |
|---|---|---|
| **URL** | https://snapai.mainnov.tech | https://pk.snapai.mainnov.tech |
| **Currency** | USD — `$` | PKR — `₨` |
| **Language** | English only | English + Urdu (RTL toggle) |
| **Brands** | 15 US brands (Carrier, Trane, York…) | 15 PK brands (Gree, Haier, Dawlance, Orient…) |
| **Refrigerants** | R-410A / R-22 | R-32 / R-410A / R-22 / Not Sure |
| **Pressure targets** | `operating_targets` table | `pak_operating_targets` table |
| **Send report** | Email (primary) | WhatsApp (primary) + Email (secondary) |
| **DB table prefix** | _(none)_ | `pak_` |
| **X-Market header** | `US` | `PK` |
| **Vercel project** | scope-snap-ai (main branch) | pk.snapai.mainnov.tech (same Vercel project, PK subdomain) |
| **Railway backend** | scopesnap-api-production.up.railway.app | Same Railway backend — market routed via header |

---

## How Market Detection Works (end-to-end)

### 1. Frontend: hostname → market constant

File: `scopesnap-web/lib/market.ts`

```typescript
export function detectMarket(): Market {
  if (typeof window !== "undefined") {
    const hostname = window.location.hostname;
    if (PK_HOSTNAMES.includes(hostname) || hostname.startsWith("pk.")) {
      return "PK";
    }
  }
  return "US";   // default
}
```

`PK_HOSTNAMES = ["pk.snapai.mainnov.tech", "pk.snapai.app"]`

Every API call in `lib/api.ts` adds `"X-Market": detectMarket()` to the request headers automatically.

### 2. Backend: X-Market header → table names

File: `scopesnap-api/api/dependencies.py`

```python
def get_tables(x_market: Optional[str] = Header(None)) -> MarketTables:
    if x_market and x_market.strip().upper() == "PK":
        return _PK_TABLES   # pak_fault_cards_v, pak_error_codes_v, etc.
    return _US_TABLES        # fault_cards, error_codes, etc.
```

All four core API files inject `tables: MarketTables = Depends(get_tables)` and use `tables.fault_cards`, `tables.labor_rates`, etc. — never hardcoded table names.

### 3. Database: pak_* tables + views

Pakistan data lives in dedicated tables and compatibility views that expose the same column names as the US tables, so backend SQL queries are identical.

| Backend symbol | US resolves to | PK resolves to |
|---|---|---|
| `tables.fault_cards` | `fault_cards` | `pak_fault_cards_v` |
| `tables.error_codes` | `error_codes` | `pak_error_codes_v` |
| `tables.labor_rates` | `labor_rates_houston` | `pak_labor_rates_v` |
| `tables.data_defaults` | `data_defaults` | `pak_data_defaults` |
| `tables.replacement_costs` | `replacement_cost_estimates` | `pak_replacement_costs_v` |
| `tables.lifecycle_rules` | `lifecycle_rules` | `pak_lifecycle_rules_v` |
| `tables.brands` | `brands` | `pak_brands` |
| _(pressure targets)_ | `operating_targets` | `pak_operating_targets` |

---

## Working Rules — Three Scenarios

### Scenario A: Change PK Only (do NOT touch US)

**Frontend gate:**
```typescript
if (detectMarket() === "PK") {
  // PK-only UI code here
}
```

**Backend gate:**
```python
if tables.market == "PK":
    # PK-only logic here
```

**DB: only modify `pak_*` tables.** Never touch `fault_cards`, `brands`, `labor_rates_houston`, etc.

**Examples of PK-only code today:**
- `RefrigerantPicker` component on assess page (gated by `detectMarket() === "PK"`)
- WhatsApp Send button (gated by `detectMarket() === "PK" && estimate.homeowner_report_url && sendPhone`)
- Urdu language toggle (PK only — `getLanguage()` returns "en" on US)
- PKR currency display (via `formatCurrency()` — auto-detects market)
- Pressure hint text showing R-32/R-410A/R-22 targets (PK only in diagnostic UI)

---

### Scenario B: Change US Only (do NOT touch PK)

**Frontend gate:**
```typescript
if (detectMarket() === "US") {
  // US-only code here
}
```

**Backend: no gate needed** — US is the default path when `tables.market !== "PK"`.

**DB: only modify the standard US tables** (`fault_cards`, `brands`, `labor_rates_houston`, etc.). Never touch `pak_*` tables.

---

### Scenario C: Universal Change (shows in BOTH apps)

**Frontend: no market gate** — write the code in the shared path.

**Backend: no market gate** — write logic that runs regardless of `tables.market`.

**DB migrations:** If you add a column to a shared table (e.g. `assessments`, `estimates`, `properties`), it applies to both markets automatically because both apps share the same Supabase database and the same Railway backend.

**Examples of shared/universal code today:**
- All authentication (Clerk) — same for both markets
- Assessment creation (`POST /api/assessments`) — shared, stores `customer_phone` etc. on the Assessment row
- Diagnostic engine (`api/diagnostic.py`) — shared question tree; PK gets pressure targets from `pak_operating_targets` via market-aware lookup
- Estimate builder UI (`/assessment/[id]`) — shared layout; currency display adapts via `formatCurrency()`
- Document generation (`POST /api/estimates/{id}/documents`) — shared PDF generator

---

## PK-Specific Files (touch these for PK changes)

### Frontend
| File | What it controls |
|---|---|
| `lib/market.ts` | `detectMarket()`, `formatCurrency()`, `getLanguage()`, `MARKET_CONFIG` |
| `lib/urdu-strings.ts` | All Urdu translation strings |
| `lib/language-context.tsx` | LanguageProvider + useLang hook |
| `components/ui/LanguageToggle.tsx` | اردو / English toggle button |
| `app/(app)/assess/page.tsx` | Lines gated `detectMarket() === "PK"`: RefrigerantPicker, WhatsApp phone field |
| `app/(app)/assessment/[id]/page.tsx` | Lines gated `detectMarket() === "PK"`: WhatsApp Send button, phone pre-fill |

### Backend
| File | What it controls |
|---|---|
| `api/dependencies.py` | `_PK_TABLES` mapping + `get_tables()` dependency |
| `api/assessments.py` | PK-market `refrigerant_type` field storage |
| `api/estimates.py` | PKR pricing; customer_phone pre-fill from Assessment row |
| `api/diagnostic.py` | `pak_operating_targets` lookup for PK pressure steps |

### Database (Supabase)
| Table/View | Type | Purpose |
|---|---|---|
| `pak_brands` | Table | 15 PK brands (Gree, Haier, Dawlance, Orient, etc.) |
| `pak_fault_cards` | Table | 15 fault cards with PKR pricing |
| `pak_fault_cards_v` | View | Schema-compatible with US `fault_cards` |
| `pak_error_codes` | Table | Error codes for PK brands |
| `pak_error_codes_v` | View | Schema-compatible with US `error_codes` |
| `pak_labor_rates` | Table | PKR labor rate (1 row) |
| `pak_labor_rates_v` | View | Schema-compatible with US `labor_rates_houston` |
| `pak_data_defaults` | Table | Electrical defaults + tech warnings |
| `pak_replacement_costs` | Table | PKR unit replacement costs by tonnage |
| `pak_replacement_costs_v` | View | Schema-compatible with US `replacement_cost_estimates` |
| `pak_lifecycle_rules` | Table | Lifecycle rules (currently 0 rows → backend defaults) |
| `pak_lifecycle_rules_v` | View | Schema-compatible with US `lifecycle_rules` |
| `pak_operating_targets` | Table | Suction/discharge PSI targets by refrigerant type (5 rows, 30-50C ambient) |
| `pak_pricing_tiers` | Table | 45 rows: 15 fault cards x 3 tiers (good/better/best) in PKR (Track P) |
| `pak_fault_card_descriptions` | Table | English descriptions per fault card + tier |
| `pak_fault_card_urdu_descriptions` | Table | Urdu descriptions per fault card + tier |

### Seed Script
`scopesnap-api/scripts/load_repo_pakistan.py` — loads all `pak_*` tables from `ac_data_repo_pakistan.json`.

Re-seeding workflow:
1. Run `python scripts/load_repo_pakistan.py` to generate INSERT SQL
2. Paste SQL into Supabase SQL editor (Monaco) and run
3. Verify row counts match expected

---

## US-Specific Files (touch these for US changes)

### Frontend
No dedicated files — all US-specific logic lives in the default (un-gated) code paths.
The assess page, diagnostic flow, and estimate builder render US behaviour by default.

### Backend
No dedicated files — US is the default path in all API files when `X-Market` header is absent or `"US"`.

### Database (Supabase)
Standard tables: `brands`, `fault_cards`, `pricing_tiers`, `error_codes`,
`labor_rates_houston`, `data_defaults`, `replacement_cost_estimates`,
`lifecycle_rules`, `operating_targets`, etc.

Seed script: `scopesnap-api/scripts/load_repo.py` (loads US data from `ac_data_repo.json`).

---

## Adding a New PK-Only Feature — Checklist

1. **Frontend:** Gate UI with `if (detectMarket() === "PK")` or `{detectMarket() === "PK" && <Component />}`
2. **Backend:** Gate logic with `if tables.market == "PK":` inside the endpoint
3. **DB:** Create `pak_<table_name>` table + a compatibility view `pak_<table_name>_v` if the backend needs to query it via `tables.*`
4. **`dependencies.py`:** Add the new table symbol to `_PK_TABLES` (and a US equivalent to `_US_TABLES`)
5. **Test:** QA on `pk.snapai.mainnov.tech` — confirm nothing changed on `snapai.mainnov.tech`

## Adding a New US-Only Feature — Checklist

1. **Frontend:** Gate UI with `if (detectMarket() === "US")` (or leave un-gated if truly US-only by default design)
2. **Backend:** Add to the default (non-PK) code path
3. **DB:** Add to standard US tables only
4. **Test:** QA on `snapai.mainnov.tech` — confirm `pk.snapai.mainnov.tech` is unaffected

## Adding a Universal Feature (both markets) — Checklist

1. **Frontend:** No market gate — write in the shared component/page
2. **Backend:** No market gate — write in the shared endpoint
3. **DB:** Add to shared tables (`assessments`, `estimates`, `properties`, etc.) — one migration applies to both
4. **Test:** QA on BOTH URLs and verify behaviour on each

---

## Environment / Infrastructure Summary

| Concern | Detail |
|---|---|
| Same backend? | **Yes** — single Railway service handles both markets |
| Same database? | **Yes** — single Supabase project; market split is by table prefix |
| Same auth? | **Yes** — Clerk, same keys |
| Same Vercel project? | **Yes** — `pk.snapai.mainnov.tech` is a custom domain on the same Next.js deployment |
| How PK gets its domain | `pk.snapai.mainnov.tech` CNAME → Vercel. App detects market from hostname at runtime |
| Separate deploy needed for PK changes? | No — one push to `main` deploys both. Market routing is runtime, not build-time |

---

## Key Decision: Why Shared Backend + DB?

See `DECISIONS.md` → DEC-011.

Summary: Both markets share one Railway instance and one Supabase project.
Market isolation is achieved at the *query* level (pak_* tables) rather than
infrastructure level. This keeps costs minimal (one Railway service, one
Supabase project) while allowing fully independent data per market.
