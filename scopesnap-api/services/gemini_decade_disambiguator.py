"""
Gemini decade disambiguator (Stage 1, v1.2 brand-decoder).

A small subset of HVAC serial formats encode the manufacture YEAR with a single
digit and no century/decade marker. The two we care about in the v1.2 data are:

  * Mitsubishi Electric (Japanese-fiscal single-digit year)
  * MrCool  (one of its two serial styles)

For these, ``serial_decoder.decode_serial`` returns a result whose
``metadata["decade_ambiguous"] is True`` and a list of
``metadata["candidate_years"]`` (e.g. ``[2008, 2018]``). Picking the right one
from the serial alone is impossible — we need an external signal.

This module resolves the ambiguity using whatever signals are cheaply
available, in priority order:

  1. Refrigerant hint (R-410A ⇒ not pre-2005; R-32 ⇒ 2018+; R-22 ⇒ older era)
     — pure logic, no API call.
  2. Rating-plate photo, read by Gemini Vision, to extract an explicit
     manufacture date / "DATE OF MFG" / build-week stamp.

The Gemini path is optional and degrades safely: if no API key is configured
or the package is missing, the function returns ``None`` (unresolved) and the
caller keeps the ambiguous result. This module never raises on a missing key.
"""

from __future__ import annotations

import base64
import json
import logging
import re
from typing import List, Optional, Sequence

try:
    from config import settings
except Exception:  # pragma: no cover - import-time fallback for tooling
    settings = None  # type: ignore

logger = logging.getLogger("snapai.decade_disambiguator")

# Refrigerant → earliest plausible manufacture year (US residential split AC).
# Conservative floors; used only to *eliminate* impossible candidates.
_REFRIGERANT_FLOOR = {
    "r-22": None,      # no floor — R-22 spans the oldest equipment
    "r22": None,
    "r-410a": 2003,    # R-410A became common ~2003-2005, mandatory new units 2010
    "r410a": 2003,
    "r-32": 2018,      # R-32 single-component appears in US/JP units ~2018+
    "r32": 2018,
    "r-454b": 2024,    # A2L low-GWP transition
    "r454b": 2024,
}


def resolve_by_refrigerant(
    candidate_years: Sequence[int],
    refrigerant_hint: Optional[str],
) -> Optional[int]:
    """Eliminate candidates that predate the refrigerant. Return the unique
    survivor, or ``None`` if 0 or >1 remain."""
    if not refrigerant_hint or not candidate_years:
        return None
    floor = _REFRIGERANT_FLOOR.get(refrigerant_hint.strip().lower(), "missing")
    if floor == "missing" or floor is None:
        return None
    survivors = [y for y in candidate_years if y >= floor]
    if len(survivors) == 1:
        return survivors[0]
    return None


# Date patterns we try to pull off a rating plate, most-specific first.
_DATE_PATTERNS = [
    re.compile(r"\b(19|20)\d{2}[-/.](0?[1-9]|1[0-2])\b"),   # 2018-06 / 2018/6
    re.compile(r"\b(0?[1-9]|1[0-2])[-/.](19|20)\d{2}\b"),   # 06/2018
    re.compile(r"\b(19|20)\d{2}\b"),                        # bare 4-digit year
]


def _extract_year_from_text(text: str, candidate_years: Sequence[int]) -> Optional[int]:
    """Find a 4-digit year in OCR/plate text that matches one of the candidate
    years. Matching against candidates avoids picking a model-number year or a
    patent year."""
    if not text:
        return None
    found = set()
    for pat in _DATE_PATTERNS:
        for m in pat.finditer(text):
            ystr = re.search(r"(19|20)\d{2}", m.group(0))
            if ystr:
                found.add(int(ystr.group(0)))
    for y in candidate_years:
        if y in found:
            return y
    return None


def _gemini_model():
    if settings is None or not getattr(settings, "gemini_api_key", ""):
        return None
    try:
        import google.generativeai as genai
    except ImportError:
        logger.warning("[decade] google-generativeai not installed; skipping vision path")
        return None
    try:
        genai.configure(api_key=settings.gemini_api_key)
        return genai.GenerativeModel("gemini-2.5-flash")
    except Exception as e:  # pragma: no cover - network/config issues
        logger.warning("[decade] Gemini init failed: %s", e)
        return None


def resolve_by_plate_photo(
    image_bytes: bytes,
    candidate_years: Sequence[int],
    mime_type: str = "image/jpeg",
) -> Optional[int]:
    """Ask Gemini Vision to read an explicit manufacture date off the rating
    plate and return whichever candidate year it confirms. Returns ``None`` if
    Gemini is unavailable or the plate has no decisive date."""
    model = _gemini_model()
    if model is None or not image_bytes or not candidate_years:
        return None

    cand_str = ", ".join(str(y) for y in candidate_years)
    prompt = (
        "You are reading an HVAC equipment rating plate. The unit's serial number "
        "is decade-ambiguous; it could have been manufactured in one of these "
        f"years: {cand_str}. Look ONLY for an explicit manufacture date on the "
        "plate (labels like 'DATE OF MFG', 'MFG DATE', 'MANUFACTURED', a build "
        "week/year stamp, or a clear 4-digit year next to the serial). Do NOT "
        "guess from model numbers, patent years, or certification years. "
        'Respond with strict JSON only: {"year": <one of the candidate years or null>, '
        '"evidence": "<short quote of what you saw, or empty>"}.'
    )
    try:
        resp = model.generate_content(
            [prompt, {"mime_type": mime_type, "data": image_bytes}]
        )
        raw = (resp.text or "").strip()
    except Exception as e:  # pragma: no cover - network
        logger.warning("[decade] Gemini call failed: %s", e)
        return None

    # Strip code fences if present.
    raw = re.sub(r"^```(?:json)?|```$", "", raw, flags=re.MULTILINE).strip()
    year = None
    try:
        data = json.loads(raw)
        year = data.get("year")
    except Exception:
        year = _extract_year_from_text(raw, candidate_years)

    if isinstance(year, int) and year in candidate_years:
        return year
    return None


def disambiguate_decade(
    candidate_years: Sequence[int],
    refrigerant_hint: Optional[str] = None,
    image_bytes: Optional[bytes] = None,
    image_mime_type: str = "image/jpeg",
) -> Optional[int]:
    """Top-level entry point. Tries the cheap refrigerant logic first, then the
    Gemini plate-photo read. Returns the resolved manufacture year, or ``None``
    if the ambiguity cannot be resolved (caller keeps the ambiguous result)."""
    candidate_years = [int(y) for y in (candidate_years or [])]
    if len(candidate_years) <= 1:
        return candidate_years[0] if candidate_years else None

    by_ref = resolve_by_refrigerant(candidate_years, refrigerant_hint)
    if by_ref is not None:
        logger.info("[decade] resolved by refrigerant '%s' -> %s", refrigerant_hint, by_ref)
        return by_ref

    if image_bytes:
        by_plate = resolve_by_plate_photo(image_bytes, candidate_years, image_mime_type)
        if by_plate is not None:
            logger.info("[decade] resolved by plate photo -> %s", by_plate)
            return by_plate

    logger.info("[decade] unresolved; candidates=%s", candidate_years)
    return None
