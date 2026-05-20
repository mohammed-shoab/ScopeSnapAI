"""
Trains the SnapAI Sensor Fault Detection Model.
XGBoost classifier on HVAC operating data.
No GPU required — trains in minutes on CPU.
"""

import pandas as pd
import numpy as np
import joblib, json, time
from pathlib import Path
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (classification_report, confusion_matrix,
                             accuracy_score, f1_score)
from xgboost import XGBClassifier

BASE   = Path("/sessions/affectionate-bold-johnson/scopesnap_ai")
DATA   = BASE / "sensor_data/hvac_sensor_training_data.csv"
MODELS = BASE / "models"
MODELS.mkdir(exist_ok=True)

FEATURES = [
    "outdoor_ambient_temp",
    "supply_air_temp",
    "return_air_temp",
    "suction_pressure",
    "discharge_pressure",
    "unit_age_years",
]

print("=" * 60)
print("SnapAI Sensor Fault Detection Model — Training")
print("=" * 60)

# ── Load data ─────────────────────────────────────────────
df = pd.read_csv(DATA)
print(f"\n✓ Loaded {len(df):,} rows from training CSV")

X = df[FEATURES].values
le = LabelEncoder()
y = le.fit_transform(df["fault_label"])
class_names = list(le.classes_)
print(f"✓ Classes ({len(class_names)}): {class_names}")

# ── Feature engineering ───────────────────────────────────
# Add derived features that improve accuracy
supply_to_outdoor_delta = df["outdoor_ambient_temp"] - df["supply_air_temp"]
return_supply_delta      = df["return_air_temp"] - df["supply_air_temp"]
pressure_ratio           = df["discharge_pressure"] / (df["suction_pressure"] + 1)
superheat_proxy          = df["suction_pressure"] * 0.1 - df["supply_air_temp"]

X_eng = np.column_stack([
    X,
    supply_to_outdoor_delta,
    return_supply_delta,
    pressure_ratio,
    superheat_proxy,
])

FEATURE_NAMES = FEATURES + [
    "supply_to_outdoor_delta",
    "return_supply_delta",
    "pressure_ratio",
    "superheat_proxy",
]

print(f"✓ Feature engineering: {len(FEATURE_NAMES)} features total")

# ── Train/test split ──────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X_eng, y, test_size=0.20, random_state=42, stratify=y
)
print(f"✓ Split: {len(X_train):,} train / {len(X_test):,} test")

# ── Train XGBoost ─────────────────────────────────────────
print("\n⏳ Training XGBoost classifier...")
t0 = time.time()

model = XGBClassifier(
    n_estimators=400,
    max_depth=7,
    learning_rate=0.05,
    subsample=0.85,
    colsample_bytree=0.85,
    min_child_weight=3,
    gamma=0.1,
    reg_alpha=0.1,
    reg_lambda=1.5,
    use_label_encoder=False,
    eval_metric="mlogloss",
    random_state=42,
    n_jobs=-1,
)

model.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    verbose=False,
)

elapsed = time.time() - t0
print(f"✓ Training complete in {elapsed:.1f} seconds")

# ── Evaluate ──────────────────────────────────────────────
y_pred = model.predict(X_test)
acc    = accuracy_score(y_test, y_pred)
f1     = f1_score(y_test, y_pred, average="weighted")

print(f"\n{'='*60}")
print(f"MODEL PERFORMANCE ON HELD-OUT TEST SET")
print(f"{'='*60}")
print(f"Overall Accuracy : {acc*100:.2f}%")
print(f"Weighted F1-Score: {f1*100:.2f}%")
print(f"\nPer-Class Report:")
print(classification_report(y_test, y_pred, target_names=class_names, digits=3))

# ── Cross-validation ──────────────────────────────────────
print("Running 5-fold cross-validation for confidence estimate...")
cv_scores = cross_val_score(model, X_eng, y,
                             cv=StratifiedKFold(5, shuffle=True, random_state=42),
                             scoring="accuracy", n_jobs=-1)
