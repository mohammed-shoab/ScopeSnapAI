"use client";

import { useState } from "react";

export interface ReadingSpec {
  type: string;         // 'uF' | 'amps_compressor' | 'amps_blower' | 'voltage' | 'voltage_drop' | 'temp_F' | 'ohms' | 'microamps' | 'psi' | etc.
  unit: string;         // display unit string e.g. 'µF', 'A', 'V', '°F', 'Ω', 'µA', 'PSI'
  compare_to?: string;  // dotted key into ocrNameplate e.g. 'cap_uf'
  tolerance_pct?: number;
  subtype?: string;     // 'suction' | 'discharge' | 'supply_air' | 'return_air' | etc.
  placeholder?: string;
  // Threshold-based classification (used for PSI pressure readings)
  low_threshold?: number;   // values below this → branchKey "low"
  high_threshold?: number;  // values above this → branchKey "high"
}

export interface ReadingResult {
  value: number;
  unit: string;
  classification: string;  // 'low' | 'ok' | 'high' | 'over_rla' | 'fault' | etc.
  passed: boolean;
  branchKey: string;       // matches a key in branch_logic_jsonb
}

interface ReadingInputProps {
  spec: ReadingSpec;
  ocrNameplate?: Record<string, unknown> | null;
  onSubmit: (result: ReadingResult) => void;
  disabled?: boolean;
}

function classifyReading(value: number, spec: ReadingSpec, nameplate: Record<string, unknown> | null): ReadingResult {
  const unit = spec.unit;

  // µF capacitor comparison
  if (spec.type === "uF" && spec.compare_to && nameplate) {
    const specVal = Number(nameplate[spec.compare_to] ?? nameplate["cap_uf"]);
    if (!isNaN(specVal) && specVal > 0) {
      const tol = (spec.tolerance_pct ?? 10) / 100;
      const low = specVal * (1 - tol);
      const high = specVal * (1 + (spec.tolerance_pct ? 0.05 : 0.05));
      if (value < low) return { value, unit, classification: "low", passed: false, branchKey: "low" };
      if (value > high) return { value, unit, classification: "high", passed: false, branchKey: "high" };
      return { value, unit, classification: "ok", passed: true, branchKey: "ok" };
    }
  }

  // Amp draw comparisons
  if ((spec.type === "amps_compressor") && spec.compare_to && nameplate) {
    const rla = Number(nameplate["rla"] ?? nameplate["RLA"]);
    if (!isNaN(rla) && rla > 0) {
      const tol = (spec.tolerance_pct ?? 10) / 100;
      if (value > rla * (1 + tol)) return { value, unit, classification: "over_rla", passed: false, branchKey: "over_rla" };
      return { value, unit, classification: "ok", passed: true, branchKey: "ok" };
    }
  }

  if (spec.type === "amps_blower" && spec.compare_to && nameplate) {
    const fla = Number(nameplate["fla_blower"] ?? nameplate["FLA"]);
    if (!isNaN(fla) && fla > 0) {
      const tol = (spec.tolerance_pct ?? 10) / 100;
      if (value > fla * (1 + tol)) return { value, unit, classification: "over_fla", passed: false, branchKey: "over_fla" };
      return { value, unit, classification: "ok", passed: true, branchKey: "ok" };
    }
  }

  // Voltage drop
  if (spec.type === "voltage_drop") {
    if (value > 3.0) return { value, unit, classification: "fault", passed: false, branchKey: "fault" };
    if (value >= 1.0) return { value, unit, classification: "elevated_high", passed: false, branchKey: "elevated_high" };
    if (value >= 0.5) return { value, unit, classification: "elevated", passed: true, branchKey: "elevated" };
    return { value, unit, classification: "ok", passed: true, branchKey: "ok" };
  }

  // Ohms — flame sensor micro-amps
  if (spec.type === "microamps") {
    if (value >= 2) return { value, unit, classification: "ok", passed: true, branchKey: "ok" };
    if (value >= 1) return { value, unit, classification: "marginal", passed: false, branchKey: "marginal" };
    return { value, unit, classification: "low", passed: false, branchKey: "low" };
  }

  // Ohms — ignitor
  if (spec.type === "ohms" && spec.subtype === "ignitor") {
    if (value === 0 || value > 10000) return { value, unit, classification: "open", passed: false, branchKey: "cracked_or_open_ohms" };
    if (value >= 40 && value <= 100) return { value, unit, classification: "ok", passed: true, branchKey: "intact_and_normal" };
    return { value, unit, classification: "suspect", passed: false, branchKey: "cracked_or_open_ohms" };
  }

  // Pressure readings (suction / discharge PSI) — threshold-based classification.
  // Thresholds come from reading_spec.low_threshold / high_threshold.
  // Default R-410A suction: low < 60 psi (refrigerant leak), high > 110 psi (dirty condenser/overcharge).
  if (spec.type === "psi") {
    const lowT = spec.low_threshold ?? 60;
    const highT = spec.high_threshold ?? 110;
    if (value < lowT) return { value, unit, classification: "low", passed: false, branchKey: "low" };
    if (value > highT) return { value, unit, classification: "high", passed: false, branchKey: "high" };
    return { value, unit, classification: "ok", passed: true, branchKey: "ok" };
  }

  // L1+L2 supply voltage — threshold-based: below low_threshold → no_power, else → power_passes_normal
  // Default threshold 100 V (splits dead-leg ~0 V from healthy ~240 V).
  if (spec.type === "voltage") {
    const lowT = spec.low_threshold ?? 100;
    if (value < lowT) return { value, unit, classification: "no_power", passed: false, branchKey: "no_power" };
    return { value, unit, classification: "power_passes_normal", passed: true, branchKey: "power_passes_normal" };
  }

  // Generic fallback — just pass through value, let backend decide
  return { value, unit, classification: "entered", passed: true, branchKey: "ok" };
}

export default function ReadingInput({ spec, ocrNameplate, onSubmit, disabled = false }: ReadingInputProps) {
  const [inputVal, setInputVal] = useState("");

  const nameplateSpec = spec.compare_to && ocrNameplate
    ? Number((ocrNameplate as Record<string, unknown>)[spec.compare_to])
    : null;

  const numVal = parseFloat(inputVal);
  const hasValue = inputVal !== "" && !isNaN(numVal);

  const preview = hasValue && nameplateSpec && !isNaN(nameplateSpec) && nameplateSpec > 0
    ? (() => {
        const pct = ((numVal - nameplateSpec) / nameplateSpec) * 100;
        const tol = spec.tolerance_pct ?? 10;
        const ok = Math.abs(pct) <= tol;
        return { pct: pct.toFixed(1), ok };
      })()
    : null;

  const handleSubmit = () => {
    if (!hasValue) return;
    const result = classifyReading(numVal, spec, ocrNameplate ?? null);
    onSubmit(result);
  };

  return (
    <div className="flex flex-col gap-4 w-full">
      <div className="relative">
        <input
          type="number"
          inputMode="decimal"
          step="any"
          value={inputVal}
          onChange={(e) => setInputVal(e.target.value)}
          placeholder={spec.placeholder ?? `Enter ${spec.unit}`}
          disabled={disabled}
          className="w-full px-4 py-4 rounded-xl text-xl font-mono font-bold text-right pr-16 border-2 bg-surface-secondary text-text-primary placeholder-text-secondary focus:outline-none transition-colors"
          style={{ borderColor: hasValue ? (preview ? (preview.ok ? "#2ecc71" : "#e74c3c") : "#3498db") : "#2a2a4a" }}
          onKeyDown={(e) => { if (e.key =