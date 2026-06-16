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
import { useAuth } from "@clerk/nextjs";
import { API_URL } from "@/lib/api";
import { checkImageQuality, type ImageQualityResult } from "@/lib/imageQuality";
import { getBrands, searchModels, type EquipmentModelRecord } from "@/lib/modelCache";
import { detectMarket } from "@/lib/market";
import { useLang } from "@/lib/language-context";
import { isOffline, subscribeToQueueCount, saveToOfflineQueue } from "@/lib/offlineQueue";

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
  /** PK market only — "inverter" | "non_inverter" | null */
  series_type?:       string | null;
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
  /** Stage 3A — install-year review fields, wired to the fault-card estimate request */
  install_year?:      number | null;
  age_source?:        string | null;
  age_confidence?:    "sure" | "approximate" | "unknown" | null;
}

interface Props {
  assessmentId?: string;  // set once assessment is created (for persisting)
  clerkToken: string | null;
  onConfirm: (result: OcrResult, ambientC: number) => void;
  onSkip: () => void;
  /** TEST-ONLY: seed a decoded unit to drive the Stage 3A prefill deterministically
   *  from the dev test-harness (never passed by the real /assess route). */
  __testSeedUnit?: NameplateUnit | null;
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
  { key: "rla",           label: "RLA",          unit: "A",      type: "number", badge: "est" },
  { key: "lra",           label: "LRA",          unit: "A",      type: "number", badge: "est" },
  { key: "capacitor_uf",  label: "Cap",          unit: "µF",     type: "text",   badge: "est" },
  { key: "mca",           label: "MCA",          unit: "A",      type: "number", badge: "est" },
  { key: "mocp",          label: "MOCP",         unit: "A",      type: "number", badge: "est" },
];

// ── Electrical spec defaults by tonnage (ac_data_repo.json §electrical_specs_by_tonnage) ──────
// Used to auto-fill RLA/LRA/MCA/MOCP/Cap when a model is selected from the DB.
// Values are midpoints from the reference ranges.
const ELECTRICAL_SPECS_BY_TONNAGE: Record<number, {
  rla: number; lra: number; mca: number; mocp: number; capacitor_uf: string;
}> = {
  1.5: { rla: 7.2,  lra: 45,  mca: 11.0, mocp: 15, capacitor_uf: "25/5 MFD 370V or 440V" },
  2.0: { rla: 9.5,  lra: 55,  mca: 13.5, mocp: 20, capacitor_uf: "35/5 MFD 370V or 440V" },
  2.5: { rla: 11.8, lra: 64,  mca: 16.5, mocp: 25, capacitor_uf: "40/5 MFD 370V or 440V" },
  3.0: { rla: 14.0, lra: 74,  mca: 19.0, mocp: 30, capacitor_uf: "45/5 MFD 370V or 440V" },
  3.5: { rla: 16.2, lra: 86,  mca: 22.5, mocp: 35, capacitor_uf: "50/5 MFD 370V or 440V" },
  4.0: { rla: 19.2, lra: 97,  mca: 26.0, mocp: 40, capacitor_uf: "55/5 MFD 370V or 440V" },
  5.0: { rla: 22.8, lra: 117, mca: 31.5, mocp: 50, capacitor_uf: "60/5 MFD 370V or 440V" },
};

// ── Component ────────────────────────────────────────────────────────────────