print(f"CV Accuracy: {cv_scores.mean()*100:.2f}% ± {cv_scores.std()*100:.2f}%")

# ── Feature importance ────────────────────────────────────
print(f"\nTop Feature Importances:")
importances = model.feature_importances_
sorted_idx = np.argsort(importances)[::-1]
for i in sorted_idx[:8]:
    bar = "█" * int(importances[i] * 200)
    print(f"  {FEATURE_NAMES[i]:30s} {importances[i]:.4f}  {bar}")

# ── Save model ────────────────────────────────────────────
model_path   = MODELS / "scopesnap_sensor_model.pkl"
encoder_path = MODELS / "scopesnap_label_encoder.pkl"
meta_path    = MODELS / "sensor_model_metadata.json"

joblib.dump(model, model_path)
joblib.dump(le, encoder_path)

metadata = {
    "model_type": "XGBoostClassifier",
    "version": "1.0",
    "trained": "March 2026",
    "accuracy": round(acc * 100, 2),
    "f1_score": round(f1 * 100, 2),
    "cv_accuracy_mean": round(cv_scores.mean() * 100, 2),
    "cv_accuracy_std":  round(cv_scores.std()  * 100, 2),
    "n_training_samples": len(X_train),
    "n_test_samples": len(X_test),
    "features": FEATURE_NAMES,
    "classes": class_names,
    "n_classes": len(class_names),
    "hyperparameters": {
        "n_estimators": 400,
        "max_depth": 7,
        "learning_rate": 0.05,
    },
    "usage": {
        "input": "6 field readings from tech + 4 derived features (auto-computed)",
        "output": "fault_label + probability score",
        "endpoint": "POST /api/sensor-diagnosis",
    }
}

with open(meta_path, "w") as f:
    json.dump(metadata, f, indent=2)

print(f"\n{'='*60}")
print(f"✅ MODEL SAVED SUCCESSFULLY")
print(f"{'='*60}")
print(f"  Model:    {model_path}")
print(f"  Encoder:  {encoder_path}")
print(f"  Metadata: {meta_path}")
print(f"\n  File sizes:")
print(f"  {model_path.name}:   {model_path.stat().st_size // 1024} KB")
print(f"  {encoder_path.name}: {encoder_path.stat().st_size // 1024} KB")

# ── Quick inference test ──────────────────────────────────
print(f"\n{'='*60}")
print("QUICK INFERENCE TEST — 3 Example Diagnoses")
print(f"{'='*60}")

test_cases = [
    {
        "name": "Mike's first job — Unit running warm",
        "readings": [95, 73, 82, 42, 228],  # low suction = refrigerant leak
        "age": 8,
    },
    {
        "name": "Service call — No cooling on hot day",
        "readings": [98, 81, 87, 70, 385],  # high discharge = dirty condenser
        "age": 11,
    },
    {
        "name": "Routine maintenance check",
        "readings": [82, 62, 78, 68, 272],  # normal range
        "age": 4,
    },
]

for tc in test_cases:
    vals = tc["readings"]
    age  = tc["age"]
    # Compute derived features
    supply_to_outdoor = vals[0] - vals[1]
    return_supply     = vals[2] - vals[1]
    pressure_ratio    = vals[4] / (vals[3] + 1)
    superheat_proxy   = vals[3] * 0.1 - vals[1]
    row = np.array([[*vals, age, supply_to_outdoor, return_supply,
                      pressure_ratio, superheat_proxy]])
    pred_class = le.inverse_transform(model.predict(row))[0]
    probs = model.predict_proba(row)[0]
    confidence = max(probs) * 100

    print(f"\n  Scenario: {tc['name']}")
    print(f"  Outdoor: {vals[0]}°F | Supply: {vals[1]}°F | Return: {vals[2]}°F")
    print(f"  Suction: {vals[3]} psi | Discharge: {vals[4]} psi | Age: {age} yrs")
    print(f"  ➤ Diagnosis: {pred_class.upper().replace('_', ' ')} ({confidence:.1f}% confident)")
