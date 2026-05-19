"""
WS-C: Phase 2 Readings Gate
Endpoints:
  PUT  /api/readings/{assessment_id}          — save readings, compute superheat/subcooling
  GET  /api/readings/{assessment_id}/targets  — return PT targets for this assessment
  POST /api/readings/{assessment_id}/trigger  — mark gate as triggered (called by frontend)
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from db.models import Assessment
from api.clerk_webhook import get_current_user, AuthContext

router = APIRouter(prefix="/api/readings", tags=["readings"])

# ---------------------------------------------------------------------------
# Complaint types that ALWAYS require readings before estimate generation
# ---------------------------------------------------------------------------
READINGS_REQUIRED_COMPLAINTS = {"not_cooling", "not_heating"}

# ---------------------------------------------------------------------------
# Compact PT tables (PSI -> saturation temperature, degrees F)
# Source: standard refrigerant PT charts, field-verified
# ---------------------------------------------------------------------------
_R410A_SUCTION_PT = {
    95: 33, 98: 34, 100: 35, 103: 36, 105: 37,
    108: 38, 110: 39, 113: 40, 115: 41, 118: 42,
    120: 43, 123: 44, 125: 45, 128: 46, 130: 47,
    133: 48, 135: 49, 138: 50, 140: 51, 143: 52,
    145: 53, 148: 54, 150: 55, 153: 56, 155: 57,
}
_R410A_DISCHARGE_PT = {
    280: 92, 295: 95, 310: 98, 325: 100, 340: 103,
    355: 106, 370: 108, 385: 111, 400: 113, 415: 116,
    430: 118, 445: 121, 460: 123, 475: 125, 490: 127,
    505: 130, 520: 132,
}
_R22_SUCTION_PT = {
    40: 19, 45: 23, 50: 26, 55: 30, 60: 34,
    65: 37, 70: 41, 75: 44, 80: 48, 85: 51,
    90: 54, 95: 57, 100: 60,
}
_R22_DISCHARGE_PT = {
    180: 94, 200: 100, 220: 106, 240: 112, 260: 117,
    280: 122, 300: 127, 320: 132,
}
_R32_SUCTION_PT = {
    100: 26, 110: 30, 120: 34, 130: 38, 140: 41,
    150: 45, 160: 48, 170: 51, 180: 54,
}
_R32_DISCHARGE_PT = {
    350: 90, 380: 95, 410: 100, 440: 105, 470: 110,
    500: 115, 530: 119, 560: 124,
}
_R454B_SUCTION_PT = {
    95: 30, 105: 34, 115: 38, 125: 42, 135: 46,
    145: 50, 155: 53, 165: 57, 175: 60,
}
_R454B_DISCHARGE_PT = {
    300: 90, 330: 95, 360: 100, 390: 105, 420: 110,
    450: 115, 480: 120, 510: 124,
}

_PT_TABLES = {
    "R-410A": {"suction": _R410A_SUCTION_PT, "discharge": _R410A_DISCHARGE_PT},
    "R-22":   {"suction": _R22_SUCTION_PT,   "discharge": _R22_DISCHARGE_PT},
    "R-32":   {"suction": _R32_SUCTION_PT,   "discharge": _R32_DISCHARGE_PT},
    "R-454B": {"suction": _R454B_SUCTION_PT, "discharge": _R454B_DISCHARGE_PT},
}

# Superheat targets by refrigerant + metering device
_SUPERHEAT_TARGETS = {
    "R-410A": {"piston": (8, 14, 10), "txv": (8, 14, 10), "eev": (6, 12, 9)},
    "R-22":   {"piston": (6, 14, 10), "txv": (8, 14, 10), "eev": (6, 12, 9)},
    "R-32":   {"piston": (8, 14, 10), "txv": (7, 12, 9),  "eev": (7, 12, 9)},
    "R-454B": {"piston": (8, 13, 9),  "txv": (7, 12, 9),  "eev": (7, 12, 9)},
}
_SUBCOOLING_TARGETS = {
    "R-410A": {"txv": (8, 15, 12), "eev": (6, 14, 10)},
    "R-22":   {"txv": (8, 15, 12), "eev": (6, 14, 10)},
    "R-32":   {"txv": (8, 14, 10), "eev": (8, 14, 10)},
    "R-454B": {"txv": (8, 14, 11), "eev": (8, 14, 11)},
}


def _interpolate_sat_temp(psig: float, table: dict) -> Optional[float]:
    """Linear interpolation of saturation temp from a PT lookup table."""
    keys = sorted(table.keys())
    if psig <= keys[0]:
        return float(table[keys[0]])
    if psig >= keys[-1]:
        return float(table[keys[-1]])
    for i in range(len(keys) - 1):
        lo, hi = keys[i], keys[i + 1]
        if lo <= psig <= hi:
            frac = (psig - lo) / (hi - lo)
            return round(table[lo] + frac * (table[hi] - table[lo]), 1)
    return None


def _classify(value: float, lo: float, hi: float) -> str:
    if value < lo:
        return "LOW"
    if value > hi:
        return "HIGH"
    return "OK"


def compute_readings(
    suction_psig: float,
    discharge_psig: float,
    ambient_temp_f: float,
    supply_air_temp_f: float,
    suction_line_temp_f: Optional[float],
    liquid_line_temp_f: Optional[float],
    refrigerant: str,
    metering: str,
) -> dict:
    """
    Compute superheat, subcooling, delta-T, and classify against targets.
    Returns a dict of computed values + classifications.
    """
    pt = _PT_TABLES.get(refrigerant)
    result: dict = {
        "refrigerant": refrigerant,
        "metering_device": metering,
        "suction_sat_temp_f": None,
        "discharge_sat_temp_f": None,
        "superheat_f": None,
        "superheat_status": None,
        "subcooling_f": None,
        "subcooling_status": None,
        "delta_t_f": None,
        "delta_t_status": None,
        "pressure_diagnosis": None,
    }

    if pt:
        result["suction_sat_temp_f"] = _interpolate_sat_temp(suction_psig, pt["suction"])
        result["discharge_sat_temp_f"] = _interpolate_sat_temp(discharge_psig, pt["discharge"])

    # Superheat (needs suction line temp)
    if suction_line_temp_f is not None and result["suction_sat_temp_f"] is not None:
        sh = round(suction_line_temp_f - result["suction_sat_temp_f"], 1)
        result["superheat_f"] = sh
        targets = _SUPERHEAT_TARGETS.get(refrigerant, {}).get(metering, (8, 14, 10))
        result["superheat_status"] = _classify(sh, targets[0], targets[1])
        result["superheat_target"] = {"min": targets[0], "max": targets[1], "ideal": targets[2]}

    # Subcooling (needs liquid line temp, only for TXV/EEV)
    if (
        liquid_line_temp_f is not None
        and result["discharge_sat_temp_f"] is not None
        and metering in ("txv", "eev")
    ):
        sc = round(result["discharge_sat_temp_f"] - liquid_line_temp_f, 1)
        result["subcooling_f"] = sc
        targets = _SUBCOOLING_TARGETS.get(refrigerant, {}).get(metering, (8, 15, 12))
        result["subcooling_status"] = _classify(sc, targets[0], targets[1])
        result["subcooling_target"] = {"min": targets[0], "max": targets[1], "ideal": targets[2]}

    # Delta-T (supply vs return — approximate from supply vs 75F Houston return baseline)
    # Full delta-T needs return air temp; we store supply only and flag incomplete
    result["delta_t_note"] = "Return air temp not collected — delta-T requires return reading"

    # Pressure pattern diagnosis (fault signature)
    result["pressure_diagnosis"] = _diagnose_pressures(
        suction_psig, discharge_psig, ambient_temp_f, refrigerant,
        result.get("superheat_f"), result.get("subcooling_f"), metering
    )

    return result


def _diagnose_pressures(
    suction: float, discharge: float, ambient: float,
    refrigerant: str, sh: Optional[float], sc: Optional[float], metering: str
) -> str:
    """
    Simple rule-based pressure pattern diagnosis using fault_pressure_signatures
    from ac_data_repo.json (R-410A Houston targets).
    Returns a diagnosis string: normal | low_charge | overcharge | dirty_condenser |
    txv_stuck_closed | txv_hunting | dirty_evap | unknown
    """
    # Expected suction range at given ambient (R-410A reference; approximate for others)
    # Lookup from JSON PT table midpoints
    expected = {75: 115, 80: 119, 85: 122, 90: 125, 95: 128, 100: 130, 105: 134}
    keys = sorted(expected.keys())
    exp_suction = expected.get(
        min(keys, key=lambda k: abs(k - ambient)), 128
    )
    suction_delta = suction - exp_suction

    if sh is not None and sh > 15 and suction < exp_suction - 15:
        return "low_charge"
    if sh is not None and sh < 5 and discharge > 440:
        return "overcharge"
    if discharge > 460 and suction >= exp_suction - 5:
        return "dirty_condenser"
    if sh is not None and sh > 20 and suction < exp_suction - 20:
        return "txv_stuck_closed"
    if suction_delta > -10 and suction_delta < 10 and sh is not None and 8 <= sh <= 14:
        return "normal"
    return "unknown"


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class ReadingsRequest(BaseModel):
    suction_psig: float = Field(..., ge=0, le=600, description="Suction pressure in PSIG")
    discharge_psig: float = Field(..., ge=0, le=800, description="Discharge pressure in PSIG")
    ambient_temp_f: float = Field(..., ge=30, le=130, description="Outdoor ambient temp F")
    supply_air_temp_f: float = Field(..., ge=30, le=100, description="Supply air temp F (at vent)")
    # Optional — enables superheat/subcooling auto-calc
    suction_line_temp_f: Optional[float] = Field(None, ge=-20, le=120)
    liquid_line_temp_f: Optional[float] = Field(None, ge=40, le=150)
    refrigerant_type: str = Field("R-410A", pattern="^(R-410A|R-22|R-32|R-454B)$")
    metering_device: str = Field("piston", pattern="^(piston|txv|eev)$")
    gate_triggered: bool = Field(
        True,
        description="Set True when frontend reaches a Phase 2 gate node"
    )


class TriggerRequest(BaseModel):
    gate_triggered: bool = True


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/{assessment_id}/trigger", status_code=status.HTTP_200_OK)
async def trigger_readings_gate(
    assessment_id: str,
    body: TriggerRequest,
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Called by the frontend when tech reaches a Phase 2 gate node.
    Marks readings_gate_triggered=True so the estimate endpoint knows to block.
    """
    result = await db.execute(
        select(Assessment).where(
            Assessment.id == assessment_id,
            Assessment.company_id == auth.company_id,
        )
    )
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    assessment.readings_gate_triggered = body.gate_triggered
    await db.commit()
    return {"assessment_id": assessment_id, "readings_gate_triggered": body.gate_triggered}


