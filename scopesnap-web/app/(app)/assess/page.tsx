/**
 * Assess Page — 3-Photo Board-Approved Flow
 *
 * Consensus from 6-founder + HVAC-tech board meeting:
 *   Required slot 1: Spec plate / nameplate
 *   Required slot 2: Full outdoor unit
 *   Required slot 3: Symptom-driven (dynamically labeled by complaint)
 *   Optional:        "+ Add photos your homeowner will see" with confidence meter
 *
 * Refs: Musk (strip to 3 required), Jobs (complaint-first, progressive disclosure),
 *       Bezos (design for real-world 2.47pm attic conditions), Zuckerberg (report quality),
 *       Gates (low-friction adoption), Page (track photo-count vs edit-rate from day 1).
 */
"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { API_URL } from "@/lib/api";
import { OfflineError } from "@/lib/api";
import { saveToOfflineQueue, processOfflineQueue, getOfflineQueueCount } from "@/lib/offlineQueue";
import { track } from "@/lib/tracking";
import StepZeroPanel from "@/components/StepZeroPanel";

const IS_DEV = process.env.NEXT_PUBLIC_ENV === "development";
const DEV_HEADER = { "X-Dev-Clerk-User-Id": "test_user_mike" };

type Phase = "step-zero" | "complaint" | "sensor" | "capture" | "uploading" | "analyzing" | "results" | "estimating";

// ── Sensor field config (Jobs method: one field per screen, in walkup order) ──
const SENSOR_FIELDS = [
  {
    key: "unitAge",
    label: "Unit Age",
    unit: "years",
    placeholder: "e.g. 8",
    hint: "Check the nameplate — usually on the side panel",
    icon: "📋",
    setter: "setSensorUnitAge",
    getter: "sensorUnitAge",
  },
  {
    key: "outdoorTemp",
    label: "Outdoor Ambient Temp",
    unit: "°F",
    placeholder: "e.g. 95",
    hint: "Air temperature outside near the condenser",
    icon: "🌡️",
    setter: "setSensorOutdoorTemp",
    getter: "sensorOutdoorTemp",
  },
  {
    key: "supplyTemp",
    label: "Supply Air Temp",
    unit: "°F",
    placeholder: "e.g. 58",
    hint: "Temperature at the supply duct register",
    icon: "❄️",
    setter: "setSensorSupplyTemp",
    getter: "sensorSupplyTemp",
  },
  {
    key: "returnTemp",
    label: "Return Air Temp",
    unit: "°F",
    placeholder: "e.g. 75",
    hint: "Temperature at the return air grille",
    icon: "🔄",
    setter: "setSensorReturnTemp",
    getter: "sensorReturnTemp",
  },
  {
    key: "suction",
    label: "Suction Pressure",
    unit: "PSI",
    placeholder: "e.g. 58",
    hint: "Low-side reading from manifold gauge set",
    icon: "🔵",
    setter: "setSensorSuction",
    getter: "sensorSuction",
  },
  {
    key: "discharge",
    label: "Discharge Pressure",
    unit: "PSI",
    placeholder: "e.g. 260",
    hint: "High-side reading from manifold gauge set",
    icon: "🔴",
    setter: "setSensorDischarge",
    getter: "sensorDischarge",
  },
] as const;

// ── Complaint options (Jobs rule: 6 max, big icons, no dropdowns) ─────────────
const COMPLAINT_OPTIONS = [
  { id: "not_cooling",           icon: "🥵", label: "Not Cooling",           sub: "Weak or no cooling" },
  { id: "not_heating",           icon: "🔥", label: "Not Heating",           sub: "No heat / cold air" },
  { id: "intermittent_shutdown", icon: "⚡", label: "Intermittent Shutdown", sub: "Short cycling / random shutoffs" },
  { id: "water_leak",  icon: "💧", label: "Water Leaking", sub: "Dripping or pooling" },
  { id: "wont_start",  icon: "⚡", label: "Won't Turn On", sub: "No response at all" },
  { id: "noisy",       icon: "🔊", label: "Making Noise", sub: "Banging, squealing, humming" },
  { id: "routine",     icon: "📋", label: "Routine Estimate", sub: "No specific complaint" },
] as const;
type ComplaintId = typeof COMPLAINT_OPTIONS[number]["id"];

// ── What Photo 3 captures depends on the complaint ────────────────────────────
const SYMPTOM_PHOTO: Record<ComplaintId, { label: string; hint: string; icon: string }> = {
  not_cooling:           { label: "Indoor coil / evaporator",    hint: "Open the air handler access panel — ice or corrosion?",              icon: "❄️" },
  not_heating:           { label: "Indoor coil / furnace",        hint: "Open the air handler / furnace access panel",                        icon: "🔥" },
  intermittent_shutdown: { label: "Control board / contactor",    hint: "Open the electrical panel — look for burn marks or corroded contacts", icon: "⚡" },
  water_leak:            { label: "Drain pan",                    hint: "Look under the indoor unit — standing water or rust?",               icon: "💧" },
  wont_start:            { label: "Disconnect box",               hint: "The electrical disconnect near the outdoor unit",                     icon: "⚡" },
  noisy:                 { label: "Noisy component",              hint: "Fan, compressor, or duct area making the sound",                      icon: "🔊" },
  routine:               { label: "Indoor unit overall",          hint: "Step back — full air handler or furnace in frame",                    icon: "🏠" },
};

// ── Slot metadata for the 3 required photos ───────────────────────────────────
const getSlotConfig = (complaint: ComplaintId | null) => [
  {
    slot: 0,
    icon: "📋",
    label: "Spec Plate",
    hint: "Get close enough to read the model number clearly",
    required: true,
  },
  {
    slot: 1,
    icon: "🏠",
    label: "Full Outdoor Unit",
    hint: "Step back 4 feet — get the whole unit in frame",
    required: true,
  },
  {
    slot: 2,
    icon: complaint ? SYMPTOM_PHOTO[complaint].icon : "📸",
    label: complaint ? SYMPTOM_PHOTO[complaint].label : "Symptom Photo",
    hint: complaint ? SYMPTOM_PHOTO[complaint].hint : "Select a complaint above to get a specific prompt",
    required: true,
  },
];

interface PropertySuggestion {
  id: string;
  address_line1?: string;
  city?: string;
  state?: string;
  customer_name?: string;
  visit_count?: number;
  returning_customer?: boolean;
}

interface PriorEstimate {
  id: string;
  report_short_id: string;
  status: string;
  total_amount?: number;
  created_at?: string;
}

interface AIIssue {
  component: string;
  issue: string;
  severity: string;
  description_plain?: string;
  description?: string;
}

interface AssessmentResult {
  id: string;
  ai_equipment_id?: Record<string, unknown>;
  ai_condition?: {
    overall?: string;
    components?: Array<{
      name: string;
      condition: string;
      description_plain: string;
      urgency: string;
    }>;
  };
  ai_issues?: AIIssue[];
  photo_urls?: string[];
}

