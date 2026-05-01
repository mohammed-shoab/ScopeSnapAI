"""
WS-G — Estimate Engine (Fault Card / Price List)
POST /api/estimates/fault-card  — generate A/B/C tiers from WS-A pricing tables

Replaces the old hardcoded A/B/C generation with a data-driven approach
using the pricing_tiers and labor_rates_houston tables populated in WS-A.

Flow:
  1. Look up fault_cards row for card_id (name, phase, difficulty, tech_notes)
  2. Look up pricing_tiers A/B/C for card_id (from price list "13. FAULT CARDS")
  3. Apply surcharges from labor_rates_houston:
       - attic_premium ($25-50 per visit)
       - after_hours (+25-50%)
       - r22_handling_surcharge ($75-150 if refrigerant=R-22)
  4. Apply company markup (from companies.default_markup_pct, default 35%)
  5. Return structured A/B/C response with line items

Acceptance criteria (WS-G M5):
  3-ton R-410A capacitor failure (card_id=1) with attic_access=True:
  → A = base_min + attic_premium_min  (e.g. 175 + 25 = 200 → after 35% markup ≈ 270)
  → Actual amounts depend on the pricing_tiers data loaded in WS-A.
  The key test is: data-driven (not hardcoded), surcharges applied, markup applied.
"""

import logging
from typing import Optional
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from db.database import get_db
from api.auth import get_current_user, AuthContext

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/estimates", tags=["estimates"])


# ── Request / Response ─────────────────────────────────────────────────────────

class FaultCardEstimateRequest(BaseModel):
    card_id: int = Field(..., ge=1, le=19, description="Fault card 1-19 (Decision D-1 numbering)")
    tonnage: Optional[float] = Field(None, ge=0.75, le=6.0, description="Equipment tonnage (0.75-6.0)")
    attic_access: bool = Field(False, description="Job requires attic access (adds premium)")
    after_hours: bool = Field(False, description="After-hours / emergency call (+25-50%)")
    refrigerant: Optional[str] = Field(None, description="Refrigerant type — R-22 triggers surcharge")
    assessment_id: Optional[str] = Field(None, description="Assessment to link estimate to")


class EstimateTier(BaseModel):
    tier: str                    # "A", "B", or "C"
    label: str                   # "Good", "Better", "Best"
    base_amount: int             # from pricing_tiers
    surcharges: dict             # breakdown of applied surcharges
    subtotal: int                # base + surcharges
    markup_amount: int           # company markup
    total: int                   # final customer-facing price
    recommended: bool = False    # lifecycle engine recommendation (WS-H)


class FaultCardEstimateResponse(BaseModel):
    card_id: int
    card_name: str
    phase: Optional[str]
    difficulty: Optional[str]
    tech_notes: Optional[str]
    tiers: list[EstimateTier]    # always 3: A, B, C
    r22_alert: bool
    attic_applied: bool
    after_hours_applied: bool
    markup_pct: float
    generated_at: str


# ── Helper ─────────────────────────────────────────────────────────────────────

def _apply_surcharges(
    base: int,
    attic_premium: int,
    after_hours_pct: float,
    r22_surcharge: int,
    attic_access: bool,
    after_hours: bool,
    is_r22: bool,
) -> tuple[int, dict]:
    """Returns (surcharge_total, breakdown_dict)."""
    breakdown = {}
    total = 0

    if attic_access and attic_premium > 0:
        breakdown["attic"] = attic_premium
        total += attic_premium

    if after_hours and after_hours_pct > 0:
        # Apply after-hours % to the base amount
        ah_amount = round(base * after_hours_pct)
        breakdown["after_hours"] = ah_amount
        total += ah_amount

    if is_r22 and r22_surcharge > 0:
        breakdown["r22_handling"] = r22_surcharge
        total += r22_surcharge

    return total, breakdown


# ── POST /api/estimates/fault-card ────────────────────────────────────────────

