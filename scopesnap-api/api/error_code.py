"""
WS-D — Brand DB & Error Code Routing (Task #12)
GET  /api/error-code/lookup?brand=X&code=Y  — returns meaning, action, card
GET  /api/error-code/brands                 — list all brand families
POST /api/error-code/lookup                 — logs analytics event + returns result

Acceptance criteria (WS-D M4):
  - Mitsubishi U4  → Card #7 (Contactor) with "MOST COMMON ~40%" badge
  - Carrier 4-flash → Card #2 (Dirty Filter / Choking)
  - Goodman E9     → Card #1 (Capacitor)
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from db.database import get_db
from api.auth import get_current_user, AuthContext
from api.events import record_event, EventPayload

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/error-code", tags=["error-code"])


# ── Response schemas ───────────────────────────────────────────────────────────

class ErrorCodeResult(BaseModel):
    found: bool
    brand_family: Optional[str] = None
    brand_family_members: Optional[list] = None
    subsystem: Optional[str] = None
    error_code: Optional[str] = None
    meaning: Optional[str] = None
    severity: Optional[str] = None
    action: Optional[str] = None
    decision_tree_card: Optional[int] = None
    card_name: Optional[str] = None
    card_houston_frequency_pct: Optional[int] = None
    # Houston field badge (shown on Tab F)
    frequency_badge: Optional[str] = None


class BrandFamily(BaseModel):
    brand_family: str
    brand_family_members: list
    code_count: int


# ── Helpers ────────────────────────────────────────────────────────────────────

def _frequency_badge(pct: Optional[int]) -> Optional[str]:
    """Returns human-readable frequency badge for the card."""
    if pct is None:
        return None
    if pct >= 18:
        return f"MOST COMMON ~{pct}% of Houston calls"
    if pct >= 10:
        return f"COMMON ~{pct}% of Houston calls"
    if pct >= 5:
        return f"~{pct}% of Houston calls"
    return f"~{pct}%"


# ── GET /api/error-code/lookup ─────────────────────────────────────────────────

@router.get("/lookup", response_model=ErrorCodeResult)
async def lookup_error_code(
    brand: str = Query(..., description="Brand name or family (e.g. 'carrier', 'mitsubishi', 'goodman')"),
    code: str = Query(..., description="Error code (e.g. 'U4', '4_flash', 'E9')"),
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    request=None,
):
    """
    WS-D Task #12 — Look up error code meaning + card routing.

    Brand matching is fuzzy (partial match on brand_family or brand_family_members).
    Code matching tries exact first, then case-insensitive.

    Returns the fault card to route the tech to, so the app can jump directly
    to the right diagnostic card when a tech scans/enters an error code.
    """
    brand_clean = brand.strip().lower()
    code_clean = code.strip()

    # ── Query error_codes table ────────────────────────────────────────────────
    # Try exact brand_family match first, then member array match, then partial
    row = await db.execute(
        text("""
            SELECT
                ec.brand_family,
                ec.brand_family_members,
                ec.subsystem,
                ec.error_code,
                ec.meaning,
                ec.severity,
                ec.action,
                ec.decision_tree_card,
                fc.card_name,
                fc.houston_frequency_pct
            FROM error_codes ec
            LEFT JOIN fault_cards fc ON fc.card_id = ec.decision_tree_card
            WHERE (
                    LOWER(ec.brand_family) = :brand
                OR  :brand = ANY(ec.brand_family_members::text[])
                OR  ec.brand_family LIKE ('%' || :brand || '%')
                OR  EXISTS (
                    SELECT 1 FROM unnest(ec.brand_family_members) m
                    WHERE LOWER(m) = :brand OR m LIKE ('%' || :brand || '%')
                )
            )
            AND (
                    LOWER(ec.error_code) = LOWER(:code)
                OR  ec.error_code = :code
            )
            ORDER BY
                -- Prefer exact brand_family match
                CASE WHEN LOWER(ec.brand_family) = :brand THEN 0 ELSE 1 END,
                -- Prefer codes with a card mapping
                CASE WHEN ec.decision_tree_card IS NOT NULL THEN 0 ELSE 1 END
            LIMIT 1
        """),
        {"brand": brand_clean, "code": code_clean},
    )
    result = row.fetchone()

    # ── Log analytics event ────────────────────────────────────────────────────
    # Every lookup persists to app_events so we can track Houston field codes
    try:
        if request:
            await record_event(
                EventPayload(
                    event_name="feedback_submitted",
                    event_data={
                        "type": "error_code_lookup",
                        "brand": brand,
                        "code": code,
                        "found": result is not None,
                        "card": result.decision_tree_card if result else None,
                    },
                ),
                request,
            )
    except Exception:
        pass  # Never fail a lookup due to analytics error

    if not result:
        return ErrorCodeResult(found=False)

    return ErrorCodeResult(
        found=True,
        brand_family=result.brand_family,
        brand_family_members=list(result.brand_family_members or []),
        subsystem=result.subsystem,
        error_code=result.error_code,
        meaning=result.meaning,
        severity=result.severity,
        action=result.action,
        decision_tree_card=result.decision_tree_card,
        card_name=result.card_name,
        card_houston_frequency_pct=result.houston_frequency_pct,
        frequency_badge=_frequency_badge(result.houston_frequency_pct),
    )


# ── GET /api/error-code/brands ────────────────────────────────────────────────

@router.get("/brands", response_model=list[BrandFamily])
async def list_error_code_brands(
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns all brand families in the error_codes table with code counts.
    Used to populate the brand dropdown on Tab F.
    """
    rows = await db.execute(
        text("""
            SELECT
                brand_family,
                brand_family_members,
                COUNT(*) as code_count
            FROM error_codes
            GROUP BY brand_family, brand_family_members
            ORDER BY code_count DESC
        """),
    )
    return [
        BrandFamily(
            brand_family=r.brand_family,
            brand_family_members=list(r.brand_family_members or []),
            code_count=r.code_count,
        )
        for r in rows.fetchall()
    ]
