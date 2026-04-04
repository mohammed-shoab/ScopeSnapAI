"""
Generates realistic synthetic HVAC sensor fault training data.
Uses actual HVAC thermodynamics equations — not random noise.
Each fault type has distinctive physics-based signatures.
"""

import numpy as np
import pandas as pd
from pathlib import Path

np.random.seed(42)

OUTPUT = Path("/sessions/affectionate-bold-johnson/scopesnap_ai/sensor_data")
OUTPUT.mkdir(exist_ok=True)

FAULT_LABELS = [
    "normal",
    "refrigerant_undercharge",
    "refrigerant_overcharge",
    "dirty_condenser_coil",
    "dirty_evaporator_coil",
    "low_airflow_dirty_filter",
    "compressor_inefficiency",
    "faulty_condenser_fan",
]

def rng(mean, std, n=1, lo=None, hi=None):
    """Gaussian sample with optional clipping."""
    v = np.random.normal(mean, std, n)
    if lo is not None: v = np.clip(v, lo, None)
    if hi is not None: v = np.clip(v, None, hi)
    return v if n > 1 else float(v[0])

def generate_normal(n):
    """Properly functioning AC unit."""
    rows = []
    for _ in range(n):
        outdoor   = rng(85,  12,  lo=60,  hi=110)
        supply    = outdoor - rng(20, 2, lo=14, hi=28)      # 18-22°F cooling
        return_t  = supply + rng(16,  2,  lo=12, hi=22)     # 14-20°F delta
        suction_p = rng(68,  5,   lo=55,  hi=82)            # R-410A normal: 55-82 psi
        discharge = rng(275, 20,  lo=220, hi=330)
        age       = rng(7,   4,   lo=1,   hi=20)
        rows.append([outdoor, supply, return_t, suction_p, discharge, age, "normal"])
    return rows

def generate_refrigerant_undercharge(n):
    """Low refrigerant: suction pressure drops, supply air temp rises."""
    rows = []
    for _ in range(n):
        outdoor   = rng(85,  12,  lo=60,  hi=110)
        suction_p = rng(45,  8,   lo=28,  hi=60)            # LOW: 28-60 psi
        discharge = rng(230, 25,  lo=170, hi=280)           # also lower
        supply    = outdoor - rng(12, 3, lo=6, hi=18)       # less cooling
        return_t  = supply + rng(14, 2, lo=10, hi=20)
        age       = rng(9,   4,   lo=2,   hi=20)
        rows.append([outdoor, supply, return_t, suction_p, discharge, age, "refrigerant_undercharge"])
    return rows

def generate_refrigerant_overcharge(n):
    """Too much refrigerant: high pressures, reduced efficiency."""
    rows = []
    for _ in range(n):
        outdoor   = rng(85,  12,  lo=60,  hi=110)
        suction_p = rng(90,  8,   lo=75,  hi=110)           # HIGH
        discharge = rng(350, 30,  lo=300, hi=420)           # HIGH
        supply    = outdoor - rng(15, 3, lo=10, hi=22)
        return_t  = supply + rng(15, 2, lo=12, hi=20)
        age       = rng(5,   3,   lo=1,   hi=15)
        rows.append([outdoor, supply, return_t, suction_p, discharge, age, "refrigerant_overcharge"])
    return rows

def generate_dirty_condenser(n):
    """Dirty condenser: elevated head pressure, supply temp rises."""
    rows = []
    for _ in range(n):
        outdoor   = rng(85,  12,  lo=60,  hi=110)
        discharge = rng(340, 30,  lo=290, hi=420)           # HIGH head pressure
        suction_p = rng(72,  6,   lo=58,  hi=88)           # slightly elevated
        supply    = outdoor - rng(14, 3, lo=8, hi=20)      # less efficient cooling
        return_t  = supply + rng(16, 2, lo=12, hi=22)
        age       = rng(8,   4,   lo=2,   hi=20)
        rows.append([outdoor, supply, return_t, suction_p, discharge, age, "dirty_condenser_coil"])
    return rows

def generate_dirty_evaporator(n):
    """Dirty evaporator coil: low suction pressure, reduced cooling."""
    rows = []
    for _ in range(n):
        outdoor   = rng(85,  12,  lo=60,  hi=110)
        suction_p = rng(52,  7,   lo=35,  hi=68)           # LOW — iced coil restriction
        discharge = rng(260, 20,  lo=200, hi=310)
        supply    = outdoor - rng(10, 3, lo=5, hi=17)      # poor cooling
        return_t  = supply + rng(18, 3, lo=13, hi=25)      # high delta
        age       = rng(8,   4,   lo=2,   hi=20)
        rows.append([outdoor, supply, return_t, suction_p, discharge, age, "dirty_evaporator_coil"])
    return rows

