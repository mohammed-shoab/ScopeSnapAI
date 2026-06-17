"""Constraint #8 — per-brand refrigerant_for_year() (pure-unit, DB-free).

Execs only the _R2025_BY_BRAND constants + refrigerant_for_year() out of
api/fault_estimate.py so it runs without the DB/FastAPI app.
"""
from __future__ import annotations

import os
import re
import types

_API_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _load():
    src = open(os.path.join(_API_DIR, "api", "fault_estimate.py"), encoding="utf-8").read()
    start = src.index("_R2025_BY_BRAND = {")
    end = src.index("\n\n\n", src.index("def refrigerant_for_year"))
    region = src[start:end]
    mod = types.ModuleType("rfy")
    mod.__dict__["Optional"] = __import__("typing").Optional
    exec(compile(region, "fault_estimate.py", "exec"), mod.__dict__)
    return mod


fe = _load()


def test_none_year_returns_none():
    assert fe.refrigerant_for_year("Carrier", None) is None


def test_pre_2010_is_r22():
    assert fe.refrigerant_for_year("Carrier", 2005) == "R-22"
    assert fe.refrigerant_for_year("Goodman", 2009) == "R-22"


def test_2010_to_2024_is_r410a():
    assert fe.refrigerant_for_year("Trane", 2010) == "R-410A"
    assert fe.refrigerant_for_year("Lennox", 2024) == "R-410A"


def test_2025_r32_adopters():
    assert fe.refrigerant_for_year("Daikin", 2025) == "R-32"
    assert fe.refrigerant_for_year("Goodman", 2026) == "R-32"
    assert fe.refrigerant_for_year("Amana", 2025) == "R-32"


def test_2025_r454b_adopters():
    for b in ("Carrier", "Bryant", "Trane", "Lennox", "Rheem", "York", "MrCool"):
        assert fe.refrigerant_for_year(b, 2025) == "R-454B", b


def test_2025_nortek_family_hypothesis_r454b():
    assert fe.refrigerant_for_year("Frigidaire HVAC", 2025) == "R-454B"


def test_2025_unknown_brand_defaults_r454b():
    assert fe.refrigerant_for_year("SomeUnknownBrand", 2025) == "R-454B"


def test_case_insensitive_brand():
    assert fe.refrigerant_for_year("daikin", 2025) == "R-32"
    assert fe.refrigerant_for_year("  CARRIER  ", 2025) == "R-454B"
