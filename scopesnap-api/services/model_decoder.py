"""
SnapAI - Model Number Decoder
==============================
Extracts tonnage from HVAC model number strings for all 15 brands.

Priority chain for tonnage:
  1. decode_model_tonnage(brand, model_number)  <- this module
  2. Lookup equipment_models DB row
  3. Tech manual entry

Usage:
    from services.model_decoder import decode_model_tonnage, decode_model_info

    tons = decode_model_tonnage("Carrier", "24ACC636A003")   # -> 3.0
    info = decode_model_info("Goodman", "GSX14036")          # -> {"tonnage": 3.0, ...}

All functions return None if the model number cannot be decoded.

Brand families handled (15 brands -> 6 decode families):
  Carrier family  : Carrier, Bryant, Payne
  Trane family    : Trane, American Standard
  Lennox family   : Lennox
  Goodman family  : Goodman, Amana, Daikin
  Rheem family    : Rheem, Ruud
  JCI family      : York, Heil, Coleman
  Mitsubishi      : Mitsubishi Electric

HOW TONNAGE ENCODING WORKS:
  Most brands:   zero-padded 3-digit BTU/1000 code embedded in model string
                   e.g. GSX14036 -> "036" -> 36000 BTU -> 3.0 tons
  Carrier style: non-padded 2-digit BTU code between generation digit and voltage letter
                   e.g. 24ACC636A003 -> C6[36]A -> "36" -> 36000 BTU -> 3.0 tons
  Mitsubishi:    2-digit kBTU code after series prefix (no leading zero)
                   e.g. MSZ-GS18NA -> "18" -> 18000 BTU -> 1.5 tons
"""

import re
from typing import Optional


# BTU -> Tonnage maps
BTU_TO_TONS = {
    18: 1.5,
    24: 2.0,
    30: 2.5,
    36: 3.0,
    42: 3.5,
    48: 4.0,
    60: 5.0,
}

BTU_MINISPLIT_TO_TONS = {
    9:  0.75,
    12: 1.0,
    15: 1.25,
    18: 1.5,
    24: 2.0,
    27: 2.25,
    30: 2.5,
    36: 3.0,
    42: 3.5,
    48: 4.0,
}

# Ordered highest-first so the first match wins
_BTU_CODES_3DIGIT = [
    ("060", 5.0),
    ("048", 4.0),
    ("042", 3.5),
    ("036", 3.0),
    ("030", 2.5),
    ("024", 2.0),
    ("018", 1.5),
]


def _normalize(model):
    return model.upper().replace("-", "").replace(" ", "")


def _find_3digit_btu(model_norm):
    """
    Search for a zero-padded 3-digit BTU/1000 code as a SUBSTRING.
    Works for Goodman GSX14036, Trane 4TTR6036L, Lennox 16ACX036-230, etc.
    Uses substring search (not regex) to avoid non-overlapping match issues.
    e.g. PA14036JK -> '036' found at pos 4 -> 3.0 tons
         4TTR6036L -> '036' found at pos 5 -> 3.0 tons
    """
    for code, tons in _BTU_CODES_3DIGIT:
        if code in model_norm:
            return tons
    return None


def _find_carrier_embedded_btu(model_norm):
    """
    Carrier-family models embed a 2-digit BTU code between a generation digit
    and a voltage letter: [A-Z][digit][2-digit-BTU-code][A-Z]
    e.g. 24ACC6[36]A003 -> 'C6' + '36' + 'A' -> 36 -> 3.0 tons
         24ACC6[48]A003 -> '48' -> 4.0 tons
    """
    for m in re.finditer(r'[A-Z]\d(\d{2})[A-Z]', model_norm):
        code = int(m.group(1))
        if code in BTU_TO_TONS:
            return BTU_TO_TONS[code]
    return None


# Furnace detection - furnace BTU codes = heat input capacity, NOT cooling tonnage
_FURNACE_PREFIXES = (
    "58STA", "58CVA", "58MXA", "58MTA", "58SCA", "58PAV", "58WAV",
    "GMEC", "GMVC", "GMSS", "AMEC", "AMVC", "AMSS",
    "RPGE", "RGPJ", "RSPM", "RGPM", "RGDA", "RGDM",
    "TUSE", "TUSA", "TUSB", "TUSC", "TUSD", "TUX1", "TUX2",
    "SL280", "SL297", "EL296",
    "YHJF", "YHJE", "YCJD",
    "N9MSB", "N9MSE", "TC9",
)


def _is_furnace(model_norm):
    for prefix in _FURNACE_PREFIXES:
        if model_norm.startswith(prefix):
            return True
    return False


def _decode_standard(model):
    """
    Standard decoder: find 3-digit zero-padded BTU code as substring.
    Covers Trane, Am. Std., Lennox, Rheem, York, Heil, Coleman + newer Carrier/Bryant/Payne.
    """
    norm = _normalize(model)
    if _is_furnace(norm):
        return None
    return _find_3digit_btu(norm)


def _decode_carrier_family(model):
    """
    Carrier family (Carrier, Bryant, Payne) decoder.
    Two-pass:
      1. Standard 3-digit substring search (catches LCA036, 38AH036, PA14036)
      2. Carrier-embedded 2-digit search (catches 24ACC636A003, 25HCB648A003)
    """
    norm = _normalize(model)
    if _is_furnace(norm):
        return None
    result = _find_3digit_btu(norm)
    if result:
        return result
    return _find_carrier_embedded_btu(norm)


