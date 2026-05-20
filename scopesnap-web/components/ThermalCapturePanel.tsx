/**
 * WS-E — Thermal Camera Capture Panel (Card #16 Path A)
 *
 * Card #16: Loose Terminal / Wiring Fault
 * "FLIR One ~$400. 10-15% missed without camera." — SnapAI_Decision_Tree.html
 *
 * Path A1: Web Bluetooth FLIR One pairing (Chrome desktop/Android only — iOS Safari blocked)
 * Path A2: Manual upload of thermal .jpg/.png (guaranteed fallback — all browsers)
 * Path B:  No thermal photo → Gemini multi-input fallback (existing flow)
 *
 * Usage: Mount this when the assessment reaches Card #16 (Loose Terminal).
 * onConfirmed(result) fires when hotspot analysis completes.
 * onSkip() fires if tech doesn't have a thermal camera.
 */
"use client";

import { useState, useRef, useCallback } from "react";
import { API_URL } from "@/lib/api";

// ── Types ────────────────────────────────────────────────────────────────────

interface ThermalHotspot {
  location: string;
  severity: "mild" | "moderate" | "severe";
  temp_delta_estimate: string | null;
  likely_cause: string | null;
  confidence: number;
}

interface ThermalResult {
  hotspots_detected: boolean;
  hotspot_count: number;
  hotspots: ThermalHotspot[];
  overall_assessment: "normal" | "suspect" | "fault_confirmed";
  recommended_action: string | null;
  card_16_confirmed: boolean;
  notes: string | null;
  capture_method: string;
  analyzed_at: string;
}

interface Props {
  assessmentId?: string;
  clerkToken: string | null;
  onConfirmed: (result: ThermalResult) => void;
  onSkip: () => void;
}

// ── Severity helpers ─────────────────────────────────────────────────────────

const SEVERITY_STYLE: Record<string, React.CSSProperties> = {
  mild:     { background: "#fef3e8", color: "#c4600a", borderColor: "#f6c07e" },
  moderate: { background: "#fce8d5", color: "#9b3d0a", borderColor: "#e8945e" },
  severe:   { background: "#fce8e8", color: "#c62828", borderColor: "#e88e8e" },
};

const ASSESSMENT_STYLE: Record<string, { bg: string; color: string; label: string }> = {
  normal:          { bg: "#e8f5ee", color: "#1a8754", label: "No fault detected" },
  suspect:         { bg: "#fef3e8", color: "#c4600a", label: "Suspect — verify with multimeter" },
  fault_confirmed: { bg: "#fce8e8", color: "#c62828", label: "Fault confirmed — route to Card #16" },
};

// ── Component ────────────────────────────────────────────────────────────────

