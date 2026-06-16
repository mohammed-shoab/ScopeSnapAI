"""Stage 3 glue — pure-function tests for the two backend integration seams.

DB-free: extracts only the target helpers out of api/fault_estimate.py and
api/reports.py (along with their light dependencies) so the suite runs without
a database, FastAPI app, or asyncpg.

Covers:
  SEAM 1 — _remaining_life_band (range string, never year-exact; None for unknown)
           _refrigerant_2025_compatible (r22/r410a/r32/r454b mapping)
  SEAM 2 — correct-age relative-age conversion + neither-field-provided -> 400
"""
from __future__ import annotations

import os
import re
import types

_API_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _extract_funcs(rel_path, func_names, extra_globals=None):
    """Exec only the named top-level functions from a source file into a throwaway
    module, with their light dependencies injected as globals. Avoids importing
    the module (which would pull in DB/FastAPI)."""
    path = os.path.join(_API_DIR, rel_path)
    src = open(path, encoding="utf-8").read()
    lines = src.splitlines()
    blocks = []
    for name in func_names:
        # find "def <name>(" at column 0
        start = None
        for i, ln in enumerate(lines):
            if re.match(rf"def {re.escape(name)}\b", ln):
                start = i
                break
        assert start is not None, f"{name} not found in {rel_path}"
        end = len(lines)
        for j in range(start + 1, len(lines)):
            ln = lines[j]
            if ln and not ln[0].isspace() and not ln.startswith(")"):
                end = j
                break
        blocks.append("\n".join(lines[start:end]))
    mod = types.ModuleType("glue_funcs")
    g = mod.__dict__
    g["Optional"] = __import__("typing").Optional
    g["datetime"] = __import__("datetime").datetime
    g["timezone"] = __import__("datetime").timezone
    if extra_globals:
        g.update(extra_globals)
    exec(compile("\n\n".join(blocks), path, "exec"), g)
    return mod


# fault_estimate helpers (remaining-life band needs lifespan parse helpers).
_fe = _extract_funcs(
    os.path.join("api", "fault_estimate.py"),
    ["_parse_lifespan_years", "_typical_lifespan_years",
     "_remaining_life_band", "_refrigerant_2025_compatible",
     "_estimated_install_year"],
    extra_globals={"_DEFAULT_HOUSTON_LIFESPAN_YEARS": 18},
)

# reports correct-age helpers (request model + resolver + band).
import sys  # noqa: E402
from pydantic import BaseModel  # noqa: E402


from typing import Optional  # noqa: E402


class CorrectAgeRequest(BaseModel):
    install_year: Optional[int] = None
    corrected_year: Optional[int] = None
    relative_age_years: Optional[int] = None
    source: Optional[str] = None
    corrected_by: Optional[str] = "homeowner"


_rep = _extract_funcs(
    os.path.join("api", "reports.py"),
    ["_remaining_life_band_for_year", "_resolve_corrected_year"],
    extra_globals={"CorrectAgeRequest": CorrectAgeRequest},
)

_CY = __import__("datetime").datetime.now(
    __import__("datetime").timezone.utc
).year


# ── SEAM 1: remaining-life band ──────────────────────────────────────────────

def test_remaining_life_band_is_a_range_string():
    band = _fe._remaining_life_band(5)  # 18 - 5 = 13 -> "11-15 years"
    assert isinstance(band, str)
    assert band.endswith(" years")
    assert "-" in band
    lo, hi = band.replace(" years", "").split("-")
    assert int(lo) <= int(hi)


def test_remaining_life_band_is_never_year_exact():
    # Must be a span, not a single calendar year like "2031".
    band = _fe._remaining_life_band(8)
    nums = band.replace(" years", "").split("-")
    assert len(nums) == 2
    assert nums[0] != nums[1] or int(nums[0]) == 0  # only collapses at the 0 floor


def test_remaining_life_band_none_for_unknown_age():
    assert _fe._remaining_life_band(None) is None


def test_remaining_life_band_floored_at_zero():
    band = _fe._remaining_life_band(40)  # way past lifespan
    lo, hi = band.replace(" years", "").split("-")
    assert int(lo) == 0
    assert int(hi) >= 0


# ── SEAM 1: refrigerant 2025+ compatibility ──────────────────────────────────

def test_refrigerant_r22_not_compatible():
    assert _fe._refrigerant_2025_compatible("r22") is False
    assert _fe._refrigerant_2025_compatible("R-22") is False


def test_refrigerant_r410a_not_2025_standard():
    assert _fe._refrigerant_2025_compatible("r410a") is False
    assert _fe._refrigerant_2025_compatible("R-410A") is False


def test_refrigerant_r32_and_r454b_current():
    assert _fe._refrigerant_2025_compatible("r32") is True
    assert _fe._refrigerant_2025_compatible("R-454B") is True


def test_refrigerant_unknown_returns_none():
    assert _fe._refrigerant_2025_compatible(None) is None
    assert _fe._refrigerant_2025_compatible("propane") is None


def test_estimated_install_year_echo():
    assert _fe._estimated_install_year(10) == _CY - 10
    assert _fe._estimated_install_year(None) is None


# ── SEAM 2: correct-age relative-age conversion + validation ─────────────────

def test_relative_age_conversion():
    body = CorrectAgeRequest(relative_age_years=10)
    assert _rep._resolve_corrected_year(body) == _CY - 10


def test_explicit_year_takes_precedence():
    body = CorrectAgeRequest(corrected_year=2015, relative_age_years=10)
    assert _rep._resolve_corrected_year(body) == 2015


def test_install_year_accepted():
    body = CorrectAgeRequest(install_year=2012)
    assert _rep._resolve_corrected_year(body) == 2012


def test_neither_field_resolves_to_none_then_400():
    # The handler raises HTTP 400 when _resolve_corrected_year returns None.
    body = CorrectAgeRequest()
    assert _rep._resolve_corrected_year(body) is None


def test_correct_age_band_is_range_never_exact():
    band = _rep._remaining_life_band_for_year(_CY - 5)
    assert band.endswith(" years") and "-" in band
    assert _rep._remaining_life_band_for_year(None) is None