@router.put("/{assessment_id}", status_code=status.HTTP_200_OK)
async def save_readings(
    assessment_id: str,
    body: ReadingsRequest,
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Save pressure readings for an assessment and compute superheat/subcooling.

    Required (4 fields — gates the estimate):
      suction_psig, discharge_psig, ambient_temp_f, supply_air_temp_f

    Optional (enable auto-calc):
      suction_line_temp_f  → superheat
      liquid_line_temp_f   → subcooling (TXV/EEV only)
    """
    result = await db.execute(
        select(Assessment).where(
            Assessment.id == assessment_id,
            Assessment.company_id == auth.company_id,
        )
    )
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    # Save the 4 required readings
    assessment.suction_psig = body.suction_psig
    assessment.discharge_psig = body.discharge_psig
    assessment.ambient_temp_f = body.ambient_temp_f
    assessment.supply_air_temp_f = body.supply_air_temp_f
    assessment.refrigerant_type = body.refrigerant_type
    assessment.metering_device = body.metering_device
    assessment.readings_gate_triggered = body.gate_triggered

    # Save optional temps
    assessment.suction_line_temp_f = body.suction_line_temp_f
    assessment.liquid_line_temp_f = body.liquid_line_temp_f

    # Compute derived values
    computed = compute_readings(
        suction_psig=body.suction_psig,
        discharge_psig=body.discharge_psig,
        ambient_temp_f=body.ambient_temp_f,
        supply_air_temp_f=body.supply_air_temp_f,
        suction_line_temp_f=body.suction_line_temp_f,
        liquid_line_temp_f=body.liquid_line_temp_f,
        refrigerant=body.refrigerant_type,
        metering=body.metering_device,
    )

    # Store computed values
    assessment.superheat_f = computed.get("superheat_f")
    assessment.subcooling_f = computed.get("subcooling_f")
    # Mark gate completed — all 4 required fields are now filled
    assessment.readings_completed = True

    await db.commit()

    # ── Pipe readings into XGBoost sensor-diagnosis model (Track A) ─────────
    xgboost_result: dict = {}
    try:
        from services.sensor_service import SensorService
        _svc = SensorService()
        # Derive return_air_temp: use supply + estimated delta-T.
        # Houston baseline: return ~75F, supply ~55-60F for a working system.
        # If supply is known, we approximate return = supply + 20F (typical delta-T).
        return_air_approx = float(body.supply_air_temp_f) + 20.0
        # Derive unit age from assessment equipment data if available
        unit_age = 10.0  # default
        eq = assessment.ai_equipment_id or {}
        if isinstance(eq, dict) and eq.get("install_year"):
            import datetime
            unit_age = float(datetime.datetime.now().year - int(eq["install_year"]))
            unit_age = max(0.5, min(unit_age, 30.0))
        pred = _svc.predict(
            outdoor_ambient_temp=float(body.ambient_temp_f),
            supply_air_temp=float(body.supply_air_temp_f),
            return_air_temp=return_air_approx,
            suction_pressure=float(body.suction_psig),
            discharge_pressure=float(body.discharge_psig),
            unit_age_years=unit_age,
        )
        xgboost_result = {
            "fault_label": pred.fault_label,
            "confidence": round(pred.confidence, 3),
            "high_confidence": pred.high_confidence,
        }
    except Exception as _xgb_err:
        # Non-fatal: XGBoost unavailable (model not yet downloaded, etc.)
        xgboost_result = {"error": str(_xgb_err), "fault_label": None}

    return {
        "assessment_id": assessment_id,
        "readings_saved": True,
        "readings_completed": True,
        "computed": computed,
        "xgboost_diagnosis": xgboost_result,
    }


@router.get("/{assessment_id}/targets", status_code=status.HTTP_200_OK)
async def get_readings_targets(
    assessment_id: str,
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Return the expected PT targets for this assessment based on:
    - refrigerant_type (from Step Zero OCR or readings)
    - ambient_temp_f (from readings or Houston summer default 95F)

    Helps the tech know what pressures they should be seeing on a healthy system.
    """
    result = await db.execute(
        select(Assessment).where(
            Assessment.id == assessment_id,
            Assessment.company_id == auth.company_id,
        )
    )
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    ref = assessment.refrigerant_type or "R-410A"
    ambient = float(assessment.ambient_temp_f or 95)
    metering = assessment.metering_device or "piston"

    pt = _PT_TABLES.get(ref, _PT_TABLES["R-410A"])

    # R-410A operating targets by ambient (from ac_data_repo.json)
    _R410A_OP = {
        75:  {"suction": (108, 122), "discharge": (325, 365)},
        80:  {"suction": (112, 126), "discharge": (345, 385)},
        85:  {"suction": (115, 128), "discharge": (360, 400)},
        90:  {"suction": (118, 132), "discharge": (378, 418)},
        95:  {"suction": (120, 135), "discharge": (395, 440)},
        100: {"suction": (122, 138), "discharge": (415, 460)},
        105: {"suction": (125, 142), "discharge": (430, 480)},
    }
    op_keys = sorted(_R410A_OP.keys())
    nearest_amb = min(op_keys, key=lambda k: abs(k - ambient))
    op_target = _R410A_OP.get(nearest_amb, _R410A_OP[95])

    sh_target = _SUPERHEAT_TARGETS.get(ref, {}).get(metering, (8, 14, 10))
    sc_target = _SUBCOOLING_TARGETS.get(ref, {}).get(metering)

    return {
        "refrigerant": ref,
        "metering_device": metering,
        "ambient_temp_f": ambient,
        "expected_suction_psig": {
            "min": op_target["suction"][0],
            "max": op_target["suction"][1],
        },
        "expected_discharge_psig": {
            "min": op_target["discharge"][0],
            "max": op_target["discharge"][1],
        },
        "superheat_target": {
            "min": sh_target[0], "max": sh_target[1], "ideal": sh_target[2]
        },
        "subcooling_target": (
            {"min": sc_target[0], "max": sc_target[1], "ideal": sc_target[2]}
            if sc_target else None
        ),
        "houston_note": (
            "R-410A targets shown for R-32/R-454B ambient — use manufacturer specs for precise values"
            if ref in ("R-32", "R-454B") else None
        ),
    }
