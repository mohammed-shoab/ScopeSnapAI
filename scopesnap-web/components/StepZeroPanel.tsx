/**
 * WS-B — Step Zero OCR Panel
 *
 * Shown before any complaint is selected. Tech photographs the unit
 * nameplate(s); Gemini extracts 10 fields; tech confirms/edits; then
 * the assessment advances to the complaint-selection phase.
 *
 * Design reference: SnapAI_Decision_Tree.html .step-zero-banner
 * App theme: white/light, brand-green #1a8754, orange alerts #c4600a
 */
"use client";

import { useState, useRef, useCallback } from "react";
import { API_URL } from "@/lib/api";

// ── Types ───────────────────────────────────────────────────────────────────

interface NameplateUnit {
  model_number:       string | null;
  serial_number:      string | null;
  tonnage:            number | null;
  refrigerant:        string | null;
  factory_charge_oz:  number | null;
  rla:                number | null;
  lra:                number | null;
  capacitor_uf:       string | null;
  mca:                number | null;
  mocp:               number | null;
  voltage:            string | null;
  brand_id:           string | null;
  series_id:          string | null;
  charging_method:    string | null;
  metering_device:    string | null;
  is_legacy:          boolean;
  year_of_manufacture: number | null;
  r22_alert:          boolean;
  confidence:         number;
  notes:              string | null;
}

interface OcrResult {
  outdoor:            NameplateUnit;
  indoor:             NameplateUnit | null;
  captured_at:        string;
  capture_method:     string;
  d7_brand_detected:  boolean;
  d7_brand_name:      string | null;
}

interface Props {
  assessmentId?: string;  // set once assessment is created (for persisting)
  clerkToken: string | null;
  onConfirm: (result: OcrResult) => void;
  onSkip: () => void;
}

// ── OCR field display config ─────────────────────────────────────────────────

const OCR_FIELDS: { key: keyof NameplateUnit; label: string; unit?: string; type: "text" | "number" }[] = [
  { key: "model_number",      label: "Model #",       type: "text" },
  { key: "serial_number",     label: "Serial #",      type: "text" },
  { key: "tonnage",           label: "Tonnage",       unit: "ton",    type: "number" },
  { key: "refrigerant",       label: "Refrigerant",   type: "text" },
  { key: "factory_charge_oz", label: "Factory Charge", unit: "oz",   type: "number" },
  { key: "rla",               label: "RLA",           unit: "A",      type: "number" },
  { key: "lra",               label: "LRA",           unit: "A",      type: "number" },
  { key: "capacitor_uf",      label: "Cap",           unit: "uF",     type: "text" },
  { key: "mca",               label: "MCA",           unit: "A",      type: "number" },
  { key: "mocp",              label: "MOCP",          unit: "A",      type: "number" },
  { key: "voltage",           label: "Voltage",       type: "text" },
];

// ── Component ────────────────────────────────────────────────────────────────

