"""
SnapAI — Property API Endpoints
WP-05: Property History + Customer Management

Enables address lookup so techs can see previous visits, equipment history, and customer info.
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func

from db.database import get_db
from db.models import Property, Assessment, EquipmentInstance, AssessmentPhoto
from api.auth import get_current_user, AuthContext

router = APIRouter(prefix="/api/properties", tags=["properties"])


# ── Request Models ────────────────────────────────────────────────────────────

class UpdatePropertyRequest(BaseModel):
    address_line1: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    notes: Optional[str] = None


# ── Helpers ───────────────────────────────────────────────────────────────────

def _normalize_address(address: str) -> str:
    """Normalize address for fuzzy matching."""
    return address.lower().strip()


def _address_matches(prop: Property, query: str) -> bool:
    """Check if property address matches query string (fuzzy)."""
    q = _normalize_address(query)
    addr = _normalize_address(prop.address_line1 or "")
    city = _normalize_address(prop.city or "")
    zip_code = (prop.zip or "").strip()

    # Check if query terms appear in address or city
    terms = q.split()
    return all(
        term in addr or term in city or term in zip_code
        for term in terms
    )


def _equipment_to_summary(eq: EquipmentInstance) -> dict:
    """Serializes equipment instance for the history display."""
    return {
        "id": str(eq.id),
        "equipment_type": eq.equipment_type,
        "brand": eq.brand,
        "model_number": eq.model_number,
        "serial_number": eq.serial_number,
        "install_year": eq.install_year,
        "condition": eq.condition,
        "last_assessed_at": eq.last_assessed_at.isoformat() if eq.last_assessed_at else None,
        "ai_confidence": float(eq.ai_confidence) if eq.ai_confidence else None,
    }


def _property_to_dict(prop: Property, include_equipment: bool = False, include_assessments: bool = False) -> dict:
    """Serializes a Property ORM record to a response dict."""
    result = {
        "id": str(prop.id),
        "address_line1": prop.address_line1,
        "city": prop.city,
        "state": prop.state,
        "zip": prop.zip,
        "customer_name": prop.customer_name,
        "customer_email": prop.customer_email,
        "customer_phone": prop.customer_phone,
        "visit_count": prop.visit_count,
        "last_visit_at": prop.last_visit_at.isoformat() if prop.last_visit_at else None,
        "notes": prop.notes,
        "created_at": prop.created_at.isoformat() if prop.created_at else None,
    }

    if include_equipment and hasattr(prop, 'equipment_instances'):
        result["equipment"] = [
            _equipment_to_summary(eq) for eq in prop.equipment_instances
        ]

    if include_assessments and hasattr(prop, 'assessments'):
        result["assessments"] = [
            {
                "id": str(a.id),
                "status": a.status,
                "created_at": a.created_at.isoformat() if a.created_at else None,
                "ai_condition": a.ai_condition,
            }
            for a in sorted(prop.assessments, key=lambda x: x.created_at, reverse=True)[:5]
        ]

    return result


# ── GET /api/properties/search ─────────────────────────────────────────────────

@router.get("/search")
async def search_properties(
    q: str = Query(..., min_length=3, description="Address or customer name to search"),
    limit: int = Query(10, le=50),
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Fuzzy address search across all properties for the current company.

    Returns matching properties with:
    - Visit count and last visit date
    - Customer name + contact info
    - Linked equipment (brand, model, condition)
    - Latest assessment date

    Used by tech when starting a new assessment at an existing address.
    """
    # Fetch all properties for this company (SQLite doesn't support ILIKE/trigram)
    # For production PostgreSQL, use pg_trgm GIN index
    result = await db.execute(
        select(Property).where(
            Property.company_id == auth.company_id,
        ).order_by(Property.last_visit_at.desc().nulls_last()).limit(200)
    )
    all_properties = result.scalars().all()

    # Fuzzy match client-side (SQLite limitation; prod uses pg_trgm)
    q_lower = _normalize_address(q)
    matched = []
    for prop in all_properties:
        addr = _normalize_address(prop.address_line1 or "")
        city = _normalize_address(prop.city or "")
        zip_code = (prop.zip or "").strip().lower()
        name = _normalize_address(prop.customer_name or "")

        # Check if ANY query term matches
        terms = q_lower.split()
        if any(
            any(term in field for field in [addr, city, zip_code, name])
            for term in terms
        ):
            matched.append(prop)

        if len(matched) >= limit:
            break

    # Load equipment instances for each matched property
    properties_data = []
    for prop in matched:
        # Get equipment instances
        eq_result = await db.execute(
            select(EquipmentInstance).where(
                EquipmentInstance.property_id == prop.id
            ).order_by(EquipmentInstance.last_assessed_at.desc())
        )
        equipment = eq_result.scalars().all()

        # Get latest assessment count
        assess_result = await db.execute(
            select(Assessment).where(
                Assessment.property_id == prop.id,
                Assessment.company_id == auth.company_id,
            ).order_by(Assessment.created_at.desc()).limit(1)
        )
        latest_assess = assess_result.scalar_one_or_none()

        prop_dict = _property_to_dict(prop)
        prop_dict["equipment"] = [_equipment_to_summary(eq) for eq in equipment]
        prop_dict["latest_assessment"] = {
            "id": str(latest_assess.id),
            "status": latest_assess.status,
            "created_at": latest_assess.created_at.isoformat() if latest_assess.created_at else None,
        } if latest_assess else None

        # Add a "returning_customer" flag for the tech UI
        prop_dict["returning_customer"] = prop.visit_count > 1

        properties_data.append(prop_dict)

    return {
        "query": q,
        "count": len(properties_data),
        "results": properties_data,
    }


