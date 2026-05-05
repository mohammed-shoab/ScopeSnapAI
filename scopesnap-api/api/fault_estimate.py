"""
WS-G — Estimate Engine (Fault Card / Price List)
POST /api/estimates/fault-card  — generate A/B/C tiers from WS-A pricing tables
POST /api/estimates/service     — generate service estimate from session findings (WS-L3)
"""

import json
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


# ── Service Estimate Request / Response ───────────────────────────────────────

class ServiceEstimateRequest(BaseModel):
    assessment_id: str = Field(..., description="Assessment UUID")
    session_id: str = Field(..., description="Diagnostic session UUID")
    attic_access: bool = Field(False)
    after_hours: bool = Field(False)


class ServiceLineItem(BaseModel):
    code: str
    description: str
    amount_min: int
    amount_max: int
    amount_typical: int
    card_id: Optional[int] = None
    is_flag: bool = False        # informational finding — no dollar amount


class ServiceEstimateResponse(BaseModel):
    session_id: str
    base_items: list[ServiceLineItem]
    add_ons: list[ServiceLineItem]
    flags: list[ServiceLineItem]   # informational, no amount
    total_min: int
    total_max: int
    total_typical: int
    markup_pct: float
    findings_count: int
    generated_at: str


# ── Line item lookup ───────────────────────────────────────────────────────────

# Dollar amounts from SnapAI_Decision_Tree.html Tab S section + price list
SERVICE_LINE_ITEMS: dict = {
    "base_labor":          {"description": "Base service labor (1–1.5 hrs)", "min": 85,  "max": 130, "typical": 107, "card_id": None},
    "flush_tablet":        {"description": "Condensate drain flush + tablet",  "min": 12,  "max": 18,  "typical": 15,  "card_id": None},
    "filter_replacement":  {"description": "Air filter replacement",           "min": 18,  "max": 45,  "typical": 30,  "card_id": 2},
    "coil_cleaning":       {"description": "Condenser coil cleaning",          "min": 80,  "max": 150, "typical": 110, "card_id": None},
    "card_1_addon":        {"description": "Capacitor — preventive replacement (before peak summer)",
                                                                                "min": 175, "max": 310, "typical": 245, "card_id": 1},
    "card_16_addon":       {"description": "Loose terminal — repair / retorque",
                                                                                "min": 85,  "max": 150, "typical": 115, "card_id": 16},
}

SERVICE_FLAGS = {
    "flag_over_amping":        "Compressor over-amping — schedule full assessment",
    "flag_over_amping_blower": "Blower over-FLA — schedule full assessment",
    "flag_low_deltaT":         "Low delta-T detected — refrigerant or airflow issue. Recommend follow-up Tab A diagnostic.",
}