export default function StepZeroPanel({ assessmentId, clerkToken, onConfirm, onSkip }: Props) {
  const [outdoorFile,  setOutdoorFile]  = useState<File | null>(null);
  const [indoorFile,   setIndoorFile]   = useState<File | null>(null);
  const [outdoorPreview, setOutdoorPreview] = useState<string | null>(null);
  const [indoorPreview,  setIndoorPreview]  = useState<string | null>(null);
  const [loading,      setLoading]      = useState(false);
  const [error,        setError]        = useState<string | null>(null);
  const [ocrResult,    setOcrResult]    = useState<OcrResult | null>(null);
  const [editedUnit,   setEditedUnit]   = useState<NameplateUnit | null>(null);

  const outdoorInputRef = useRef<HTMLInputElement>(null);
  const indoorInputRef  = useRef<HTMLInputElement>(null);

  // ── Photo selection ─────────────────────────────────────────────────────

  const handleFileChange = useCallback(
    (slot: "outdoor" | "indoor", file: File | null) => {
      if (!file) return;
      const url = URL.createObjectURL(file);
      if (slot === "outdoor") {
        setOutdoorFile(file);
        setOutdoorPreview(url);
      } else {
        setIndoorFile(file);
        setIndoorPreview(url);
      }
      setOcrResult(null);
      setEditedUnit(null);
      setError(null);
    },
    []
  );

  // ── Run OCR ─────────────────────────────────────────────────────────────

  const runOCR = useCallback(async () => {
    if (!outdoorFile) {
      setError("Please capture the outdoor unit nameplate first.");
      return;
    }

    setLoading(true);
    setError(null);
    setOcrResult(null);

    try {
      const fd = new FormData();
      fd.append("outdoor_photo", outdoorFile);
      if (indoorFile) fd.append("indoor_photo", indoorFile);

      const headers: Record<string, string> = {};
      if (clerkToken) {
        headers["Authorization"] = `Bearer ${clerkToken}`;
      } else if (process.env.NEXT_PUBLIC_ENV === "development") {
        headers["X-Dev-Clerk-User-Id"] = "test_user_mike";
      }

      const res = await fetch(`${API_URL}/api/ocr/nameplate`, {
        method: "POST",
        headers,
        body: fd,
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `OCR failed (${res.status})`);
      }

      const result: OcrResult = await res.json();
      setOcrResult(result);
      setEditedUnit({ ...result.outdoor });
    } catch (e) {
      setError(e instanceof Error ? e.message : "OCR failed. Try again.");
    } finally {
      setLoading(false);
    }
  }, [outdoorFile, indoorFile, clerkToken]);

  // ── Confirm / persist ───────────────────────────────────────────────────

  const handleConfirm = useCallback(async () => {
    if (!ocrResult || !editedUnit) return;

    const finalResult: OcrResult = { ...ocrResult, outdoor: editedUnit };

    // Persist to assessment if we have an ID
    if (assessmentId && clerkToken) {
      try {
        const headers: Record<string, string> = {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${clerkToken}`,
        };
        await fetch(`${API_URL}/api/ocr/assessments/${assessmentId}/nameplate`, {
          method: "PATCH",
          headers,
          body: JSON.stringify({ ocr_result: finalResult }),
        });
      } catch {
        // Non-fatal — proceed even if persist fails
      }
    }

    onConfirm(finalResult);
  }, [ocrResult, editedUnit, assessmentId, clerkToken, onConfirm]);

  // ── Edit field helper ───────────────────────────────────────────────────

  const updateField = useCallback(
    (key: keyof NameplateUnit, value: string) => {
      setEditedUnit(prev => {
        if (!prev) return prev;
        const parsed = OCR_FIELDS.find(f => f.key === key)?.type === "number"
          ? (value === "" ? null : parseFloat(value))
          : value || null;
        return { ...prev, [key]: parsed };
      });
    },
    []
  );

  // ── Render ──────────────────────────────────────────────────────────────

  return (
    <div className="max-w-md mx-auto px-4 pb-8 pt-4 space-y-5">

      {/* Header */}
      <div className="bg-white border-2 rounded-2xl overflow-hidden"
           style={{ borderColor: "#f39c12" }}>
        <div className="px-4 py-3" style={{ background: "linear-gradient(135deg,#fff9f0,#fff3e0)" }}>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-black uppercase tracking-widest px-2 py-0.5 rounded-full text-black"
                  style={{ background: "#f39c12" }}>
              Step Zero
            </span>
            <span className="text-xs text-gray-500 font-medium">Every Call</span>
          </div>
          <h2 className="text-base font-black text-gray-900 leading-tight">
            Nameplate Photo — Before Any Complaint
          </h2>
          <p className="text-xs text-gray-500 mt-0.5">
            AI reads nameplate and pre-loads all system specs automatically
          </p>
        </div>
      </div>

      {/* D-7 brand warning */}
      {ocrResult?.d7_brand_detected && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-3 flex gap-2">
          <span className="text-yellow-600 flex-shrink-0">!</span>
          <div>
            <p className="text-sm font-bold text-yellow-800">
              {(ocrResult.d7_brand_name || "Mini-split").charAt(0).toUpperCase() +
               (ocrResult.d7_brand_name || "mini-split").slice(1)} — manual entry required
            </p>
            <p className="text-xs text-yellow-700 mt-0.5">
              Auto-detect not yet available for this brand. Please verify fields below.
            </p>
          </div>
        </div>
      )}

      {/* R-22 alert */}
      {editedUnit?.r22_alert && (
        <div className="bg-red-50 border-2 border-red-400 rounded-xl p-3 flex gap-2">
          <span className="text-red-600 font-bold flex-shrink-0">!</span>
          <div>
            <p className="text-sm font-black text-red-800">R-22 Legacy Unit Detected</p>
            <p className="text-xs text-red-700 mt-0.5">
              Pre-2010 unit. R-22 refrigerant only — no R-410A substitution.
              Refrigerant charge is $200–320/lb installed.
            </p>
          </div>
        </div>
      )}

      {/* Photo capture boxes */}
      <div className="grid grid-cols-2 gap-3">
        {/* Outdoor */}
        <button
          onClick={() => outdoorInputRef.current?.click()}
          className="relative rounded-xl border-2 overflow-hidden flex flex-col items-center justify-center min-h-[120px] transition-colors"
          style={{ borderColor: outdoorFile ? "#1a8754" : "#e2dfd7", background: "#fafaf8" }}
        >
          {outdoorPreview ? (
            <>
              <img src={outdoorPreview} alt="Outdoor nameplate" className="w-full h-full object-cover absolute inset-0" />
              <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/60 to-transparent px-2 py-1.5">
                <p className="text-xs font-bold text-white">Outdoor</p>
                <p className="text-[10px] text-white/80">Tap to retake</p>
              </div>
            </>
          ) : (
            <div className="flex flex-col items-center gap-1.5 p-3 text-center">
              <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center text-xl">+</div>
              <p className="text-xs font-bold text-gray-700">Outdoor</p>
              <p className="text-[10px] text-gray-400">Required</p>
            </div>
          )}
          <input
            ref={outdoorInputRef}
            type="file"
            accept="image/*"
            capture="environment"
            className="hidden"
            onChange={e => handleFileChange("outdoor", e.target.files?.[0] ?? null)}
          />
        </button>

        {/* Indoor */}
        <button
          onClick={() => indoorInputRef.current?.click()}
          className="relative rounded-xl border-2 overflow-hidden flex flex-col items-center justify-center min-h-[120px] transition-colors"
          style={{ borderColor: indoorFile ? "#1a8754" : "#e2dfd7", background: "#fafaf8" }}
        >
          {indoorPreview ? (
            <>
              <img src={indoorPreview} alt="Indoor nameplate" className="w-full h-full object-cover absolute inset-0" />
              <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/60 to-transparent px-2 py-1.5">
                <p className="text-xs font-bold text-white">Indoor</p>
                <p className="text-[10px] text-white/80">Tap to retake</p>
              </div>
            </>
          ) : (
            <div className="flex flex-col items-center gap-1.5 p-3 text-center">
              <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center text-xl">+</div>
              <p className="text-xs font-bold text-gray-700">Indoor</p>
              <p className="text-[10px] text-gray-400">If accessible</p>
            </div>
          )}
          <input
            ref={indoorInputRef}
            type="file"
            accept="image/*"
            capture="environment"
            className="hidden"
            onChange={e => handleFileChange("indoor", e.target.files?.[0] ?? null)}
          />
        </button>
      </div>

      {/* Extract button */}
      {outdoorFile && !ocrResult && (
        <button
          onClick={runOCR}
          disabled={loading}
          className="w-full py-3.5 rounded-xl font-black text-white text-sm transition-all"
          style={{ background: loading ? "#ccc" : "#f39c12" }}
        >
          {loading ? "Reading nameplate..." : "Extract Specs with AI"}
        </button>
      )}

      {/* Loading indicator */}
      {loading && (
        <div className="flex items-center justify-center gap-3 py-2">
          {[0,1,2].map(i => (
            <div key={i} className="w-2.5 h-2.5 rounded-full animate-bounce"
                 style={{ background: "#f39c12", animationDelay: `${i * 0.15}s` }} />
          ))}
          <span className="text-sm text-gray-500 font-medium">Gemini reading nameplate...</span>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-3 text-sm text-red-700 font-medium">
          {error}
        </div>
      )}

      {/* OCR Results — edit-in-place grid */}
      {editedUnit && (
        <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden">
          <div className="px-4 py-2.5 border-b border-gray-100 flex items-center justify-between">
            <span className="text-xs font-black uppercase tracking-wider text-green-600">
              AI Extracted — verify &amp; edit
            </span>
            <span className="text-xs font-mono text-gray-400">{editedUnit.confidence}% confidence</span>
          </div>

          {/* Charging method badge */}
          {editedUnit.charging_method && (
            <div className="px-4 pt-2.5 flex gap-2">
              <span className="px-2 py-0.5 rounded-full text-xs font-bold"
                    style={{ background: "#e8f5ee", color: "#1a8754" }}>
                {editedUnit.metering_device === "piston" ? "Superheat" : "Subcooling"} charging
              </span>
              {editedUnit.metering_device && (
                <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-gray-100 text-gray-600">
                  {editedUnit.metering_device === "piston" ? "Piston / Fixed orifice" : editedUnit.metering_device.toUpperCase()}
                </span>
              )}
              {editedUnit.year_of_manufacture && (
                <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-gray-100 text-gray-600">
                  Mfg {editedUnit.year_of_manufacture}
                </span>
              )}
            </div>
          )}

          <div className="p-3 grid grid-cols-2 gap-2">
            {OCR_FIELDS.map(({ key, label, unit, type }) => {
              const val = editedUnit[key];
              const displayVal = val === null || val === undefined ? "" : String(val);
              const isEmpty = displayVal === "";
              return (
                <div key={key} className="flex flex-col gap-0.5">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400">{label}</span>
                  <div className="relative flex items-center">
                    <input
                      type={type === "number" ? "number" : "text"}
                      value={displayVal}
                      onChange={e => updateField(key, e.target.value)}
                      placeholder="—"
                      className="w-full text-sm font-mono font-bold rounded-lg border px-2 py-1.5 focus:outline-none focus:ring-1 transition-colors"
                      style={{
                        borderColor: isEmpty ? "#e2dfd7" : "#1a8754",
                        background: isEmpty ? "#fafaf8" : "#f0faf6",
                        color: isEmpty ? "#aaa" : "#1a1a1a",
                        focusRing: "#1a8754",
                      } as React.CSSProperties}
                    />
                    {unit && !isEmpty && (
                      <span className="absolute right-2 text-[10px] font-bold text-gray-400">{unit}</span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Brand/series info */}
          {editedUnit.brand_id && (
            <div className="px-4 pb-3">
              <p className="text-xs text-gray-400">
                Matched: <span className="font-bold text-gray-600 capitalize">{editedUnit.brand_id}</span>
                {editedUnit.series_id && ` — ${editedUnit.series_id.split("_").slice(1).join(" ")}`}
                {editedUnit.is_legacy && " (legacy / pre-2010)"}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Confirm + Skip */}
      <div className="flex gap-3">
        <button
          onClick={onSkip}
          className="flex-1 py-3 rounded-xl border-2 border-gray-200 text-sm font-bold text-gray-500 hover:border-gray-300 transition-colors"
        >
          Skip for now
        </button>
        <button
          onClick={editedUnit ? handleConfirm : onSkip}
          className="flex-2 py-3 px-6 rounded-xl text-sm font-black text-white transition-all"
          style={{ background: "#1a8754", flex: 2 }}
        >
          {editedUnit ? "Confirm & Continue" : "Continue without scan"}
        </button>
      </div>

      <p className="text-center text-xs text-gray-400">
        Nameplate specs auto-fill all cards — save time on every call
      </p>
    </div>
  );
}