export default function StepZeroPanel({ assessmentId, clerkToken, onConfirm, onSkip, __testSeedUnit }: Props) {
  const { t } = useLang();
  // BUG-034 Root Cause A fix: get live Clerk JWT instead of relying on prop (which was hardcoded null)
  const { getToken } = useAuth();
  const [outdoorFile,  setOutdoorFile]  = useState<File | null>(null);
  const [indoorFile,   setIndoorFile]   = useState<File | null>(null);
  const [outdoorPreview, setOutdoorPreview] = useState<string | null>(null);
  const [indoorPreview,  setIndoorPreview]  = useState<string | null>(null);
  const [loading,      setLoading]      = useState(false);
  const [error,        setError]        = useState<string | null>(null);
  const [ocrResult,    setOcrResult]    = useState<OcrResult | null>(null);
  // Ambient temperature bucket — drives PSI threshold lookup in operating_targets
  // "mild" = 25°C (<86°F), "hot" = 35°C (86-100°F, default Houston summer), "extreme" = 40°C (>100°F)
  const [ambientBucket, setAmbientBucket] = useState<"mild" | "hot" | "extreme">("hot");
  const AMBIENT_C_MAP: Record<"mild" | "hot" | "extreme", number> = { mild: 25, hot: 35, extreme: 40 };
  const [editedUnit,   setEditedUnit]   = useState<NameplateUnit | null>(null);

  // TEST-ONLY: seed a decoded unit (from the dev harness) so Playwright can drive
  // the Stage 3A install-year prefill without the auth-gated OCR/upload pipeline.
  useEffect(() => {
    if (__testSeedUnit) setEditedUnit(__testSeedUnit as NameplateUnit);
  }, [__testSeedUnit]);

  // ── Stage 3A: install-year + age-confidence review ─────────────────────────
  // Year picker range 1980–2026. Confidence: Sure / Approximate / Unknown.
  const AGE_YEAR_MIN = 1980;
  const AGE_YEAR_MAX = 2026;
  const [installYear, setInstallYear] = useState<number | null>(null);
  const [ageConfidence, setAgeConfidence] = useState<"sure" | "approximate" | "unknown">("unknown");
  // age_source describes WHERE the year came from (drives backend reliable-age gate)
  const [ageSource, setAgeSource] = useState<string>("unknown");
  // Legacy-brand estimate badge: shown when year was derived from a discontinued brand midpoint
  const [ageIsLegacyEstimate, setAgeIsLegacyEstimate] = useState<boolean>(false);
  // Track whether the tech has manually touched the year/confidence (then we stop auto-prefilling)
  const ageTouchedRef = useRef<boolean>(false);

  const outdoorInputRef = useRef<HTMLInputElement>(null);
  const indoorInputRef  = useRef<HTMLInputElement>(null);

  // ── Blur / quality warnings (Section 5B) ──────────────────────────────
  const [outdoorQuality, setOutdoorQuality] = useState<ImageQualityResult | null>(null);
  const [indoorQuality,  setIndoorQuality]  = useState<ImageQualityResult | null>(null);

  // ── Section 6B/6C: Offline state ────────────────────────────────────────
  const [offlineCount,    setOfflineCount]   = useState<number>(0);
  const [savedOffline,    setSavedOffline]   = useState(false);
  // BUG-034: fields with confidence 40-69 get yellow border (needs-confirmation)
  const [needsConfirmationFields, setNeedsConfirmationFields] = useState<Set<string>>(new Set());
  const [confirmationHeading, setConfirmationHeading] = useState<string | null>(null);

  // Subscribe to offline queue count
  useEffect(() => {
    const unsub = subscribeToQueueCount(setOfflineCount);
    return unsub;
  }, []);

  // ── Market detection (useEffect so it runs after hydration, not SSR) ──
  const [isPK, setIsPK] = useState(false);
  useEffect(() => { setIsPK(detectMarket() === "PK"); }, []);

  // ── Section 5C: Manual entry tab ───────────────────────────────────────
  const [activeTab, setActiveTab] = useState<"photo" | "manual">("photo");

  // Scenario D — restore last-used path; Scenario E — A/B variant for new users
  useEffect(() => {
    if (typeof window === "undefined") return;
    const saved = localStorage.getItem("snap_sz_path") as "photo" | "manual" | null;
    if (saved) {
      // Returning user: restore last-used path
      setActiveTab(saved);
    } else {
      // New user: assign 50/50 A/B variant and fire telemetry
      const variant: "photo" | "manual" = Math.random() < 0.5 ? "photo" : "manual";
      localStorage.setItem("snap_sz_variant", variant);
      (window as Window & { posthog?: { capture?: (e: string, p: Record<string, unknown>) => void } })
        .posthog?.capture?.("ab_test_variant_assigned", {
          default_path_variant: variant,
          market: detectMarket(),
        });
      if (variant === "manual") setActiveTab("manual");
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  /** Explicit user-initiated tab switch — persists preference for Scenario D */
  const handleTabSelect = (tab: "photo" | "manual") => {
    localStorage.setItem("snap_sz_path", tab);
    setActiveTab(tab);
  };
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
  // PK-only: selected tonnage key from tonnage_data (e.g. "1.5", "2.0")
  const [pkSelectedTonnageKey, setPkSelectedTonnageKey] = useState<string | null>(null);
  // PK-only: tonnage_data from the selected model record
  const [pkTonnageData, setPkTonnageData] = useState<EquipmentModelRecord["tonnage_data"] | null>(null);
  const [selectedSeriesType, setSelectedSeriesType] = useState<string | null>(null);

  // B.3: Auto-select PK refrigerant based on manufacture year + inverter type
  useEffect(() => {
    if (!isPK || manualUnit.year_of_manufacture === null) return;
    const yr = manualUnit.year_of_manufacture as number;
    if (yr >= 2018 && selectedSeriesType === "inverter") {
      setPkRefrigerant("R-32");
    } else if (yr >= 2010) {
      setPkRefrigerant("R-410A");
    } else {
      setPkRefrigerant("R-22");
    }
  }, [isPK, manualUnit.year_of_manufacture, selectedSeriesType]);

  // ── Section 5A: Brand/model lookup ─────────────────────────────────────────
  const [brands,           setBrands]           = useState<Array<{ brand: string; model_count: number }>>([]);
  const [brandsLoading,    setBrandsLoading]    = useState(false);
  const [selectedBrand,    setSelectedBrand]    = useState<string>("");
  const [modelQuery,       setModelQuery]       = useState<string>("");
  const [modelResults,     setModelResults]     = useState<EquipmentModelRecord[]>([]);
  const [modelSearching,   setModelSearching]   = useState(false);
  const [showModelDropdown, setShowModelDropdown] = useState(false);
  // BUG-011: Track which DB-filled fields the tech has manually edited
  const [editedManualFields, setEditedManualFields] = useState<Set<string>>(new Set());

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
    // PK: store tonnage_data and reset selected tonnage key (user picks via picker)
    if (isPK) {
      setPkTonnageData(model.tonnage_data ?? null);
      setPkSelectedTonnageKey(null);
      setSelectedSeriesType(model.series_type ?? null);
    }
    setManualUnit(prev => {
      const next = { ...prev };
      next.brand_id   = model.brand;
      next.series_id  = model.model_series;
      next.model_number = model.model_series;
      // Tonnage: PK — clear until user picks via picker; US — parse range midpoint
      if (!isPK && model.tonnage_range) {
        const parts = model.tonnage_range.split("-").map(Number).filter(n => !isNaN(n));
        if (parts.length === 2) next.tonnage = Math.round((parts[0] + parts[1]) / 2 * 2) / 2;
        else if (parts.length === 1) next.tonnage = parts[0];
      } else if (isPK) {
        next.tonnage = null; // cleared — awaiting PK tonnage picker
        next.rla = null; next.lra = null; next.mca = null;
        next.mocp = null; next.capacitor_uf = null;
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
      // US only: electrical spec estimation from reference table (ac_data_repo.json)
      // PK: specs come from tonnage_data via applyPkTonnage below
      if (!isPK && next.tonnage !== null) {
        const elecSpec = ELECTRICAL_SPECS_BY_TONNAGE[next.tonnage];
        if (elecSpec) {
          if (next.rla === null)          next.rla          = elecSpec.rla;
          if (next.lra === null)          next.lra          = elecSpec.lra;
          if (next.mca === null)          next.mca          = elecSpec.mca;
          if (next.mocp === null)         next.mocp         = elecSpec.mocp;
          if (next.capacitor_uf === null) next.capacitor_uf = elecSpec.capacitor_uf;
        }
      }
      return next;
    });
    setShowModelDropdown(false);
    setEditedManualFields(new Set()); // Reset edited badges when new model applied
  }, [isPK]);

  /** PK only — apply electrical specs for the chosen tonnage key (e.g. "1.5") */
  const applyPkTonnage = useCallback((key: string) => {
    setPkSelectedTonnageKey(key);
    const td = pkTonnageData?.[key];
    const tonNum = parseFloat(key);
    setManualUnit(prev => {
      const next = { ...prev, tonnage: isNaN(tonNum) ? prev.tonnage : tonNum };
      if (td) {
        const amps = td.electrical?.amps;
        const cap  = td.capacitors;
        // Compressor cap + indoor fan cap, formatted like "25/5 µF"
        const capStr = cap?.compressor_uf != null && cap?.indoor_fan_uf != null
          ? `${cap.compressor_uf}/${cap.indoor_fan_uf} µF`
          : cap?.compressor_uf != null ? `${cap.compressor_uf} µF` : null;
        if (amps?.rated != null) next.rla = amps.rated;
        if (amps?.lra   != null) next.lra = amps.lra;
        if (td.electrical?.mca  != null) next.mca  = td.electrical.mca;
        if (td.electrical?.mop  != null) next.mocp = td.electrical.mop;
        if (capStr) next.capacitor_uf = capStr;
      }
      return next;
    });
    setEditedManualFields(new Set()); // fresh DB badges
  }, [pkTonnageData]);

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
    // BUG-011: mark this field as manually edited so badge flips to "✏ Edited"
    setEditedManualFields(prev => { const next = new Set(prev); next.add(String(key)); return next; });
  }, []);

  // ── Stage 3A: derive install-year + age confidence from decoder output ──────
  // Runs when the active unit (photo OCR result OR manual DB-matched unit) changes.
  // Pre-fills only while the tech has NOT manually overridden the fields.
  const activeAgeUnit: NameplateUnit | null = editedUnit ?? (manualUnit.series_id || manualUnit.year_of_manufacture !== null ? manualUnit : null);
  useEffect(() => {
    if (ageTouchedRef.current) return;            // tech is in control — never clobber edits
    const unit = activeAgeUnit;
    if (!unit) return;
    const decodeConf = typeof unit.confidence === "number" ? unit.confidence : 0;
    const yr = unit.year_of_manufacture;

    // Legacy brand (discontinued) → pre-fill computed midpoint year (already on the unit),
    // show an "estimated from brand discontinue" badge, confidence = approximate.
    if (unit.is_legacy && yr != null) {
      setInstallYear(yr);
      setAgeConfidence("approximate");
      setAgeSource("legacy_brand_age_floor");
      setAgeIsLegacyEstimate(true);
      return;
    }

    // High-confidence decode (>=70) → pre-fill year, confidence = Sure.
    // Medium (40-69) → pre-fill year, confidence = Approximate.
    if (yr != null && decodeConf >= 70) {
      setInstallYear(yr);
      setAgeConfidence("sure");
      setAgeSource("serial_decode_high");
      setAgeIsLegacyEstimate(false);
      return;
    }
    if (yr != null && decodeConf >= 40) {
      setInstallYear(yr);
      setAgeConfidence("approximate");
      setAgeSource("serial_decode_medium");
      setAgeIsLegacyEstimate(false);
      return;
    }

    // Decode failed / low / unknown → leave year BLANK, confidence = unknown.
    // No yellow highlight, no alarm — just an empty input with an "Ask homeowner" hint.
    setInstallYear(null);
    setAgeConfidence("unknown");
    setAgeSource("unknown");
    setAgeIsLegacyEstimate(false);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeAgeUnit?.year_of_manufacture, activeAgeUnit?.confidence, activeAgeUnit?.is_legacy, activeAgeUnit?.series_id]);

  /** Stage 3A — user picks/edits the install year. Marks the field as tech-controlled. */
  const handleInstallYearChange = useCallback((raw: string) => {
    ageTouchedRef.current = true;
    setAgeIsLegacyEstimate(false);
    if (raw === "") {
      setInstallYear(null);
      // Blank year → unknown confidence + source (matches backend "unknown" gate).
      setAgeConfidence("unknown");
      setAgeSource("unknown");
      return;
    }
    const n = parseInt(raw, 10);
    if (Number.isNaN(n)) return;
    setInstallYear(n);
    // A tech-entered year is a plate/homeowner observation, not a decode.
    if (ageSource === "unknown") setAgeSource("plate_date");
  }, [ageSource]);

  /** Stage 3A — user overrides the age-confidence selector. */
  const handleAgeConfidenceChange = useCallback((c: "sure" | "approximate" | "unknown") => {
    ageTouchedRef.current = true;
    setAgeConfidence(c);
    if (c === "sure" && (ageSource === "unknown" || ageSource === "plate_date")) {
      setAgeSource("homeowner_sure");
    } else if (c === "approximate" && (ageSource === "unknown" || ageSource === "plate_date")) {
      setAgeSource("homeowner_approximate");
    } else if (c === "unknown") {
      setAgeSource("unknown");
    }
  }, [ageSource]);

  /** Stage 3A — stash the captured age data so the fault-card estimate request can read it. */
  const persistAgeForEstimate = useCallback((iy: number | null, src: string, conf: string) => {
    if (typeof window === "undefined") return;
    try {
      if (iy == null) {
        sessionStorage.removeItem("snap_age_capture");
      } else {
        sessionStorage.setItem("snap_age_capture", JSON.stringify({
          install_year: iy, age_source: src, age_confidence: conf,
        }));
      }
    } catch { /* sessionStorage unavailable — non-fatal */ }
  }, []);

  /** Confirm manual entry — wraps manualUnit into an OcrResult */
  const handleManualConfirm = useCallback(() => {
    // PK: bake the picker selection into the outdoor unit before confirming
    const outdoor = isPK
      ? { ...manualUnit, refrigerant: pkRefrigerant, series_type: selectedSeriesType }
      : { ...manualUnit };
    // Stage 3A: carry install-year + age confidence/source through to the estimate.
    persistAgeForEstimate(installYear, ageSource, ageConfidence);
    const result: OcrResult = {
      outdoor,
      indoor: null,
      captured_at: new Date().toISOString(),
      capture_method: "manual",
      d7_brand_detected: false,
      d7_brand_name: null,
      install_year: installYear,
      age_source: ageSource,
      age_confidence: ageConfidence,
    };
    onConfirm(result, AMBIENT_C_MAP[ambientBucket]);
  }, [manualUnit, pkRefrigerant, isPK, onConfirm, ambientBucket, installYear, ageSource, ageConfidence, persistAgeForEstimate]);

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

  // ── Section 6B: OCR pipeline — Gemini AI → DB lookup → Manual entry ──────
  // BUG-034: Root Cause A fix (live JWT) + Root Cause B fix (Tesseract removed)
  const runOCR = useCallback(async () => {
    if (!outdoorFile) {
      setError("Please capture the outdoor unit nameplate first.");
      return;
    }

    setLoading(true);
    setError(null);
    setOcrResult(null);
    setSavedOffline(false);
    setNeedsConfirmationFields(new Set());
    setConfirmationHeading(null);

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

    // ── Tier 1: Gemini AI OCR ─────────────────────────────────────────────────
    // BUG-034 Root Cause A: get live JWT from Clerk (prop was hardcoded null in page.tsx)
    const IS_DEV = process.env.NEXT_PUBLIC_ENV === "development";
    const market = detectMarket(); // BUG-034: market-aware header
    let token: string | null = null;
    if (!IS_DEV) {
      try { token = await getToken(); } catch { token = null; }
    }

    const authHeaders: Record<string, string> = {
      "X-Market": market, // BUG-034: market-aware OCR (Root Cause A companion)
      ...(IS_DEV
        ? { "X-Dev-Clerk-User-Id": "test_user_mike" }
        : token ? { "Authorization": `Bearer ${token}` } : {}),
    };

    const tStart = Date.now();
    let geminiSucceeded = false;
    let overallConfidence = 0;
    let finalTier = 4;

    try {
      const fd = new FormData();
      fd.append("outdoor_photo", outdoorFile);
      if (indoorFile) fd.append("indoor_photo", indoorFile);

      const res = await fetch(`${API_URL}/api/ocr/nameplate`, {
        method: "POST",
        headers: authHeaders,
        body: fd,
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `OCR failed (${res.status})`);
      }

      const result: OcrResult = await res.json();
      const withSource: OcrResult = { ...result, source: "gemini" };
      overallConfidence = result.outdoor.confidence ?? 0;
      geminiSucceeded = true;

      // ── Tier 2: Field-level confidence gating ─────────────────────────────
      const needsConfirm = new Set<string>();
      const fieldsToCheck: (keyof NameplateUnit)[] = [
        "model_number", "tonnage", "refrigerant", "rla", "lra",
        "capacitor_uf", "mca", "mocp",
      ];
      for (const field of fieldsToCheck) {
        const val = result.outdoor[field];
        const fieldConf = val !== null && val !== undefined ? overallConfidence : 0;
        if (fieldConf >= 40 && fieldConf < 70) needsConfirm.add(field);
      }

      // ── Tier 3: DB lookup fills missing electrical specs ──────────────────────
      if (result.outdoor.tonnage !== null && overallConfidence >= 40) {
        const elecSpec = ELECTRICAL_SPECS_BY_TONNAGE[result.outdoor.tonnage];
        if (elecSpec) {
          const patched = { ...result.outdoor };
          if (!patched.rla        || overallConfidence < 40) patched.rla        = elecSpec.rla;
          if (!patched.lra        || overallConfidence < 40) patched.lra        = elecSpec.lra;
          if (!patched.mca        || overallConfidence < 40) patched.mca        = elecSpec.mca;
          if (!patched.mocp       || overallConfidence < 40) patched.mocp       = elecSpec.mocp;
          if (!patched.capacitor_uf || overallConfidence < 40) patched.capacitor_uf = elecSpec.capacitor_uf;
          setOcrResult({ ...withSource, outdoor: patched });
          setEditedUnit({ ...patched });
        } else {
          setOcrResult(withSource);
          setEditedUnit({ ...result.outdoor });
        }
      } else {
        setOcrResult(withSource);
        setEditedUnit({ ...result.outdoor });
      }

      if (needsConfirm.size > 0) {
        setNeedsConfirmationFields(needsConfirm);
        setConfirmationHeading("Confirm these specs — we\'ll take care of the rest.");
      }
      finalTier = needsConfirm.size > 0 ? 2 : 1;

    } catch (geminiErr) {
      // ── Tier 4 (invisible failure): Gemini failed → silent fallback to manual ──
      // BUG-034 item 6: Do NOT show "Both AI and local OCR failed" error
      console.warn("[OCR] Gemini failed, falling back to manual entry:", geminiErr);
      geminiSucceeded = false;
      finalTier = 4;
      setConfirmationHeading("Let\'s confirm the specs together.");
      setActiveTab("manual");
    }

    // ── Telemetry (BUG-034 item 8) ─────────────────────────────────────────────────────
    try {
      (window as Window & { posthog?: { capture?: (event: string, props: Record<string, unknown>) => void } })
        .posthog?.capture?.("nameplate_ocr_attempt", {
          market,
          gemini_called: true,
          gemini_succeeded: geminiSucceeded,
          overall_confidence: overallConfidence,
          final_tier: finalTier,
          time_ms: Date.now() - tStart,
        });
    } catch { /* PostHog never breaks the flow */ }

    setLoading(false);
  }, [outdoorFile, indoorFile, getToken]);

  // ── Auto-trigger OCR when outdoor photo is captured ─────────────────────
  useEffect(() => {
    if (!outdoorFile || ocrResult || loading) return;
    const timer = setTimeout(runOCR, 300); // small delay lets UI settle
    return () => clearTimeout(timer);
  }, [outdoorFile]); // eslint-disable-line react-hooks/exhaustive-deps

  // ── Confirm / persist ───────────────────────────────────────────────────

  const handleConfirm = useCallback(async () => {
    if (!ocrResult || !editedUnit) return;

    // Stage 3A: carry install-year + age confidence/source through to the estimate.
    persistAgeForEstimate(installYear, ageSource, ageConfidence);
    const finalResult: OcrResult = {
      ...ocrResult,
      outdoor: editedUnit,
      install_year: installYear,
      age_source: ageSource,
      age_confidence: ageConfidence,
    };

    // BUG-034: persist uses live JWT (not the null prop)
    if (assessmentId) {
      try {
        const IS_DEV = process.env.NEXT_PUBLIC_ENV === "development";
        let tok: string | null = null;
        if (!IS_DEV) { try { tok = await getToken(); } catch { tok = null; } }
        const persistHeaders: Record<string, string> = {
          "Content-Type": "application/json",
          "X-Market": detectMarket(),
          ...(IS_DEV
            ? { "X-Dev-Clerk-User-Id": "test_user_mike" }
            : tok ? { "Authorization": `Bearer ${tok}` } : {}),
        };
        await fetch(`${API_URL}/api/ocr/assessments/${assessmentId}/nameplate`, {
          method: "PATCH",
          headers: persistHeaders,
          body: JSON.stringify({ ocr_result: finalResult }),
        });
      } catch {
        // Non-fatal — proceed even if persist fails
      }
    }

    onConfirm(finalResult, AMBIENT_C_MAP[ambientBucket]);
  }, [ocrResult, editedUnit, assessmentId, getToken, onConfirm, installYear, ageSource, ageConfidence, persistAgeForEstimate]);

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

  // ── Stage 3A: Install-year + age-confidence review block ───────────────────
  // Rendered in BOTH the photo-review and manual paths (single-screen UX).
  // Accessible: <label htmlFor>, <fieldset>/<legend> for the confidence radios,
  // high-contrast (WCAG AA) badge + hint text, large tappable controls (truck-cab).
  const yearOptions: number[] = [];
  for (let y = AGE_YEAR_MAX; y >= AGE_YEAR_MIN; y--) yearOptions.push(y);
  const installYearReview = (
    <div
      className="bg-white border border-gray-200 rounded-2xl overflow-hidden"
      style={{ marginTop: 8 }}
    >
      <div className="px-4 py-2.5 border-b border-gray-100">
        <span className="text-xs font-black uppercase tracking-wider text-gray-500">
          {t("Install year")}
        </span>
      </div>
      <div className="p-3 flex flex-col gap-3" data-testid="stage3-age-review">
        {/* Year picker */}
        <div className="flex flex-col gap-1">
          <label
            htmlFor="install-year-select"
            className="text-[10px] font-bold uppercase tracking-wider text-gray-500"
          >
            {t("Year installed")}
          </label>
          <select
            id="install-year-select"
            value={installYear ?? ""}
            onChange={(e) => handleInstallYearChange(e.target.value)}
            className="w-full text-sm font-bold rounded-lg border px-2 py-2.5 focus:outline-none focus:ring-2"
            style={{
              borderColor: installYear == null ? "#9ca3af" : "#1a8754",
              background: installYear == null ? "#ffffff" : "#f0faf6",
              color: installYear == null ? "#6b7280" : "#111827",
              fontStyle: installYear == null ? "italic" : "normal",
              minHeight: 44,
            } as React.CSSProperties}
          >
            <option value="">{t("Ask homeowner")}</option>
            {yearOptions.map((y) => (
              <option key={y} value={y} style={{ fontStyle: "normal", color: "#111827" }}>
                {y}
              </option>
            ))}
          </select>
          {installYear == null && (
            <span className="text-[11px] italic" style={{ color: "#6b7280" }}>
              {t("We couldn't read the age — ask the homeowner if they know.")}
            </span>
          )}
          {ageIsLegacyEstimate && installYear != null && (
            <span
              className="inline-flex items-center self-start text-[10px] font-bold px-1.5 py-0.5 rounded mt-0.5"
              style={{ background: "#e0e7ff", color: "#3730a3" }}
            >
              {t("estimated from brand discontinue")}
            </span>
          )}
        </div>

        {/* Age-confidence selector (Sure / Approximate / Unknown) */}
        <fieldset style={{ border: "none", margin: 0, padding: 0 }}>
          <legend className="text-[10px] font-bold uppercase tracking-wider text-gray-500 mb-1">
            {t("How sure are we?")}
          </legend>
          <div className="grid grid-cols-3 gap-2">
            {([
              { key: "sure" as const,        label: t("Sure") },
              { key: "approximate" as const, label: t("Approximate") },
              { key: "unknown" as const,     label: t("Unknown") },
            ]).map((opt) => {
              const selected = ageConfidence === opt.key;
              return (
                <label
                  key={opt.key}
                  className="flex items-center justify-center text-center rounded-lg cursor-pointer text-xs font-semibold focus-within:outline focus-within:outline-2 focus-within:outline-offset-2 focus-within:outline-[#1a8754]"
                  style={{
                    background: selected ? "#1a8754" : "#ffffff",
                    color: selected ? "#ffffff" : "#374151",
                    border: selected ? "1.5px solid #1a8754" : "1.5px solid #d1d5db",
                    padding: "10px 4px",
                    minHeight: 44,
                  }}
                >
                  <input
                    type="radio"
                    name="age-confidence"
                    value={opt.key}
                    checked={selected}
                    onChange={() => handleAgeConfidenceChange(opt.key)}
                    style={{ position: "absolute", opacity: 0, width: 1, height: 1 }}
                  />
                  {opt.label}
                </label>
              );
            })}
          </div>
        </fieldset>
      </div>
    </div>
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
              {t("Step Zero")}
            </span>
            <span className="text-xs text-gray-500 font-medium">{t("Every Call")}</span>
          </div>
          <h2 className="text-base font-black text-gray-900 leading-tight">
            {t("Nameplate Photo — Before Any Complaint")}
          </h2>
          <p className="text-xs text-gray-500 mt-0.5">
            AI reads nameplate and pre-loads all system specs automatically
          </p>
        </div>
      </div>

      {/* Section 5C: Entry method — Scan Nameplate primary, manual secondary (B.2) */}
      <div className="flex flex-col gap-2">
        <button
          onClick={() => handleTabSelect("photo")}
          className="w-full py-3 rounded-2xl font-bold text-sm transition-all"
          style={{
            background: activeTab === "photo" ? "#1a8754" : "#e8f5ef",
            color: activeTab === "photo" ? "white" : "#1a8754",
            border: activeTab === "photo" ? "none" : "1.5px solid #a7d9be",
          }}
        >
          📸 {t("Scan Nameplate")}
        </button>
        <button
          onClick={() => handleTabSelect("manual")}
          className="text-xs font-medium text-center py-1 w-full"
          style={{
            color: activeTab === "manual" ? "#1a8754" : "#9ca3af",
            background: "none",
            border: "none",
            cursor: "pointer",
            textDecoration: activeTab === "manual" ? "underline" : "none",
          }}
        >
          ✏️ {t("I'll enter manually")}
        </button>
      </div>

      {/* ── MANUAL ENTRY TAB (Section 5A + 5C + 5D) ─────────────────────── */}
      {activeTab === "manual" && (
        <div className="space-y-4">
          {/* Scenario C: photo persists after Tier-4 silent fallback */}
          {outdoorPreview && (
            <button
              onClick={() => handleTabSelect("photo")}
              className="relative w-full rounded-xl border-2 overflow-hidden flex items-center gap-3 px-3 py-2 transition-colors"
              style={{ borderColor: "#1a8754", background: "#f0faf6" }}
            >
              <img src={outdoorPreview} alt="Outdoor nameplate" className="w-14 h-14 rounded-lg object-cover flex-shrink-0" />
              <div className="flex-1 text-left">
                <p className="text-xs font-bold text-gray-800">📷 Photo attached</p>
                <p className="text-[10px] text-gray-500">Tap to retake or use AI scan</p>
              </div>
              <span className="text-[10px] font-bold text-green-700 uppercase tracking-wider">Retake</span>
            </button>
          )}
          <p className="text-xs text-gray-500 text-center">
            Select brand &amp; model to auto-fill, or type specs directly.
          </p>

          {/* Section 5A: Brand dropdown + model search */}
          {/* BUG-014b: overflow-visible so model results dropdown is not clipped */}
          <div className="bg-white border border-gray-200 rounded-2xl overflow-visible">
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
                            <div className="flex items-center gap-1">
                              {m.series_type === "inverter" && (
                                <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-blue-100 text-blue-700 uppercase">
                                  Inverter
                                </span>
                              )}
                              <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded-full bg-gray-100 text-gray-500 uppercase">
                                {m.equipment_type.replace("_", " ")}
                              </span>
                            </div>
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
                    <div className="flex items-center gap-1.5 flex-wrap">
                      <span className="text-xs font-bold text-green-800">
                        {manualUnit.brand_id} — {manualUnit.series_id}
                      </span>
                      {selectedSeriesType === "inverter" && (
                        <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-blue-100 text-blue-700 uppercase">
                          Inverter
                        </span>
                      )}
                    </div>
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
                      setEditedManualFields(new Set());
                      setSelectedSeriesType(null);
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

          {/* ── PK-only: Tonnage Picker (shown after model selected) ──────────── */}
          {isPK && pkTonnageData && Object.keys(pkTonnageData).length > 0 && (
            <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden">
              <div className="px-4 py-2.5 border-b border-gray-100">
                <span className="text-xs font-black uppercase tracking-wider text-blue-600">
                  ⚖️ Select Tonnage
                </span>
              </div>
              <div className="p-3">
                <p className="text-[10px] text-gray-400 mb-2">
                  Choose the unit capacity — specs will auto-fill from the brand database.
                </p>
                <div className="flex flex-wrap gap-2">
                  {Object.keys(pkTonnageData).sort((a, b) => parseFloat(a) - parseFloat(b)).map((key) => {
                    const isSelected = pkSelectedTonnageKey === key;
                    return (
                      <button
                        key={key}
                        onClick={() => applyPkTonnage(key)}
                        className="flex flex-col items-center px-3 py-2 rounded-xl border-2 transition-all min-w-[56px]"
                        style={{
                          borderColor: isSelected ? "#1a8754" : "#e2dfd7",
                          background:  isSelected ? "#f0faf6" : "#fafaf8",
                        }}
                      >
                        <span
                          className="text-sm font-black"
                          style={{ color: isSelected ? "#1a8754" : "#374151" }}
                        >
                          {key}T
                        </span>
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
          )}

          {/* ── PK-only: 2.5T commercial warning banner (A-5) ──────────────── */}
          {isPK && manualUnit.tonnage === 2.5 && (
            <div className="bg-amber-50 border-2 border-amber-400 rounded-xl p-3 flex gap-2">
              <span className="text-amber-600 font-bold flex-shrink-0 text-lg">⚠️</span>
              <div>
                <p className="text-sm font-black text-amber-800">Commercial / Light Commercial Unit</p>
                <p className="text-xs text-amber-700 mt-0.5">
                  2.5-ton units are typically used in commercial or light-commercial applications in Pakistan.
                  Verify with the customer whether this is a residential or commercial installation.
                </p>
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
                const isEditedDbField = badge === "db" && !isEmpty && !!manualUnit.series_id && editedManualFields.has(key);
                const isDbField  = badge === "db"  && !isEmpty && !!manualUnit.series_id && !editedManualFields.has(key);
                const isEstField = badge === "est";
                return (
                  <div key={key} className="flex flex-col gap-0.5">
                    <div className="flex items-center gap-1">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400">
                        {label}
                        {key === "refrigerant" && !isPK && <span className="text-blue-400 ml-1">(auto)</span>}
                      </span>
                      {isEditedDbField && (
                        <span className="text-[9px] font-black px-1 py-0.5 rounded"
                              style={{ background: "#fff3e0", color: "#c4600a" }}>✏ Edited</span>
                      )}
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

          {/* Outdoor temperature — ambient selector (Phase 2: drives PSI threshold lookup) */}
          {/* Show when user picked a series from DB lookup */}
          {(editedUnit || manualUnit.series_id) && (
            <div className="space-y-2 mt-2">
              <label className="text-sm font-bold" style={{ color: "#c9d1d9" }}>
                Outdoor temperature
              </label>
              <div className="grid grid-cols-3 gap-2">
                {(["mild", "hot", "extreme"] as const).map((bucket) => {
                  const labels: Record<typeof bucket, { title: string; sub: string }> = {
                    mild:    { title: "Mild",    sub: "< 86°F (30°C)" },
                    hot:     { title: "Hot",     sub: "86–100°F (30–38°C)" },
                    extreme: { title: "Extreme", sub: "> 100°F (38°C+)" },
                  };
                  const selected = ambientBucket === bucket;
                  return (
                    <button
                      key={bucket}
                      onClick={() => setAmbientBucket(bucket)}
                      className="py-2 px-1 rounded-lg text-xs font-semibold transition-all text-center leading-tight"
                      style={{
                        background: selected ? "#1a8754" : "#1e2330",
                        color: selected ? "#ffffff" : "#7a8299",
                        border: selected ? "1.5px solid #1a8754" : "1.5px solid #2d3547",
                      }}
                    >
                      {labels[bucket].title}
                      <br />
                      <span style={{ fontWeight: 400, opacity: 0.8 }}>{labels[bucket].sub}</span>
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* Stage 3A — install-year review (manual path) */}
          {installYearReview}

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
                <p className="text-xs font-bold text-white">{t("Outdoor")}</p>
                <p className="text-[10px] text-white/80">Tap to retake</p>
              </div>
            </>
          ) : (
            <div className="flex flex-col items-center gap-1.5 p-3 text-center">
              <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center text-xl">+</div>
              <p className="text-xs font-bold text-gray-700">{t("Outdoor")}</p>
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
                <p className="text-xs font-bold text-white">{t("Indoor")}</p>
                <p className="text-[10px] text-white/80">Tap to retake</p>
              </div>
            </>
          ) : (
            <div className="flex flex-col items-center gap-1.5 p-3 text-center">
              <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center text-xl">+</div>
              <p className="text-xs font-bold text-gray-700">{t("Indoor")}</p>
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

      {/* Section 6B: Loading indicator */}
      {loading && (
        <div className="flex items-center justify-center gap-3 py-2">
          {[0,1,2].map(i => (
            <div key={i} className="w-2.5 h-2.5 rounded-full animate-bounce"
                 style={{ background: "#f39c12", animationDelay: `${i * 0.15}s` }} />
          ))}
          <span className="text-sm text-gray-500 font-medium">Reading nameplate…</span>
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
                {confirmationHeading ?? "AI Extracted — verify & edit"}
              </span>
              <span
                className="text-[10px] font-bold px-1.5 py-0.5 rounded-full"
                style={{ background: "#e8f5ee", color: "#1a8754" }}
              >
                ✶ Gemini AI
              </span>
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
              // BUG-034: yellow border for 40-69 confidence fields
              const needsConfirm = needsConfirmationFields.has(key);
              return (
                <div key={key} className="flex flex-col gap-0.5">
                  <div className="flex items-center gap-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400">{label}</span>
                    {needsConfirm && (
                      <span className="text-[9px] font-black px-1 py-0.5 rounded"
                            style={{ background: "#fef9c3", color: "#a16207" }}>?</span>
                    )}
                    {!needsConfirm && isDbField && (
                      <span className="text-[9px] font-black px-1 py-0.5 rounded"
                            style={{ background: "#e8f5ee", color: "#1a8754" }}>DB</span>
                    )}
                    {!needsConfirm && isEstField && (
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
                        borderColor: needsConfirm ? "#facc15" : isEmpty ? "#e2dfd7" : isEstField ? "#c4600a" : "#1a8754",
                        background:  needsConfirm ? "#fefce8" : isEmpty ? "#fafaf8" : isEstField ? "#fffaf5" : "#f0faf6",
                        color: isEmpty ? "#aaa" : "#1a1a1a",
                        boxShadow: needsConfirm ? "0 0 0 2px #fde047" : undefined,
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

      {/* Outdoor temperature — ambient selector (Phase 2: drives PSI threshold lookup) */}
      {/* Show when: (a) OCR returned a unit, or (b) user picked a series from DB lookup */}
      {(editedUnit || manualUnit.series_id) && (
        <div className="space-y-2 mt-2">
          <label className="text-sm font-bold" style={{ color: "#c9d1d9" }}>
            Outdoor temperature
          </label>
          <div className="grid grid-cols-3 gap-2">
            {(["mild", "hot", "extreme"] as const).map((bucket) => {
              const labels: Record<typeof bucket, { title: string; sub: string }> = {
                mild:    { title: "Mild",    sub: "< 86°F (30°C)" },
                hot:     { title: "Hot",     sub: "86–100°F (30–38°C)" },
                extreme: { title: "Extreme", sub: "> 100°F (38°C+)" },
              };
              const selected = ambientBucket === bucket;
              return (
                <button
                  key={bucket}
                  onClick={() => setAmbientBucket(bucket)}
                  className="py-2 px-1 rounded-lg text-xs font-semibold transition-all text-center leading-tight"
                  style={{
                    background: selected ? "#1a8754" : "#1e2330",
                    color: selected ? "#ffffff" : "#7a8299",
                    border: selected ? "1.5px solid #1a8754" : "1.5px solid #2d3547",
                  }}
                >
                  {labels[bucket].title}
                  <br />
                  <span style={{ fontWeight: 400, opacity: 0.8 }}>{labels[bucket].sub}</span>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Stage 3A — install-year review (photo path) */}
      {editedUnit && installYearReview}

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
          
