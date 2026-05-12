"""
models.py — Board Session 8, Section 5A
Model Lookup API

Exposes the EquipmentModel table to the frontend for:
  - Brand discovery:  GET /api/models/brands
  - Model search:     GET /api/models/lookup?brand=Carrier&q=24V

No auth required — this is reference data, not tenant data.
Rate-limited to 60 req/min per IP.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import Optional

from db.database import get_db
from db.models import EquipmentModel
from rate_limit import limiter
from fastapi import Request

router = APIRouter(prefix="/api/models", tags=["models"])


# ── Response shapes ────────────────────────────────────────────────────────────

def _brand_row(brand: str, count: int) -> dict:
    return {"brand": brand, "model_count": count}


def _model_row(m: EquipmentModel) -> dict:
    return {
        "id": m.id,
        "brand": m.brand,
        "model_series": m.model_series,
        "equipment_type": m.equipment_type,
        "seer_rating": float(m.seer_rating) if m.seer_rating is not None else None,
        "tonnage_range": m.tonnage_range,
        "manufacture_years": m.manufacture_years,
        "avg_lifespan_years": m.avg_lifespan_years,
        "known_issues": m.known_issues or [],
        "replacement_models": m.replacement_models or [],
    }


# ── GET /api/models/brands ─────────────────────────────────────────────────────

@router.get("/brands")
@limiter.limit("60/minute")
async def list_brands(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Returns all distinct brands with their model count, sorted by prevalence
    (total_assessments desc, then alphabetically).

    Response:
      [
        {"brand": "Carrier", "model_count": 10},
        {"brand": "Trane",   "model_count": 10},
        ...
      ]
    """
    result = await db.execute(
        select(
            EquipmentModel.brand,
            func.count(EquipmentModel.id).label("model_count"),
            func.sum(EquipmentModel.total_assessments).label("total_assess"),
        )
        .group_by(EquipmentModel.brand)
        .order_by(
            func.sum(EquipmentModel.total_assessments).desc(),
            EquipmentModel.brand.asc(),
        )
    )
    rows = result.all()
    return [_brand_row(r.brand, r.model_count) for r in rows]


# ── GET /api/models/lookup ─────────────────────────────────────────────────────

@router.get("/lookup")
@limiter.limit("60/minute")
async def lookup_models(
    request: Request,
    brand: Optional[str] = Query(None, description="Filter by brand name (exact, case-insensitive)"),
    q: Optional[str] = Query(None, min_length=1, max_length=40, description="Model series prefix search"),
    equipment_type: Optional[str] = Query(None, description="Filter by equipment_type"),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """
    Search equipment models by brand + model series prefix.

    Examples:
      /api/models/lookup?brand=Carrier&q=24V        → Carrier 24V* models
      /api/models/lookup?brand=Goodman              → all Goodman models
      /api/models/lookup?equipment_type=ac_unit     → all AC unit models

    Response:
      [
        {
          "id": "...",
          "brand": "Carrier",
          "model_series": "24VNA636",
          "equipment_type": "ac_unit",
          "seer_rating": 20.0,
          "tonnage_range": "1.5-5",
          "manufacture_years": "2019-present",
          "avg_lifespan_years": 18,
          "known_issues": [...],
          "replacement_models": [...]
        },
        ...
      ]
    """
    stmt = select(EquipmentModel)

    # Brand filter (case-insensitive)
    if brand:
        stmt = stmt.where(func.lower(EquipmentModel.brand) == brand.lower().strip())

    # Model series prefix search (case-insensitive)
    if q:
        pattern = f"{q.strip()}%"
        stmt = stmt.where(
            or_(
                EquipmentModel.model_series.ilike(pattern),
                EquipmentModel.model_series.ilike(f"%{q.strip()}%"),
            )
        )

    # Equipment type filter
    if equipment_type:
        stmt = stmt.where(EquipmentModel.equipment_type == equipment_type)

    # Sort: most-assessed first, then alphabetical
    stmt = (
        stmt
        .order_by(EquipmentModel.total_assessments.desc(), EquipmentModel.model_series.asc())
        .limit(limit)
    )

    result = await db.execute(stmt)
    models = result.scalars().all()
    return [_model_row(m) for m in models]


# ── GET /api/models/all ────────────────────────────────────────────────────────
# Full dump for IndexedDB seeding — used once on first app load.

@router.get("/all")
@limiter.limit("10/minute")
async def all_models(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Returns ALL equipment models for local IndexedDB caching.
    Clients should call this once and cache with 24-hour TTL.

    Returns up to 500 models (current DB has 50).
    """
    result = await db.execute(
        select(EquipmentModel)
        .order_by(EquipmentModel.brand.asc(), EquipmentModel.model_series.asc())
        .limit(500)
    )
    models = result.scalars().all()
    return {
        "models": [_model_row(m) for m in models],
        "count": len(models),
        "cached_at": func.now(),  # client uses response timestamp for TTL
    }
