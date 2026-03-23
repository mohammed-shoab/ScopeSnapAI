/**
 * Assess Page - Full camera capture, upload, AI analysis, intelligence results
 * Redesigned to match ScopeSnap_Prototype_Demo.html screens exactly
 */
"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { API_URL } from "@/lib/api";
import { OfflineError } from "@/lib/api";
import { saveToOfflineQueue, processOfflineQueue, getOfflineQueueCount } from "@/lib/offlineQueue";
import { track } from "@/lib/tracking";

const IS_DEV = process.env.NEXT_PUBLIC_ENV === "development";
const DEV_HEADER = { "X-Dev-Clerk-User-Id": "test_user_mike" };
type Phase = "capture" | "uploading" | "analyzing" | "results" | "estimating";

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

const DRAFT_KEY = "scopesnap_draft_assessment";

export default function AssessPage() {
  const router = useRouter();
  const { getToken } = useAuth();

  /** Returns the correct auth headers for API calls (dev bypass or real JWT). */
  const getAuthHeaders = useCallback(async (): Promise<Record<string, string>> => {
    if (IS_DEV) return DEV_HEADER;
    const token = await getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  }, [getToken]);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const [phase, setPhase] = useState<Phase>("capture");
  const [photos, setPhotos] = useState<File[]>([]);
  const [previewUrls, setPreviewUrls] = useState<string[]>([]);
  const [address, setAddress] = useState("");
  const [customerName, setCustomerName] = useState("");
  const [customerPhone, setCustomerPhone] = useState("");
  const [draftRecovery, setDraftRecovery] = useState<{address:string;customerName:string;timestamp:number}|null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [analysisStep, setAnalysisStep] = useState(0);
  const [suggestions, setSuggestions] = useState<PropertySuggestion[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [assessment, setAssessment] = useState<AssessmentResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [cameraStream, setCameraStream] = useState<MediaStream | null>(null);
  const [usingCamera, setUsingCamera] = useState(false);
  const [selectedProperty, setSelectedProperty] = useState<PropertySuggestion | null>(null);
  const [priorEstimates, setPriorEstimates] = useState<PriorEstimate[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [offlineQueued, setOfflineQueued] = useState(false);
  const [pendingCount, setPendingCount] = useState(0);

  // Draft recovery on mount + offline queue check
  useEffect(() => {
    try {
      const raw = localStorage.getItem(DRAFT_KEY);
      if (raw) {
        const draft = JSON.parse(raw);
        const ageHrs = (Date.now() - draft.timestamp) / 3600000;
        if (ageHrs < 4 && draft.address) setDraftRecovery(draft);
      }
    } catch { /* ignore */ }

    // Check for pending offline uploads
    getOfflineQueueCount().then(count => {
      if (count > 0) setPendingCount(count);
    }).catch(() => {});

    // Auto-sync offline queue when network reconnects
    const handleOnline = () => {
      getAuthHeaders().then(headers =>
        processOfflineQueue(API_URL, headers).then(({ uploaded }) => {
          if (uploaded > 0) setPendingCount(0);
        })
      ).catch(() => {});
    };
    window.addEventListener("online", handleOnline);
    // Attempt sync immediately if we're already online and have pending items
    if (typeof navigator !== "undefined" && navigator.onLine) {
      handleOnline();
    }
    return () => window.removeEventListener("online", handleOnline);
  }, []);

  // Save draft whenever address/name changes
  useEffect(() => {
    if (address || customerName) {
      try {
        localStorage.setItem(DRAFT_KEY, JSON.stringify({ address, customerName, timestamp: Date.now() }));
      } catch { /* ignore */ }
    }
  }, [address, customerName]);

  useEffect(() => {
    if (address.length < 3) {
      setSuggestions([]);
      return;
    }
    const t = setTimeout(async () => {
      try {
        const authHeaders = await getAuthHeaders();
        const r = await fetch(
          `${API_URL}/api/properties/search?q=${encodeURIComponent(address)}&limit=5`,
          { headers: authHeaders }
        );
        if (r.ok) {
          setSuggestions(await r.json());
          setShowSuggestions(true);
        }
      } catch {
        /* ignore */
      }
    }, 300);
    return () => clearTimeout(t);
  }, [address]);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment" },
      });
      setCameraStream(stream);
      setUsingCamera(true);
      if (videoRef.current) videoRef.current.srcObject = stream;
    } catch {
      setError("Camera unavailable — use file upload.");
    }
  };

  const capturePhoto = () => {
    if (!videoRef.current) return;
    const canvas = document.createElement("canvas");
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    canvas.getContext("2d")?.drawImage(videoRef.current, 0, 0);
    canvas.toBlob(
      (blob) => {
        if (!blob) return;
        addPhoto(
          new File([blob], `capture-${Date.now()}.jpg`, {
            type: "image/jpeg",
          })
        );
      },
      "image/jpeg",
      0.9
    );
  };

  const stopCamera = useCallback(() => {
    cameraStream?.getTracks().forEach((t) => t.stop());
    setCameraStream(null);
    setUsingCamera(false);
  }, [cameraStream]);

  const addPhoto = (file: File) => {
    if (photos.length >= 5) return;
    setPhotos((p) => [...p, file]);
    setPreviewUrls((p) => [...p, URL.createObjectURL(file)]);
    // SOW Task 1.10 — Bezos req: track photo count + file size for field connection diagnostics
    track.photoAdded(photos.length + 1, file.size);
  };

  const removePhoto = (i: number) => {
    setPhotos((p) => p.filter((_, idx) => idx !== i));
    setPreviewUrls((p) => p.filter((_, idx) => idx !== i));
  };

  const handleSubmit = async () => {
    if (!photos.length) {
      setError("Add at least 1 photo of the equipment.");
      return;
    }
    setError(null);
    setPhase("uploading");
    setUploadProgress(0);
    setAnalysisStep(0);
    const fd = new FormData();
    photos.forEach((p) => fd.append("photos", p));
    if (address) fd.append("property_address", address);
    if (customerName) fd.append("homeowner_name", customerName);
    if (customerPhone) fd.append("homeowner_phone", customerPhone);

    let uploaded: { id: string } | null = null;
    try {
      if (typeof navigator !== "undefined" && !navigator.onLine) {
        // Save to offline IndexedDB queue for auto-sync when reconnected
        await saveToOfflineQueue(photos, { address, customerName, customerPhone });
        setOfflineQueued(true);
        setPendingCount(c => c + 1);
        setPhase("capture");
        return;
      }
      setUploadProgress(30);
      const uploadAuthHeaders = await getAuthHeaders();
      let up: Response;
      try {
        up = await fetch(`${API_URL}/api/assessments/`, {
          method: "POST",
          headers: uploadAuthHeaders,
          body: fd,
        });
      } catch {
        // Network error mid-upload — queue for later
        await saveToOfflineQueue(photos, { address, customerName, customerPhone });
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

    // ── Analyze with 30s timeout and one retry ────────────────────────────
    setPhase("analyzing");
    setAnalysisStep(1);

    const analyzeAuthHeaders = await getAuthHeaders();
    const analyzeWithTimeout = async (attempt: number): Promise<Response> => {
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), 30000); // 30s timeout
      try {
        const r = await fetch(
          `${API_URL}/api/assessments/${uploaded!.id}/analyze`,
          { method: "POST", headers: analyzeAuthHeaders, signal: controller.signal }
        );
        clearTimeout(timer);
        return r;
      } catch (e: unknown) {
        clearTimeout(timer);
        const isAbort = e instanceof Error && e.name === "AbortError";
        if (isAbort && attempt === 1) {
          // First timeout — retry once
          setAnalysisStep(s => Math.min(s + 1, 4));
          return analyzeWithTimeout(2);
        }
        throw e;
      }
    };

    try {
      const stepTimer = setInterval(() => {
        setAnalysisStep(s => Math.min(s + 1, 4));
      }, 3500);
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
      setAssessment(await an.json());
      // Clear the draft now that assessment is created
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
      if (!r.ok)
        throw new Error((await r.json()).detail || "Generate failed");
      const est = await r.json();
      router.push(`/estimate/${est.id}`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Error");
      setPhase("results");
    }
  };

  // Uploading / Analyzing screen
  if (phase === "uploading" || phase === "analyzing") {
    const STEPS = [
      "Uploading photos…",
      "Reading equipment details…",
      "Identifying brand & model…",
      "Checking condition & wear…",
      "Building your estimate…",
    ];
    const currentMsg = phase === "uploading" ? STEPS[0] : (STEPS[analysisStep] || STEPS[1]);
    const progressPct = phase === "uploading" ? uploadProgress : Math.min(20 + analysisStep * 20, 90);

    return (
      <div className="max-w-md mx-auto pt-16 text-center space-y-6 px-4">
        {/* Pulsing dots animation — SOW Task 1.8 */}
        <div className="flex gap-3 justify-center" aria-label="Loading">
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              className="w-4 h-4 rounded-full bg-brand-green"
              style={{
                animation: `pulseDot 1.4s ease-in-out ${i * 0.2}s infinite`,
              }}
            />
          ))}
          <style>{`
            @keyframes pulseDot {
              0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
              40% { transform: scale(1.2); opacity: 1; }
            }
          `}</style>
        </div>

        <div>
          <h2 className="text-2xl font-extrabold tracking-tight mb-2">
            {phase === "uploading" ? "Uploading Photos" : "Analyzing Equipment"}
          </h2>
          <p className="text-sm text-text-secondary">{currentMsg}</p>
        </div>

        {/* Step checklist */}
        <div className="card p-4 space-y-2.5 text-left">
          {[
            "Reading photos",
            "Identifying brand & model",
            "Checking condition & wear",
            "Finding issues",
            "Building estimate",
          ].map((task, i) => {
            const done = phase === "analyzing" && i < analysisStep;
            const active = phase === "analyzing" && i === analysisStep;
            return (
              <div key={i} className="flex items-center gap-3 text-sm">
                <div className={`w-2 h-2 rounded-full flex-shrink-0 ${
                  done ? "bg-brand-green" : active ? "bg-brand-green animate-pulse" : "bg-surface-border"
                }`} />
                <span className={done ? "text-text-primary font-semibold" : active ? "text-text-primary" : "text-text-secondary"}>
                  {task}
                  {done && " ✓"}
                </span>
              </div>
            );
          })}
        </div>

        {/* Progress bar */}
        <div className="w-48 h-1.5 mx-auto bg-surface-secondary rounded-full overflow-hidden">
          <div
            className="h-full bg-brand-green rounded-full transition-all duration-700"
            style={{ width: `${progressPct}%` }}
          />
        </div>
        <p className="text-xs text-text-secondary font-mono">Usually takes 8–15 seconds</p>
      </div>
    );
  }

  // Estimating screen
  if (phase === "estimating") {
    return (
      <div className="max-w-md mx-auto pt-16 text-center space-y-4">
        <div className="text-5xl">⚙️</div>
        <h2 className="text-xl font-black">Building Estimate...</h2>
        <p className="text-sm text-gray-600">
          Calculating Good/Better/Best pricing
        </p>
      </div>
    );
  }

  // Results screen - Intelligence cards
  if (phase === "results" && assessment) {
    const eq = (assessment.ai_equipment_id || {}) as Record<
      string,
      string | number
    >;
    const cond = assessment.ai_condition || {};
    const issues = assessment.ai_issues || [];
    const overall = (cond.overall || "unknown").toLowerCase();

    const conditionColor: Record<string, string> = {
      excellent: "#1a8754",
      good: "#1a8754",
      fair: "#c4600a",
      poor: "#c4600a",
      critical: "#c62828",
      failed: "#c62828",
    };
    const color = conditionColor[overall] || "#7a7770";

    return (
      <div className="max-w-2xl mx-auto space-y-4 px-4">
        {/* Header */}
        <div className="flex items-center gap-3 pt-4">
          <button
            onClick={() => {
              setPhase("capture");
              setAssessment(null);
            }}
            className="text-sm text-gray-600 hover:text-gray-900"
          >
            ← Back
          </button>
          <h1 className="text-2xl font-black flex-1">Intelligence Results</h1>
        </div>

        {/* GREEN CARD: Equipment Identification */}
        <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden">
          <div
            className="px-4 py-3 border-b-2 font-mono text-xs font-bold uppercase tracking-wider text-green-600"
            style={{ borderBottomColor: "#1a8754" }}
          >
            ✓ Equipment Identified
          </div>
          <div className="p-4 space-y-3">
            <div className="font-mono text-2xl font-black text-gray-900">
              {String(eq.brand || "Unknown")}
              {eq.model ? ` ${eq.model}` : ""}
            </div>
            <div className="flex flex-wrap gap-2">
              {eq.serial && (
                <span className="px-2 py-1 bg-gray-100 rounded-lg text-xs font-semibold text-gray-600 font-mono">
                  SN: {eq.serial}
                </span>
              )}
              {eq.install_year && (
                <span className="px-2 py-1 bg-gray-100 rounded-lg text-xs font-semibold text-gray-600 font-mono">
                  Mfg: {eq.install_year}
                </span>
              )}
              {eq.confidence && (
                <span className="px-2 py-1 bg-gray-100 rounded-lg text-xs font-semibold text-gray-600 font-mono">
                  {Math.round(Number(eq.confidence))}% confidence
                </span>
              )}
            </div>

            {/* Confidence bar */}
            {eq.confidence && (
              <div className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-gray-600">ID Confidence</span>
                  <span className="font-mono font-bold text-green-600">
                    {Math.round(Number(eq.confidence))}%
                  </span>
                </div>
                <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-green-600 rounded-full"
                    style={{
                      width: `${Math.round(Number(eq.confidence))}%`,
                    }}
                  />
                </div>
              </div>
            )}
          </div>
        </div>

        {/* ORANGE CARD: Condition Assessment */}
        {(cond.components || []).length > 0 && (
          <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden">
            <div
              className="px-4 py-3 border-b-2 font-mono text-xs font-bold uppercase tracking-wider text-orange-600"
              style={{ borderBottomColor: "#c4600a" }}
            >
              ⚠ Condition Assessment
            </div>
            <div className="p-4 space-y-3">
              {(cond.components || []).map((comp, i) => (
                <div key={i} className="flex gap-3 items-start">
                  <div
                    className="w-7 h-7 rounded flex items-center justify-center flex-shrink-0 text-sm font-bold"
                    style={{
                      backgroundColor:
                        comp.condition === "normal"
                          ? "#e8f5ee"
                          : comp.condition.includes("minor")
                            ? "#fef3e8"
                            : "#fce8e8",
                      color:
                        comp.condition === "normal"
                          ? "#1a8754"
                          : comp.condition.includes("minor")
                            ? "#c4600a"
                            : "#c62828",
                    }}
                  >
                    {comp.condition === "normal" ? "✓" : "⚠"}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-bold text-gray-900">
                      {comp.name.replace(/_/g, " ")}
                    </h4>
                    <p className="text-sm text-gray-600 mt-0.5">
                      {comp.description_plain}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* BLUE CARD: Lifecycle Intelligence */}
        <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden">
          <div
            className="px-4 py-3 border-b-2 font-mono text-xs font-bold uppercase tracking-wider text-blue-600"
            style={{ borderBottomColor: "#1565c0" }}
          >
            Lifecycle Intelligence
          </div>
          <div className="p-4 space-y-2">
            <div className="flex justify-between items-center py-2 border-b border-gray-200">
              <span className="text-sm text-gray-600">Expected Lifespan</span>
              <span className="text-sm font-bold text-gray-900 font-mono">
                15–20 years
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-gray-200">
              <span className="text-sm text-gray-600">Current Age</span>
              <span className="text-sm font-bold text-gray-900 font-mono">
                {eq.install_year
                  ? new Date().getFullYear() - Number(eq.install_year)
                  : "Unknown"}{" "}
                years
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-gray-200">
              <span className="text-sm text-gray-600">Remaining Life (est.)</span>
              <span className="text-sm font-bold font-mono" style={{ color: "#f9a825" }}>
                6–11 years
              </span>
            </div>
            <div className="flex justify-between items-center py-2">
              <span className="text-sm text-gray-600">Active Recalls</span>
              <span className="text-sm font-bold text-green-600 font-mono">
                None ✓
              </span>
            </div>
          </div>
        </div>

        {/* PURPLE CARD: Recalls & History (if issues) */}
        {issues.length > 0 && (
          <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden">
            <div
              className="px-4 py-3 border-b-2 font-mono text-xs font-bold uppercase tracking-wider text-purple-600"
              style={{ borderBottomColor: "#6a1b9a" }}
            >
              Issues Found ({issues.length})
            </div>
            <div className="p-4 space-y-3">
              {issues.map((iss, i) => (
                <div key={i} className="flex gap-3 items-start">
                  <div
                    className="w-2 h-2 rounded-full mt-2 flex-shrink-0"
                    style={{
                      backgroundColor:
                        iss.severity === "high" || iss.severity === "critical"
                          ? "#c62828"
                          : iss.severity === "low"
                            ? "#1a8754"
                            : "#c4600a",
                    }}
                  />
                  <div>
                    <p className="text-sm font-bold text-gray-900">
                      {iss.component} — {iss.issue}
                    </p>
                    <p className="text-xs text-gray-600 mt-0.5">
                      {iss.description_plain || iss.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-3 text-sm text-red-600 font-medium">
            ⚠ {error}
          </div>
        )}

        {/* Build Estimate CTA */}
        <button
          onClick={handleGenerateEstimate}
          className="w-full text-white font-bold py-4 rounded-xl text-base shadow-lg transition-shadow hover:shadow-xl"
          style={{ background: "linear-gradient(135deg, #1a8754 0%, #159a5e 100%)", boxShadow: "0 4px 14px rgba(26,135,84,.45)" }}
        >
          Build Estimate →
        </button>
      </div>
    );
  }

  // ── Drag-drop handlers (desktop fallback) ────────────────────────────────
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };
  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const files = Array.from(e.dataTransfer.files)
      .filter(f => f.type.startsWith("image/"))
      .slice(0, 5 - photos.length);
    files.forEach(addPhoto);
  };

  // Capture screen
  return (
    <div className="max-w-lg mx-auto space-y-4 px-4 pb-4">
      {/* Offline queued banner */}
      {offlineQueued && (
        <div className="flex items-center gap-3 bg-yellow-50 border border-yellow-200 rounded-xl px-4 py-3 mt-2">
          <span className="text-base">📡</span>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-bold text-yellow-900">Saved for when you&apos;re back online</p>
            <p className="text-xs text-yellow-700">
              {pendingCount} assessment{pendingCount !== 1 ? "s" : ""} will upload automatically when connected.
            </p>
          </div>
        </div>
      )}

      {/* Draft Recovery Banner */}
      {draftRecovery && (
        <div className="flex items-center gap-3 bg-brand-gold-light border border-brand-gold rounded-xl px-4 py-3 mt-2">
          <span className="text-base">📋</span>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-bold text-text-primary">Unsaved draft found</p>
            <p className="text-xs text-text-secondary truncate">{draftRecovery.address}</p>
          </div>
          <button
            onClick={() => {
              setAddress(draftRecovery.address);
              setCustomerName(draftRecovery.customerName || "");
              setDraftRecovery(null);
            }}
            className="text-xs font-bold text-brand-orange hover:underline flex-shrink-0"
          >
            Continue
          </button>
          <button
            onClick={() => {
              localStorage.removeItem(DRAFT_KEY);
              setDraftRecovery(null);
            }}
            className="text-xs text-text-secondary hover:text-text-primary flex-shrink-0"
          >
            Discard
          </button>
        </div>
      )}

      {/* Header */}
      <div className="pt-2">
        <h1 className="text-3xl font-extrabold tracking-tight">New Assessment</h1>
        <p className="text-text-secondary text-sm mt-1">
          Photo → AI analysis in under 15 seconds
        </p>
      </div>

      {/* Camera or upload area */}
      {usingCamera ? (
        <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            className="w-full aspect-video object-cover bg-gray-900"
          />
          <div className="p-3 flex gap-2">
            <button
              onClick={capturePhoto}
              className="flex-1 bg-green-600 hover:bg-green-700 text-white font-bold py-3 rounded-xl transition-colors"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{display:"inline",marginRight:5,verticalAlign:"middle"}}><path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/><circle cx="12" cy="13" r="4"/></svg>Capture ({photos.length}/5)
            </button>
            <button
              onClick={stopCamera}
              className="px-4 bg-gray-100 hover:bg-gray-200 rounded-xl text-sm font-semibold transition-colors"
            >
              Done
            </button>
          </div>
        </div>
      ) : (
        <div
          className="bg-white border-2 border-dashed rounded-2xl p-6 text-center cursor-pointer transition-colors"
          style={{ borderColor: isDragging ? "#1a8754" : "#d1d5db", background: isDragging ? "rgba(26,135,84,.04)" : "white" }}
          onClick={() => fileInputRef.current?.click()}
          onDragOver={handleDragOver}
          onDragEnter={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <div className="mb-3 flex justify-center">
            {isDragging ? (
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#1a8754" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/>
                <polyline points="16 16 12 12 8 16"/><line x1="12" y1="12" x2="12" y2="21"/>
              </svg>
            ) : (
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/>
                <circle cx="12" cy="13" r="4"/>
              </svg>
            )}
          </div>
          <p className="font-bold text-gray-900 mb-1">
            {isDragging ? "Drop photos here" : "Add Equipment Photos"}
          </p>
          <p className="text-sm text-gray-600 mb-4">
            1–5 photos. Include the data plate if visible.
            <span className="hidden md:inline"> Or drag &amp; drop files here.</span>
          </p>
          <div className="flex gap-2 justify-center">
            <button
              onClick={(e) => {
                e.stopPropagation();
                // On mobile: use native camera capture input (rear camera directly)
                // On desktop: fall back to getUserMedia stream
                if (/Mobi|Android|iPhone|iPad/i.test(navigator.userAgent)) {
                  cameraInputRef.current?.click();
                } else {
                  startCamera();
                }
              }}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-xl text-sm transition-colors"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{display:"inline",marginRight:5,verticalAlign:"middle"}}><path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/><circle cx="12" cy="13" r="4"/></svg>Camera
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation();
                fileInputRef.current?.click();
              }}
              className="px-4 py-2 bg-gray-100 hover:bg-gray-200 border border-gray-300 font-semibold rounded-xl text-sm transition-colors"
            >
              Choose Files
            </button>
          </div>
          {/* Standard file picker */}
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            multiple
            className="hidden"
            onChange={(e) =>
              Array.from(e.target.files || [])
                .slice(0, 5 - photos.length)
                .forEach(addPhoto)
            }
          />
          {/* Mobile rear camera — capture="environment" opens native camera directly */}
          <input
            ref={cameraInputRef}
            type="file"
            accept="image/*"
            capture="environment"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) addPhoto(file);
              e.target.value = "";
            }}
          />
        </div>
      )}

      {/* Photo thumbnails */}
      {previewUrls.length > 0 && (
        <div className="flex gap-2 overflow-x-auto py-1">
          {previewUrls.map((url, i) => (
            <div key={i} className="relative flex-shrink-0">
              <img
                src={url}
                alt=""
                className="w-20 h-20 object-cover rounded-xl"
              />
              <button
                onClick={() => removePhoto(i)}
                className="absolute -top-2 -right-2 w-5 h-5 bg-red-600 text-white rounded-full text-xs flex items-center justify-center font-bold hover:bg-red-700 transition-colors"
              >
                ×
              </button>
            </div>
          ))}
          {photos.length < 5 && (
            <button
              onClick={() => fileInputRef.current?.click()}
              className="w-20 h-20 rounded-xl border-2 border-dashed border-gray-300 flex items-center justify-center flex-shrink-0 text-2xl text-gray-500 hover:border-green-500 transition-colors"
            >
              +
            </button>
          )}
        </div>
      )}

      {/* Property/customer info section */}
      <div className="bg-white border border-gray-200 rounded-2xl p-4 space-y-3">
        <p className="text-xs font-mono text-gray-600 uppercase tracking-widest font-bold">
          Job Info
        </p>

        {/* Address search */}
        <div className="relative">
          <input
            type="text"
            placeholder="Property address (search existing...)"
            value={address}
            onChange={(e) => {
              setAddress(e.target.value);
              setShowSuggestions(true);
            }}
            onFocus={() => setShowSuggestions(true)}
            className="w-full border border-gray-300 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:border-green-600 focus:ring-1 focus:ring-green-500 transition-colors"
          />
          {showSuggestions && suggestions.length > 0 && (
            <div className="absolute z-10 w-full bg-white border border-gray-300 rounded-xl mt-1 shadow-lg">
              {suggestions.map((s) => (
                <button
                  key={s.id}
                  onMouseDown={async () => {
                    setAddress(s.address_line1 || "");
                    setCustomerName(s.customer_name || "");
                    setShowSuggestions(false);
                    setSelectedProperty(s);
                    // Fetch prior estimates for this property
                    try {
                      const priorAuthHeaders = await getAuthHeaders();
                      const r = await fetch(
                        `${API_URL}/api/estimates/?property_id=${s.id}&limit=5`,
                        { headers: priorAuthHeaders }
                      );
                      if (r.ok) {
                        const data = await r.json();
                        const items = Array.isArray(data.items) ? data.items : Array.isArray(data) ? data : [];
                        setPriorEstimates(items);
                      }
                    } catch {
                      /* ignore */
                    }
                  }}
                  className="w-full text-left px-3 py-2.5 hover:bg-gray-100 text-sm border-b border-gray-200 last:border-0 transition-colors"
                >
                  <p className="font-semibold text-gray-900">
                    {s.address_line1}
                  </p>
                  <p className="text-xs text-gray-600">
                    {[
                      s.customer_name,
                      s.returning_customer && "⚡ Previous visit found",
                    ]
                      .filter(Boolean)
                      .join(" · ")}
                  </p>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Name and phone grid */}
        <div className="grid grid-cols-2 gap-2">
          <input
            type="text"
            placeholder="Homeowner name"
            value={customerName}
            onChange={(e) => setCustomerName(e.target.value)}
            className="border border-gray-300 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:border-green-600 focus:ring-1 focus:ring-green-500 transition-colors"
          />
          <input
            type="tel"
            placeholder="Phone number"
            value={customerPhone}
            onChange={(e) => setCustomerPhone(e.target.value)}
            className="border border-gray-300 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:border-green-600 focus:ring-1 focus:ring-green-500 transition-colors"
          />
        </div>
      </div>

      {/* Prior Property History Card */}
      {selectedProperty && (
        <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden">
          <div className="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-base">🏠</span>
              <div>
                <p className="text-xs font-mono text-gray-600 uppercase tracking-widest font-bold">
                  Returning Customer
                </p>
                <p className="text-sm font-bold text-gray-900">
                  {selectedProperty.customer_name || selectedProperty.address_line1}
                </p>
              </div>
            </div>
            <button
              onClick={() => { setSelectedProperty(null); setPriorEstimates([]); }}
              className="text-xs text-gray-500 hover:text-gray-700 font-semibold"
            >
              ✕
            </button>
          </div>
          <div className="p-4">
            {priorEstimates.length === 0 ? (
              <p className="text-sm text-gray-500 text-center py-2">
                No prior estimates on file for this property.
              </p>
            ) : (
              <div className="space-y-2">
                <p className="text-xs text-gray-500 font-semibold mb-2">
                  Prior Estimates ({priorEstimates.length})
                </p>
                {priorEstimates.map((est) => {
                  const statusColors: Record<string, string> = {
                    approved: "bg-green-100 text-green-700",
                    deposit_paid: "bg-green-100 text-green-700",
                    sent: "bg-blue-100 text-blue-700",
                    viewed: "bg-blue-100 text-blue-700",
                    estimated: "bg-yellow-100 text-yellow-700",
                    draft: "bg-gray-100 text-gray-600",
                  };
                  const daysAgo = est.created_at
                    ? Math.floor((Date.now() - new Date(est.created_at).getTime()) / 86400000)
                    : null;
                  return (
                    <a
                      key={est.id}
                      href={`/estimate/${est.id}`}
                      className="flex items-center justify-between gap-3 p-3 bg-gray-50 hover:bg-gray-100 rounded-xl transition-colors"
                    >
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-bold text-gray-900">
                          {est.report_short_id}
                        </span>
                        <span
                          className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
                            statusColors[est.status] || "bg-gray-100 text-gray-600"
                          }`}
                        >
                          {est.status.replace(/_/g, " ")}
                        </span>
                      </div>
                      <div className="flex items-center gap-3 text-xs text-gray-500">
                        {est.total_amount != null && (
                          <span className="font-mono font-bold text-gray-900">
                            ${est.total_amount.toLocaleString()}
                          </span>
                        )}
                        {daysAgo != null && (
                          <span>
                            {daysAgo === 0
                              ? "today"
                              : daysAgo === 1
                              ? "yesterday"
                              : `${daysAgo}d ago`}
                          </span>
                        )}
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

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-3 text-sm text-red-600 font-medium">
          ⚠ {error}
        </div>
      )}

      {/* Submit button */}
      <button
        onClick={handleSubmit}
        disabled={!photos.length}
        className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-bold py-4 rounded-xl text-base shadow-lg transition-colors"
      >
        {!photos.length
          ? "Add Photos to Continue"
          : `Analyze ${photos.length} Photo${photos.length > 1 ? "s" : ""} →`}
      </button>
    </div>
  );
}
