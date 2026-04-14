"""
SnapAI — XGBoost Sensor Fault Detection Service
Wraps the trained sensor model for use in the AI cascade.

Model: XGBoostClassifier — 400 estimators, max depth 7
Accuracy: 90.09%  |  F1: 90.06%  |  5-fold CV: 89.88% ± 0.53%
Speed: < 1ms per inference (CPU only, no GPU needed)
"""
import joblib
import numpy as np
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

MODELS_DIR = Path(__file__).parent.parent / "models"
SENSOR_THRESHOLD = 0.85  # confidence >= this = HIGH CONFIDENCE on Track A

# 8 fault classes
FAULT_CLASSES = [
    "normal",
    "refrigerant_undercharge",
    "refrigerant_overcharge",
    "dirty_condenser_coil",
    "dirty_evaporator_coil",
    "low_airflow_dirty_filter",
    "compressor_inefficiency",
    "faulty_condenser_fan",
]


@dataclass
class SensorResult:
    fault_label: str
    confidence: float
    high_confidence: bool
    all_probabilities: dict


class SensorService:
    """
    Singleton wrapper around the XGBoost sensor fault detection model.
    Loaded once at startup, reused for all requests.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._loaded = False
        return cls._instance

    def _load_models(self):
        if self._loaded:
            return
        model_path = MODELS_DIR / "scopesnap_sensor_model.pkl"
        encoder_path = MODELS_DIR / "scopesnap_label_encoder.pkl"

        if not model_path.exists():
            raise FileNotFoundError(
                f"Sensor model not found: {model_path}\n"
                "Copy scopesnap_sensor_model.pkl from AI_Models/ to scopesnap-api/models/"
            )
        if not encoder_path.exists():
            raise FileNotFoundError(
                f"Label encoder not found: {encoder_path}\n"
                "Copy scopesnap_label_encoder.pkl from AI_Models/ to scopesnap-api/models/"
            )

        self.model = joblib.load(model_path)
        self.encoder = joblib.load(encoder_path)
        self._loaded = True
        print("[SensorService] ✅ XGBoost sensor model loaded (90.09% accuracy)")

    def predict(
        self,
        outdoor_ambient_temp: float,  # °F
        supply_air_temp: float,        # °F
        return_air_temp: float,        # °F
        suction_pressure: float,       # PSI
        discharge_pressure: float,     # PSI
        unit_age_years: float,         # years
    ) -> SensorResult:
        """
        Run XGBoost inference on 6 raw sensor readings.
        Automatically computes 4 derived features (same as training).
        Returns fault label + confidence.
        """
        self._load_models()

        # 6 raw features
        raw = [
            outdoor_ambient_temp,
            supply_air_temp,
            return_air_temp,
            suction_pressure,
            discharge_pressure,
            unit_age_years,
        ]

        # 4 auto-derived features (must match training script exactly)
        supply_to_outdoor_delta = outdoor_ambient_temp - supply_air_temp
        return_supply_delta = return_air_temp - supply_air_temp
        pressure_ratio = discharge_pressure / (suction_pressure + 1e-6)  # avoid div/0
        superheat_proxy = suction_pressure * 0.1 - supply_air_temp

        features = raw + [
            supply_to_outdoor_delta,
            return_supply_delta,
            pressure_ratio,
            superheat_proxy,
        ]

        X = np.array([features])
        proba = self.model.predict_proba(X)[0]  # shape: (n_classes,)

        # Map probabilities to fault labels via encoder
        try:
            labels = list(self.encoder.classes_)
        except AttributeError:
            labels = FAULT_CLASSES

        all_probs = dict(zip(labels, [round(float(p), 4) for p in proba]))
        best_idx = int(np.argmax(proba))
        fault_label = labels[best_idx]
        confidence = float(proba[best_idx])

        return SensorResult(
            fault_label=fault_label,
            confidence=confidence,
            high_confidence=confidence >= SENSOR_THRESHOLD,
            all_probabilities=all_probs,
        )
