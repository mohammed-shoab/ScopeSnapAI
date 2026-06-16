"""Stage 1 — v1.2 serial decoder tests.

Vectors come from the REAL ``sample_verifications`` baked into
``data/serial_decoder_data_v1.2.json`` (field-captured serials with an
expert-claimed manufacture year). No database is required; these are pure-unit.
"""
from __future__ import annotations

import os
import re
import sys

import pytest

# Make the api package importable when pytest is run from repo root or api dir.
_API_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _API_DIR not in sys.path:
    sys.path.insert(0, _API_DIR)

from services import brand_data_loader  # noqa: E402
from services.serial_decoder import (  # noqa: E402
    SerialDecodeFailure,
    SerialDecodeResult,
    decode_serial,
)
from services.gemini_decade_disambiguator import (  # noqa: E402
    disambiguate_decade,
    resolve_by_refrigerant,
)

# Brands whose samples are NOT expected to decode to a concrete year directly
# (PK market, decade-ambiguous single-digit families, plate-only, non-decodable,
# legacy floors). Excluded from the strict year-match parametrization.
_SKIP_YEAR_MATCH = {
    "mitsubishi electric", "mrcool", "lg",
    "gree", "cooper&hunter", "ecostar",
    "pioneer", "senville", "della", "samsung",
    "sears kenmore hvac", "whirlpool hvac", "janitrol (pre-1982)",
}


def _clean_serial(raw: str) -> str:
    # Samples sometimes annotate: "2804E06345 (model PA10JA036-C)" -> take token 1.
    return re.split(r"[\s(]", raw.strip(), maxsplit=1)[0].strip()


def _claimed_year(raw) -> int | None:
    if raw is None:
        return None
    m = re.search(r"(19|20)\d{2}", str(raw))
    return int(m.group(0)) if m else None


def _decodable_samples():
    brands = brand_data_loader.get_serial_brands()
    cases = []
    for rec in brands:
        canon = (rec.get("canonical_name") or "").strip()
        if not canon or canon.lower() in _SKIP_YEAR_MATCH:
            continue
        if (rec.get("market") or "US").upper() == "PK":
            continue
        for vname, v in (rec.get("variants") or {}).items():
            for sv in (v or {}).get("sample_verifications", []) or []:
                if not sv.get("agree", False):
                    continue
                serial = _clean_serial(sv.get("serial", ""))
                year = _claimed_year(sv.get("claimed"))
                regex = (v or {}).get("modern_regex")
                if not serial or year is None:
                    continue
                # Only test serials the format actually claims to match.
                if regex:
                    try:
                        if not re.match(regex, serial, re.IGNORECASE):
                            continue
                    except re.error:
                        pass
                cases.append(
                    pytest.param(canon, vname, serial, year,
                                 id=f"{canon}-{vname}-{serial}")
                )
    return cases


_CASES = _decodable_samples()


def test_we_have_a_meaningful_number_of_real_vectors():
    # Guard against the parametrization silently collapsing to zero.
    assert len(_CASES) >= 8, f"expected >=8 real decodable vectors, got {len(_CASES)}"


@pytest.mark.parametrize("brand,variant,serial,claimed_year", _CASES)
def test_real_sample_decodes_to_claimed_year(brand, variant, serial, claimed_year):
    result, failure = decode_serial(brand, serial, variant=variant)
    assert failure is None, f"{brand}/{serial} unexpectedly failed: {failure}"
    assert isinstance(result, SerialDecodeResult)
    assert result.year == claimed_year, (
        f"{brand}/{serial}: decoded {result.year}, expected {claimed_year}"
    )


# ── PK market ────────────────────────────────────────────────────────────────
def _pk_brands():
    out = []
    for rec in brand_data_loader.get_serial_brands():
        if (rec.get("market") or "US").upper() == "PK":
            out.append(rec.get("canonical_name"))
    return out


@pytest.mark.parametrize("brand", _pk_brands())
def test_pk_brands_return_pk_no_format(brand):
    result, failure = decode_serial(brand, "1234567890")
    assert result is None
    assert failure == SerialDecodeFailure.PK_NO_FORMAT


# ── Non-decodable brands ─────────────────────────────────────────────────────
@pytest.mark.parametrize("brand,expected", [
    ("Pioneer", SerialDecodeFailure.PIONEER_NOT_DECODABLE),
    ("Senville", SerialDecodeFailure.SENVILLE_NOT_DECODABLE),
    ("Della", SerialDecodeFailure.DELLA_NOT_DECODABLE),
    ("Samsung", SerialDecodeFailure.SAMSUNG_POST_2018_UNKNOWN),
])
def test_non_decodable_brands(brand, expected):
    result, failure = decode_serial(brand, "ABCD12345678")
    assert result is None
    assert failure == expected


# ── Unknown brand ────────────────────────────────────────────────────────────
def test_unknown_brand_returns_unknown_failure():
    result, failure = decode_serial("NotARealHvacBrand", "12345")
    assert result is None
    assert failure == SerialDecodeFailure.UNKNOWN_BRAND


def test_empty_brand_returns_unknown_failure():
    result, failure = decode_serial("", "12345")
    assert result is None
    assert failure == SerialDecodeFailure.UNKNOWN_BRAND


# ── Legacy age floors ────────────────────────────────────────────────────────
def test_whirlpool_legacy_floor():
    result, failure = decode_serial("Whirlpool HVAC", "ANYTHING123")
    assert failure is None
    assert result is not None
    assert result.year == 1995
    assert result.metadata.get("min_age", 0) >= 18


def test_kenmore_oem_unknown():
    result, failure = decode_serial("Sears Kenmore HVAC", "ANYTHING123")
    assert result is None
    assert failure == SerialDecodeFailure.KENMORE_OEM_UNKNOWN


# ── Decade ambiguity (Mitsubishi single-digit fiscal year) ───────────────────
def test_mitsubishi_ambiguous_without_hint():
    # 8X... -> year digit 8, month X=Oct; no decade marker => ambiguous.
    result, failure = decode_serial("Mitsubishi Electric", "8X00123")
    assert failure is None
    assert result is not None
    assert result.year is None
    assert result.metadata.get("decade_ambiguous") is True
    cands = result.metadata.get("candidate_years")
    assert cands and all(isinstance(y, int) for y in cands)


def test_mitsubishi_resolved_with_r410a_hint():
    result, failure = decode_serial(
        "Mitsubishi Electric", "8X00123", refrigerant_hint="R-410A"
    )
    assert failure is None
    assert result is not None
    assert result.year == 2018  # 2010 decade + digit 8


# ── Disambiguator unit logic ─────────────────────────────────────────────────
def test_resolve_by_refrigerant_eliminates_old_decade():
    # R-410A floor (2003) eliminates the 1990s candidate.
    assert resolve_by_refrigerant([1998, 2008], "R-410A") == 2008
    # R-32 floor (2018) eliminates the 2008 candidate.
    assert resolve_by_refrigerant([2008, 2018], "R-32") == 2018


def test_resolve_by_refrigerant_ambiguous_returns_none():
    # R-22 has no floor -> cannot disambiguate.
    assert resolve_by_refrigerant([2008, 2018], "R-22") is None


def test_disambiguate_single_candidate_passthrough():
    assert disambiguate_decade([2014]) == 2014


def test_disambiguate_unresolvable_returns_none():
    assert disambiguate_decade([2008, 2018], refrigerant_hint=None) is None
