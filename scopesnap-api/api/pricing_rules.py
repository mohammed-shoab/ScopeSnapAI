"""
SnapAI — Pricing Rules API
GET/POST/PATCH/DELETE /api/pricing-rules/

Company-specific labor rates, parts costs, and markup overrides.
Contractors use this to customize how SnapAI estimates are priced
relative to national defaults.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel

from db.database import get_db
from db.models import PricingRule
from api.auth import get_current_user, AuthContext

router = APIRouter(prefix="/api/pricing-rules", tags=["pricing-rules"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class PricingRuleOut(BaseModel):
    id: str
    company_id: Optional[str] = None
    equipment_type: str
    job_type: str
    region: str
    parts_cost: Optional[dict] = None
    labor_hours: Optional[dict] = None
    labor_rate: Optional[float] = None
    permit_cost: Optional[float] = None
    refrigerant_cost_per_lb: Optional[float] = None
    additional_costs: Optional[dict] = None

    class Config:
        from_attributes = True


class PricingRuleCreate(BaseModel):
    equipment_type: str
    job_type: str
    region: str = "national"
    labor_rate: Optional[float] = None
    permit_cost: Optional[float] = None
    refrigerant_cost_per_lb: Optional[float] = None
    parts_cost: Optional[dict] = None
    labor_hours: Optional[dict] = None
    additional_costs: Optional[dict] = None


class PricingRulePatch(BaseModel):
    labor_rate: Optional[float] = None
    permit_cost: Optional[float] = None
    refrigerant_cost_per_lb: Optional[float] = None
    parts_cost: Optional[dict] = None
    labor_hours: Optional[dict] = None
    additional_costs: Optional[dict] = None


# ── GET /api/pricing-rules/ ───────────────────────────────────────────────────

@router.get("/", response_model=List[PricingRuleOut])
async def list_pricing_rules(
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns all pricing rules for the authenticated company,
    plus any global defaults (company_id IS NULL).
    Company-specific rules override global defaults in the UI.
    """
    result = await db.execute(
        select(PricingRule).where(
            (PricingRule.company_id == auth.company_id) |
            (PricingRule.company_id.is_(None))
        ).order_by(PricingRule.equipment_type, PricingRule.job_type)
    )
    rules = result.scalars().all()
    return rules


# ── POST /api/pricing-rules/ ──────────────────────────────────────────────────

@router.post("/", response_model=PricingRuleOut, status_code=status.HTTP_201_CREATED)
async def create_pricing_rule(
    body: PricingRuleCreate,
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new company-specific pricing rule override.
    If a rule for the same equipment_type + job_type + region already exists
    for this company, returns 409 — use PATCH to update it.
    """
    # Check for duplicate
    existing = await db.execute(
        select(PricingRule).where(
            PricingRule.company_id == auth.company_id,
            PricingRule.equipment_type == body.equipment_type,
            PricingRule.job_type == body.job_type,
            PricingRule.region == body.region,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A pricing rule for {body.equipment_type}/{body.job_type} in region '{body.region}' already exists. Use PATCH to update it.",
        )

    rule = PricingRule(
        company_id=auth.company_id,
        equipment_type=body.equipment_type,
        job_type=body.job_type,
        region=body.region,
        labor_rate=body.labor_rate,
        permit_cost=body.permit_cost,
        refrigerant_cost_per_lb=body.refrigerant_cost_per_lb,
        parts_cost=body.parts_cost,
        labor_hours=body.labor_hours,
        additional_costs=body.additional_costs,
    )
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule


# ── PATCH /api/pricing-rules/{rule_id} ───────────────────────────────────────

@router.patch("/{rule_id}", response_model=PricingRuleOut)
async def update_pricing_rule(
    rule_id: str,
    body: PricingRulePatch,
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update fields on an existing company-specific pricing rule.
    Contractors can only update their own rules, not global defaults.
    """
    result = await db.execute(
        select(PricingRule).where(
            PricingRule.id == rule_id,
            PricingRule.company_id == auth.company_id,
        )
    )
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pricing rule not found or not owned by your company.",
        )

    patch = body.model_dump(exclude_unset=True)
    for field, value in patch.items():
        setattr(rule, field, value)

    await db.commit()
    await db.refresh(rule)
    return rule


# ── DELETE /api/pricing-rules/{rule_id} ───────────────────────────────────────

@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pricing_rule(
    rule_id: str,
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a company-specific pricing rule, reverting that
    equipment/job combination back to national defaults.
    """
    result = await db.execute(
        select(PricingRule).where(
            PricingRule.id == rule_id,
            PricingRule.company_id == auth.company_id,
        )
    )
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pricing rule not found or not owned by your company.",
        )

    await db.delete(rule)
    await db.commit()
