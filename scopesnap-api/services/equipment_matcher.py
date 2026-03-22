"""
ScopeSnap — Equipment Model Matcher
Matches Vision AI brand+model results to known equipment_models records.
Uses regex patterns stored in equipment_models.model_pattern.

WP-03 deliverable.
"""

import re
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import EquipmentModel


async def match_equipment_model(
    brand: str,
    model_number: str,
    db: AsyncSession,
) -> Optional[EquipmentModel]:
    """
    Matches a brand + model_number from Vision AI to a known equipment_models record.

    Matching strategy (in order):
    1. Exact match on (brand, model_series) where model_number starts with model_series
    2. Regex match using model_pattern field
    3. Fuzzy brand-only match if model can't be matched

    Returns:
        EquipmentModel record if matched, None if no match found.
        (Non-matches go into an "unmatched" queue via assessment data.)
    """
    if not brand or not model_number:
        return None

    brand_clean = brand.strip()
    model_clean = model_number.strip().upper()

    # ── Step 1: Get all models for this brand ─────────────────────────────────
    result = await db.execute(
        select(EquipmentModel).where(
            EquipmentModel.brand.ilike(f"%{brand_clean}%")
        )
    )
    candidates = result.scalars().all()

    if not candidates:
        return None

    # ── Step 2: Try model_pattern regex match ─────────────────────────────────
    for model in candidates:
        if model.model_pattern:
            try:
                pattern = model.model_pattern.strip()
                if re.match(pattern, model_clean, re.IGNORECASE):
                    return model
            except re.error:
                pass  # Bad regex in DB — skip

    # ── Step 3: Try model_series prefix match ─────────────────────────────────
    for model in candidates:
        if model.model_series:
            series = model.model_series.strip().upper()
            if model_clean.startswith(series):
                return model

    # ── Step 4: Partial match on series ──────────────────────────────────────
    for model in candidates:
        if model.model_series:
            series = model.model_series.strip().upper()
            if series in model_clean or model_clean[:6] in series:
                return model

    return None


async def get_equipment_by_id(
    model_id: str,
    db: AsyncSession,
) -> Optional[EquipmentModel]:
    """Retrieve an equipment model by ID."""
    result = await db.execute(
        select(EquipmentModel).where(EquipmentModel.id == model_id)
    )
    return result.scalar_one_or_none()


async def get_equipment_models_for_brand(
    brand: str,
    db: AsyncSession,
) -> list[EquipmentModel]:
    """Returns all known models for a brand."""
    result = await db.execute(
        select(EquipmentModel).where(
            EquipmentModel.brand.ilike(f"%{brand}%")
        ).order_by(EquipmentModel.model_series)
    )
    return result.scalars().all()
