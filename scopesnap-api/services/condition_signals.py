"""
services/condition_signals.py
REC.2 — Derive condition_signal for lifecycle_rules lookup.

Takes assessment data (AI results, OCR nameplate, reading_inputs, diagnostic session
answers) and emits one of 9 vocabulary signals matching lifecycle_rules.condition_signal.

Priority chain: first match wins. Default fallback when nothing matches.

Signal vocabulary (v1 -- do not rename existing signals; add new ones only):
    under_warranty          install_year within last 2 years
    photo_confirmed_pitting AI photo: pitting / electrical_damage
    formicary_confirmed     AI photo: formicary_corrosion
    rla_over_nameplate      Tech reading: amperage > nameplate RLA spec
    recurring_clog          2nd+ Card 5 diagnosis for same property in 12 months
    attic_location          Nameplate / tech override: location = attic
    bearing_noise           Tech selected grinding/noise symptom
    sensor_only             Error code maps to sensor failure only (Card 11)
    default                 No specific condition matched
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

async def derive_condition_signal_from_assessment(
    assessment_id: Optional[str],
    card_id: int,
    unit_age_years: Optional[int],
    db: AsyncSession,
) -> str:
    """
    Derive the best condition_signal for lifecycle_rules lookup.

    Args:
        assessment_id: UUID string of the assessment row. May be None.
        card_id:       Fault card number (1-19).
        unit_age_years: Pre-computed unit age (None if unknown).
        db:            Async SQLAlchemy session.

    Returns:
        One of the 9 vocabulary signal strings.
    """
    try:
        return await _derive(assessment_id, card_id, unit_age_years, db)
    except Exception:
        logger.warning(
            "[condition_signals] signal derivation failed -- returning default",
            exc_info=True,
        )
        return "default"


# ---------------------------------------------------------------------------
# Internal priority chain
# ---------------------------------------------------------------------------

async def _derive(
    assessment_id: Optional[str],
    card_id: int,
    unit_age_years: Optional[int],
    db: AsyncSession,
) -> str:

    # 1. under_warranty: unit installed within the last 2 years
    if unit_age_years is not None and unit_age_years <= 2:
        return "under_warranty"

    if not assessment_id:
        return "default"

    # Fetch assessment row (lightweight -- only needed columns via raw SQL)
    asmt_row = await db.execute(
        text("""
            SELECT ai_issues, ai_condition, ocr_nameplate, tech_overrides,
                   complaint_type, property_id
            FROM assessments
            WHERE id = :aid
            LIMIT 1
        """),
        {"aid": assessment_id},
    )
    asmt = asmt_row.fetchone()
    if asmt is None:
        return "default"

    ai_issues    = asmt.ai_issues or []
    ai_condition = asmt.ai_condition or {}
    ocr          = asmt.ocr_nameplate or {}
    overrides    = asmt.tech_overrides or {}
    complaint    = (asmt.complaint_type or "").lower()
    property_id  = asmt.property_id

    # Flatten AI issues to a single searchable string
    issues_text = _flatten_issues(ai_issues)
    condition_text = str(ai_condition.get("overall", "")).lower()

    # 2. photo_confirmed_pitting: AI returned pitting / electrical_damage
    if _any_keyword(issues_text, ["pitting", "electrical_damage", "electrical damage"]):
        return "photo_confirmed_pitting"

    # 3. formicary_confirmed: AI returned formicary_corrosion
    if _any_keyword(issues_text, ["formicary"]):
        return "formicary_confirmed"

    # 4. bearing_noise: tech-selected grinding / noise symptom
    symptom = str(overrides.get("symptom", "")).lower()
    if _any_keyword(symptom, ["grind", "noise", "bearing", "squeal", "rattle"]):
        return "bearing_noise"
    # Also catch complaint types that inherently signal noise
    if "making_noise" in complaint:
        return "bearing_noise"

    # 5. rla_over_nameplate: tech reading amperage exceeded nameplate RLA
    rla_exceeded = await _check_rla_over_nameplate(assessment_id, db)
    if rla_exceeded:
        return "rla_over_nameplate"

    # 6. sensor_only: error code maps to sensor failure only (Card 11 context)
    if card_id == 11:
        error_code_type = str(overrides.get("error_code_type", "")).lower()
        error_desc      = str(overrides.get("error_description", "")).lower()
        if _any_keyword(error_code_type + " " + error_desc, ["sensor"]) and not _any_keyword(
            error_code_type + " " + error_desc, ["ignitor", "igniter", "flame", "burner"]
        ):
            return "sensor_only"

    # 7. attic_location: installation is in the attic
    location_hint = _extract_location(ocr, overrides)
    if "attic" in location_hint:
        return "attic_location"

    # 8. recurring_clog: 2nd+ Card 5 diagnosis for same property in 12 months
    if card_id == 5 and property_id:
        clog_count = await _count_recent_card5_diagnoses(property_id, db)
        if clog_count >= 2:
            return "recurring_clog"

    return "default"


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _flatten_issues(ai_issues: list) -> str:
    """Flatten ai_issues list to a single lowercase string for keyword search."""
    if not isinstance(ai_issues, list):
        return ""
    parts = []
    for item in ai_issues:
        if isinstance(item, dict):
            parts.append(str(item.get("issue", "")))
            parts.append(str(item.get("description", "")))
            parts.append(str(item.get("component", "")))
        elif isinstance(item, str):
            parts.append(item)
    return " ".join(parts).lower()


def _any_keyword(text: str, keywords: list) -> bool:
    """Return True if any keyword appears in text."""
    return any(kw in text for kw in keywords)


def _extract_location(ocr: dict, overrides: dict) -> str:
    """Return a lowercase location string from OCR or tech overrides."""
    candidates = [
        str(ocr.get("location", "")),
        str(ocr.get("installation_type", "")),
        str(overrides.get("location", "")),
        str(overrides.get("installation_location", "")),
        str(overrides.get("unit_location", "")),
    ]
    return " ".join(candidates).lower()


async def _check_rla_over_nameplate(assessment_id: str, db: AsyncSession) -> bool:
    """Return True if any amperage_rla reading exceeded the nameplate spec."""
    row = await db.execute(
        text("""
            SELECT actual_value, nameplate_spec, passed
            FROM reading_inputs
            WHERE assessment_id = :aid
              AND reading_type = 'amperage_rla'
            ORDER BY created_at DESC
            LIMIT 1
        """),
        {"aid": assessment_id},
    )
    r = row.fetchone()
    if r is None:
        return False
    # passed=False is the authoritative flag; fall back to numeric comparison
    if r.passed is not None:
        return not r.passed
    if r.actual_value is not None and r.nameplate_spec is not None:
        try:
            return float(r.actual_value) > float(r.nameplate_spec)
        except (ValueError, TypeError):
            pass
    return False


async def _count_recent_card5_diagnoses(property_id: str, db: AsyncSession) -> int:
    """Count Card 5 (drain clog) completed diagnostic sessions for this property in last 12 months."""
    one_year_ago = (datetime.now(timezone.utc) - timedelta(days=365)).isoformat()
    row = await db.execute(
        text("""
            SELECT COUNT(*) AS cnt
            FROM diagnostic_sessions ds
            JOIN assessments a ON ds.assessment_id = a.id
            WHERE a.property_id = :pid
              AND ds.resolved_card_id = 5
              AND ds.status = 'complete'
              AND ds.created_at >= :since
        """),
        {"pid": property_id, "since": one_year_ago},
    )
    r = row.fetchone()
    return int(r.cnt) if r and r.cnt else 0
