"""
SnapAI -- Equipment Model Matcher
Matches Vision AI brand+model results to known equipment_models records.
Uses regex patterns stored in equipment_models.model_pattern.

Also calls model_decoder to extract tonnage from the model number string
BEFORE hitting the DB -- cheapest first-pass tonnage source.

Tonnage priority chain:
  1. decode_model_tonnage(brand, model_number)  <- model_decoder.py
  2. EquipmentModel.tonnage_range from DB lookup
  3. Tech manual entry (UI fallback)

WP-03 deliverable.
"""

import re
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import EquipmentModel
from services.model_decoder import decode_model_tonnage


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

    # -- Step 1: Get all models for this brand ---------------------------------
    result = await db.execute(
        select(EquipmentModel).where(
            EquipmentModel.brand.ilike(f"%{brand_clean}%")
        )
    )
    candidates = result.scalars().all()

    if not candidates:
        return None

    # -- Step 2: Try model_pattern regex match ---------------------------------
    for model in candidates:
        if model.model_pattern:
            try:
                pattern = model.model_pattern.strip()
                if re.match(pattern, model_clean, re.IGNORECASE):
                    return model
            except re.error:
                pass  # Bad regex in DB -- skip

    # -- Step 3: Try model_series prefix match ---------------------------------
    for model in candidates:
        if model.model_series:
            series = model.model_series.strip().upper()
            if model_clean.startswith(series):
                return model

    # -- Step 4: Partial match on series ---------------------------------------
    for model in candidates:
        if model.model_series:
            series = model.model_series.strip().upper()
            if series in model_clean or model_clean[:6] in series:
                return model

    return None


async def match_equipment_with_tonnage(
    brand: str,
    model_number: str,
    db: AsyncSession,
) -> dict:
    """
    Full match + tonnage resolution.

    Returns a dict with:
      - matched_model: EquipmentModel | None
      - tonnage: float | None
      - tonnage_source: "model_decode" | "db_lookup" | "unknown"

    Tonnage priority:
      1. decode_model_tonnage() -- parse BTU code from model string (instant, no DB)
      2. matched_model.tonnage_range -- from equipment_models table
      3. None -> tech must enter manually
    """
    # Step 1: model-number string decode (no DB needed)
    decoded_tons = decode_model_tonnage(brand, model_number)

    # Step 2: DB lookup
    matched = await match_equipment_model(brand, model_number, db)

    # Determine final tonnage + source
    if decoded_tons is not None:
        tonnage = decoded_tons
        tonnage_source = "model_decode"
    elif matched and matched.tonnage_range:
        # tonnage_range is stored as "1.5-5" -- extract min as best estimate
        try:
            tonnage = float(matched.tonnage_range.split("-")[0])
        except (ValueError, IndexError):
            tonnage = None
        tonnage_source = "db_lookup" if tonnage else "unknown"
    else:
        tonnage = None
        tonnage_source = "unknown"

    return {
        "matched_model": matched,
        "tonnage": tonnage,
        "tonnage_source": tonnage_source,
    }


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
