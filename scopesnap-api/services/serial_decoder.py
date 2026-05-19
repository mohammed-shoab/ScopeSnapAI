"""
SnapAI -- Serial Number Decoder
Decodes HVAC equipment serial numbers to extract manufacture year and week.
Implements patterns for all 5 major brands: Carrier, Trane, Lennox, Goodman, Rheem.

WP-03 deliverable.
"""

from typing import Optional
import re


# -- Decode Result -------------------------------------------------------------

class SerialDecodeResult:
    def __init__(self, year: int, week: Optional[int] = None, month: Optional[int] = None):
        self.year = year
        self.week = week
        self.month = month

    def to_dict(self) -> dict:
        result = {"year": self.year}
        if self.week is not None:
            result["week"] = self.week
        if self.month is not None:
            result["month"] = self.month
        return result


# -- Brand-Specific Decoders ---------------------------------------------------

def _decode_carrier(serial: str) -> Optional[SerialDecodeResult]:
    """
    Carrier serial format: XXYYMMDDNNN or 4-digit year-week at position 0-3.

    Common Carrier patterns:
    - Pattern 1 (post-2010): Positions 0-1 = week (2 digits), positions 2-3 = year (2 digits)
      e.g., "3516E12345" -> week=35, year=2016
    - Pattern 2 (pre-2010): Positions 0-3 = year+week
      e.g., "0504F12345" -> week=04, year=2005
    """
    if not serial or len(serial) < 4:
        return None

    serial = serial.strip().upper()

    # Try pattern 1: WWYYXXXXXXX (week first, then 2-digit year)
    m = re.match(r'^(\d{2})(\d{2})', serial)
    if m:
        week = int(m.group(1))
        yr_2digit = int(m.group(2))
        if 1 <= week <= 53:
            year = 2000 + yr_2digit if yr_2digit <= 30 else 1900 + yr_2digit
            return SerialDecodeResult(year=year, week=week)

    return None


def _decode_trane(serial: str) -> Optional[SerialDecodeResult]:
    """
    Trane serial format:
    - Modern (2010+): 1 letter + 8 digits. Letter = decade indicator.
      Positions 1-4 = YYWW (year + week)
      e.g., "U16W123456" -> year=2016, week=23 (U = 2010s era)
    - Older: MMYYNNNNN
    """
    if not serial or len(serial) < 5:
        return None

    serial = serial.strip().upper()

    # Modern pattern: letter + YYWW + more digits
    m = re.match(r'^[A-Z](\d{2})([A-Z])(\d{2})', serial)
    if m:
        yr_2digit = int(m.group(1))
        week = int(m.group(3))
        if 1 <= week <= 53:
            year = 2000 + yr_2digit if yr_2digit <= 30 else 1900 + yr_2digit
            return SerialDecodeResult(year=year, week=week)

    # Try numeric pattern: first 4 digits = YYWW
    m = re.match(r'^[A-Z]?(\d{2})(\d{2})', serial)
    if m:
        yr_2digit = int(m.group(1))
        week_or_month = int(m.group(2))
        if 1 <= week_or_month <= 53:
            year = 2000 + yr_2digit if yr_2digit <= 30 else 1900 + yr_2digit
            return SerialDecodeResult(year=year, week=week_or_month)

    return None


def _decode_lennox(serial: str) -> Optional[SerialDecodeResult]:
    """
    Lennox serial format:
    - Positions 0-3 = YYWW (year 2 digits + week 2 digits)
    - e.g., "1535A12345" -> year=2015, week=35
    """
    if not serial or len(serial) < 4:
        return None

    serial = serial.strip().upper()

    m = re.match(r'^(\d{2})(\d{2})', serial)
    if m:
        yr_2digit = int(m.group(1))
        week = int(m.group(2))
        if 1 <= week <= 53:
            year = 2000 + yr_2digit if yr_2digit <= 30 else 1900 + yr_2digit
            return SerialDecodeResult(year=year, week=week)

    return None


