"""Data-isolation tests for the market-routing boundary (api.dependencies).

Every read/write in the API resolves its tables through get_tables(), keyed on
the X-Market header. These tests pin the isolation invariant: a PK request can
never resolve a US table (or vice versa) for any market-specific table, and the
resolver is immutable + defaults safely. This is the layer that prevents
cross-market data contamination.
"""
import dataclasses

import pytest

from api.dependencies import (
    get_tables, get_market, MarketTables, _US_TABLES, _PK_TABLES,
)

# Fields that MUST differ between markets (market-specific physical tables/views).
# `data_defaults`/`brands`/`pricing_tiers` use distinct PK names too; assert all.
_MARKET_SPECIFIC = [
    "fault_cards", "error_codes", "labor_rates", "data_defaults",
    "replacement_costs", "lifecycle_rules", "brands", "pricing_tiers",
]


def test_pk_header_routes_to_pk_tables():
    t = get_tables("PK")
    assert t.market == "PK"
    assert t is _PK_TABLES


@pytest.mark.parametrize("hdr", [None, "", "US", "us", "  ", "ZZ", "p k"])
def test_non_pk_defaults_to_us(hdr):
    t = get_tables(hdr)
    assert t.market == "US"
    assert t is _US_TABLES


@pytest.mark.parametrize("hdr", ["PK", "pk", "Pk", " pk ", "PK\n"])
def test_pk_header_case_and_whitespace_insensitive(hdr):
    assert get_tables(hdr).market == "PK"
    assert get_market(hdr) == "PK"


def test_no_market_specific_table_name_is_shared():
    """The core isolation invariant: no market-specific table resolves to the
    same physical name in both markets."""
    for field in _MARKET_SPECIFIC:
        us = getattr(_US_TABLES, field)
        pk = getattr(_PK_TABLES, field)
        assert us != pk, f"{field} resolves to the same table in US and PK: {us!r}"


def test_pk_tables_are_namespaced():
    """Every PK market-specific table is in the pak_* namespace, so a stray US
    query string can never accidentally hit PK data and vice versa."""
    for field in _MARKET_SPECIFIC:
        assert getattr(_PK_TABLES, field).startswith("pak_"), field
        assert not getattr(_US_TABLES, field).startswith("pak_"), field


def test_resolver_is_immutable():
    """Frozen dataclass — a request handler cannot mutate the shared singleton
    and leak a table name into another market's request."""
    with pytest.raises(dataclasses.FrozenInstanceError):
        _PK_TABLES.fault_cards = "fault_cards"  # type: ignore[misc]


def test_singletons_are_stable_across_calls():
    """Same object returned every call — no per-request rebuild that could drift."""
    assert get_tables("PK") is get_tables("pk")
    assert get_tables("US") is get_tables(None)
