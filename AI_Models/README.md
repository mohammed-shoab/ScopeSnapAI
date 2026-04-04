# SnapAI AI Models — What's In This Folder

## ✅ DONE — Sensor Fault Detection Model (Numbers/Readings Feature)

These files are **trained and ready to deploy** into your FastAPI backend today:

| File | What it is |
|------|-----------|
| `scopesnap_sensor_model.pkl` | The trained XGBoost model (6.6 MB) — **90.09% accuracy** |
| `scopesnap_label_encoder.pkl` | Converts numbers back to fault names like "refrigerant_undercharge" |
| `sensor_model_metadata.json` | Model stats: accuracy, F1, features, classes |
| `train_sensor_model.py` | The Python script that trained it (re-run anytime to retrain) |
| `generate_sensor_data.py` | The script that generated 22,000 synthetic training rows |

**What it detects from 6 field readings:**
1. Normal (no fault)
2. Refrigerant Undercharge
3. Refrigerant Overcharge
4. Dirty Condenser Coil
5. Dirty Evaporator Coil
6. Low Airflow / Dirty Filter
7. Compressor Inefficiency
8. Faulty Condenser Fan

**To deploy:** Copy `scopesnap_sensor_model.pkl` and `scopesnap_label_encoder.pkl`
into your FastAPI backend's models folder. The API endpoint is `POST /api/sensor-diagnosis`.
Full integration code is in Section 10 of `AC_Defect_Detection_AI_Guide_Updated.docx`.

---

## 🚀 NEXT STEP — YOLO Visual Defect Model (Photo Feature)

| File | What it is |
|------|-----------|
| `SnapAI_YOLO_Training.ipynb` | Google Colab notebook — open this on Colab to train |
| `scopesnap_yolo_dataset.zip` | 1,280 synthetic training images (starter dataset) |

**To train YOLO (free, ~90 minutes):**

1. Go to **roboflow.com** → sign up free with ds.shoab@gmail.com
2. Get your free API key from Settings → API
3. Go to **colab.research.google.com** → upload `SnapAI_YOLO_Training.ipynb`
4. Runtime → Change runtime type → **T4 GPU** (free)
5. Run all cells — enter your Roboflow API key when Cell 3 asks
6. The notebook downloads real public datasets, merges them with your synthetic data,
   trains YOLOv8, and exports `scopesnap_yolo.onnx` (~10-15 MB)
7. Download `scopesnap_yolo.onnx` to this folder when done

**Expected accuracy:**
- With synthetic + public data: ~75-80%
- After 500+ real Mike photos added: ~90-95%

---

## Performance Summary

| Model | Accuracy | Training Time | Cost | Where it runs |
|-------|----------|--------------|------|---------------|
| Sensor (XGBoost) | **90.09%** | 2.2 seconds | Free forever | FastAPI backend |
| YOLO (after Colab) | ~75-80% | ~90 min on Colab | Free forever | On-device (ONNX) |
| Gemini 2.5 Flash | ~90-95% | — | ~$0.01/photo | Google Cloud |
