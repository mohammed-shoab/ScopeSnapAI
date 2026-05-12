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

import { useState, useRef, useCallback, useEffect } from "react";
import { API_URL } from "@/lib/api";
import { checkImageQuality, type ImageQualityResult } from "@/lib/imageQuality";
import { getBrands, searchModels, type EquipmentModelRecord } from "@/lib/modelCache";

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

  // ── Blur / quality warnings (Section 5B) ──────────────────────────────
  const [outdoorQuality, setOutdoorQuality] = useState<ImageQualityResult | null>(null);
  const [indoorQuality,  setIndoorQuality]  = useState<ImageQualityResult | null>(null);

  // ── Section 5C: Manual entry tab ───────────────────────────────────────
  const [activeTab, setActiveTab] = useState<"photo" | "manual">("photo");
  const BLANK_UNIT: NameplateUnit = {
    model_number: null, serial_number: null, tonnage: null, refrigerant: null,
    factory_charge_oz: null, rla: null, lra: null, capacitor_uf: null,
    mca: null, mocp: null, voltage: null, brand_id: null, series_id: null,
    charging_method: null, metering_device: null, is_legacy: false,
    year_of_manufacture: null, r22_alert: false, confidence: 100, notes: null,
  };
  const [manualUnit, setManualUnit] = useState<NameplateUnit>({ ...BLANK_UNIT });

  // ── Section 5A: Brand/model lookup ─────────────────────────────────────────
  const [brands,           setBrands]           = useState<Array<{ brand: string; model_count: number }>>([]);
  const [brandsLoading,    setBrandsLoading]    = useState(false);
  const [selectedBrand,    setSelectedBrand]    = useState<string>("");
  const [modelQuery,       setModelQuery]       = useState<string>("");
  const [modelResults,     setModelResults]     = useState<EquipmentModelRecord[]>([]);
  const [modelSearching,   setModelSearching]   = useState(false);
  const [showModelDropdown, setShowModelDropdown] = useState(false);

  // Load brands when user opens manual tab
  useEffect(() => {
    if (activeTab !== "manual" || brands.length > 0) return;
    setBrandsLoading(true);
    getBrands()
      .then(b => setBrands(b))
      .catch(() => {/* silent */})
      .finally(() => setBrandsLoading(false));
  }, [activeTab, brands.length]);

  // Debounced model search when brand or query changes
  useEffect(() => {
    if (!selectedBrand) {
      setModelResults([]);
      setShowModelDropdown(false);
      return;
    }
    const t = setTimeout(async () => {
      setModelSearching(true);
      try {
        const results = await searchModels(selectedBrand, modelQuery, undefined, 12);
        setModelResults(results);
        setShowModelDropdown(results.length > 0);
      } catch {
        setModelResults([]);
      } finally {
        setModelSearching(false);
      }
    }, 250);
    return () => clearTimeout(t);
  }, [selectedBrand, modelQuery]);

  /** Apply a selected model record to the manual unit fields */
  const applyModelRecord = useCallback((model: EquipmentModelRecord) => {
    setManualUnit(prev => {
      const next = { ...prev };
      next.brand_id   = model.brand;
      next.series_id  = model.model_series;
      next.model_number = model.model_series;
      // Tonnage: parse the low end of "1.5-5" → 3 (midpoint) or leave null
      if (model.tonnage_range) {
        const parts = model.tonnage_range.split("-").map(Number).filter(n => !isNaN(n));
        if (parts.length === 2) next.tonnage = Math.round((parts[0] + parts[1]) / 2 * 2) / 2;
        else if (parts.length === 1) next.tonnage = parts[0];
      }
      return next;
    });
    setShowModelDropdown(false);
  }, []);

  /** Section 5D: Auto-select refrigerant based on manufacture year */
  const updateManualField = useCallback((key: keyof NameplateUnit, value: string) => {
    setManualUnit(prev => {
      const fieldDef = OCR_FIELDS.find(f => f.key === key);
      const parsed = fieldDef?.type === "number"
        ? (value === "" ? null : parseFloat(value))
        : (value || null);
      const next = { ...prev, [key]: parsed };
      // 5D-1: auto-set refrigerant from year_of_manufacture
      if (key === "year_of_manufacture" && parsed !== null) {
        const yr = parsed as number;
        if (yr < 2010) {
          next.refrigerant = "R-22";
          next.r22_alert   = true;
          next.is_legacy   = true;
        } else if (yr >= 2023) {
          next.refrigerant = "R-454B";  // New low-GWP replacement
          next.r22_alert   = false;
        } else {
          next.refrigerant = "R-410A";
          next.r22_alert   = false;
        }
      }
      return next;
    });
  }, []);

  /** Confirm manual entry — wraps manualUnit into an OcrResult */
  const handleManualConfirm = useCallback(() => {
    const result: OcrResult = {
      outdoor: { ...manualUnit },
      indoor: null,
      captured_at: new Date().toISOString(),
      capture_method: "manual",
      d7_brand_detected: false,
      d7_brand_name: null,
    };
    onConfirm(result);
  }, [manualUnit, onConfirm]);

  // ── Photo selection ─────────────────────────────────────────────────────

  const handleFileChange = useCallback(
    async (slot: "outdoor" | "indoor", file: File | null) => {
      if (!file) return;
      const url = URL.createObjectURL(file);
      if (slot === "outdoor") {
        setOutdoorFile(file);
        setOutdoorPreview(url);
        setOutdoorQuality(null);
        // Run blur check in background — don't block the UI
        checkImageQuality(file).then(q => setOutdoorQuality(q)).catch(() => {});
      } else {
        setIndoorFile(file);
        setIndoorPreview(url);
        setIndoorQuality(null);
        checkImageQuality(file).then(q => setIndoorQuality(q)).catch(() => {});
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

      {/* Section 5C: Tab switcher — Photo OCR | Manual Entry */}
      <div className="flex rounded-xl border border-gray-200 overflow-hidden bg-gray-50 p-0.5 gap-0.5">
        <button
          onClick={() => setActiveTab("photo")}
          className="flex-1 py-2 text-xs font-bold rounded-lg transition-all"
          style={{
            background: activeTab === "photo" ? "#1a8754" : "transparent",
            color: activeTab === "photo" ? "white" : "#6b7280",
          }}
        >
          📸 Photo OCR
        </button>
        <button
          onClick={() => setActiveTab("manual")}
          className="flex-1 py-2 text-xs font-bold rounded-lg transition-all"
          style={{
            background: activeTab === "manual" ? "#1a8754" : "transparent",
            color: activeTab === "manual" ? "white" : "#6b7280",
          }}
        >
          ✏️ Manual Entry
        </button>
      </div>

      {/* ── MANUAL ENTRY TAB (Section 5A + 5C + 5D) ─────────────────────── */}
      {activeTab === "manual" && (
        <div className="space-y-4">
          <p className="text-xs text-gray-500 text-center">
            Select brand &amp; model to auto-fill, or type specs directly.
          </p>

          {/* Section 5A: Brand dropdown + model search */}
          <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden">
            <div className="px-4 py-2.5 border-b border-gray-100">
              <span className="text-xs font-black uppercase tracking-wider text-blue-600">
                🔍 Model Lookup — auto-fill from database
              </span>
            </div>
            <div className="p-3 space-y-2">
              {/* Brand select */}
              <div>
                <label className="block text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1">
                  Brand
                </label>
                <select
                  value={selectedBrand}
                  onChange={e => {
                    setSelectedBrand(e.target.value);
                    setModelQuery("");
                    setModelResults([]);
                    setShowModelDropdown(false);
                  }}
                  className="w-full text-sm font-semibold rounded-lg border px-3 py-2 focus:outline-none transition-colors"
                  style={{
                    borderColor: selectedBrand ? "#1a8754" : "#e2dfd7",
                    background: selectedBrand ? "#f0faf6" : "#fafaf8",
                    color: selectedBrand ? "#1a1a1a" : "#9ca3af",
                  } as React.CSSProperties}
                >
                  <option value="">
                    {brandsLoading ? "Loading brands…" : "Select brand…"}
                  </option>
                  {brands.map(b => (
                    <option key={b.brand} value={b.brand}>
                      {b.brand} ({b.model_count} models)
                    </option>
                  ))}
                </select>
              </div>

              {/* Model series search — only shown once brand is selected */}
              {selectedBrand && (
                <div className="relative">
                  <label className="block text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1">
                    Model Series
                  </label>
                  <input
                    type="text"
                    value={modelQuery}
                    onChange={e => {
                      setModelQuery(e.target.value);
                      setShowModelDropdown(true);
                    }}
                    onFocus={() => modelResults.length > 0 && setShowModelDropdown(true)}
                    placeholder={`Search ${selectedBrand} models…`}
                    className="w-full text-sm font-mono font-semibold rounded-lg border px-3 py-2 focus:outline-none transition-colors"
                    style={{
                      borderColor: "#e2dfd7",
                      background: "#fafaf8",
                    } as React.CSSProperties}
                  />
                  {modelSearching && (
                    <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-400">
                      …
                    </span>
                  )}

                  {/* Model results dropdown */}
                  {showModelDropdown && modelResults.length > 0 && (
                    <div
                      className="absolute z-50 left-0 right-0 bg-white border border-gray-200 rounded-xl shadow-lg mt-1 overflow-hidden"
                      style={{ maxHeight: 220, overflowY: "auto" }}
                    >
                      {modelResults.map(m => (
                        <button
                          key={m.id}
                          onClick={() => applyModelRecord(m)}
                          className="w-full text-left px-3 py-2 hover:bg-green-50 transition-colors border-b border-gray-50 last:border-0"
                        >
                          <div className="flex items-center justify-between">
                            <span className="text-sm font-bold text-gray-800">{m.model_series}</span>
                            <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded-full bg-gray-100 text-gray-500 uppercase">
                              {m.equipment_type.replace("_", " ")}
                            </span>
                          </div>
                          <div className="flex gap-3 mt-0.5">
                            {m.seer_rating && (
                              <span className="text-[10px] text-gray-400">{m.seer_rating} SEER</span>
                            )}
                            {m.tonnage_range && (
                              <span className="text-[10px] text-gray-400">{m.tonnage_range} ton</span>
                            )}
                            {m.manufacture_years && (
                              <span className="text-[10px] text-gray-400">{m.manufacture_years}</span>
                            )}
                            {m.avg_lifespan_years && (
                              <span className="text-[10px] text-gray-400">{m.avg_lifespan_years}yr avg life</span>
                            )}
                          </div>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Applied model confirmation chip */}
              {manualUnit.brand_id && manualUnit.series_id && (
                <div className="flex items-center gap-2 px-3 py-2 bg-green-50 border border-green-200 rounded-xl">
                  <span className="text-green-600 text-sm">✓</span>
                  <div className="flex-1 min-w-0">
                    <span className="text-xs font-bold text-green-800">
                      {manualUnit.brand_id} — {manualUnit.series_id}
                    </span>
                    {manualUnit.tonnage && (
                      <span className="text-xs text-green-600 ml-2">({manualUnit.tonnage}t auto-filled)</span>
                    )}
                  </div>
                  <button
                    onClick={() => {
                      setManualUnit(prev => ({ ...prev, brand_id: null, series_id: null, model_number: null, tonnage: null }));
                      setSelectedBrand("");
                      setModelQuery("");
                    }}
                    className="text-xs text-green-500 hover:text-green-700 font-bold flex-shrink-0"
                  >
                    ✕
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* R-22 alert for manual entry */}
          {manualUnit.r22_alert && (
            <div className="bg-red-50 border-2 border-red-400 rounded-xl p-3 flex gap-2">
              <span className="text-red-600 font-bold flex-shrink-0">!</span>
              <div>
                <p className="text-sm font-black text-red-800">R-22 Legacy Unit</p>
                <p className="text-xs text-red-700 mt-0.5">
                  Pre-2010 unit. R-22 refrigerant — $200–320/lb installed.
                </p>
              </div>
            </div>
          )}

          <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden">
            <div className="px-4 py-2.5 border-b border-gray-100">
              <span className="text-xs font-black uppercase tracking-wider text-gray-500">
                Enter specs manually
              </span>
            </div>
            <div className="p-3 grid grid-cols-2 gap-2">
              {OCR_FIELDS.map(({ key, label, unit, type }) => {
                const val = manualUnit[key];
                const displayVal = val === null || val === undefined ? "" : String(val);
                const isEmpty = displayVal === "";
                return (
                  <div key={key} className="flex flex-col gap-0.5">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400">
                      {label}
                      {key === "refrigerant" && <span className="text-blue-400 ml-1">(auto)</span>}
                    </span>
                    <div className="relative flex items-center">
                      <input
                        type={type === "number" ? "number" : "text"}
                        value={displayVal}
                        onChange={e => updateManualField(key, e.target.value)}
                        placeholder={key === "year_of_manufacture" ? "e.g. 2018" : "—"}
                        className="w-full text-sm font-mono font-bold rounded-lg border px-2 py-1.5 focus:outline-none transition-colors"
                        style={{
                          borderColor: isEmpty ? "#e2dfd7" : "#1a8754",
                          background: isEmpty ? "#fafaf8" : "#f0faf6",
                          color: isEmpty ? "#aaa" : "#1a1a1a",
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
          </div>

          <div className="flex gap-3">
            <button
              onClick={onSkip}
              className="flex-1 py-3 rounded-xl border-2 border-gray-200 text-sm font-bold text-gray-500 hover:border-gray-300 transition-colors"
            >
              Skip
            </button>
            <button
              onClick={handleManualConfirm}
              className="py-3 px-6 rounded-xl text-sm font-black text-white transition-all"
              style={{ background: "#1a8754", flex: 2 }}
            >
              Confirm & Continue
            </button>
          </div>
          <p className="text-center text-xs text-gray-400">
            Year field auto-selects R-22, R-410A, or R-454B
          </p>
        </div>
      )}

      {/* ── PHOTO OCR TAB — only shown when activeTab === "photo" ─────────── */}
      {activeTab === "photo" && (
        <>

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

      {/* Section 5B: Quality warnings — shown after photo selection, before OCR */}
      {!ocrResult && (outdoorQuality?.message || indoorQuality?.message) && (
        <div className="space-y-2">
          {outdoorQuality?.message && (
            <div className="flex items-start gap-2 bg-amber-50 border border-amber-200 rounded-xl p-3">
              <span className="text-amber-500 text-base flex-shrink-0 mt-0.5">⚠</span>
              <div>
                <p className="text-xs font-bold text-amber-800">Outdoor photo</p>
                <p className="text-xs text-amber-700 mt-0.5">{outdoorQuality.message}</p>
              </div>
              <button
                onClick={() => outdoorInputRef.current?.click()}
                className="ml-auto text-xs font-bold text-amber-700 underline flex-shrink-0"
              >
                Retake
              </button>
            </div>
          )}
          {indoorQuality?.message && (
            <div className="flex items-start gap-2 bg-amber-50 border border-amber-200 rounded-xl p-3">
              <span className="text-amber-500 text-base flex-shrink-0 mt-0.5">⚠</span>
              <div>
                <p className="text-xs font-bold text-amber-800">Indoor photo</p>
                <p className="text-xs text-amber-700 mt-0.5">{indoorQuality.message}</p>
              </div>
              <button
                onClick={() => indoorInputRef.current?.click()}
                className="ml-auto text-xs font-bold text-amber-700 underline flex-shrink-0"
              >
                Retake
              </button>
            </div>
          )}
        </div>
      )}

      {/* Section 5B: Camera coaching tips — shown before any photo is taken */}
      {!outdoorFile && !ocrResult && (
        <div className="bg-blue-50 border border-blue-100 rounded-xl p-3">
          <p className="text-xs font-bold text-blue-800 mb-1.5">📸 Tips for a clear nameplate photo</p>
          <ul className="space-y-1">
            {[
              "Use flashlight in dark areas",
              "Hold phone steady — tap screen to focus",
              "Fill the frame with the nameplate",
              "Avoid glare — angle slightly if needed",
            ].map(tip => (
              <li key={tip} className="text-xs text-blue-700 flex items-center gap-1.5">
                <span className="text-blue-400">·</span> {tip}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Extract button */}
      {outdoorFile && !ocrResult && (
        <div className="space-y-2">
          <button
            onClick={runOCR}
            disabled={loading}
            className="w-full py-3.5 rounded-xl font-black text-white text-sm transition-all"
            style={{ background: loading ? "#ccc" : "#f39c12" }}
          >
            {loading ? "Reading nameplate..." : "Extract Specs with AI"}
          </button>
          {/* Section 5B-3: Photo unclear fallback */}
          {(outdoorQuality?.blurry || outdoorQuality?.tooDark) && (
            <button
              onClick={onSkip}
              className="w-full py-2.5 rounded-xl text-xs font-bold text-gray-500 border border-gray-200 hover:border-gray-300 transition-colors"
            >
              Photo too unclear — enter specs manually instead
            </button>
          )}
        </div>
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

          {editedUnit.charging_method && (
            <div className="px-4 pt-2.5 flex gap-2 flex-wrap">
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

        </> /* end activeTab === "photo" */
      )}

    </div>
  );
}