def _build_service_item(code: str, data: dict) -> ServiceLineItem:
    return ServiceLineItem(
        code=code,
        description=data["description"],
        amount_min=data["min"],
        amount_max=data["max"],
        amount_typical=data["typical"],
        card_id=data.get("card_id"),
    )


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
    """

    # 1. Load fault card metadata
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

    # 2. Load pricing tiers A/B/C
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

    # 3. Load labor rates
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

    attic_premium = int((lr.attic_premium_min + lr.attic_premium_max) / 2) if lr else 37
    after_hours_pct = 0.375 if lr else 0.375
    r22_surcharge = int((lr.r22_surcharge_min + lr.r22_surcharge_max) / 2) if lr else 112

    is_r22 = (body.refrigerant or "").upper().startswith("R-22")

    # 4. Company markup
    markup_row = await db.execute(
        text("SELECT default_markup_pct FROM companies WHERE id = :cid LIMIT 1"),
        {"cid": auth.company_id},
    )
    markup_result = markup_row.fetchone()
    markup_pct = float(markup_result.default_markup_pct) if markup_result else 35.0
    markup_mult = 1 + markup_pct / 100

    # 5. Build tiers
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
            recommended=(tier_key == "B"),
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


# ── POST /api/estimates/service (WS-L3) ───────────────────────────────────────

@router.post("/service", status_code=200, response_model=ServiceEstimateResponse)
async def generate_service_estimate(
    body: ServiceEstimateRequest,
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    WS-L3: Generate service estimate from diagnostic_sessions.service_findings.
    Returns base service + all add-ons accumulated through the 8-step checklist.
    """

    # 1. Load session and verify ownership
    sess_row = await db.execute(
        text("""
            SELECT ds.session_id, ds.company_id, ds.service_findings,
                   a.ocr_nameplate
            FROM diagnostic_sessions ds
            JOIN assessments a ON a.id = ds.assessment_id
            WHERE ds.id = :sid AND ds.complaint_type = 'service'
        """),
        {"sid": body.session_id},
    )
    # Fallback query without session_id alias difference
    sess_row2 = await db.execute(
        text("""
            SELECT company_id, service_findings
            FROM diagnostic_sessions
            WHERE id = :sid AND complaint_type = 'service'
        """),
        {"sid": body.session_id},
    )
    sess = sess_row2.fetchone()
    if not sess:
        raise HTTPException(status_code=404, detail="Service session not found")

    if str(sess.company_id) != str(auth.company_id):
        raise HTTPException(status_code=403, detail="Not authorized")

    # 2. Parse service_findings JSONB
    findings_raw = sess.service_findings or []
    if isinstance(findings_raw, str):
        findings_raw = json.loads(findings_raw)

    # 3. Get company markup
    markup_row = await db.execute(
        text("SELECT default_markup_pct FROM companies WHERE id = :cid LIMIT 1"),
        {"cid": auth.company_id},
    )
    markup_result = markup_row.fetchone()
    markup_pct = float(markup_result.default_markup_pct) if markup_result else 35.0
    markup_mult = 1 + markup_pct / 100

    # 4. Build base items (always present)
    base_items = [
        _build_service_item("base_labor",   SERVICE_LINE_ITEMS["base_labor"]),
        _build_service_item("flush_tablet", SERVICE_LINE_ITEMS["flush_tablet"]),
    ]

    # 5. Build add-ons from findings
    add_ons: list[ServiceLineItem] = []
    flags: list[ServiceLineItem] = []
    seen_codes: set = set()

    for finding in findings_raw:
        li = finding.get("line_item") or finding.get("line_item_code")
        if not li:
            continue

        # Normalize: finding may have line_item as dict or line_item_code as str
        if isinstance(li, dict):
            code = li.get("code") or li.get("line_item_code", "")
        else:
            code = str(li)

        if not code or code in seen_codes:
            continue
        seen_codes.add(code)

        if code in SERVICE_FLAGS:
            flags.append(ServiceLineItem(
                code=code,
                description=SERVICE_FLAGS[code],
                amount_min=0, amount_max=0, amount_typical=0,
                is_flag=True,
            ))
        elif code in SERVICE_LINE_ITEMS:
            add_ons.append(_build_service_item(code, SERVICE_LINE_ITEMS[code]))
        # Unknown codes: log and skip
        else:
            logger.warning("Unknown service line item code: %s", code)

    # 6. Compute totals with markup
    all_dollar_items = base_items + add_ons
    total_min     = round(sum(i.amount_min     for i in all_dollar_items) * markup_mult)
    total_max     = round(sum(i.amount_max     for i in all_dollar_items) * markup_mult)
    total_typical = round(sum(i.amount_typical for i in all_dollar_items) * markup_mult)

    return ServiceEstimateResponse(
        session_id=body.session_id,
        base_items=base_items,
        add_ons=add_ons,
        flags=flags,
        total_min=total_min,
        total_max=total_max,
        total_typical=total_typical,
        markup_pct=markup_pct,
        findings_count=len(findings_raw),
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
