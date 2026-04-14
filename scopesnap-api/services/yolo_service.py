"""
SnapAI — YOLO Visual Detection Service
Wraps Corrosion v4 and Multi-class v1 YOLO models.

Corrosion v4:   85% mAP50 — binary (corrosion only)     | threshold: 0.75
Multi-class v1: ~50% mAP50 — 8 HVAC classes (synthetic) | threshold: 0.80
"""
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional
from io import BytesIO

MODELS_DIR = Path(__file__).parent.parent / "models"
CORROSION_THRESHOLD = 0.75   # Confirmed 85% mAP50 — tight threshold suppresses false positives
MULTICLASS_THRESHOLD = 0.80  # Only trust high-confidence detections (50% mAP50 synthetic data)

# 8 HVAC fault classes for multi-class model
HVAC_FAULT_CLASSES = [
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
class Detection:
    label: str
    confidence: float
    bbox: list  # [x1, y1, x2, y2] in pixels


@dataclass
class YOLOResult:
    corrosion: List[Detection] = field(default_factory=list)
    multiclass: List[Detection] = field(default_factory=list)

    @property
    def has_high_confidence(self) -> bool:
        """True if any model made a detection above its threshold."""
        return bool(self.corrosion or self.multiclass)

    @property
    def best_detection(self) -> Optional[Detection]:
        """Returns the single highest-confidence detection across both models."""
        all_det = self.corrosion + self.multiclass
        return max(all_det, key=lambda d: d.confidence) if all_det else None

    def to_dict(self) -> dict:
        return {
            "corrosion": [
                {"label": d.label, "confidence": d.confidence, "bbox": d.bbox}
                for d in self.corrosion
            ],
            "multiclass": [
                {"label": d.label, "confidence": d.confidence, "bbox": d.bbox}
                for d in self.multiclass
            ],
        }


class YOLOService:
    """
    Singleton wrapper around both YOLO models.
    Loaded once at startup, reused for all requests.

    NOTE: Requires best_corrosion_v4.pt and scopesnap_multiclass_v1.pt
    in scopesnap-api/models/ (download from Google Drive — too large for git).
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
        try:
            from ultralytics import YOLO
        except ImportError:
            raise ImportError(
                "ultralytics not installed. Run: pip install ultralytics"
            )

        corr_path = MODELS_DIR / "best_corrosion_v4.pt"
        multi_path = MODELS_DIR / "scopesnap_multiclass_v1.pt"

        if not corr_path.exists():
            raise FileNotFoundError(
                f"Corrosion model not found: {corr_path}\n"
                "Download best_corrosion_v4.pt from Google Drive → MyDrive/ScopeSnapAI/"
            )
        if not multi_path.exists():
            raise FileNotFoundError(
                f"Multi-class model not found: {multi_path}\n"
                "Download from Google Drive → Backups/2026-04-03_0256/best_corrosion_v2__synthetic_data.pt"
                " and rename to scopesnap_multiclass_v1.pt"
            )

        self.corrosion_model = YOLO(str(corr_path))
        self.multiclass_model = YOLO(str(multi_path))
        self._loaded = True
        print("[YOLOService] ✅ Corrosion v4 (85% mAP50) + Multi-class v1 loaded")

    def detect(self, image_bytes: bytes) -> YOLOResult:
        """
        Run both YOLO models in parallel on the image.
        Returns detections above their respective confidence thresholds.
        """
        self._load_models()

        from PIL import Image
        img = Image.open(BytesIO(image_bytes)).convert("RGB")

        corrosion_dets = self._run_corrosion(img)
        multiclass_dets = self._run_multiclass(img)

        return YOLOResult(corrosion=corrosion_dets, multiclass=multiclass_dets)

    def _run_corrosion(self, img) -> List[Detection]:
        results = self.corrosion_model(img, verbose=False)
        detections = []
        for r in results:
            for box in r.boxes:
                conf = float(box.conf[0])
                if conf >= CORROSION_THRESHOLD:
                    cls_idx = int(box.cls[0])
                    label = self.corrosion_model.names.get(cls_idx, "corrosion")
                    x1, y1, x2, y2 = [float(v) for v in box.xyxy[0]]
                    detections.append(Detection(
                        label=label,
                        confidence=conf,
                        bbox=[x1, y1, x2, y2],
                    ))
        return detections

    def _run_multiclass(self, img) -> List[Detection]:
        results = self.multiclass_model(img, verbose=False)
        detections = []
        for r in results:
            for box in r.boxes:
                conf = float(box.conf[0])
                if conf >= MULTICLASS_THRESHOLD:
                    cls_idx = int(box.cls[0])
                    label = self.multiclass_model.names.get(cls_idx, f"fault_{cls_idx}")
                    x1, y1, x2, y2 = [float(v) for v in box.xyxy[0]]
                    detections.append(Detection(
                        label=label,
                        confidence=conf,
                        bbox=[x1, y1, x2, y2],
                    ))
        return detections

    def is_available(self) -> bool:
        """Check if YOLO models are available without loading them."""
        corr_path = MODELS_DIR / "best_corrosion_v4.pt"
        multi_path = MODELS_DIR / "scopesnap_multiclass_v1.pt"
        return corr_path.exists() and multi_path.exists()
