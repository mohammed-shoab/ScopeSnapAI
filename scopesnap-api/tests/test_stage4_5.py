"""Stage 4 + 5 — weighted replace score, version endpoint, confidence recompute.

Pure-unit: no DB, no FastAPI app context. The Stage-4 scoring helpers live in the
dependency-light leading section of api/fault_estimate.py; we exec just that head
(stripping its import lines) and inject the globals it needs — same technique as
tests/test_fault_estimate_age_v2.py, extended to inject the real brand_data_loader,
re, os and dataclasses so the replace-score functions resolve.
"""
from __future__ import annotations

import importlib
import os
import re
import sys
import types

_API_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _API_DIR not in sys.path:
    sys.path.insert(0, _API_DIR)

import services.brand_data_loader as bdl  # noqa: E402
import api.version as version_api          # noqa: E402 (pure helper, no DB)


def _load_fault_estimate_head():
    """Exec the leading dependency-light portion of fault_estimate.py with the
    globals the replace-score helpers need injected (real brand_data_loader)."""
    path = os.path.join(_API_DIR, "api", "fault_estimate.py")
    src = open(path, encoding="utf-8").read()
    # The pure-function constants/helpers live in the leading section; the Stage-4
    # replace-score block sits between the "Request / Response models" marker and
    # the "POST /api/estimates/fault-card" route marker. Stitch the leading
    # constants head with the Stage-4 block, skipping the pydantic model classes
    # (which need BaseModel/Field and aren't under test here).
    models_marker = "# -- Request / Response models"
    stage4_marker = (
        "# =====================================================================\n"
        "# Stage 4 -- Track 2 shadow-mode weighted replace score"
    )
    route_marker = "# -- POST /api/estimates/fault-card"
    head_part = src[: src.index(models_marker)]
    stage4_part = src[src.index(stage4_marker) : src.index(route_marker)]
    head = head_part + "\n" + stage4_part
    mod = types.ModuleType("fe45_head")
    # Register in sys.modules so @dataclass can resolve cls.__module__ via
    # sys.modules[...] when processing annotations.
    sys.modules["fe45_head"] = mod
    import dataclasses
    mod.__dict__.update({
        "__file__": path,
        "__name__": "fe45_head",
        "os": __import__("os"),
        "Optional": __import__("typing").Optional,
        "Any": __import__("typing").Any,
        "math": __import__("math"),
        "datetime": __import__("datetime").datetime,
        "timezone": __import__("datetime").timezone,
        "logging": __import__("logging"),
        "os": os,
        "re": re,
        "dataclass": dataclasses.dataclass,
        "field": dataclasses.field,
        "asdict": dataclasses.asdict,
        "brand_data_loader": bdl,
        # capture_event is referenced only inside the route (cut away), but inject
        # a no-op just in case the head ever references it.
        "capture_event": lambda *a, **k: False,
    })
    # Strip top-level imports / router lines so exec is self-contained.
    head = "\n".join(
        ln for ln in head.splitlines()
        if not re.match(r"\s*(from|import)\s", ln)
        and not re.match(r"router\s*=", ln)
        and not ln.startswith("@router")
    )
    exec(compile(head, path, "exec"), mod.__dict__)
    return mod


fe = _load_fault_estimate_head()


# ── Stage 4: weighted replace score returns [0,1] + 5-factor breakdown ───────
def test_score_in_range_and_five_factors():
    s = fe._compute_weighted_replace_score(
        brand="Carrier", tier="entry", variant="split_ac", region="US",
        unit_age_years=14, refrigerant="R-410A",
        repair_cost=900, replacement_cost=5500,
    )
    assert 0.0 <= s.score <= 1.0
    assert set(s.factors.keys()) == {
        "remaining_life", "refrigerant", "cost_ratio", "climate", "repair_history"
    }
    # each factor carries raw / weight / contribution
    for f in s.factors.values():
        assert 0.0 <= f["raw"] <= 1.0
        assert "weight" in f and "contribution" in f


def test_unknown_brand_uses_neutral_defaults_still_in_range():
    s = fe._compute_weighted_replace_score(
        brand="NoSuchBrand", tier=None, variant=None, region="US",
    )
    assert s.record_found is False
    assert 0.0 <= s.score <= 1.0
    # with no data and neutral 0.5 factors, score should be ~0.5
    assert abs(s.score - 0.5) < 0.2


# ── cr_substituted lowers the remaining_life contribution ────────────────────
def _synthetic_record(cr_substituted: bool) -> dict:
    return {
        "brand": "TestBrand", "market": "US", "tier": "mid", "variant": "split_ac",
        "reliability_profile": {"houston_climate_adjusted": "12-16"},
        "refrigerant_compatibility": {"2010_2024": "R-410A"},
        "confidence": "medium",
        "cr_substituted": cr_substituted,
        "source_links": ["example.com (T3)"],
    }