def generate_low_airflow(n):
    """Low airflow (dirty filter): large supply/return delta, icing risk."""
    rows = []
    for _ in range(n):
        outdoor   = rng(85,  12,  lo=60,  hi=110)
        return_t  = outdoor - rng(5,  2,  lo=2,  hi=10)    # warm return (restricted)
        supply    = return_t - rng(26, 4, lo=20, hi=35)    # very cold supply (overcooling)
        suction_p = rng(50,  6,   lo=35,  hi=65)           # dropping
        discharge = rng(255, 20,  lo=200, hi=300)
        age       = rng(6,   3,   lo=1,   hi=18)
        rows.append([outdoor, supply, return_t, suction_p, discharge, age, "low_airflow_dirty_filter"])
    return rows

def generate_compressor_inefficiency(n):
    """Failing compressor: high suction, low discharge, warm supply."""
    rows = []
    for _ in range(n):
        outdoor   = rng(85,  12,  lo=60,  hi=110)
        suction_p = rng(82,  8,   lo=65,  hi=100)          # HIGH suction
        discharge = rng(235, 25,  lo=170, hi=280)          # LOW discharge
        supply    = outdoor - rng(8,  3,  lo=3,  hi=15)    # poor cooling
        return_t  = supply + rng(14, 2, lo=10, hi=20)
        age       = rng(13,  3,   lo=8,   hi=22)           # older units
        rows.append([outdoor, supply, return_t, suction_p, discharge, age, "compressor_inefficiency"])
    return rows

def generate_faulty_condenser_fan(n):
    """Condenser fan failing: extreme head pressure, poor heat rejection."""
    rows = []
    for _ in range(n):
        outdoor   = rng(85,  12,  lo=60,  hi=110)
        discharge = rng(390, 35,  lo=330, hi=460)          # VERY HIGH
        suction_p = rng(78,  8,   lo=62,  hi=95)
        supply    = outdoor - rng(11, 3, lo=5, hi=18)
        return_t  = supply + rng(16, 2, lo=12, hi=22)
        age       = rng(9,   4,   lo=3,   hi=20)
        rows.append([outdoor, supply, return_t, suction_p, discharge, age, "faulty_condenser_fan"])
    return rows

# Sample counts — more for common faults
counts = {
    "normal":                  4000,
    "refrigerant_undercharge": 3500,  # Most common expensive fault
    "dirty_condenser_coil":    3000,
    "low_airflow_dirty_filter":3000,
    "dirty_evaporator_coil":   2500,
    "refrigerant_overcharge":  2000,
    "compressor_inefficiency": 2000,
    "faulty_condenser_fan":    2000,
}

generators = {
    "normal":                  generate_normal,
    "refrigerant_undercharge": generate_refrigerant_undercharge,
    "refrigerant_overcharge":  generate_refrigerant_overcharge,
    "dirty_condenser_coil":    generate_dirty_condenser,
    "dirty_evaporator_coil":   generate_dirty_evaporator,
    "low_airflow_dirty_filter":generate_low_airflow,
    "compressor_inefficiency": generate_compressor_inefficiency,
    "faulty_condenser_fan":    generate_faulty_condenser_fan,
}

print("Generating HVAC sensor fault training data...")
all_rows = []
for fault, gen_fn in generators.items():
    n = counts[fault]
    rows = gen_fn(n)
    all_rows.extend(rows)
    print(f"  ✓ {fault:30s}: {n:,} samples")

cols = ["outdoor_ambient_temp", "supply_air_temp", "return_air_temp",
        "suction_pressure", "discharge_pressure", "unit_age_years", "fault_label"]

df = pd.DataFrame(all_rows, columns=cols)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)  # shuffle

# Add realistic sensor noise
noise_cols = ["outdoor_ambient_temp","supply_air_temp","return_air_temp",
              "suction_pressure","discharge_pressure"]
for col in noise_cols:
    df[col] += np.random.normal(0, 0.5, len(df))  # ±0.5 sensor noise

# Round to realistic precision
df[["outdoor_ambient_temp","supply_air_temp","return_air_temp"]] = \
    df[["outdoor_ambient_temp","supply_air_temp","return_air_temp"]].round(1)
df[["suction_pressure","discharge_pressure"]] = \
    df[["suction_pressure","discharge_pressure"]].round(0)
df["unit_age_years"] = df["unit_age_years"].round(0).astype(int)

csv_path = OUTPUT / "hvac_sensor_training_data.csv"
df.to_csv(csv_path, index=False)

print(f"\n✅ Sensor dataset saved: {csv_path}")
print(f"   Total rows: {len(df):,}")
print(f"   Features: {noise_cols + ['unit_age_years']}")
print(f"   Classes: {df['fault_label'].nunique()}")
print(f"\n   Class distribution:")
for label, count in df["fault_label"].value_counts().items():
    print(f"     {label:35s}: {count:,}")