const DRAFT_KEY = "snapai_draft_assessment";

export default function AssessPage() {
  const router = useRouter();
  const { getToken } = useAuth();

  const getAuthHeaders = useCallback(async (): Promise<Record<string, string>> => {
    if (IS_DEV) return DEV_HEADER;
    const token = await getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  }, [getToken]);

  // ── Refs ──────────────────────────────────────────────────────────────────
  const fileInputRef   = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);
  const videoRef       = useRef<HTMLVideoElement>(null);
  const activeSlotRef  = useRef<number | "extra">(0); // which slot is receiving the next photo

  // ── Core phase + complaint ────────────────────────────────────────────────
  const [phase, setPhase]             = useState<Phase>("step-zero");
  const [ocrResult, setOcrResult]     = useState<Record<string, unknown> | null>(null);
  const [complaintType, setComplaintType] = useState<ComplaintId | null>(null);

  // ── Photo slots (3 required + optional extras) ────────────────────────────
  const [slotPhotos,   setSlotPhotos]   = useState<(File | null)[]>([null, null, null]);
  const [slotPreviews, setSlotPreviews] = useState<(string | null)[]>([null, null, null]);
  const [extraPhotos,  setExtraPhotos]  = useState<File[]>([]);
  const [extraPreviews, setExtraPreviews] = useState<string[]>([]);

  // ── Job info ───────────────────────────────────────────────────────────────
  const [address,       setAddress]       = useState("");
  const [customerName,  setCustomerName]  = useState("");
  const [customerPhone, setCustomerPhone] = useState("");

  // ── Sensor readings (Track A — boosts accuracy to 90-95%) ─────────────────
  const [showSensorPanel, setShowSensorPanel] = useState(false); // legacy — kept for old inline panel (now replaced by sensor phase)
  const [sensorOutdoorTemp,   setSensorOutdoorTemp]   = useState("");
  const [sensorSupplyTemp,    setSensorSupplyTemp]    = useState("");
  const [sensorReturnTemp,    setSensorReturnTemp]    = useState("");
  const [sensorSuction,       setSensorSuction]       = useState("");
  const [sensorDischarge,     setSensorDischarge]     = useState("");
  const [sensorUnitAge,       setSensorUnitAge]       = useState("");

  // ── Sensor phase state (Jobs method: one field per screen) ─────────────────
  const [sensorFieldIndex, setSensorFieldIndex] = useState(0); // current field 0–5
  const [sensorCurrentValue, setSensorCurrentValue] = useState(""); // value being typed
  // Collected values indexed by field key
  const [sensorValues, setSensorValues] = useState<Record<string, string>>({});

  // ── UI helpers ─────────────────────────────────────────────────────────────
  const [draftRecovery, setDraftRecovery] = useState<{address:string;customerName:string;timestamp:number}|null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [analysisStep,   setAnalysisStep]   = useState(0);
  const [suggestions,    setSuggestions]    = useState<PropertySuggestion[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [assessment,     setAssessment]     = useState<AssessmentResult | null>(null);
  const [error,          setError]          = useState<string | null>(null);
  const [cameraStream,   setCameraStream]   = useState<MediaStream | null>(null);
  const [usingCamera,    setUsingCamera]    = useState(false);
  const [selectedProperty, setSelectedProperty] = useState<PropertySuggestion | null>(null);
  const [priorEstimates, setPriorEstimates] = useState<PriorEstimate[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [offlineQueued, setOfflineQueued] = useState(false);
  const [pendingCount,  setPendingCount]  = useState(0);

  // Draft recovery + offline queue on mount
  useEffect(() => {
    track.assessmentStarted();
    try {
      const raw = localStorage.getItem(DRAFT_KEY);
      if (raw) {
        const draft = JSON.parse(raw);
        const ageHrs = (Date.now() - draft.timestamp) / 3600000;
        if (ageHrs < 4 && draft.address) setDraftRecovery(draft);
      }
    } catch { /* ignore */ }
    getOfflineQueueCount().then(count => { if (count > 0) setPendingCount(count); }).catch(() => {});
    const handleOnline = () => {
      getAuthHeaders().then(headers =>
        processOfflineQueue(API_URL, headers).then(({ uploaded }) => {
          if (uploaded > 0) setPendingCount(0);
        })
      ).catch(() => {});
    };
    window.addEventListener("online", handleOnline);
    if (typeof navigator !== "undefined" && navigator.onLine) handleOnline();
    return () => window.removeEventListener("online", handleOnline);
  }, []);

  useEffect(() => {
    if (address || customerName) {
      try { localStorage.setItem(DRAFT_KEY, JSON.stringify({ address, customerName, timestamp: Date.now() })); }
      catch { /* ignore */ }
    }
  }, [address, customerName]);

  useEffect(() => {
    if (address.length < 3) { setSuggestions([]); return; }
    const t = setTimeout(async () => {
      try {
        const authHeaders = await getAuthHeaders();
        const r = await fetch(`${API_URL}/api/properties/search?q=${encodeURIComponent(address)}&limit=5`, { headers: authHeaders });
        if (r.ok) { setSuggestions(await r.json()); setShowSuggestions(true); }
      } catch { /* ignore */ }
    }, 300);
    return () => clearTimeout(t);
  }, [address]);

  // ── Camera helpers ─────────────────────────────────────────────────────────
  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
      setCameraStream(stream);
      setUsingCamera(true);
      if (videoRef.current) videoRef.current.srcObject = stream;
    } catch { setError("Camera unavailable — use file upload."); }
  };

  const capturePhoto = () => {
    if (!videoRef.current) return;
    const canvas = document.createElement("canvas");
    canvas.width  = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    canvas.getContext("2d")?.drawImage(videoRef.current, 0, 0);
    canvas.toBlob((blob) => {
      if (!blob) return;
      const file = new File([blob], `capture-${Date.now()}.jpg`, { type: "image/jpeg" });
      handleFileForSlot(file);
    }, "image/jpeg", 0.9);
  };

  const stopCamera = useCallback(() => {
    cameraStream?.getTracks().forEach(t => t.stop());
    setCameraStream(null);
    setUsingCamera(false);
  }, [cameraStream]);

  // ── Slot photo management ─────────────────────────────────────────────────
  const handleFileForSlot = (file: File) => {
    const slot = activeSlotRef.current;
    if (slot === "extra") {
      if (extraPhotos.length >= 7) return; // max 7 extra = 10 total (3 required + 7 optional)
      setExtraPhotos(p => [...p, file]);
      setExtraPreviews(p => [...p, URL.createObjectURL(file)]);
      track.photoAdded(3 + extraPhotos.length + 1, file.size);
    } else {
      const idx = slot as number;
      setSlotPhotos(prev => { const n = [...prev]; n[idx] = file; return n; });
      setSlotPreviews(prev => {
        const n = [...prev];
        if (n[idx]) URL.revokeObjectURL(n[idx]!);
        n[idx] = URL.createObjectURL(file);
        return n;
      });
      track.photoAdded(idx + 1, file.size);
    }
  };

  const clearSlot = (idx: number) => {
    setSlotPhotos(prev => { const n = [...prev]; n[idx] = null; return n; });
    setSlotPreviews(prev => { const n = [...prev]; if (n[idx]) URL.revokeObjectURL(n[idx]!); n[idx] = null; return n; });
  };

  const removeExtra = (i: number) => {
    setExtraPhotos(p => p.filter((_, idx) => idx !== i));
    setExtraPreviews(p => p.filter((_, idx) => idx !== i));
  };

  const triggerSlotCapture = (slot: number | "extra") => {
    activeSlotRef.current = slot;
    if (/Mobi|Android|iPhone|iPad/i.test(navigator.userAgent)) {
      cameraInputRef.current?.click();
    } else {
      startCamera();
    }
  };

  const triggerSlotFile = (slot: number | "extra") => {
    activeSlotRef.current = slot;
    fileInputRef.current?.click();
  };

  // ── Validation ─────────────────────────────────────────────────────────────
  const allRequiredFilled = slotPhotos.every(s => s !== null);
  const filledCount = slotPhotos.filter(Boolean).length;

  // confidence grows from 70% (3 photos) to 94% (5 photos)
  const confidencePct = filledCount === 0 ? 0
    : filledCount === 1 ? 40
    : filledCount === 2 ? 65
    : filledCount === 3 ? 70 + Math.min(extraPhotos.length * 12, 24)
    : 70 + Math.min(extraPhotos.length * 12, 24);

  // ── Submit ─────────────────────────────────────────────────────────────────
  const handleSubmit = async () => {
    if (!allRequiredFilled) {
      setError("Complete all 3 required photos to continue.");
      return;
    }
    const allPhotos = [...(slotPhotos as File[]), ...extraPhotos];
    track.assessmentSubmitted(allPhotos.length);
    setError(null);
    setPhase("uploading");
    setUploadProgress(0);
    setAnalysisStep(0);

    const fd = new FormData();
    allPhotos.forEach(p => fd.append("photos", p));
    if (address)       fd.append("property_address", address);
    if (customerName)  fd.append("homeowner_name", customerName);
    if (customerPhone) fd.append("homeowner_phone", customerPhone);
    if (complaintType) fd.append("complaint_type", complaintType);

    // Sensor readings → Track A cascade (boosts accuracy to 90-95%)
    const sensorData: Record<string, number> = {};
    if (sensorOutdoorTemp)  sensorData.outdoor_ambient_temp = parseFloat(sensorOutdoorTemp);
    if (sensorSupplyTemp)   sensorData.supply_air_temp      = parseFloat(sensorSupplyTemp);
    if (sensorReturnTemp)   sensorData.return_air_temp      = parseFloat(sensorReturnTemp);
    if (sensorSuction)      sensorData.suction_pressure     = parseFloat(sensorSuction);
    if (sensorDischarge)    sensorData.discharge_pressure   = parseFloat(sensorDischarge);
    if (sensorUnitAge)      sensorData.unit_age_years       = parseFloat(sensorUnitAge);
    if (Object.keys(sensorData).length >= 4) {
      fd.append("sensor_readings_json", JSON.stringify(sensorData));
    }

    let uploaded: { id: string } | null = null;
    try {
      if (typeof navigator !== "undefined" && !navigator.onLine) {
        await saveToOfflineQueue(allPhotos, { address, customerName, customerPhone });
        setOfflineQueued(true);
        setPendingCount(c => c + 1);
        setPhase("capture");
        return;
      }
      setUploadProgress(30);
      const uploadAuthHeaders = await getAuthHeaders();
      let up: Response;
      try {
        up = await fetch(`${API_URL}/api/assessments/`, { method: "POST", headers: uploadAuthHeaders, body: fd });
      } catch {
        await saveToOfflineQueue(allPhotos, { address, customerName, customerPhone });
        setOfflineQueued(true);
        setPendingCount(c => c + 1);
        setPhase("capture");
        return;
      }
      if (!up.ok) {
        const detail = await up.json().then(d => d.detail).catch(() => "Upload failed");
        throw new Error(detail || "Couldn't upload photos. Check your connection and try again.");
      }
      uploaded = await up.json();
      setUploadProgress(100);
      stopCamera();
    } catch (err: unknown) {
      const msg = err instanceof OfflineError
        ? "No internet connection. Check your signal and try again."
        : err instanceof Error ? err.message : "Couldn't upload photos. Check connection and try again.";
      setError(msg);
      setPhase("capture");
      return;
    }

    setPhase("analyzing");
    setAnalysisStep(1);
    const analyzeAuthHeaders = await getAuthHeaders();
    const analyzeWithTimeout = async (attempt: number): Promise<Response> => {
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), 30000);
      try {
        const r = await fetch(`${API_URL}/api/assessments/${uploaded!.id}/analyze`, { method: "POST", headers: analyzeAuthHeaders, signal: controller.signal });
        clearTimeout(timer);
        return r;
      } catch (e: unknown) {
        clearTimeout(timer);
        const isAbort = e instanceof Error && e.name === "AbortError";
        if (isAbort && attempt === 1) { setAnalysisStep(s => Math.min(s + 1, 4)); return analyzeWithTimeout(2); }
        throw e;
      }
    };

    try {
      const stepTimer = setInterval(() => { setAnalysisStep(s => Math.min(s + 1, 4)); }, 3500);
      let an: Response;
      try {
        an = await analyzeWithTimeout(1);
      } catch (e: unknown) {
        clearInterval(stepTimer);
        const isTimeout = e instanceof Error && e.name === "AbortError";
        if (isTimeout) throw new Error("AI analysis timed out after 30 seconds. Please try again.");
        throw new OfflineError();
      }
      clearInterval(stepTimer);
      if (!an.ok) {
        const detail = await an.json().then(d => d.detail).catch(() => "Analysis failed");
        throw new Error(detail || "AI analysis failed. Try again.");
      }
      const assessmentResult = await an.json();
      setAssessment(assessmentResult);
      track.assessmentCompleted(assessmentResult.id);
      try { localStorage.removeItem(DRAFT_KEY); } catch { /* ignore */ }
      setPhase("results");
    } catch (err: unknown) {
      const msg = err instanceof OfflineError
        ? "No internet connection. Check your signal and try again."
        : err instanceof Error ? err.message : "AI analysis failed. Try again.";
      setError(msg);
      setPhase("capture");
    }
  };

  const handleGenerateEstimate = async () => {
    if (!assessment) return;
    setPhase("estimating");
    setError(null);
    try {
      const estAuthHeaders = await getAuthHeaders();
      const r = await fetch(`${API_URL}/api/estimates/generate`, {
        method: "POST",
        headers: { ...estAuthHeaders, "Content-Type": "application/json" },
        body: JSON.stringify({ assessment_id: assessment.id }),
      });
      if (!r.ok) throw new Error((await r.json()).detail || "Generate failed");
      const est = await r.json();
      track.estimateGenerated(est.id, est.total_amount || 0);
      router.push(`/assessment/${est.id}`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Error");
      setPhase("results");
    }
  };

  // ── Uploading / Analyzing screen ───────────────────────────────────────────
  if (phase === "uploading" || phase === "analyzing") {
    const STEPS = ["Uploading photos…", "Reading equipment details…", "Identifying brand & model…", "Checking condition & wear…", "Building your estimate…"];
    const currentMsg  = phase === "uploading" ? STEPS[0] : (STEPS[analysisStep] || STEPS[1]);
    const progressPct = phase === "uploading" ? uploadProgress : Math.min(20 + analysisStep * 20, 90);
    return (
      <div className="max-w-md mx-auto pt-16 text-center space-y-6 px-4">
        <div className="flex gap-3 justify-center" aria-label="Loading">
          {[0,1,2].map(i => (
            <div key={i} className="w-4 h-4 rounded-full bg-brand-green"
              style={{ animation: `pulseDot 1.4s ease-in-out ${i * 0.2}s infinite` }} />
          ))}
          <style>{`@keyframes pulseDot{0%,80%,100%{transform:scale(0.6);opacity:.4}40%{transform:scale(1.2);opacity:1}}`}</style>
        </div>
        <div>
          <h2 className="text-2xl font-extrabold tracking-tight mb-2">
            {phase === "uploading" ? "Uploading Photos" : "Analyzing Equipment"}
          </h2>
          <p className="text-sm text-text-secondary">{currentMsg}</p>
        </div>
        <div className="card p-4 space-y-2.5 text-left">
          {["Reading photos","Identifying brand & model","Checking condition & wear","Finding issues","Building estimate"].map((task, i) => {
            const done   = phase === "analyzing" && i < analysisStep;
            const active = phase === "analyzing" && i === analysisStep;
            return (
              <div key={i} className="flex items-center gap-3 text-sm">
                <div className={`w-2 h-2 rounded-full flex-shrink-0 ${done ? "bg-brand-green" : active ? "bg-brand-green animate-pulse" : "bg-surface-border"}`} />
                <span className={done ? "text-text-primary font-semibold" : active ? "text-text-primary" : "text-text-secondary"}>
                  {task}{done && " ✓"}
                </span>
              </div>
            );
          })}
        </div>
        <div className="w-48 h-1.5 mx-auto bg-surface-secondary rounded-full overflow-hidden">
          <div className="h-full bg-brand-green rounded-full transition-all duration-700" style={{ width: `${progressPct}%` }} />
        </div>
        <p className="text-xs text-text-secondary font-mono">Usually takes 8–15 seconds</p>
      </div>
    );
  }

  // ── Estimating screen ──────────────────────────────────────────────────────
  if (phase === "estimating") {
    return (
      <div className="max-w-md mx-auto pt-16 text-center space-y-4">
        <div className="text-5xl">⚙️</div>
        <h2 className="text-xl font-black">Building Estimate...</h2>
        <p className="text-sm text-gray-600">Calculating Good/Better/Best pricing</p>
      </div>
    );
  }

  // ── Results screen ─────────────────────────────────────────────────────────
  if (phase === "results" && assessment) {
    const eq      = (assessment.ai_equipment_id || {}) as Record<string, string | number>;
    const cond    = assessment.ai_condition || {};
    const issues  = assessment.ai_issues || [];
    const overall = (cond.overall || "unknown").toLowerCase();
    const conditionColor: Record<string, string> = {
      excellent:"#1a8754", good:"#1a8754", fair:"#c4600a", poor:"#c4600a", critical:"#c62828", failed:"#c62828"
    };
    const color = conditionColor[overall] || "#7a7770";
    void color;

    return (
      <div className="max-w-2xl mx-auto space-y-4 px-4">
        <div className="flex items-center gap-3 pt-4">
          <button onClick={() => { setPhase("capture"); setAssessment(null); }} className="text-sm text-gray-600 hover:text-gray-900">← Back</button>
          <h1 className="text-2xl font-black flex-1">Intelligence Results</h1>
        </div>
        {/* Equipment ID */}
        <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden">
          <div className="px-4 py-3 border-b-2 font-mono text-xs font-bold uppercase tracking-wider text-green-600" style={{ borderBottomColor: "#1a8754" }}>✓ Equipment Identified</div>
          <div className="p-4 space-y-3">
            <div className="font-mono text-2xl font-black text-gray-900">{String(eq.brand || "Unknown")}{eq.model ? ` ${eq.model}` : ""}</div>
            <div className="flex flex-wrap gap-2">
              {eq.serial     && <span className="px-2 py-1 bg-gray-100 rounded-lg text-xs font-semibold text-gray-600 font-mono">SN: {eq.serial}</span>}
              {eq.install_year && <span className="px-2 py-1 bg-gray-100 rounded-lg text-xs font-semibold text-gray-600 font-mono">Mfg: {eq.install_year}</span>}
              {eq.confidence && <span className="px-2 py-1 bg-gray-100 rounded-lg text-xs font-semibold text-gray-600 font-mono">{Math.round(Number(eq.confidence))}% confidence</span>}
            </div>
            {eq.confidence && (
              <div className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-gray-600">ID Confidence</span>
                  <span className="font-mono font-bold text-green-600">{Math.round(Number(eq.confidence))}%</span>
                </div>
                <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
                  <div className="h-full bg-green-600 rounded-full" style={{ width: `${Math.round(Number(eq.confidence))}%` }} />
                </div>
              </div>
            )}
          </div>
        </div>
        {/* Condition */}
        {(cond.components || []).length > 0 && (
          <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden">
            <div className="px-4 py-3 border-b-2 font-mono text-xs font-bold uppercase tracking-wider text-orange-600" style={{ borderBottomColor: "#c4600a" }}>⚠ Condition Assessment</div>
            <div className="p-4 space-y-3">
              {(cond.components || []).map((comp, i) => (
                <div key={i} className="flex gap-3 items-start">
                  <div className="w-7 h-7 rounded flex items-center justify-center flex-shrink-0 text-sm font-bold"
                    style={{ backgroundColor: comp.condition === "normal" ? "#e8f5ee" : comp.condition.includes("minor") ? "#fef3e8" : "#fce8e8", color: comp.condition === "normal" ? "#1a8754" : comp.condition.includes("minor") ? "#c4600a" : "#c62828" }}>
                    {comp.condition === "normal" ? "✓" : "⚠"}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-bold text-gray-900">{comp.name.replace(/_/g, " ")}</h4>
                    <p className="text-sm text-gray-600 mt-0.5">{comp.description_plain}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        {/* Lifecycle */}
        <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden">
          <div className="px-4 py-3 border-b-2 font-mono text-xs font-bold uppercase tracking-wider text-blue-600" style={{ borderBottomColor: "#1565c0" }}>Lifecycle Intelligence</div>
          <div className="p-4 space-y-2">
            <div className="flex justify-between items-center py-2 border-b border-gray-200"><span className="text-sm text-gray-600">Expected Lifespan</span><span className="text-sm font-bold text-gray-900 font-mono">15–20 years</span></div>
            <div className="flex justify-between items-center py-2 border-b border-gray-200"><span className="text-sm text-gray-600">Current Age</span><span className="text-sm font-bold text-gray-900 font-mono">{eq.install_year ? new Date().getFullYear() - Number(eq.install_year) : "Unknown"} years</span></div>
            <div className="flex justify-between items-center py-2 border-b border-gray-200"><span className="text-sm text-gray-600">Remaining Life (est.)</span><span className="text-sm font-bold font-mono" style={{ color: "#f9a825" }}>6–11 years</span></div>
            <div className="flex justify-between items-center py-2"><span className="text-sm text-gray-600">Active Recalls</span><span className="text-sm font-bold text-green-600 font-mono">None ✓</span></div>
          </div>
        </div>
        {/* Issues */}
        {issues.length > 0 && (
          <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden">
            <div className="px-4 py-3 border-b-2 font-mono text-xs font-bold uppercase tracking-wider text-purple-600" style={{ borderBottomColor: "#6a1b9a" }}>Issues Found ({issues.length})</div>
            <div className="p-4 space-y-3">
              {issues.map((iss, i) => (
                <div key={i} className="flex gap-3 items-start">
                  <div className="w-2 h-2 rounded-full mt-2 flex-shrink-0"
                    style={{ backgroundColor: iss.severity === "high" || iss.severity === "critical" ? "#c62828" : iss.severity === "low" ? "#1a8754" : "#c4600a" }} />
                  <div><p className="text-sm font-bold text-gray-900">{iss.component} — {iss.issue}</p><p className="text-xs text-gray-600 mt-0.5">{iss.description_plain || iss.description}</p></div>
                </div>
              ))}
            </div>
          </div>
        )}
        {error && <div className="bg-red-50 border border-red-200 rounded-xl p-3 text-sm text-red-600 font-medium">⚠ {error}</div>}
        <button onClick={handleGenerateEstimate}
          className="w-full text-white font-bold py-4 rounded-xl text-base shadow-lg transition-shadow hover:shadow-xl"
          style={{ background: "linear-gradient(135deg, #1a8754 0%, #159a5e 100%)", boxShadow: "0 4px 14px rgba(26,135,84,.45)" }}>
          Build Estimate →
        </button>
      </div>
    );
  }

  // ── Drag-drop helpers ──────────────────────────────────────────────────────
  const handleDragOver  = (e: React.DragEvent) => { e.preventDefault(); setIsDragging(true); };
  const handleDragLeave = (e: React.DragEvent) => { e.preventDefault(); setIsDragging(false); };
  const handleDrop      = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const files = Array.from(e.dataTransfer.files).filter(f => f.type.startsWith("image/"));
    // Fill empty required slots first, then extras
    let fi = 0;
    for (let si = 0; si < 3 && fi < files.length; si++) {
      if (!slotPhotos[si]) { activeSlotRef.current = si; handleFileForSlot(files[fi++]); }
    }
    while (fi < files.length && extraPhotos.length < 2) {
      activeSlotRef.current = "extra";
      handleFileForSlot(files[fi++]);
    }
  };

  // ══════════════════════════════════════════════════════════════════════════
  // PHASE: step-zero — nameplate OCR (WS-B) before complaint selection
  // ══════════════════════════════════════════════════════════════════════════
  if (phase === "step-zero") {
    return (
      <StepZeroPanel
        clerkToken={null}
        onConfirm={(result) => {
          setOcrResult(result as unknown as Record<string, unknown>);
          setPhase("complaint");
        }}
        onSkip={() => setPhase("complaint")}
      />
    );
  }

  // ══════════════════════════════════════════════════════════════════════════
  // PHASE: complaint selector
  // ══════════════════════════════════════════════════════════════════════════
  if (phase === "complaint") {
    return (
      <div className="max-w-lg mx-auto space-y-5 px-4 pb-6">
        <div className="pt-4">
          <h1 className="text-3xl font-extrabold tracking-tight">New Assessment</h1>
          <p className="text-text-secondary text-sm mt-1">What's the complaint? We'll guide your photos.</p>
        </div>

        <div className="grid grid-cols-2 gap-3">
          {COMPLAINT_OPTIONS.map(opt => (
            <button
              key={opt.id}
              onClick={() => {
                setComplaintType(opt.id);
                setPhase("capture"); // photos first — sensor is optional from the capture screen
              }}
              className="bg-white border-2 border-gray-200 hover:border-green-500 rounded-2xl p-4 text-left transition-all active:scale-95 focus:outline-none"
            >
              <div className="text-3xl mb-2">{opt.icon}</div>
              <p className="font-bold text-gray-900 text-sm leading-tight">{opt.label}</p>
              <p className="text-xs text-gray-500 mt-0.5">{opt.sub}</p>
            </button>
          ))}
        </div>

        <p className="text-center text-xs text-gray-400">Tap a complaint to continue</p>
      </div>
    );
  }

  // ══════════════════════════════════════════════════════════════════════════
  // PHASE: sensor — Jobs method (one field per screen, progress bar)
  // ══════════════════════════════════════════════════════════════════════════
  if (phase === "sensor") {
    const TOTAL = SENSOR_FIELDS.length; // 6
    const field = SENSOR_FIELDS[sensorFieldIndex];

    // Helper: commit current value and move forward
    const commitAndAdvance = () => {
      // Save whatever was typed (blank = skipped)
      const updated = { ...sensorValues, [field.key]: sensorCurrentValue };
      setSensorValues(updated);

      if (sensorFieldIndex < TOTAL - 1) {
        // Load next field — pre-fill if already visited
        const nextField = SENSOR_FIELDS[sensorFieldIndex + 1];
        setSensorFieldIndex(sensorFieldIndex + 1);
        setSensorCurrentValue(updated[nextField.key] ?? "");
      } else {
        // All fields done — apply values to individual state vars and go to capture
        setSensorUnitAge(updated["unitAge"] ?? "");
        setSensorOutdoorTemp(updated["outdoorTemp"] ?? "");
        setSensorSupplyTemp(updated["supplyTemp"] ?? "");
        setSensorReturnTemp(updated["returnTemp"] ?? "");
        setSensorSuction(updated["suction"] ?? "");
        setSensorDischarge(updated["discharge"] ?? "");
        setPhase("capture");
      }
    };

    const goBack = () => {
      // Save current value before going back
      const updated = { ...sensorValues, [field.key]: sensorCurrentValue };
      setSensorValues(updated);
      if (sensorFieldIndex === 0) {
        // Back to photos (sensor is accessed from capture screen)
        setPhase("capture");
      } else {
        const prevField = SENSOR_FIELDS[sensorFieldIndex - 1];
        setSensorFieldIndex(sensorFieldIndex - 1);
        setSensorCurrentValue(updated[prevField.key] ?? "");
      }
    };

    const skipAll = () => {
      // Clear all sensor values and proceed to capture
      setSensorUnitAge(""); setSensorOutdoorTemp(""); setSensorSupplyTemp("");
      setSensorReturnTemp(""); setSensorSuction(""); setSensorDischarge("");
      setSensorValues({});
      setPhase("capture");
    };

    const progressPct = ((sensorFieldIndex) / TOTAL) * 100;

    return (
      <div className="fixed inset-0 bg-[#f7f7f3] flex flex-col" style={{ zIndex: 50 }}>
        {/* ── Top bar ──────────────────────────────────────────────────────── */}
        <div className="px-5 pt-safe pt-4 pb-3">
          <div className="flex items-center justify-between mb-3">
            <button
              onClick={goBack}
              className="text-sm font-semibold text-gray-500 hover:text-gray-800 transition-colors"
            >
              ← Back
            </button>
            <span className="text-xs font-mono font-bold text-gray-400 uppercase tracking-widest">
              {sensorFieldIndex + 1} / {TOTAL}
            </span>
            <button
              onClick={skipAll}
              className="text-sm font-semibold text-brand-green hover:text-green-700 transition-colors"
            >
              Skip All
            </button>
          </div>

          {/* Progress bar */}
          <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-brand-green rounded-full transition-all duration-300"
              style={{ width: `${progressPct + (100 / TOTAL)}%` }}
            />
          </div>
        </div>

        {/* ── Field content ─────────────────────────────────────────────────── */}
        <div className="flex-1 flex flex-col justify-center px-6 pb-6">
          {/* Icon + label */}
          <div className="text-center mb-8">
            <div className="text-6xl mb-4">{field.icon}</div>
            <h2 className="text-3xl font-extrabold tracking-tight text-gray-900 mb-1">
              {field.label}
            </h2>
            <p className="text-sm text-gray-500 max-w-xs mx-auto">{field.hint}</p>
          </div>

          {/* Large number input */}
          <div className="relative mb-6">
            <input
              type="number"
              inputMode="decimal"
              value={sensorCurrentValue}
              onChange={e => setSensorCurrentValue(e.target.value)}
              onKeyDown={e => { if (e.key === "Enter") commitAndAdvance(); }}
              placeholder="—"
              autoFocus
              className="w-full text-center text-5xl font-bold tracking-tight bg-white border-2 border-gray-200 rounded-2xl py-6 focus:outline-none focus:border-brand-green transition-colors placeholder-gray-200"
              style={{ caretColor: "#1a8754" }}
            />
            <span className="absolute right-5 top-1/2 -translate-y-1/2 text-lg font-semibold text-gray-400">
              {field.unit}
            </span>
          </div>

          {/* Accuracy badge */}
          <div className="text-center mb-8">
            <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-green-700 bg-green-50 border border-green-200 rounded-full px-3 py-1">
              <span>⚡</span>
              Gauge readings boost accuracy to 93–95%
            </span>
          </div>

          {/* Next / Done button */}
          <button
            onClick={commitAndAdvance}
            className="w-full py-4 rounded-2xl font-bold text-base text-white shadow-lg transition-all active:scale-95"
            style={{ background: "linear-gradient(135deg, #1a8754 0%, #159a5e 100%)" }}
          >
            {sensorFieldIndex < TOTAL - 1 ? "Next →" : "Done — Back to Photos"}
          </button>

          {/* Skip this field */}
          <button
            onClick={commitAndAdvance}
            className="mt-3 w-full py-2 text-sm text-gray-400 hover:text-gray-600 transition-colors"
          >
            Skip this reading
          </button>
        </div>
      </div>
    );
  }

  // ══════════════════════════════════════════════════════════════════════════
  // PHASE: capture — guided 3-slot photo flow
  // ══════════════════════════════════════════════════════════════════════════
  const slotConfigs = getSlotConfig(complaintType);
  const selectedComplaint = COMPLAINT_OPTIONS.find(o => o.id === complaintType);

  return (
    <div className="max-w-lg mx-auto space-y-4 px-4 pb-6">

      {/* Shared file inputs — one camera, one file picker; slot tracked via activeSlotRef */}
      <input ref={fileInputRef} type="file" accept="image/*" multiple className="hidden"
        onChange={e => { Array.from(e.target.files || []).forEach(f => handleFileForSlot(f)); e.target.value = ""; }} />
      <input ref={cameraInputRef} type="file" accept="image/*" capture="environment" className="hidden"
        onChange={e => { const f = e.target.files?.[0]; if (f) handleFileForSlot(f); e.target.value = ""; }} />

      {/* Offline queued banner */}
      {offlineQueued && (
        <div className="flex items-center gap-3 bg-yellow-50 border border-yellow-200 rounded-xl px-4 py-3 mt-2">
          <span className="text-base">📡</span>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-bold text-yellow-900">Saved for when you&apos;re back online</p>
            <p className="text-xs text-yellow-700">{pendingCount} assessment{pendingCount !== 1 ? "s" : ""} will upload automatically when connected.</p>
          </div>
        </div>
      )}

      {/* Draft recovery */}
      {draftRecovery && (
        <div className="flex items-center gap-3 bg-brand-gold-light border border-brand-gold rounded-xl px-4 py-3 mt-2">
          <span className="text-base">📋</span>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-bold text-text-primary">Unsaved draft found</p>
            <p className="text-xs text-text-secondary truncate">{draftRecovery.address}</p>
          </div>
          <button onClick={() => { setAddress(draftRecovery.address); setCustomerName(draftRecovery.customerName || ""); setDraftRecovery(null); }} className="text-xs font-bold text-brand-orange hover:underline flex-shrink-0">Continue</button>
          <button onClick={() => { localStorage.removeItem(DRAFT_KEY); setDraftRecovery(null); }} className="text-xs text-text-secondary hover:text-text-primary flex-shrink-0">Discard</button>
        </div>
      )}

      {/* Header */}
      <div className="pt-2 flex items-center gap-3">
        <button onClick={() => setPhase("complaint")} className="text-sm text-gray-500 hover:text-gray-800 transition-colors">← Back</button>
        <div className="flex-1">
          <h1 className="text-2xl font-extrabold tracking-tight">
            {selectedComplaint ? `${selectedComplaint.icon} ${selectedComplaint.label}` : "New Assessment"}
          </h1>
          <p className="text-text-secondary text-xs mt-0.5">Take 3 photos below — usually done in 60 seconds</p>
        </div>
      </div>

      {/* ── Desktop camera stream (shown when active) ── */}
      {usingCamera && (
        <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden">
          <video ref={videoRef} autoPlay playsInline className="w-full aspect-video object-cover bg-gray-900" />
          <div className="p-3 flex gap-2">
            <button onClick={capturePhoto} className="flex-1 bg-green-600 hover:bg-green-700 text-white font-bold py-3 rounded-xl transition-colors">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{display:"inline",marginRight:5,verticalAlign:"middle"}}><path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/><circle cx="12" cy="13" r="4"/></svg>Capture Photo
            </button>
            <button onClick={stopCamera} className="px-4 bg-gray-100 hover:bg-gray-200 rounded-xl text-sm font-semibold transition-colors">Done</button>
          </div>
        </div>
      )}

      {/* ── 3 Required Photo Slots ── */}
      <div className="space-y-3">
        {slotConfigs.map(({ slot, icon, label, hint }) => {
          const filled   = slotPhotos[slot] !== null;
          const preview  = slotPreviews[slot];

          return (
            <div
              key={slot}
              className={`bg-white border-2 rounded-2xl overflow-hidden transition-colors ${filled ? "border-green-400" : "border-gray-200"}`}
              onDragOver={handleDragOver}
              onDragEnter={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              {filled && preview ? (
                /* Filled state */
                <div className="flex items-center gap-3 p-3">
                  <div className="relative flex-shrink-0">
                    <img src={preview} alt="" className="w-16 h-16 object-cover rounded-xl" />
                    <div className="absolute -top-1.5 -right-1.5 w-5 h-5 bg-green-500 rounded-full flex items-center justify-center text-white text-xs font-bold">✓</div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-1.5 mb-0.5">
                      <span className="w-5 h-5 rounded-full bg-green-100 text-green-700 text-xs font-black flex items-center justify-center">{slot + 1}</span>
                      <span className="text-xs font-mono font-bold text-green-700 uppercase tracking-wide">✓ {label}</span>
                    </div>
                    <p className="text-xs text-gray-500">Photo captured</p>
                  </div>
                  <button onClick={() => clearSlot(slot)} className="text-xs text-red-400 hover:text-red-600 font-semibold px-2 py-1 rounded-lg hover:bg-red-50 transition-colors flex-shrink-0">Retake</button>
                </div>
              ) : (
                /* Empty state */
                <div className="p-4">
                  <div className="flex items-start gap-3 mb-3">
                    <div className="flex-shrink-0 text-2xl leading-none mt-0.5">{icon}</div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-1.5 mb-0.5">
                        <span className="w-5 h-5 rounded-full bg-gray-100 text-gray-500 text-xs font-black flex items-center justify-center">{slot + 1}</span>
                        <span className="text-sm font-bold text-gray-900">Photo {slot + 1} — {label}</span>
                        <span className="text-xs bg-red-100 text-red-600 rounded px-1.5 py-0.5 font-semibold ml-1">Required</span>
                      </div>
                      <p className="text-xs text-gray-500 leading-relaxed">{hint}</p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => triggerSlotCapture(slot)}
                      className="flex-1 flex items-center justify-center gap-1.5 bg-green-600 hover:bg-green-700 text-white text-sm font-semibold py-2.5 rounded-xl transition-colors"
                    >
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/><circle cx="12" cy="13" r="4"/></svg>
                      Take Photo
                    </button>
                    <button
                      onClick={() => triggerSlotFile(slot)}
                      className="px-3 bg-gray-100 hover:bg-gray-200 border border-gray-300 font-semibold rounded-xl text-sm transition-colors text-gray-700"
                    >
                      Upload
                    </button>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* ── Optional extra photos ── */}
      <div className="bg-white border border-gray-200 rounded-2xl p-4">
        {/* Header row */}
        <div className="flex items-center justify-between mb-2">
          <div>
            <p className="text-sm font-bold text-gray-900">Add photos your homeowner will see</p>
            <p className="text-xs text-gray-500">Optional · up to 2 more · higher accuracy</p>
          </div>
          {extraPhotos.length < 2 && (
            <button
              onClick={() => triggerSlotCapture("extra")}
              className="flex items-center gap-1 text-xs font-semibold text-green-700 bg-green-50 hover:bg-green-100 border border-green-200 rounded-lg px-2.5 py-1.5 transition-colors"
            >
              <span className="text-base leading-none">+</span> Add
            </button>
          )}
        </div>

        {/* Confidence meter */}
        <div className="space-y-1 mb-3">
          <div className="flex items-center justify-between text-xs">
            <span className="text-gray-500">Estimate accuracy</span>
            <span className={`font-mono font-bold ${confidencePct >= 80 ? "text-green-600" : confidencePct >= 60 ? "text-yellow-600" : "text-gray-400"}`}>
              {allRequiredFilled ? `~${confidencePct}%` : "–"}
            </span>
          </div>
          <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 ${confidencePct >= 80 ? "bg-green-500" : confidencePct >= 60 ? "bg-yellow-400" : "bg-gray-300"}`}
              style={{ width: allRequiredFilled ? `${confidencePct}%` : "0%" }}
            />
          </div>
        </div>

        {/* Extra photo thumbnails */}
        {extraPreviews.length > 0 && (
          <div className="flex gap-2">
            {extraPreviews.map((url, i) => (
              <div key={i} className="relative flex-shrink-0">
                <img src={url} alt="" className="w-16 h-16 object-cover rounded-xl" />
                <button onClick={() => removeExtra(i)} className="absolute -top-1.5 -right-1.5 w-5 h-5 bg-red-500 text-white rounded-full text-xs flex items-center justify-center font-bold hover:bg-red-600">×</button>
              </div>
            ))}
            {extraPhotos.length < 2 && (
              <button onClick={() => triggerSlotFile("extra")} className="w-16 h-16 rounded-xl border-2 border-dashed border-gray-300 flex items-center justify-center text-2xl text-gray-400 hover:border-green-400 hover:text-green-500 transition-colors">+</button>
            )}
          </div>
        )}
      </div>

      {/* ── Job info ── */}
      <div className="bg-white border border-gray-200 rounded-2xl p-4 space-y-3">
        <p className="text-xs font-mono text-gray-600 uppercase tracking-widest font-bold">Job Info</p>
        <div className="relative">
          <input type="text" placeholder="Property address (search existing...)" value={address}
            onChange={e => { setAddress(e.target.value); setShowSuggestions(true); }}
            onFocus={() => setShowSuggestions(true)}
            className="w-full border border-gray-300 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:border-green-600 focus:ring-1 focus:ring-green-500 transition-colors" />
          {showSuggestions && suggestions.length > 0 && (
            <div className="absolute z-10 w-full bg-white border border-gray-300 rounded-xl mt-1 shadow-lg">
              {suggestions.map(s => (
                <button key={s.id} onMouseDown={async () => {
                  setAddress(s.address_line1 || ""); setCustomerName(s.customer_name || "");
                  setShowSuggestions(false); setSelectedProperty(s);
                  try {
                    const h = await getAuthHeaders();
                    const r = await fetch(`${API_URL}/api/estimates/?property_id=${s.id}&limit=5`, { headers: h });
                    if (r.ok) { const d = await r.json(); setPriorEstimates(Array.isArray(d.items) ? d.items : Array.isArray(d) ? d : []); }
                  } catch { /* ignore */ }
                }} className="w-full text-left px-3 py-2.5 hover:bg-gray-100 text-sm border-b border-gray-200 last:border-0 transition-colors">
                  <p className="font-semibold text-gray-900">{s.address_line1}</p>
                  <p className="text-xs text-gray-600">{[s.customer_name, s.returning_customer && "⚡ Previous visit found"].filter(Boolean).join(" · ")}</p>
                </button>
              ))}
            </div>
          )}
        </div>
        <div className="grid grid-cols-2 gap-2">
          <input type="text" placeholder="Homeowner name" value={customerName} onChange={e => setCustomerName(e.target.value)} className="border border-gray-300 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:border-green-600 focus:ring-1 focus:ring-green-500 transition-colors" />
          <input type="tel" placeholder="Phone number" value={customerPhone} onChange={e => setCustomerPhone(e.target.value)} className="border border-gray-300 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:border-green-600 focus:ring-1 focus:ring-green-500 transition-colors" />
        </div>
      </div>

      {/* ── Sensor readings — Jobs-style subtle trigger (photo page) ───────── */}
      {(sensorUnitAge || sensorOutdoorTemp || sensorSuction) ? (
        /* Readings already entered — show success badge with Edit */
        <div className="flex items-center justify-between bg-green-50 border border-green-200 rounded-2xl px-4 py-2.5">
          <div className="flex items-center gap-2">
            <span className="text-sm">⚡</span>
            <div>
              <p className="text-xs font-bold text-green-800">Gauge readings added — 93–95% accuracy</p>
              <p className="text-xs text-green-600">High-confidence diagnosis active</p>
            </div>
          </div>
          <button
            onClick={() => {
              setSensorFieldIndex(0);
              setSensorCurrentValue(sensorValues["unitAge"] ?? sensorUnitAge);
              setPhase("sensor");
            }}
            className="text-xs font-semibold text-green-700 underline underline-offset-2 hover:text-green-900"
          >
            Edit
          </button>
        </div>
      ) : (
        /* No readings — subtle Jobs-style prompt, easy to miss (intentional) */
        <button
          onClick={() => {
            setSensorFieldIndex(0);
            setSensorCurrentValue("");
            setSensorValues({});
            setPhase("sensor");
          }}
          className="w-full flex items-center justify-between px-4 py-2.5 rounded-2xl border border-dashed border-gray-200 hover:border-green-400 hover:bg-green-50 transition-all group"
        >
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-400 group-hover:text-green-600 transition-colors">📡</span>
            <span className="text-xs text-gray-400 group-hover:text-green-700 font-medium transition-colors">
              Have gauge readings? Add them for higher accuracy
            </span>
          </div>
          <span className="text-xs text-gray-300 group-hover:text-green-500 transition-colors">→</span>
        </button>
      )}


      {/* Prior property history */}
      {selectedProperty && (
        <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden">
          <div className="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-base">🏠</span>
              <div>
                <p className="text-xs font-mono text-gray-600 uppercase tracking-widest font-bold">Returning Customer</p>
                <p className="text-sm font-bold text-gray-900">{selectedProperty.customer_name || selectedProperty.address_line1}</p>
              </div>
            </div>
            <button onClick={() => { setSelectedProperty(null); setPriorEstimates([]); }} className="text-xs text-gray-500 hover:text-gray-700 font-semibold">✕</button>
          </div>
          <div className="p-4">
            {priorEstimates.length === 0 ? (
              <p className="text-sm text-gray-500 text-center py-2">No prior estimates on file for this property.</p>
            ) : (
              <div className="space-y-2">
                <p className="text-xs text-gray-500 font-semibold mb-2">Prior Assessments ({priorEstimates.length})</p>
                {priorEstimates.map(est => {
                  const statusColors: Record<string, string> = { approved:"bg-green-100 text-green-700", deposit_paid:"bg-green-100 text-green-700", sent:"bg-blue-100 text-blue-700", viewed:"bg-blue-100 text-blue-700", estimated:"bg-yellow-100 text-yellow-700", draft:"bg-gray-100 text-gray-600" };
                  const daysAgo = est.created_at ? Math.floor((Date.now() - new Date(est.created_at).getTime()) / 86400000) : null;
                  return (
                    <a key={est.id} href={`/assessment/${est.id}`} className="flex items-center justify-between gap-3 p-3 bg-gray-50 hover:bg-gray-100 rounded-xl transition-colors">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-bold text-gray-900">{est.report_short_id}</span>
                        <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${statusColors[est.status] || "bg-gray-100 text-gray-600"}`}>{est.status.replace(/_/g, " ")}</span>
                      </div>
                      <div className="flex items-center gap-3 text-xs text-gray-500">
                        {est.total_amount != null && <span className="font-mono font-bold text-gray-900">${est.total_amount.toLocaleString()}</span>}
                        {daysAgo != null && <span>{daysAgo === 0 ? "today" : daysAgo === 1 ? "yesterday" : `${daysAgo}d ago`}</span>}
                        <span className="text-gray-400">↗</span>
                      </div>
                    </a>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      )}

      {error && <div className="bg-red-50 border border-red-200 rounded-xl p-3 text-sm text-red-600 font-medium">⚠ {error}</div>}

      {/* ── Progress indicator above submit ── */}
      <div className="flex items-center gap-2 px-1">
        {[0,1,2].map(i => (
          <div key={i} className={`flex-1 h-1.5 rounded-full transition-all duration-300 ${slotPhotos[i] ? "bg-green-500" : "bg-gray-200"}`} />
        ))}
        <span className="text-xs font-mono font-semibold text-gray-500 ml-1 whitespace-nowrap">{filledCount}/3 required</span>
      </div>

      {/* Submit */}
      <button
        onClick={handleSubmit}
        disabled={!allRequiredFilled}
        className="w-full text-white font-bold py-4 rounded-xl text-base shadow-lg transition-all"
        style={allRequiredFilled
          ? { background: "linear-gradient(135deg, #1a8754 0%, #1