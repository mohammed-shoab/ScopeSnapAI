"""
SnapAI -- Serial Number Decoder (Master Plan v2.0, Stage 1)

Decodes HVAC equipment serial numbers to manufacture year (+ month/week) using
the v1.2 brand research data. Each brand routes to its correct format family;
returns (result, None) on success or (None, SerialDecodeFailure) with a reason.

Refs: SnapAI_Brand_Decoder_Implementation_Master_Plan_v2.md Stage 1;
      serial_decoder_data_v1.2.json decoder_implementation_spec.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Tuple

try:
    from services.brand_data_loader import get_serial_brand
except Exception:  # pragma: no cover - allows standalone import in tests
    from brand_data_loader import get_serial_brand  # type: ignore


# -- Result + Failure ----------------------------------------------------------

class SerialDecodeResult:
    def __init__(self, year: Optional[int], week: Optional[int] = None,
                 month: Optional[int] = None, confidence: str = "medium",
                 source: Optional[str] = None, source_pattern_id: Optional[str] = None,
                 variant: Optional[str] = None, metadata: Optional[dict] = None):
        self.year = year
        self.week = week
        self.month = month
        self.confidence = confidence              # high|medium|medium-low|low|unknown
        self.source = source                      # serial_decoder|plate_date|legacy_brand_age_floor
        self.source_pattern_id = source_pattern_id
        self.variant = variant
        self.metadata = metadata or {}

    def to_dict(self) -> dict:
        out = {"year": self.year, "confidence": self.confidence}
        if self.week is not None:
            out["week"] = self.week
        if self.month is not None:
            out["month"] = self.month
        if self.source:
            out["source"] = self.source
        if self.source_pattern_id:
            out["source_pattern_id"] = self.source_pattern_id
        if self.variant:
            out["variant"] = self.variant
        if self.metadata:
            out["metadata"] = self.metadata
        return out


class SerialDecodeFailure(str, Enum):
    PIONEER_NOT_DECODABLE = "pioneer_not_decodable"
    SENVILLE_NOT_DECODABLE = "senville_not_decodable"
    DELLA_NOT_DECODABLE = "della_not_decodable"
    SAMSUNG_POST_2018_UNKNOWN = "samsung_post_2018_unknown"
    PK_NO_FORMAT = "pk_no_format"
    FORMAT_NOT_MATCHED = "format_not_matched"
    UNKNOWN_BRAND = "unknown_brand"
    KENMORE_OEM_UNKNOWN = "kenmore_oem_unknown"


# -- Shared helpers ------------------------------------------------------------

# Month letter map (A=Jan..M=Dec, I skipped). Single Lennox/JCI/Friedrich convention.
_MONTH_LETTER = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7,
                 "H": 8, "J": 9, "K": 10, "L": 11, "M": 12}


def _yy_to_year(yy: int, lo: int = 1980) -> int:
    """2-digit year -> 4-digit, biased to recent (<= ~next year => 20xx)."""
    cur = datetime.now(timezone.utc).year
    candidate = 2000 + yy
    if candidate <= cur + 1:
        return candidate
    return 1900 + yy


# -- Family decoders -----------------------------------------------------------

def _decode_carrier(serial: str) -> Optional[SerialDecodeResult]:
    # WWYY + plant letter + 5 digits  e.g. 2714B12345 -> week27 2014
    m = re.match(r'^(0[1-9]|[1-4]\d|5[0-3])(\d{2})[A-Z]\d{5}$', serial)
    if m:
        return SerialDecodeResult(year=_yy_to_year(int(m.group(2))), week=int(m.group(1)),
                                  source_pattern_id="carrier_wwyy")
    return None


def _decode_jci(serial: str) -> Optional[SerialDecodeResult]:
    # York/Coleman/Luxaire: L D L D + 6 digits. year=pos2&pos4 (20YY), month=pos3 letter
    m = re.match(r'^[A-Z](\d)([A-Z])(\d)\d{6}$', serial)
    if m:
        yy = int(m.group(1) + m.group(3))
        month = _MONTH_LETTER.get(m.group(2))
        return SerialDecodeResult(year=2000 + yy, month=month, source_pattern_id="jci_ldld")
    return None


def _decode_lennox(serial: str) -> Optional[SerialDecodeResult]:
    # plant(2) + year(2) + month-letter + 4-5 seq  e.g. 5207K24862 -> Oct 2007
    m = re.match(r'^\d{2}(\d{2})([A-HJ-M])\w{4,5}$', serial)
    if m:
        return SerialDecodeResult(year=_yy_to_year(int(m.group(1))),
                                  month=_MONTH_LETTER.get(m.group(2)),
                                  source_pattern_id="lennox_plant_yy_monthletter")
    return None


def _decode_goodman(serial: str) -> Optional[SerialDecodeResult]:
    # 10-digit all-numeric YYMM + 6 seq  e.g. 0408523498 -> Aug 2004
    m = re.match(r'^(\d{2})(\d{2})\d{6}$', serial)
    if m:
        month = int(m.group(2))
        if 1 <= month <= 12:
            return SerialDecodeResult(year=_yy_to_year(int(m.group(1))), month=month,
                                      source_pattern_id="goodman_yymm")
    return None


def _decode_trane(serial: str) -> Optional[SerialDecodeResult]:
    # 2010+: chars1-2=year, chars3-4=week (e.g. 10161KEDAA -> 2010 wk16)
    m = re.match(r'^(\d{2})(\d{2})[A-Z0-9].*$', serial)
    if m:
        wk = int(m.group(2))
        if 1 <= wk <= 53:
            return SerialDecodeResult(year=_yy_to_year(int(m.group(1))), week=wk,
                                      source_pattern_id="trane_yyww_2010")
    # legacy letter-year e.g. F23456789 (F=1991) - leave to medium/None
    return None


def _decode_rheem(serial: str) -> Optional[SerialDecodeResult]:
    # factory letter [FMGWN] + WWYY + seq  e.g. W421724596 -> week42 2017
    m = re.match(r'^[FMGWN]\s?(0[1-9]|[1-4]\d|5[0-3])(\d{2})\d+$', serial, re.IGNORECASE)
    if m:
        return SerialDecodeResult(year=_yy_to_year(int(m.group(2))), week=int(m.group(1)),
                                  source_pattern_id="rheem_letter_wwyy")
    return None


def _decode_nortek(serial: str) -> Optional[SerialDecodeResult]:
    # 3 letters + 9 digits: year=digits4-5, month=digits6-7  e.g. FGA030310579 -> Oct 2003
    m = re.match(r'^[A-Z]{3}(\d{2})(\d{2})\d{5}$', serial)
    if m:
        month = int(m.group(2))
        if 1 <= month <= 12:
            return SerialDecodeResult(year=_yy_to_year(int(m.group(1))), month=month,
                                      source_pattern_id="nortek_3l_yymm")
    return None


def _candidate_decades(yr_digit: int):
    """Plausible full years for a single-digit year with no decade marker."""
    cur = datetime.now(timezone.utc).year
    return [d + yr_digit for d in (2000, 2010, 2020) if d + yr_digit <= cur + 1]


def _decode_mitsubishi(serial: str, refrigerant_hint: Optional[str] = None,
                       era_hint: Optional[str] = None) -> Optional[SerialDecodeResult]:
    # Japanese fiscal-year. char1=year digit (decade ambiguous), char2=month 1-9/X/Y/Z
    m = re.match(r'^(\d)([0-9XYZ])', serial)
    if not m:
        return None
    yr_digit = int(m.group(1))
    mon_ch = m.group(2)
    month = {"X": 10, "Y": 11, "Z": 12}.get(mon_ch)
    if month is None and mon_ch.isdigit() and mon_ch != "0":
        month = int(mon_ch)
    # decade disambiguation
    decade = None
    if era_hint in ("2000s", "2010s", "2020s"):
        decade = {"2000s": 2000, "2010s": 2010, "2020s": 2020}[era_hint]
    elif refrigerant_hint:
        rh = refrigerant_hint.upper().replace("-", "")
        if rh in ("R454B", "R32"):
            decade = 2020
        elif rh == "R410A":
            decade = 2010
    if decade is not None:
        return SerialDecodeResult(year=decade + yr_digit, month=month, confidence="medium",
                                  source_pattern_id="mitsubishi_fiscal",
                                  metadata={"decade_ambiguous": False})
    return SerialDecodeResult(year=None, month=month, confidence="low",
                              source_pattern_id="mitsubishi_fiscal",
                              metadata={"decade_ambiguous": True, "year_digit": yr_digit,
                                        "candidate_years": _candidate_decades(yr_digit)})


def _decode_mrcool(serial: str, refrigerant_hint: Optional[str] = None) -> Optional[SerialDecodeResult]:
    # Style 1 legacy: chars1-2=week, chars3-4=year  e.g. 1920K08283 -> wk19 2020
    m = re.match(r'^(\d{2})(\d{2})[A-Z]', serial)
    if m:
        wk = int(m.group(1))
        if 1 <= wk <= 53:
            return SerialDecodeResult(year=_yy_to_year(int(m.group(2))), week=wk,
                                      source_pattern_id="mrcool_style1")
    # Style 2 (21/22-digit): pos12 = single-digit year (decade ambiguous), pos13 = month
    if len(serial) >= 15 and serial[:11].isdigit():
        yr_digit = int(serial[11])
        mon_ch = serial[12]
        month = {"A": 10, "B": 11, "C": 12}.get(mon_ch)
        if month is None and mon_ch.isdigit() and mon_ch != "0":
            month = int(mon_ch)
        decade = 2020 if (refrigerant_hint and "454" in refrigerant_hint) else None
        if decade is not None:
            return SerialDecodeResult(year=decade + yr_digit, month=month, confidence="medium",
                                      source_pattern_id="mrcool_style2")
        return SerialDecodeResult(year=None, month=month, confidence="low",
                                  source_pattern_id="mrcool_style2",
                                  metadata={"decade_ambiguous": True, "year_digit": yr_digit,
                                            "candidate_years": _candidate_decades(yr_digit)})
    return None


def _decode_daikin(serial: str) -> Optional[SerialDecodeResult]:
    # (A) Waller ducted 10-digit YYMM ; (B) Japan Style2: 4 letters + YYMM
    if re.match(r'^\d{10}$', serial):
        r = _decode_goodman(serial)
        if r:
            r.source_pattern_id = "daikin_waller_yymm"
            return r
    m = re.match(r'^[A-Z]{4}(\d{2})(\d{2})\d{6}$', serial)
    if m:
        month = int(m.group(2))
        if 1 <= month <= 12:
            return SerialDecodeResult(year=_yy_to_year(int(m.group(1))), month=month,
                                      source_pattern_id="daikin_japan_style2")
    return None


def _decode_friedrich(serial: str) -> Optional[SerialDecodeResult]:
    # Numeric era (Dec2017+): YYMM   e.g. 1801M01258 -> Jan 2018
    m = re.match(r'^(\d{2})(\d{2})', serial)
    if m:
        month = int(m.group(2))
        if 1 <= month <= 12:
            return SerialDecodeResult(year=_yy_to_year(int(m.group(1))), month=month,
                                      confidence="medium-low", source_pattern_id="friedrich_numeric")
    # Letter era (2000-2017): char1 decade(L=2000s,A=2010s), char2 year-letter(K=0,A=1..J=9), char3 month
    m = re.match(r'^([LA])([A-K])([A-HJ-M])', serial)
    if m:
        decade = 2000 if m.group(1) == "L" else 2010
        year_letter_map = {"K": 0, "A": 1, "B": 2, "C": 3, "D": 4, "E": 5,
                           "F": 6, "G": 7, "H": 8, "J": 9}
        yr = year_letter_map.get(m.group(2))
        month = _MONTH_LETTER.get(m.group(3))
        if yr is not None:
            return SerialDecodeResult(year=decade + yr, month=month, confidence="medium-low",
                                      source_pattern_id="friedrich_letter")
    return None


def _decode_lg(serial: str) -> Optional[SerialDecodeResult]:
    # char1 = year digit; decade not encoded -> assume 2010s/2020s, low-medium
    m = re.match(r'^(\d)', serial)
    if m:
        yr_digit = int(m.group(1))
        cur = datetime.now(timezone.utc).year
        cand2020 = 2020 + yr_digit
        year = cand2020 if cand2020 <= cur + 1 else 2010 + yr_digit
        return SerialDecodeResult(year=year, confidence="low", source_pattern_id="lg_leading_digit",
                                  metadata={"decade_ambiguous": True,
                                            "candidate_years": _candidate_decades(yr_digit)})
    return None


def decode_plate_date(plate_string: str) -> Optional[SerialDecodeResult]:
    """Gree/Cooper&Hunter/EcoStar/Panasonic/Daikin-Style1: printed YYYY.MM on the plate."""
    if not plate_string:
        return None
    m = re.search(r'(20\d{2})[.\-/ ]?(0[1-9]|1[0-2])', plate_string)
    if m:
        return SerialDecodeResult(year=int(m.group(1)), month=int(m.group(2)),
                                  confidence="high", source="plate_date",
                                  source_pattern_id="plate_yyyymm")
    return None


# -- Routing tables ------------------------------------------------------------

_FAMILY = {
    "carrier": _decode_carrier, "bryant": _decode_carrier, "payne": _decode_carrier,
    "york": _decode_jci, "coleman": _decode_jci, "luxaire": _decode_jci,
    "champion": _decode_jci, "fraser-johnston": _decode_jci, "guardian": _decode_jci,
    "lennox": _decode_lennox,
    "goodman": _decode_goodman, "amana": _decode_goodman,
    "daikin": _decode_daikin, "daikin mini-split": _decode_daikin,
    "trane": _decode_trane, "american standard": _decode_trane,
    "rheem": _decode_rheem, "ruud": _decode_rheem,
    "frigidaire hvac": _decode_nortek, "maytag hvac": _decode_nortek,
    "westinghouse hvac": _decode_nortek, "nutone hvac": _decode_nortek,
    "gibson hvac": _decode_nortek, "tappan hvac": _decode_nortek,
    "kelvinator hvac": _decode_nortek, "philco hvac": _decode_nortek,
    "intertherm hvac": _decode_nortek, "miller hvac": _decode_nortek,
    "mitsubishi electric": _decode_mitsubishi,
    "mrcool": _decode_mrcool,
    "friedrich": _decode_friedrich,
    "heil": None,  # ICP family handled below (closure over modern_regex)
    "lg": _decode_lg,
}

# ICP family (Heil): leading letter + YYWW
def _decode_icp(serial: str) -> Optional[SerialDecodeResult]:
    m = re.match(r'^[A-Z](\d{2})(\d{2})\d+$', serial)
    if m:
        wk = int(m.group(2))
        if 1 <= wk <= 53:
            return SerialDecodeResult(year=_yy_to_year(int(m.group(1))), week=wk,
                                      source_pattern_id="icp_letter_yyww")
    return None

for _b in ("heil",):
    _FAMILY[_b] = _decode_icp

_PLATE_ONLY = {"gree", "cooper&hunter", "ecostar"}
_NON_DECODABLE = {
    "pioneer": SerialDecodeFailure.PIONEER_NOT_DECODABLE,
    "senville": SerialDecodeFailure.SENVILLE_NOT_DECODABLE,
    "della": SerialDecodeFailure.DELLA_NOT_DECODABLE,
    "samsung": SerialDecodeFailure.SAMSUNG_POST_2018_UNKNOWN,
}
# Legacy brand age floors: midpoint default + discontinued year for min_age.
_LEGACY_FLOORS = {
    "sears kenmore hvac": {"discontinued": 2012, "default": 2002, "failure": SerialDecodeFailure.KENMORE_OEM_UNKNOWN},
    "whirlpool hvac": {"discontinued": 2005, "default": 1995},
    "janitrol (pre-1982)": {"discontinued": 1982, "default": 1977},
}


def _legacy_floor(canon: str) -> SerialDecodeResult:
    cfg = _LEGACY_FLOORS[canon]
    cur = datetime.now(timezone.utc).year
    return SerialDecodeResult(year=cfg["default"], confidence="low",
                              source="legacy_brand_age_floor",
                              source_pattern_id="legacy_floor",
                              metadata={"min_age": cur - cfg["discontinued"]})


# -- Public API ----------------------------------------------------------------

def decode_serial(brand: str, serial: str, variant: str = "split_ac",
                  refrigerant_hint: Optional[str] = None,
                  era_hint: Optional[str] = None
                  ) -> Tuple[Optional[SerialDecodeResult], Optional[SerialDecodeFailure]]:
    """Decode an HVAC serial. Returns (result, None) or (None, failure_reason)."""
    if not brand:
        return None, SerialDecodeFailure.UNKNOWN_BRAND
    canon_key = brand.strip().lower()
    rec = get_serial_brand(brand)
    canon = (rec.get("canonical_name").lower() if rec and rec.get("canonical_name") else canon_key)

    # PK market: no decodable format (per PK positioning)
    if rec and (rec.get("market") or "").upper() == "PK":
        return None, SerialDecodeFailure.PK_NO_FORMAT

    # Legacy age floors
    if canon in _LEGACY_FLOORS:
        cfg = _LEGACY_FLOORS[canon]
        if cfg.get("failure"):
            return None, cfg["failure"]
        return _legacy_floor(canon), None

    # Explicitly non-decodable
    if canon in _NON_DECODABLE:
        return None, _NON_DECODABLE[canon]

    if not serial:
        if rec is None:
            return None, SerialDecodeFailure.UNKNOWN_BRAND
        return None, SerialDecodeFailure.FORMAT_NOT_MATCHED

    s = serial.strip().upper()

    # Plate-only brands: try the printed-date extractor on the supplied string
    if canon in _PLATE_ONLY:
        r = decode_plate_date(serial)
        if r:
            r.variant = variant
            return r, None
        return None, SerialDecodeFailure.FORMAT_NOT_MATCHED

    decoder = _FAMILY.get(canon)
    if decoder is None and rec is not None:
        # brand known but no dedicated decoder -> try plate date, else format-not-matched
        r = decode_plate_date(serial)
        if r:
            r.variant = variant
            return r, None
        return None, SerialDecodeFailure.FORMAT_NOT_MATCHED
    if decoder is None:
        return None, SerialDecodeFailure.UNKNOWN_BRAND

    # call family decoder (some accept hints)
    if decoder is _decode_mitsubishi:
        result = decoder(s, refrigerant_hint=refrigerant_hint, era_hint=era_hint)
    elif decoder is _decode_mrcool:
        result = decoder(s, refrigerant_hint=refrigerant_hint)
    else:
        result = decoder(s)

    if result is None:
        return None, SerialDecodeFailure.FORMAT_NOT_MATCHED

    # attach metadata from the brand record
    if result.source is None:
        result.source = "serial_decoder"
    if rec and rec.get("confidence") and result.confidence == "medium":
        result.confidence = rec["confidence"]
    result.variant = variant
    return result, None