export default function ThermalCapturePanel({ assessmentId, clerkToken, onConfirmed, onSkip }: Props) {
  const [photo,       setPhoto]       = useState<File | null>(null);
  const [preview,     setPreview]     = useState<string | null>(null);
  const [method,      setMethod]      = useState<string>("manual_upload");
  const [loading,     setLoading]     = useState(false);
  const [error,       setError]       = useState<string | null>(null);
  const [result,      setResult]      = useState<ThermalResult | null>(null);
  const [bleStatus,   setBleStatus]   = useState<"idle" | "scanning" | "connected" | "unsupported">("idle");

  const fileInputRef = useRef<HTMLInputElement>(null);

  // ── Path A2: Manual upload ────────────────────────────────────────────────

  const handleFileChange = useCallback((file: File | null) => {
    if (!file) return;
    setPhoto(file);
    setPreview(URL.createObjectURL(file));
    setResult(null);
    setError(null);
    setMethod("manual_upload");
  }, []);

  // ── Path A1: Web Bluetooth FLIR One ──────────────────────────────────────

  const connectFLIR = useCallback(async () => {
    if (!("bluetooth" in navigator)) {
      setBleStatus("unsupported");
      return;
    }
    setBleStatus("scanning");
    try {
      // FLIR One Pro Edge BLE service UUID (FLIR Systems)
      const device = await (navigator as any).bluetooth.requestDevice({
        filters: [
          { namePrefix: "FLIR" },
          { services: ["0000ffd0-0000-1000-8000-00805f9b34fb"] },
        ],
        optionalServices: ["0000ffd0-0000-1000-8000-00805f9b34fb"],
      });
      setBleStatus("connected");
      setMethod("flir_ble");
      // Note: Full FLIR BLE image transfer is ~300 bytes/packet.
      // For now, connected state confirms device is paired.
      // Full capture implementation: subscribe to image characteristic,
      // reassemble packets, convert to .jpg, call analyzeImage().
      // This is a progressive enhancement — the manual upload below handles all cases.
      setError("FLIR One connected. Use the camera app to capture, then upload the .jpg below.");
    } catch (e) {
      setBleStatus("idle");
      setError("FLIR One pairing cancelled or failed. Use manual upload instead.");
    }
  }, []);

  // ── POST /api/thermal/analyze ─────────────────────────────────────────────

  const analyzeImage = useCallback(async () => {
    if (!photo) {
      setError("Please capture or upload a thermal photo first.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const fd = new FormData();
      fd.append("photo", photo);
      fd.append("capture_method", method);
      if (assessmentId) fd.append("assessment_id", assessmentId);

      const headers: Record<string, string> = {};
      if (clerkToken) {
        headers["Authorization"] = `Bearer ${clerkToken}`;
      } else if (process.env.NEXT_PUBLIC_ENV === "development") {
        headers["X-Dev-Clerk-User-Id"] = "test_user_mike";
      }

      const res = await fetch(`${API_URL}/api/thermal/analyze`, {
        method: "POST",
        headers,
        body: fd,
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Analysis failed (${res.status})`);
      }

      const data: ThermalResult = await res.json();
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Analysis failed. Retry or skip.");
    } finally {
      setLoading(false);
    }
  }, [photo, method, assessmentId, clerkToken]);

  // ── Render ────────────────────────────────────────────────────────────────

  const bleUnsupported = bleStatus === "unsupported" || typeof window !== "undefined" && !("bluetooth" in navigator);

  return (
    <div className="max-w-md mx-auto px-4 pb-8 pt-4 space-y-4">

      {/* Header */}
      <div className="bg-white border-2 rounded-2xl overflow-hidden" style={{ borderColor: "#6a1b9a" }}>
        <div className="px-4 py-3" style={{ background: "linear-gradient(135deg,#f8f0ff,#f0e4ff)" }}>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-black uppercase tracking-widest px-2 py-0.5 rounded-full text-white"
                  style={{ background: "#6a1b9a" }}>
              Card #16 — Path A
            </span>
            <span className="text-xs text-gray-500">Thermal Camera</span>
          </div>
          <h2 className="text-base font-black text-gray-900">Loose Terminal / Wiring Fault</h2>
          <p className="text-xs text-gray-500 mt-0.5">
            Thermal photo detects hotspots {">"} 20°F above ambient = fault confirmed
          </p>
        </div>
      </div>

      {/* Path A1 — FLIR One BLE (optional, Chrome/Android only) */}
      {!bleUnsupported && (
        <div className="bg-white border border-gray-200 rounded-xl p-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-bold text-gray-800">FLIR One — Pair via Bluetooth</p>
              <p className="text-xs text-gray-500">Chrome desktop / Android only. Not available on Safari iOS.</p>
            </div>
            <button
              onClick={connectFLIR}
              disabled={bleStatus === "scanning" || bleStatus === "connected"}
              className="text-xs font-bold px-3 py-1.5 rounded-lg transition-colors"
              style={{
                background: bleStatus === "connected" ? "#e8f5ee" : "#6a1b9a",
                color: bleStatus === "connected" ? "#1a8754" : "#fff",
              }}
            >
              {bleStatus === "scanning" ? "Scanning..." :
               bleStatus === "connected" ? "Connected" : "Pair FLIR One"}
            </button>
          </div>
        </div>
      )}

      {/* Path A2 — Manual upload (guaranteed fallback) */}
      <div>
        <p className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">
          {bleUnsupported ? "Upload thermal photo" : "Or upload thermal photo (.jpg / .png)"}
        </p>
        <button
          onClick={() => fileInputRef.current?.click()}
          className="relative w-full rounded-xl border-2 overflow-hidden flex flex-col items-center justify-center min-h-[140px] transition-colors"
          style={{ borderColor: photo ? "#6a1b9a" : "#e2dfd7", background: "#fafaf8" }}
        >
          {preview ? (
            <>
              <img src={preview} alt="Thermal photo" className="w-full h-full object-cover absolute inset-0" />
              <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/70 to-transparent px-3 py-2">
                <p className="text-xs font-bold text-white">Tap to retake</p>
                <p className="text-[10px] text-white/70">{method === "flir_ble" ? "FLIR One BLE" : "Manual upload"}</p>
              </div>
            </>
          ) : (
            <div className="flex flex-col items-center gap-2 p-4 text-center">
              <div className="w-12 h-12 rounded-full flex items-center justify-center text-2xl"
                   style={{ background: "#f0e4ff" }}>
                +
              </div>
              <p className="text-sm font-bold text-gray-700">Upload thermal image</p>
              <p className="text-xs text-gray-400">FLIR .jpg, thermal screenshot, or regular photo with burn marks</p>
            </div>
          )}
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            capture="environment"
            className="hidden"
            onChange={e => handleFileChange(e.target.files?.[0] ?? null)}
          />
        </button>
      </div>

      {/* Analyze button */}
      {photo && !result && (
        <button
          onClick={analyzeImage}
          disabled={loading}
          className="w-full py-3.5 rounded-xl font-black text-white text-sm"
          style={{ background: loading ? "#ccc" : "#6a1b9a" }}
        >
          {loading ? "Analyzing for hotspots..." : "Detect Hotspots with AI"}
        </button>
      )}

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center gap-3 py-2">
          {[0,1,2].map(i => (
            <div key={i} className="w-2.5 h-2.5 rounded-full animate-bounce"
                 style={{ background: "#6a1b9a", animationDelay: `${i*0.15}s` }} />
          ))}
          <span className="text-sm text-gray-500 font-medium">Gemini scanning for hotspots...</span>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-3 text-sm text-yellow-800 font-medium">
          {error}
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-3">
          {/* Overall assessment badge */}
          <div className="rounded-xl border-2 p-3"
               style={{
                 background: ASSESSMENT_STYLE[result.overall_assessment]?.bg || "#f7f7f3",
                 borderColor: ASSESSMENT_STYLE[result.overall_assessment]?.color || "#ccc",
               }}>
            <div className="flex items-center justify-between">
              <p className="text-sm font-black"
                 style={{ color: ASSESSMENT_STYLE[result.overall_assessment]?.color }}>
                {result.card_16_confirmed ? "Card #16 CONFIRMED — Loose Terminal" : ASSESSMENT_STYLE[result.overall_assessment]?.label}
              </p>
              {result.card_16_confirmed && (
                <span className="text-xs font-bold px-2 py-0.5 rounded-full text-white"
                      style={{ background: "#c62828" }}>
                  Route to Card #16
                </span>
              )}
            </div>
            {result.recommended_action && (
              <p className="text-xs mt-1 text-gray-600">{result.recommended_action}</p>
            )}
          </div>

          {/* Hotspot list */}
          {result.hotspots.length > 0 && (
            <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden">
              <div className="px-4 py-2.5 border-b border-gray-100">
                <span className="text-xs font-black uppercase tracking-wider"
                      style={{ color: "#c62828" }}>
                  {result.hotspot_count} Hotspot{result.hotspot_count !== 1 ? "s" : ""} detected
                </span>
              </div>
              <div className="p-3 space-y-2">
                {result.hotspots.map((h, i) => (
                  <div key={i} className="rounded-xl border px-3 py-2.5"
                       style={SEVERITY_STYLE[h.severity] || SEVERITY_STYLE.mild}>
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1">
                        <p className="text-sm font-bold">{h.location}</p>
                        {h.temp_delta_estimate && (
                          <p className="text-xs font-mono mt-0.5">{h.temp_delta_estimate}</p>
                        )}
                        {h.likely_cause && (
                          <p className="text-xs mt-0.5 opacity-80">{h.likely_cause}</p>
                        )}
                      </div>
                      <div className="text-right flex-shrink-0">
                        <span className="text-xs font-black uppercase px-1.5 py-0.5 rounded"
                              style={{ background: "rgba(0,0,0,0.08)" }}>
                          {h.severity}
                        </span>
                        <p className="text-[10px] mt-0.5 opacity-70">{h.confidence}% conf.</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {result.notes && (
            <p className="text-xs text-gray-400 px-1">{result.notes}</p>
          )}
        </div>
      )}

      {/* Action buttons */}
      <div className="flex gap-3 pt-1">
        <button
          onClick={onSkip}
          className="flex-1 py-3 rounded-xl border-2 border-gray-200 text-sm font-bold text-gray-500"
        >
          No thermal camera
        </button>
        <button
          onClick={() => result ? onConfirmed(result) : onSkip()}
          className="py-3 px-6 rounded-xl text-sm font-black text-white"
          style={{ background: result?.card_16_confirmed ? "#c62828" : "#6a1b9a", flex: 2 }}
        >
          {result?.card_16_confirmed ? "Confirm Card #16 Fault" :
           result ? "Continue with findings" : "Skip thermal"}
        </button>
      </div>

      {!bleUnsupported && (
        <p className="text-center text-[10px] text-gray-400">
          Web Bluetooth requires Chrome desktop or Android. Safari iOS not supported — use manual upload.
        </p>
      )}
    </div>
  );
}
