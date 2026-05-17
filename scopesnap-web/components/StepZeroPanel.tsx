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
import { detectMarket } from "@/lib/market";
import { isOffline, subscribeToQueueCount, saveToOfflineQueue } from "@/lib/offlineQueue";
import { runTesseractOcr, terminateTesseractWorker } from "@/lib/tesseractOcr";

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
  /** Section 6B: which engine produced this result */
  source?:            "gemini" | "tesseract" | "manual";
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
// Removed: serial_number, factory_charge_oz, voltage (not used in diagnostics)
// badge: "db"  → value sourced from model-DB lookup (green "DB")
// badge: "est" → value inferred / estimated (orange "Est.")
// badge: null  → no badge (plain entry)

const OCR_FIELDS: {
  key: keyof NameplateUnit;
  label: string;
  unit?: string;
  type: "text" | "number";
  badge?: "db" | "est" | null;
}[] = [
  { key: "model_number",  label: "Model #",     type: "text",   badge: "db"  },
  { key: "tonnage",       label: "Tonnage",      unit: "ton",    type: "number", badge: "db"  },
  { key: "refrigerant",   label: "Refrigerant",  type: "text",   badge: "db"  },
  { key: "rla",           label: "RLA",          unit: "A",      type: "number", badge: "db"  },
  { key: "lra",           label: "LRA",          unit: "A",      type: "number", badge: "db"  },
  { key: "capacitor_uf",  label: "Cap",          unit: "µF",     type: "text",   badge: "est" },
  { key: "mca",           label: "MCA",          unit: "A",      type: "number", badge: "db"  },
  { key: "mocp",          label: "MOCP",         unit: "A",      type: "number", badge: "db"  },
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

  // ── Section 6B/6C: Offline + Tesseract state ───────────────────────────
  const [ocrSource,       setOcrSource]      = useState<"gemini" | "tesseract" | null>(null);
  const [tesseractPct,    setTesseractPct]   = useState<number>(0);
  const [tesseractStatus, setTesseractStatus] = useState<string>("");
  const [offlineCount,    setOfflineCount]   = useState<number>(0);
  const [savedOffline,    setSavedOffline]   = useState(false);

  // Subscribe to offline queue count
  useEffect(() => {
    const unsub = subscribeToQueueCount(setOfflineCount);
    return unsub;
  }, []);

  // Terminate Tesseract worker when component unmounts
  useEffect(() => {
    return () => { terminateTesseractWorker().catch(() => {}); };
  }, []);

  // ── Market detection (useEffect so it runs after hydration, not SSR) ──
  const [isPK, setIsPK] = useState(false);
  useEffect(() => { setIsPK(detectMarket() === "PK"); }, []);

  // ── Section 5C: Manual entry tab ───────────────────────────────────────
  const [activeTab, setActiveTab] = useState<"photo" | "manual">("manual");
  const BLANK_UNIT: NameplateUnit = {
    model_number: null, serial_number: null, tonnage: null, refrigerant: null,
    factory_charge_oz: null, rla: null, lra: null, capacitor_uf: null,
    mca: null, mocp: null, voltage: null, brand_id: null, series_id: null,
    charging_method: null, metering_device: null, is_legacy: false,
    year_of_manufacture: null, r22_alert: false, confidence: 100, notes: null,
  };
  const [manualUnit, setManualUnit] = useState<NameplateUnit>({ ...BLANK_UNIT });
  // PK-only: explicit refrigerant selection ("R-32" | "R-410A" | "R-22" | "not_sure")
  const [pkRefrigerant, setPkRefrigerant] = useState<string>("not_sure");

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
    if (!selectedBrand || selectedBrand === "__unlisted__") {
      setModelResults([]);
      setShowModelDropdown(false);
      return;
    }
    const t = setTimeout(async () => {
      setModelSearching(true);
      try {
        const results = await searchModels(selectedBrand, modelQuery, undefined, 50);
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
      // Refrigerant: derive from manufacture_years — US only; PK uses explicit picker
      if (!isPK && model.manufacture_years) {
        const yearStr = model.manufacture_years.split("-")[0].trim();
        const yr = parseInt(yearStr, 10);
        if (!isNaN(yr)) {
          if (yr < 2010) {
            next.refrigerant = "R-22";
            next.r22_alert   = true;
            next.is_legacy   = true;
          } else if (yr >= 2023) {
            next.refrigerant = "R-454B";
            next.r22_alert   = false;
          } else {
            next.refrigerant = "R-410A";
            next.r22_alert   = false;
          }
        }
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
      // 5D-1: auto-set refrigerant from year_of_manufacture — US only; PK uses explicit picker
      if (!isPK && key === "year_of_manufacture" && parsed !== null) {
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
    // PK: bake the picker selection into the outdoor unit before confirming
    const outdoor = isPK
      ? { ...manualUnit, refrigerant: pkRefrigerant }
      : { ...manualUnit };
    const result: OcrResult = {
      outdoor,
      indoor: null,
      captured_at: new Date().toISOString(),
      capture_method: "manual",
      d7_brand_detected: false,
      d7_brand_name: null,
    };
    onConfirm(result);
  }, [manualUnit, pkRefrigerant, isPK, onConfirm]);

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

  // ── Section 6B: Hybrid OCR pipeline — Gemini first, Tesseract fallback ──
  const runOCR = useCallback(async () => {
    if (!outdoorFile) {
      setError("Please capture the outdoor unit nameplate first.");
      return;
    }

    setLoading(true);
    setError(null);
    setOcrResult(null);
    setOcrSource(null);
    setSavedOffline(false);

    // ── Branch A: Device is fully offline → queue for later ────────────────
    if (isOffline()) {
      try {
        await saveToOfflineQueue(
          [outdoorFile, ...(indoorFile ? [indoorFile] : [])],
          { address: "", customerName: "", customerPhone: "" }
        );
        setSavedOffline(true);
      } catch {
        setError("Offline and could not save to queue. Please retry when connected.");
      } finally {
        setLoading(false);
      }
      return;
    }

    // ── Branch B: Try Gemini AI first ──────────────────────────────────────
    const IS_DEV = process.env.NEXT_PUBLIC_ENV === "development";
    const headers: Record<string, string> = {};
    if (clerkToken) {
      headers["Authorization"] = `Bearer ${clerkToken}`;
    } else if (IS_DEV) {
      headers["X-Dev-Clerk-User-Id"] = "test_user_mike";
    }

    let geminiSucceeded = false;

    try {
      const fd = new FormData();
      fd.append("outdoor_photo", outdoorFile);
      if (indoorFile) fd.append("indoor_photo", indoorFile);

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
      const withSource: OcrResult = { ...result, source: "gemini" };
      setOcrResult(withSource);
      setEditedUnit({ ...result.outdoor });
      setOcrSource("gemini");
      geminiSucceeded = true;
    } catch (geminiErr) {
      // Gemini failed — fall through to Tesseract
      console.warn("[OCR] Gemini failed, trying local Tesseract:", geminiErr);
    }

    // ── Branch C: Tesseract local fallback ─────────────────────────────────
    if (!geminiSucceeded) {
      try {
        setTesseractPct(0);
        setTesseractStatus("Starting local OCR…");

        const tessResult = await runTesseractOcr(
          outdoorFile,
          indoorFile ?? undefined,
          (pct, status) => {
            setTesseractPct(pct);
            setTesseractStatus(status);
          }
        );

        const asOcrResult: OcrResult = {
          outdoor:           tessResult.outdoor,
          indoor:            tessResult.indoor,
          captured_at:       tessResult.captured_at,
          capture_method:    "tesseract",
          source:            "tesseract",
          d7_brand_detected: tessResult.d7_brand_detected,
          d7_brand_name:     tessResult.d7_brand_name,
        };

        setOcrResult(asOcrResult);
        setEditedUnit({ ...tessResult.outdoor });
        setOcrSource("tesseract");
      } catch (tessErr) {
        setError(
          "Both AI and local OCR failed. Check your connection and try again, or use Manual Entry."
        );
        console.error("[OCR] Tesseract also failed:", tessErr);
      }
    }

    setLoading(false);
    setTesseractPct(0);
    setTesseractStatus("");
  }, [outdoorFile, indoorFile, clerkToken]);

  // ── Auto-trigger OCR when outdoor photo is captured ─────────────────────
  useEffect(() => {
    if (!outdoorFile || ocrResult || loading) return;
    const timer = setTimeout(runOCR, 300); // small delay lets UI settle
    return () => clearTimeout(timer);
  }, [outdoorFile]); // eslint-disable-line react-hooks/exhaustive-deps

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

      {/* Section 6C: Offline saved banner */}
      {savedOffline && (
        <div className="flex items-start gap-3 bg-amber-50 border border-amber-200 rounded-2xl p-3">
          <span className="text-amber-500 text-xl flex-shrink-0">📶</span>
          <div>
            <p className="text-sm font-black text-amber-800">Saved for when you're back online</p>
            <p className="text-xs text-amber-700 mt-0.5">
              This assessment will upload automatically once your connection is restored.
            </p>
          </div>
        </div>
      )}

      {/* Section 6C: Offline queue badge — shown when items are waiting to sync */}
      {offlineCount > 0 && !savedOffline && (
        <div className="flex items-center gap-2 bg-orange-50 border border-orange-200 rounded-xl px-3 py-2">
          <span className="text-orange-500 text-sm">⏳</span>
          <p className="text-xs font-bold text-orange-800 flex-1">
            {offlineCount} assessment{offlineCount > 1 ? "s" : ""} waiting to sync
          </p>
          <span className="text-[10px] text-orange-400">Auto-syncs on reconnect</span>
        </div>
      )}

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
                  {/* Task-9: escape hatch so tech can proceed without a DB match */}
                  <option value="__unlisted__">My brand isn't listed…</option>
                </select>
                {selectedBrand === "__unlisted__" && (
                  <div className="mt-2 flex items-start gap-2 bg-amber-50 border border-amber-200 rounded-xl px-3 py-2">
                    <span className="text-amber-500 flex-shrink-0">ℹ</span>
                    <div>
                      <p className="text-xs font-bold text-amber-800">Brand not in database</p>
                      <p className="text-xs text-amber-700 mt-0.5">
                        Enter specs manually below. No DB auto-fill — use nameplate values.
                      </p>
                    </div>
                  </div>
                )}
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
                    onFocus={() => setShowModelDropdown(true)}
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
                      <span className="text-xs text-green-600 ml-2">({manualUnit.tonnage}t</span>
                    )}
                    {!isPK && manualUnit.refrigerant && (
                      <span className="text-xs text-green-600">, {manualUnit.refrigerant} auto-filled)</span>
                    )}
                    {!isPK && manualUnit.tonnage && !manualUnit.refrigerant && (
                      <span className="text-xs text-green-600"> auto-filled)</span>
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

          {/* ── PK-only: Refrigerant Picker ───────────────────────────────────── */}
          {isPK && (
            <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden">
              <div className="px-4 py-2.5 border-b border-gray-100">
                <span className="text-xs font-black uppercase tracking-wider text-blue-600">
                  ❄️ Refrigerant Type
                </span>
              </div>
              <div className="p-3">
                <p className="text-[10px] text-gray-400 mb-2">
                  Check the nameplate or outdoor unit label. If unknown, select "Not Sure".
                </p>
                <div className="grid grid-cols-2 gap-2">
                  {(["R-32", "R-410A", "R-22", "not_sure"] as const).map((ref) => {
                    const label = ref === "not_sure" ? "Not Sure" : ref;
                    const desc: Record<string, string> = {
                      "R-32":    "Newer inverter units",
                      "R-410A":  "Common 2010–2022",
                      "R-22":    "Older / legacy units",
                      "not_sure": "Use R-410A targets",
                    };
                    const isSelected = pkRefrigerant === ref;
                    return (
                      <button
                        key={ref}
                        onClick={() => setPkRefrigerant(ref)}
                        className="flex flex-col items-start px-3 py-2 rounded-xl border-2 transition-all text-left"
                        style={{
                          borderColor: isSelected ? "#1a8754" : "#e2dfd7",
                          background:  isSelected ? "#f0faf6" : "#fafaf8",
                        }}
                      >
                        <span
                          className="text-sm font-black"
                          style={{ color: isSelected ? "#1a8754" : "#374151" }}
                        >
                          {label}
                        </span>
                        <span className="text-[10px] text-gray-400 mt-0.5">{desc[ref]}</span>
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
          )}

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
            <div className="px-4 py-2.5 border-b border-gray-100 flex items-center justify-between">
              <span className="text-xs font-black uppercase tracking-wider text-gray-500">
                Enter specs manually
              </span>
              {/* Path B notice: if tonnage filled but no model match, show generic-range note */}
              {manualUnit.tonnage && !manualUnit.series_id && (
                <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded"
                      style={{ background: "#fff3e0", color: "#c4600a" }}>
                  Path B — generic ranges
                </span>
              )}
            </div>
            <div className="p-3 grid grid-cols-2 gap-2">
              {OCR_FIELDS.filter(f => !(isPK && f.key === "refrigerant")).map(({ key, label, unit, type, badge }) => {
                const val = manualUnit[key];
                const displayVal = val === null || val === undefined ? "" : String(val);
                const isEmpty = displayVal === "";
                const isDbField  = badge === "db"  && !isEmpty && !!manualUnit.series_id;
                const isEstField = badge === "est";
                return (
                  <div key={key} className="flex flex-col gap-0.5">
                    <div className="flex items-center gap-1">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400">
                        {label}
                        {key === "refrigerant" && !isPK && <span className="text-blue-400 ml-1">(auto)</span>}
                      </span>
                      {isDbField && (
                        <span className="text-[9px] font-black px-1 py-0.5 rounded"
                              style={{ background: "#e8f5ee", color: "#1a8754" }}>DB</span>
                      )}
                      {isEstField && (
                        <span className="text-[9px] font-black px-1 py-0.5 rounded"
                              style={{ background: "#fff3e0", color: "#c4600a" }}>Est.</span>
                      )}
                    </div>
                    <div className="relative flex items-center">
                      <input
                        type={type === "number" ? "number" : "text"}
                        value={displayVal}
                        onChange={e => updateManualField(key, e.target.value)}
                        placeholder="—"
                        className="w-full text-sm font-mono font-bold rounded-lg border px-2 py-1.5 focus:outline-none transition-colors"
                        style={{
                          borderColor: isEmpty ? "#e2dfd7" : isEstField ? "#c4600a" : "#1a8754",
                          background:  isEmpty ? "#fafaf8" : isEstField ? "#fffaf5" : "#f0faf6",
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
              onClick={handleManualConfirm}
              className="w-full py-3 px-6 rounded-xl text-sm font-black text-white transition-all"
              style={{ background: "#1a8754" }}
            >
              Confirm & Continue
            </button>
          </div>
          <p className="text-center text-xs text-gray-400">
            {isPK
              ? "Select refrigerant type above for accurate pressure targets"
              : "Year field auto-selects R-22, R-410A, or R-454B"}
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

      {/* Section 5B-3: Photo unclear fallback */}
      {outdoorFile && !ocrResult && (outdoorQuality?.blurry || outdoorQuality?.tooDark) && (
        <button
          onClick={() => setActiveTab("manual")}
          className="w-full py-2.5 rounded-xl text-xs font-bold text-gray-500 border border-gray-200 hover:border-gray-300 transition-colors"
        >
          Photo too unclear — enter specs manually instead
        </button>
      )}

      {/* Section 6B: Loading indicator — Gemini or Tesseract progress */}
      {loading && (
        <div className="space-y-2">
          <div className="flex items-center justify-center gap-3 py-2">
            {[0,1,2].map(i => (
              <div key={i} className="w-2.5 h-2.5 rounded-full animate-bounce"
                   style={{ background: "#f39c12", animationDelay: `${i * 0.15}s` }} />
            ))}
            <span className="text-sm text-gray-500 font-medium">
              {tesseractPct > 0 ? tesseractStatus : "Gemini reading nameplate…"}
            </span>
          </div>
          {/* Tesseract progress bar */}
          {tesseractPct > 0 && (
            <div className="mx-2">
              <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-300"
                  style={{ width: `${tesseractPct}%`, background: "#f39c12" }}
                />
              </div>
              <p className="text-[10px] text-center text-amber-600 mt-1 font-semibold">
                Local OCR fallback — AI not reachable
              </p>
            </div>
          )}
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
            <div className="flex items-center gap-2">
              <span className="text-xs font-black uppercase tracking-wider text-green-600">
                {ocrSource === "tesseract" ? "Local OCR" : "AI Extracted"} — verify &amp; edit
              </span>
              {/* Section 6B: source badge */}
              {ocrSource && (
                <span
                  className="text-[10px] font-bold px-1.5 py-0.5 rounded-full"
                  style={{
                    background: ocrSource === "gemini" ? "#e8f5ee" : "#fff3e0",
                    color:      ocrSource === "gemini" ? "#1a8754" : "#c4600a",
                  }}
                >
                  {ocrSource === "gemini" ? "✶ Gemini AI" : "📱 Local OCR"}
                </span>
              )}
            </div>
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
            {OCR_FIELDS.map(({ key, label, unit, type, badge }) => {
              const val = editedUnit[key];
              const displayVal = val === null || val === undefined ? "" : String(val);
              const isEmpty = displayVal === "";
              const isDbField  = badge === "db"  && !isEmpty;
              const isEstField = badge === "est";
              return (
                <div key={key} className="flex flex-col gap-0.5">
                  <div className="flex items-center gap-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400">{label}</span>
                    {isDbField && (
                      <span className="text-[9px] font-black px-1 py-0.5 rounded"
                            style={{ background: "#e8f5ee", color: "#1a8754" }}>DB</span>
                    )}
                    {isEstField && (
                      <span className="text-[9px] font-black px-1 py-0.5 rounded"
                            style={{ background: "#fff3e0", color: "#c4600a" }}>Est.</span>
                    )}
                  </div>
                  <div className="relative flex items-center">
                    <input
                      type={type === "number" ? "number" : "text"}
                      value={displayVal}
                      onChange={e => updateField(key, e.target.value)}
                      placeholder="—"
                      className="w-full text-sm font-mono font-bold rounded-lg border px-2 py-1.5 focus:outline-none focus:ring-1 transition-colors"
                      style={{
                        borderColor: isEmpty ? "#e2dfd7" : isEstField ? "#c4600a" : "#1a8754",
                        background:  isEmpty ? "#fafaf8" : isEstField ? "#fffaf5" : "#f0faf6",
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

      {/* Confirm */}
      {editedUnit && (
        <div className="flex gap-3">
          <button
            onClick={handleConfirm}
            className="w-full py-3 px-6 rounded-xl text-sm font-black text-white transition-all"
            style={{ background: "#1a8754" }}
          >
            Confirm & Continue
          </button>
        </div>
      )}

      <p className="text-center text-xs text-gray-400">
        Nameplate specs auto-fill all cards — save time on every call
      </p>

        </> /* end activeTab === "photo" */
      )}

    </div>
  );
}
          