def _decode_goodman_family(model):
    """Goodman / Amana / Daikin - standard 3-digit BTU code, skip furnaces."""
    norm = _normalize(model)
    if _is_furnace(norm):
        return None
    return _find_3digit_btu(norm)


def _decode_rheem_family(model):
    """Rheem / Ruud - standard 3-digit BTU code, skip furnaces."""
    norm = _normalize(model)
    if _is_furnace(norm):
        return None
    return _find_3digit_btu(norm)


def _decode_mitsubishi(model):
    """
    Mitsubishi Electric mini-splits use 2-digit kBTU codes (no leading zero).
    e.g. MSZ-GS18NA -> '18' -> 18000 BTU -> 1.5 tons
    """
    norm = _normalize(model)
    for m in re.finditer(r'(\d{2})', norm):
        code = int(m.group(1))
        if code in BTU_MINISPLIT_TO_TONS:
            return BTU_MINISPLIT_TO_TONS[code]
    return None


# Brand routing
_BRAND_DECODER_MAP = {
    "carrier":             _decode_carrier_family,
    "bryant":              _decode_carrier_family,
    "payne":               _decode_carrier_family,
    "trane":               _decode_standard,
    "american standard":   _decode_standard,
    "lennox":              _decode_standard,
    "dave lennox":         _decode_standard,
    "goodman":             _decode_goodman_family,
    "amana":               _decode_goodman_family,
    "daikin":              _decode_goodman_family,
    "rheem":               _decode_rheem_family,
    "ruud":                _decode_rheem_family,
    "york":                _decode_standard,
    "heil":                _decode_standard,
    "coleman":             _decode_standard,
    "luxaire":             _decode_standard,
    "mitsubishi":          _decode_mitsubishi,
    "mitsubishi electric": _decode_mitsubishi,
}


def _get_decoder(brand):
    if not brand:
        return None
    key = brand.lower().strip()
    if key in _BRAND_DECODER_MAP:
        return _BRAND_DECODER_MAP[key]
    for brand_key, fn in _BRAND_DECODER_MAP.items():
        if brand_key in key or key in brand_key:
            return fn
    return None


def decode_model_tonnage(brand, model_number):
    """
    Extract tonnage from an HVAC model number string.

    Args:
        brand:        Brand name (e.g. "Carrier", "Goodman", "York")
        model_number: Full model number string from nameplate

    Returns:
        Tonnage as float (e.g. 3.0) or None if cannot be decoded.
    """
    if not model_number:
        return None
    decoder = _get_decoder(brand)
    if not decoder:
        return _decode_standard(model_number)
    return decoder(model_number)


def decode_model_info(brand, model_number):
    """
    Decode all extractable info from a model number.
    Returns dict with brand, model_number, tonnage, tonnage_source.
    """
    tonnage = decode_model_tonnage(brand, model_number)
    return {
        "brand": brand,
        "model_number": model_number,
        "tonnage": tonnage,
        "tonnage_source": "model_decode" if tonnage is not None else "unknown",
    }


def get_all_brand_decode_notes():
    """Documentation of the decode pattern for each brand family."""
    return {
        "carrier_family": {
            "brands": ["Carrier", "Bryant", "Payne"],
            "pattern": "2-digit BTU/1000 code in Carrier format C6[36]A (e.g. 24ACC636A003 -> 3 tons), "
                       "OR 3-digit zero-padded code for simpler models (LCA036A -> 3 tons)",
            "example": "24ACC636A003 -> 3.0 tons",
        },
        "trane_family": {
            "brands": ["Trane", "American Standard"],
            "pattern": "3-digit zero-padded BTU/1000 code as substring (4TTR6036L -> 3 tons)",
            "example": "4TTR6036L1000A -> 3.0 tons",
        },
        "lennox": {
            "brands": ["Lennox"],
            "pattern": "3-digit zero-padded BTU/1000 code (16ACX036-230 -> 3 tons)",
            "example": "16ACX036-230 -> 3.0 tons",
        },
        "goodman_family": {
            "brands": ["Goodman", "Amana", "Daikin"],
            "pattern": "3-digit zero-padded BTU/1000 code. Furnace models (GMEC/GMVC prefix) skipped.",
            "example": "GSX14036 -> 3.0 tons",
        },
        "rheem_family": {
            "brands": ["Rheem", "Ruud"],
            "pattern": "3-digit zero-padded BTU/1000 code. Furnace models (RPGE/RGPJ prefix) skipped.",
            "example": "RA14AZ036JK -> 3.0 tons",
        },
        "jci_family": {
            "brands": ["York", "Heil", "Coleman", "Luxaire"],
            "pattern": "3-digit zero-padded BTU/1000 code (YCC036 -> 3 tons)",
            "example": "YCC036 -> 3.0 tons",
        },
        "mitsubishi": {
            "brands": ["Mitsubishi Electric"],
            "pattern": "2-digit kBTU code: 09=0.75t, 12=1t, 18=1.5t, 24=2t, 30=2.5t, 36=3t",
            "example": "MSZ-GS18NA -> 1.5 tons",
        },
    }


# BTU reference table
BTU_TONNAGE_TABLE = {
    "018": 1.5,
    "024": 2.0,
    "030": 2.5,
    "036": 3.0,
    "042": 3.5,
    "048": 4.0,
    "060": 5.0,
}
