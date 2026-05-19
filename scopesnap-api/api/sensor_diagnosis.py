"""
SnapAI — Standalone Sensor Diagnosis API Endpoint
POST /api/sensor-diagnosis — returns fault diagnosis from field sensor readings.

No photo required. Runs XGBoost in < 1ms. 90.09% accuracy.
Used by technicians who have sensor readings but no photo yet.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from services.sensor_service import SensorService

router = APIRouter(prefix="/api/sensor-diagnosis", tags=["sensor-diagnosis"])

# Lazy-load singleton (loaded on first request, cached after)
_sensor_svc: Optional[SensorService] = None


def get_sensor_service() -> SensorService:
    global _sensor_svc
    if _sensor_svc is None:
        _sensor_svc = SensorService()
    return _sensor_svc


# Per-fault technician recommendations
FAULT_RECOMMENDATIONS = {
    "refrigerant_undercharge": (
        "Check refrigerant charge. Suction pressure is low — likely a slow leak. "
        "Inspect service valves, fittings, and evaporator coil for signs of oil staining."
    ),
    "refrigerant_overcharge": (
        "Reduce refrigerant charge. Discharge pressure is elevated — risk of compressor damage. "
        "Recover refrigerant and recharge to manufacturer spec."
    ),
    "dirty_condenser_coil": (
        "Clean condenser coil. Discharge pressure and ambient temperature differential indicate "
        "restricted airflow through the coil. Use coil cleaner and rinse thoroughly."
    ),
    "dirty_evaporator_coil": (
        "Clean evaporator coil. Supply air temperature is higher than expected — "
        "coil surface may be fouled with dirt or mold. Check drain pan too."
    ),
    "low_airflow_dirty_filter": (
        "Replace or clean air filter immediately. Return-to-supply temperature differential "
        "indicates restricted airflow. Check all supply and return registers are open."
    ),
    "compressor_inefficiency": (
        "Inspect compressor. Pressure ratio is low — compressor may have internal valve wear. "
        "Check amp draw and compare to nameplate. Consider replacement if out of spec."
    ),
    "faulty_condenser_fan": (
        "Inspect condenser fan motor and blade. High discharge pressure with normal ambient temp "
        "suggests inadequate condenser airflow. Check capacitor, fan blade pitch, and motor."
    ),
    "normal": (
        "System readings are within normal operating parameters. No fault detected. "
        "Perform standard preventive maintenance and document readings."
    ),
}


class SensorDiagnosisRequest(BaseModel):
    outdoor_ambient_temp: float = Field(..., description="Outdoor ambient temperature (°F)")
    supply_air_temp: float = Field(..., description="Supply air temperature (°F)")
    return_air_temp: float = Field(..., description="Return air temperature (°F)")
    suction_pressure: float = Field(..., description="Suction pressure (PSI)")
    discharge_pressure: float = Field(..., description="Discharge pressure (PSI)")
    unit_age_years: float = Field(..., description="Unit age in years")


class SensorDiagnosisResponse(BaseModel):
    fault_label: str
    confidence: float
    high_confidence: bool
    all_probabilities: dict
    recommendation: str
    track: str = "A"
    method: str = "sensor_only"


@router.post("/", response_model=SensorDiagnosisResponse)
def diagnose_from_sensor(req: SensorDiagnosisRequest):
    """
    Diagnose HVAC fault from sensor readings alone.

    - Uses XGBoost model trained on 90.09% accuracy
    - Returns fault label, confidence, and technician recommendation
    - Runs in < 1ms — zero API cost
    - Track A of the Dual-Track Cascade

    Example request:
    {
        "outdoor_ambient_temp": 95.0,
        "supply_air_temp": 58.0,
        "return_air_temp": 75.0,
        "suction_pressure": 58.0,
        "discharge_pressure": 260.0,
        "unit_age_years": 8.0
    }
    """
    try:
        svc = get_sensor_service()
        result = svc.predict(
            outdoor_ambient_temp=req.outdoor_ambient_temp,
            supply_air_temp=req.supply_air_temp,
            return_air_temp=req.return_air_temp,
            suction_pressure=req.suction_pressure,
            discharge_pressure=req.discharge_pressure,
            unit_age_years=req.unit_age_years,
        )
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Sensor model not loaded: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Sensor diagnosis failed: {str(e)}"
        )

    recommendation = FAULT_RECOMMENDATIONS.get(
        result.fault_label,
        "Perform a full manual inspection. Consult manufacturer specs."
    )

    return SensorDiagnosisResponse(
        fault_label=result.fault_label,
        confidence=result.confidence,
        high_confidence=result.high_confidence,
        all_probabilities=result.all_probabilities,
        recommendation=recommendation,
    )
