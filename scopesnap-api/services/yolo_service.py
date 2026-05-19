"""
SnapAI — YOLO Visual Detection Service
Wraps Corrosion v4 and Multi-class v1 YOLO models via ONNX Runtime.

ONNX Runtime replaces ultralytics/PyTorch for inference:
  - onnxruntime ~50MB vs PyTorch ~2GB — fits Railway Hobby build
  - Same model weights, same accuracy (lossless export)
  - Models: best_corrosion_v4.onnx + scopesnap_multiclass_v1.onnx
  - Exported once via: scripts/export_to_onnx.py (run on Modal)

Corrosion v4:   85% mAP50 — binary (corrosion only)     | threshold: 0.75
Multi-class v1: ~50% mAP50 — 8 HVAC classes (synthetic) | threshold: 0.80
"""
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional
from io import BytesIO
import numpy as np

MODELS_DIR = Path(__file__).parent.parent / "models"
CORROSION_THRESHOLD = 0.75
MULTICLASS_THRESHOLD = 0.80

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

INPUT_SIZE = 640  # YOLOv8 default inference size


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
        return bool(self.corrosion or self.multiclass)

    @property
    def best_detection(self) -> Optional[Detection]:
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


def _preprocess(image_bytes: bytes) -> tuple:
    """
    Resize image to 640x640, normalise to [0,1], return (tensor, scale_x, scale_y).
    Returns NCHW float32 array for ONNX Runtime.
    """
    from PIL import Image
    img = Image.open(BytesIO(image_bytes)).convert("RGB")
    orig_w, orig_h = img.size
    img_resized = img.resize((INPUT_SIZE, INPUT_SIZE))
    arr = np.array(img_resized, dtype=np.float32) / 255.0  # HWC
    arr = arr.transpose(2, 0, 1)                            # CHW
    arr = np.expand_dims(arr, 0)                            # NCHW
    scale_x = orig_w / INPUT_SIZE
    scale_y = orig_h / INPUT_SIZE
    return arr, scale_x, scale_y


def _parse_yolov8_output(output: np.ndarray, class_names: List[str],
                          threshold: float, scale_x: float, scale_y: float) -> List[Detection]:
    """
    Parse YOLOv8 ONNX output tensor [1, num_classes+4, num_anchors].
    YOLOv8 exports predictions as [x_center, y_center, w, h, cls0, cls1, ...].
    """
    preds = output[0]           # (num_classes+4, num_anchors)
    preds = preds.T             # (num_anchors, num_classes+4)

    detections = []
    for row in preds:
        box = row[:4]           # cx, cy, w, h
        scores = row[4:]        # class probabilities
        best_cls = int(np.argmax(scores))
        best_conf = float(scores[best_cls])

        if best_conf < threshold:
            continue

        cx, cy, w, h = box
        x1 = (cx - w / 2) * scale_x
        y1 = (cy - h / 2) * scale_y
        x2 = (cx + w / 2) * scale_x
        y2 = (cy + h / 2) * scale_y

        label = class_names[best_cls] if best_cls < len(class_names) else f"class_{best_cls}"
        detections.append(Detection(label=label, confidence=best_conf, bbox=[x1, y1, x2, y2]))

    # NMS — keep highest-confidence non-overlapping boxes
    detections.sort(key=lambda d: d.confidence, reverse=True)
    kept = []
    for det in detections:
        overlap = any(_iou(det.bbox, k.bbox) > 0.5 for k in kept)
        if not overlap:
            kept.append(det)
    return kept


def _iou(a: list, b: list) -> float:
    """Intersection over Union for two [x1,y1,x2,y2] boxes."""
    ix1 = max(a[0], b[0]); iy1 = max(a[1], b[1])
    ix2 = min(a[2], b[2]); iy2 = min(a[3], b[3])
    inter = max(0, ix2 - ix1) * max(0, iy2 - iy1)
    area_a = (a[2]-a[0]) * (a[3]-a[1])
    area_b = (b[2]-b[0]) * (b[3]-b[1])
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


class YOLOService:
    """
    Singleton YOLO inference via ONNX Runtime.
    Loaded once at startup, reused for all requests.

    ONNX model files are downloaded from R2 by scripts/download_models.py
    at container startup. If not present, falls back to Gemini gracefully.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._loaded = False
            cls._instance._corrosion_session = None
            cls._instance._multiclass_session = None
        return cls._instance

    def _load_models(self):
        if self._loaded:
            return
        try:
            import onnxruntime as ort
        except ImportError:
            raise ImportError(
                "onnxruntime not installed. Add onnxruntime to requirements.txt."
            )

        corr_path  = MODELS_DIR / "best_corrosion_v4.onnx"
        multi_path = MODELS_DIR / "scopesnap_multiclass_v1.onnx"

        if not corr_path.exists():
            raise FileNotFoundError(
                f"Corrosion ONNX model not found: {corr_path}\n"
                "Run scripts/export_to_onnx.py on Modal to generate it, "
                "then upload to R2 — download_models.py will pull it on startup."
            )
        if not multi_path.exists():
            raise FileNotFoundError(
                f"Multi-class ONNX model not found: {multi_path}\n"
                "Same process — export via Modal, upload to R2."
            )

        opts = ort.SessionOptions()
        opts.inter_op_num_threads = 2
        opts.intra_op_num_threads = 2
        providers = ["CPUExecutionProvider"]

        self._corrosion_session  = ort.InferenceSession(str(corr_path),  sess_options=opts, providers=providers)
        self._multiclass_session = ort.InferenceSession(str(multi_path), sess_options=opts, providers=providers)
        self._loaded = True
        print("[YOLOService] ✅ ONNX Runtime — Corrosion v4 + Multi-class v1 loaded")

    def detect(self, image_bytes: bytes) -> YOLOResult:
        self._load_models()
        tensor, sx, sy = _preprocess(image_bytes)

        corr_input  = self._corrosion_session.get_inputs()[0].name
        multi_input = self._multiclass_session.get_inputs()[0].name

        corr_out  = self._corrosion_session.run(None,  {corr_input:  tensor})[0]
        multi_out = self._multiclass_session.run(None, {multi_input: tensor})[0]

        corrosion_dets  = _parse_yolov8_output(corr_out,  ["corrosion"], CORROSION_THRESHOLD, sx, sy)
        multiclass_dets = _parse_yolov8_output(multi_out, HVAC_FAULT_CLASSES, MULTICLASS_THRESHOLD, sx, sy)

        return YOLOResult(corrosion=corrosion_dets, multiclass=multiclass_dets)

    def is_available(self) -> bool:
        """Check if ONNX model files exist — used by cascade to decide track."""
        corr_path  = MODELS_DIR / "best_corrosion_v4.onnx"
        multi_path = MODELS_DIR / "scopesnap_multiclass_v1.onnx"
        return corr_path.exists() and multi_path.exists()