@router.post("/fault-card", status_code=200, response_model=FaultCardEstimateResponse)
async def generate_fault_card_estimate(
    body: FaultCardEstimateRequest,
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    WS-G: Generate A/B/C estimate from fault card using pricing_tiers + labor_rates_houston.

    This replaces the old hardcoded A/B/C generation. Prices are data-driven
    from the WS-A tables: pricing_tiers (from price list sheet "13. FAULT CARDS")
    and labor_rates_houston (surcharge rates).
    """

    # ── 1. Load fault card metadata ──────────────────────────────────────────
    fc_row = await db.execute(
        text("""
            SELECT card_id, card_name, phase, difficulty, tech_notes,
                   price_list_min, price_list_typical, price_list_max
            FROM fault_cards
            WHERE card_id = :card_id
        """),
        {"card_id": body.card_id},
    )
    fc = fc_row.fetchone()
    if not fc:
        raise HTTPException(
            status_code=404,
            detail=f"Fault card {body.card_id} not found. Check migration 007 ran."
        )

    # ── 2. Load pricing tiers A/B/C ──────────────────────────────────────────
    pt_rows = await db.execute(
        text("""
            SELECT tier, estimate_amount
            FROM pricing_tiers
            WHERE card_id = :card_id
            ORDER BY tier
        """),
        {"card_id": body.card_id},
    )
    pricing = {row.tier: row.estimate_amount for row in pt_rows.fetchall()}

    if not pricing:
        raise HTTPException(
            status_code=404,
            detail=f"No pricing tiers found for card {body.card_id}. Run WS-A data seed."
        )

    base_A = pricing.get("A", fc.price_list_min or 0)
    base_B = pricing.get("B", fc.price_list_typical or 0)
    base_C = pricing.get("C", fc.price_list_max or 0)

    # ── 3. Load labor rates / surcharge config ───────────────────────────────
    lr_row = await db.execute(
        text("""
            SELECT attic_premium_min, attic_premium_max,
                   after_hours_premium, emergency_weekend_premium,
                   r22_surcharge_min, r22_surcharge_max
            FROM labor_rates_houston
            LIMIT 1
        """),
    )
    lr = lr_row.fetchone()

    # Surcharge values (use "typical" = midpoint)
    attic_premium = int((lr.attic_premium_min + lr.attic_premium_max) / 2) if lr else 37
    # After-hours: parse "25–50% surcharge" → 37.5% midpoint
    after_hours_pct = 0.375 if lr else 0.375
    r22_surcharge = int((lr.r22_surcharge_min + lr.r22_surcharge_max) / 2) if lr else 112

    is_r22 = (body.refrigerant or "").upper().startswith("R-22")

    # ── 4. Get company markup ────────────────────────────────────────────────
    markup_row = await db.execute(
        text("SELECT default_markup_pct FROM companies WHERE id = :cid LIMIT 1"),
        {"cid": auth.company_id},
    )
    markup_result = markup_row.fetchone()
    markup_pct = float(markup_result.default_markup_pct) if markup_result else 35.0
    markup_mult = 1 + markup_pct / 100

    # ── 5. Build tiers ───────────────────────────────────────────────────────
    tier_configs = [
        ("A", "Good",   base_A),
        ("B", "Better", base_B),
        ("C", "Best",   base_C),
    ]

    tiers = []
    for tier_key, tier_label, base in tier_configs:
        surcharge_total, breakdown = _apply_surcharges(
            base=base,
            attic_premium=attic_premium,
            after_hours_pct=after_hours_pct,
            r22_surcharge=r22_surcharge,
            attic_access=body.attic_access,
            after_hours=body.after_hours,
            is_r22=is_r22,
        )
        subtotal = base + surcharge_total
        markup_amount = round(subtotal * (markup_mult - 1))
        total = subtotal + markup_amount

        tiers.append(EstimateTier(
            tier=tier_key,
            label=tier_label,
            base_amount=base,
            surcharges=breakdown,
            subtotal=subtotal,
            markup_amount=markup_amount,
            total=total,
            recommended=(tier_key == "B"),  # Default B as recommended; WS-H overrides
        ))

    return FaultCardEstimateResponse(
        card_id=fc.card_id,
        card_name=fc.card_name,
        phase=fc.phase,
        difficulty=fc.difficulty,
        tech_notes=fc.tech_notes,
        tiers=tiers,
        r22_alert=is_r22,
        attic_applied=body.attic_access,
        after_hours_applied=body.after_hours,
        markup_pct=markup_pct,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
