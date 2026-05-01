"""
WS-H — Recommended-badge engine
GET /api/estimates/recommend?card_id=X&age=Y&condition=Z

Queries lifecycle_rules table (seeded in WS-A) to determine which A/B/C
tier should get the green "Recommended" badge.

Acceptance criteria (WS-H M10):
  7yr Carrier with photo_confirmed_pitting → C recommended
  2yr unit under_warranty → A recommended
  Default when data missing → B
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from db.database import get_db
from api.auth import get_current_user, AuthContext

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/estimates", tags=["estimates"])

@router.get("/recommend")
async def get_recommended_tier(
    card_id: int = Query(..., ge=1, le=19, description="Fault card 1-19"),
    age_years: Optional[float] = Query(None, description="Unit age in years (from Step Zero OCR)"),
    condition_signal: Optional[str] = Query(None, description="Condition signal (e.g. photo_confirmed_pitting, under_warranty)"),
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    WS-H — Determine recommended A/B/C tier for a given fault card + unit conditions.

    Priority order:
    1. Exact match on card_id + condition_signal + age threshold
    2. Match on card_id + condition_signal (any age)
    3. Match on card_id + default condition
    4. Global default: B (Typical)
    """
    # Try condition + age match first
    if condition_signal and age_years is not None:
        row = await db.execute(
            text("""
                SELECT recommended_tier, note
                FROM lifecycle_rules
                WHERE card_id = :card_id
                  AND condition_signal = :condition
                  AND (age_threshold_years IS NULL OR :age >= age_threshold_years)
                ORDER BY
                    CASE WHEN age_threshold_years IS NOT NULL THEN 0 ELSE 1 END,
                    age_threshold_years DESC NULLS LAST
                LIMIT 1
            """),
            {"card_id": card_id, "condition": condition_signal, "age": age_years},
        )
        r = row.fetchone()
        if r:
            return {"card_id": card_id, "recommended_tier": r.recommended_tier,
                    "reason": r.note, "source": "lifecycle_rule"}

    # Try condition match without age
    if condition_signal:
        row = await db.execute(
            text("""
                SELECT recommended_tier, note FROM lifecycle_rules
                WHERE card_id = :card_id AND condition_signal = :condition
                ORDER BY age_threshold_years DESC NULLS LAST LIMIT 1
            """),
            {"card_id": card_id, "condition": condition_signal},
        )
        r = row.fetchone()
        if r:
            return {"card_id": card_id, "recommended_tier": r.recommended_tier,
                    "reason": r.note, "source": "lifecycle_rule_no_age"}

    # Try default for this card
    row = await db.execute(
        text("""
            SELECT recommended_tier, note FROM lifecycle_rules
            WHERE card_id = :card_id AND condition_signal = 'default'
            LIMIT 1
        """),
        {"card_id": card_id},
    )
    r = row.fetchone()
    if r:
        return {"card_id": card_id, "recommended_tier": r.recommended_tier,
                "reason": r.note, "source": "lifecycle_rule_default"}

    # Global default: B
    return {"card_id": card_id, "recommended_tier": "B",
            "reason": "Default recommendation — insufficient data", "source": "global_default"}