def test_cr_substituted_lowers_remaining_life_contribution(monkeypatch):
    """Same record, cr_substituted True vs False — the True variant must have a
    strictly smaller remaining_life contribution (weight halved)."""
    def _records():
        return [_synthetic_record(cr_substituted=False)]
    def _records_cr():
        return [_synthetic_record(cr_substituted=True)]

    monkeypatch.setattr(fe.brand_data_loader, "get_replace_records", _records)
    s_false = fe._compute_weighted_replace_score(
        brand="TestBrand", tier="mid", variant="split_ac", region="US",
        unit_age_years=10,
    )
    monkeypatch.setattr(fe.brand_data_loader, "get_replace_records", _records_cr)
    s_true = fe._compute_weighted_replace_score(
        brand="TestBrand", tier="mid", variant="split_ac", region="US",
        unit_age_years=10,
    )
    assert s_true.cr_substituted is True
    assert s_false.cr_substituted is False
    rl_false = s_false.factors["remaining_life"]["contribution"]
    rl_true = s_true.factors["remaining_life"]["contribution"]
    assert rl_true < rl_false, (rl_true, rl_false)


# ── threshold env var flips the recommendation ───────────────────────────────
def test_threshold_flips_recommendation(monkeypatch):
    # Construct a record that yields a mid-range score, then move the threshold
    # below and above the score to flip recommend_replace.
    def _records():
        return [_synthetic_record(cr_substituted=False)]
    monkeypatch.setattr(fe.brand_data_loader, "get_replace_records", _records)

    s = fe._compute_weighted_replace_score(
        brand="TestBrand", tier="mid", variant="split_ac", region="US",
        unit_age_years=10, threshold=0.0,
    )
    assert s.recommend_replace is True   # threshold 0 -> always recommend

    s2 = fe._compute_weighted_replace_score(
        brand="TestBrand", tier="mid", variant="split_ac", region="US",
        unit_age_years=10, threshold=1.01,
    )
    assert s2.recommend_replace is False  # threshold > 1 -> never recommend


def test_threshold_env_var_default(monkeypatch):
    monkeypatch.delenv("RECOMMEND_REPLACE_THRESHOLD", raising=False)
    assert fe._replace_recommend_threshold() == 0.6
    monkeypatch.setenv("RECOMMEND_REPLACE_THRESHOLD", "0.42")
    assert fe._replace_recommend_threshold() == 0.42
    monkeypatch.setenv("RECOMMEND_REPLACE_THRESHOLD", "garbage")
    assert fe._replace_recommend_threshold() == 0.6  # bad value -> default


# ── confidence_recompute demotes synthetic medium+cr_sub+no-Tier1 record ─────
def test_confidence_recompute_demotes(monkeypatch):
    synthetic = [
        # demote: cr_substituted + medium + zero Tier-1 sources
        {"brand": "X", "tier": "mid", "variant": "split_ac",
         "confidence": "medium", "cr_substituted": True,
         "source_links": ["a.com (T3)", "b.com (T2)"]},
        # keep: has a Tier-1 source
        {"brand": "Y", "tier": "mid", "variant": "split_ac",
         "confidence": "medium", "cr_substituted": True,
         "source_links": ["ahri.org (T1)"]},
        # keep: not cr_substituted
        {"brand": "Z", "tier": "mid", "variant": "split_ac",
         "confidence": "medium", "cr_substituted": False,
         "source_links": ["a.com (T3)"]},
    ]
    monkeypatch.setattr(bdl, "_replace_data", lambda: {"brand_tier_records": synthetic})
    bdl._recomputed_replace_records.cache_clear()
    out = bdl.get_replace_records()
    by_brand = {r["brand"]: r for r in out}
    assert by_brand["X"]["confidence"] == "low"
    assert by_brand["X"].get("confidence_demoted") is True
    assert by_brand["Y"]["confidence"] == "medium"  # Tier-1 present
    assert by_brand["Z"]["confidence"] == "medium"  # not cr_substituted
    bdl._recomputed_replace_records.cache_clear()


def test_tier1_source_counter():
    assert bdl._count_tier1_sources({"source_links": ["a (T1)", "b (T3)"]}) == 1
    assert bdl._count_tier1_sources({"source_links": ["a (T2)", "b (T3)"]}) == 0
    assert bdl._count_tier1_sources({}) == 0


# ── /api/version logic returns 1.2 ───────────────────────────────────────────
def test_version_payload_returns_1_2():
    payload = version_api.get_version_payload()
    assert payload["decoder_version"] == "1.2"
    assert payload["brand_data_version"] == "1.2"
    # replace_logic_version falls back to BRAND_DATA_VERSION (spec has no version key)
    assert payload["replace_logic_version"] == "1.2"