def _decode_goodman(serial: str) -> Optional[SerialDecodeResult]:
    """
    Goodman (also Amana, Daikin) serial format:
    - 1 letter + 9 digits
    - Letter encodes decade: M=2000s, A=2010s, R=2020s
    - Digits 1-2 = year within decade, digits 3-4 = week
    - e.g., "A916D12345" -> A=2010s, 9=2019, 16=week16 -> 2019, week 16
    - OR: first 2 digits = year, next 2 = week
    """
    if not serial or len(serial) < 5:
        return None

    serial = serial.strip().upper()

    decade_map = {
        'M': 2000, 'N': 2001, 'P': 2002, 'Q': 2003,  # older
        'A': 2010, 'B': 2011, 'C': 2012, 'D': 2013, 'E': 2014,
        'F': 2015, 'G': 2016, 'H': 2017, 'J': 2018, 'K': 2019,
        'L': 2020, 'R': 2021, 'S': 2022, 'T': 2023, 'U': 2024,
    }

    if serial[0] in decade_map and len(serial) >= 5:
        base_year = decade_map[serial[0]]
        m = re.match(r'^[A-Z](\d{1})(\d{2})', serial)
        if m:
            # Single digit year offset + 2-digit week
            year = base_year + int(m.group(1))
            week = int(m.group(2))
            if 1 <= week <= 53:
                return SerialDecodeResult(year=year, week=week)

        # Full 2-digit year + 2-digit week after letter
        m = re.match(r'^[A-Z](\d{2})(\d{2})', serial)
        if m:
            yr_2digit = int(m.group(1))
            week = int(m.group(2))
            if 1 <= week <= 53:
                year = 2000 + yr_2digit if yr_2digit <= 30 else 1900 + yr_2digit
                return SerialDecodeResult(year=year, week=week)

    return None


def _decode_rheem(serial: str) -> Optional[SerialDecodeResult]:
    """
    Rheem (also Ruud) serial format:
    - F-series: First 4 digits = YYWW
    - Older: MMYYNNNNN
    - e.g., "F1735A12345" -> year=2017, week=35
    - e.g., "0316A12345" -> year=2016, month=03
    """
    if not serial or len(serial) < 4:
        return None

    serial = serial.strip().upper()

    # F-series
    if serial.startswith('F') and len(serial) >= 5:
        m = re.match(r'^F(\d{2})(\d{2})', serial)
        if m:
            yr_2digit = int(m.group(1))
            week = int(m.group(2))
            if 1 <= week <= 53:
                year = 2000 + yr_2digit if yr_2digit <= 30 else 1900 + yr_2digit
                return SerialDecodeResult(year=year, week=week)

    # Older MMYY format
    m = re.match(r'^(\d{2})(\d{2})', serial)
    if m:
        month = int(m.group(1))
        yr_2digit = int(m.group(2))
        if 1 <= month <= 12:
            year = 2000 + yr_2digit if yr_2digit <= 30 else 1900 + yr_2digit
            return SerialDecodeResult(year=year, month=month)

        # Might be week-first format
        week = month
        if 1 <= week <= 53:
            year = 2000 + yr_2digit if yr_2digit <= 30 else 1900 + yr_2digit
            return SerialDecodeResult(year=year, week=week)

    return None


# -- Main Decode Function ------------------------------------------------------

BRAND_DECODERS = {
    # Carrier family
    "carrier": _decode_carrier,
    "bryant": _decode_carrier,          # Bryant = Carrier OEM
    "payne": _decode_carrier,           # Payne = Carrier OEM
    # Trane family
    "trane": _decode_trane,
    "american standard": _decode_trane, # American Standard = Trane OEM
    # Lennox
    "lennox": _decode_lennox,
    "dave lennox signature": _decode_lennox,
    # Goodman / Daikin family
    "goodman": _decode_goodman,
    "amana": _decode_goodman,           # Amana = Goodman/Daikin OEM
    "daikin": _decode_goodman,          # Daikin = same serial format (Waller TX factory)
    # Rheem family
    "rheem": _decode_rheem,
    "ruud": _decode_rheem,              # Ruud = Rheem OEM
    # Johnson Controls / ICP family (York/Heil/Coleman all use YYWW format)
    "york": _decode_carrier,
    "heil": _decode_carrier,
    "coleman": _decode_carrier,
    "luxaire": _decode_carrier,
    # Mitsubishi Electric (YYWW embedded in first 4 digits)
    "mitsubishi": _decode_lennox,
    "mitsubishi electric": _decode_lennox,
}


def decode_serial(brand: str, serial: str) -> Optional[dict]:
    """
    Decodes a serial number for the given brand.

    Args:
        brand: Equipment brand name (case-insensitive)
        serial: Serial number string

    Returns:
        dict with 'year' and optionally 'week' or 'month', or None if can't decode.

    Examples:
        decode_serial("Carrier", "3516E12345") -> {"year": 2016, "week": 35}
        decode_serial("Rheem", "0316A12345") -> {"year": 2016, "month": 3}
        decode_serial("BrandX", "ZZZZZ") -> None
    """
    if not brand or not serial:
        return None

    brand_key = brand.lower().strip()
    decoder = BRAND_DECODERS.get(brand_key)

    if not decoder:
        # Try partial match
        for key, fn in BRAND_DECODERS.items():
            if key in brand_key or brand_key in key:
                decoder = fn
                break

    if not decoder:
        return None

    result = decoder(serial)
    return result.to_dict() if result else None
