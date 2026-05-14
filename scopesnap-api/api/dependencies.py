"""
SnapAI — Market-aware FastAPI dependencies (Phase 3)

Reads the X-Market HTTP header (set by the frontend lib/api.ts on every
request) and resolves the correct Supabase table names for the active market.

Markets:
  US (default) — Houston production tables
  PK           — Pakistan pak_* tables

Usage in any endpoint:
    from api.dependencies import get_tables, MarketTables

    @router.get("/something")
    async def my_endpoint(
        tables: MarketTables = Depends(get_tables),
        db: AsyncSession = Depends(get_db),
    ):
        row = await db.execute(text(f"SELECT * FROM {tables.fault_cards} WHERE ..."))
"""

from dataclasses import dataclass
from typing import Optional
from fastapi import Header


@dataclass(frozen=True)
class MarketTables:
    """Resolved table names for the active market."""
    market: str               # "US" | "PK"
    fault_cards: str
    error_codes: str
    labor_rates: str
    data_defaults: str
    replacement_costs: str
    lifecycle_rules: str
    brands: str


_US_TABLES = MarketTables(
    market="US",
    fault_cards="fault_cards",
    error_codes="error_codes",
    labor_rates="labor_rates_houston",
    data_defaults="data_defaults",
    replacement_costs="replacement_cost_estimates",
    lifecycle_rules="lifecycle_rules",
    brands="brands",
)

_PK_TABLES = MarketTables(
    market="PK",
    fault_cards="pak_fault_cards",
    error_codes="pak_error_codes",
    labor_rates="pak_labor_rates",
    data_defaults="pak_data_defaults",
    replacement_costs="pak_replacement_costs",
    lifecycle_rules="pak_lifecycle_rules",
    brands="pak_brands",
)


def get_tables(x_market: Optional[str] = Header(None)) -> MarketTables:
    """
    FastAPI dependency — returns the correct MarketTables for this request.

    X-Market header is injected by:
      - Frontend: lib/api.ts (detectMarket() on every fetch)
      - Middleware: middleware.ts (x-market from hostname, server-side)
    Falls back to US when header is absent or unrecognised.
    """
    if x_market and x_market.strip().upper() == "PK":
        return _PK_TABLES
    return _US_TABLES


def get_market(x_market: Optional[str] = Header(None)) -> str:
    """Convenience dep — returns 'PK' or 'US'."""
    if x_market and x_market.strip().upper() == "PK":
        return "PK"
    return "US"