# ── GET /api/properties/{id} ───────────────────────────────────────────────────

@router.get("/{property_id}")
async def get_property(
    property_id: str,
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns full property details including all equipment and assessment history."""
    result = await db.execute(
        select(Property).where(
            Property.id == property_id,
            Property.company_id == auth.company_id,
        )
    )
    prop = result.scalar_one_or_none()
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")

    # Get equipment instances
    eq_result = await db.execute(
        select(EquipmentInstance).where(
            EquipmentInstance.property_id == property_id
        ).order_by(EquipmentInstance.last_assessed_at.desc())
    )
    equipment = eq_result.scalars().all()

    # Get assessment history (last 10)
    assess_result = await db.execute(
        select(Assessment).where(
            Assessment.property_id == property_id,
            Assessment.company_id == auth.company_id,
        ).order_by(Assessment.created_at.desc()).limit(10)
    )
    assessments = assess_result.scalars().all()

    prop_dict = _property_to_dict(prop)
    prop_dict["equipment"] = [_equipment_to_summary(eq) for eq in equipment]
    prop_dict["assessments"] = [
        {
            "id": str(a.id),
            "status": a.status,
            "ai_condition": a.ai_condition,
            "ai_equipment_id": a.ai_equipment_id,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in assessments
    ]

    return prop_dict


# ── PATCH /api/properties/{id} ─────────────────────────────────────────────────

@router.patch("/{property_id}")
async def update_property(
    property_id: str,
    body: UpdatePropertyRequest,
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Updates property customer info and notes."""
    result = await db.execute(
        select(Property).where(
            Property.id == property_id,
            Property.company_id == auth.company_id,
        )
    )
    prop = result.scalar_one_or_none()
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")

    if body.address_line1 is not None:
        prop.address_line1 = body.address_line1
    if body.city is not None:
        prop.city = body.city
    if body.state is not None:
        prop.state = body.state
    if body.zip is not None:
        prop.zip = body.zip
    if body.customer_name is not None:
        prop.customer_name = body.customer_name
    if body.customer_email is not None:
        prop.customer_email = body.customer_email
    if body.customer_phone is not None:
        prop.customer_phone = body.customer_phone
    if body.notes is not None:
        prop.notes = body.notes

    await db.commit()
    await db.refresh(prop)
    return _property_to_dict(prop)


# ── GET /api/properties/ ───────────────────────────────────────────────────────

@router.get("/")
async def list_properties(
    limit: int = Query(20, le=100),
    offset: int = 0,
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lists all properties for the current company, most recently visited first."""
    result = await db.execute(
        select(Property).where(
            Property.company_id == auth.company_id,
        ).order_by(Property.last_visit_at.desc().nulls_last())
        .offset(offset).limit(limit)
    )
    properties = result.scalars().all()
    return {
        "items": [_property_to_dict(p) for p in properties],
        "count": len(properties),
        "offset": offset,
        "limit": limit,
    }
