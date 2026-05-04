"use client";

import { useState, useRef } from "react";
import { API_URL } from "@/lib/api";

export interface PhotoSlotSpec {
  slot_name: string;
  photo_type: "diagnostic" | "evidence";
  instruction: string;
  ai_prompt?: string | null;
}

export interface PhotoResult {
  slot_name: string;
  photo_type: "diagnostic" | "evidence";
  photo_url: string;
  ai_grade?: string | null;
}

interface PhotoSlotProps {
  spec: PhotoSlotSpec;
  assessmentId: string;
  authHeaders: Record<string, string>;
  onCapture: (result: PhotoResult) => void;
  disabled?: boolean;
}

export default function PhotoSlot({ spec, assessmentId, authHeaders, onCapture, disabled = false }: PhotoSlotProps) {
  const [preview, setPreview] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [aiGrade, setAiGrade] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const isDiagnostic = spec.photo_type === "diagnostic";
  const borderStyle = isDiagnostic
    ? "2px solid #2ecc71"
    : "2px dashed #3498db";
  const chipLabel = isDiagnostic ? "Diagnostic Photo" : "Evidence Only";
  const chipColor = isDiagnostic ? "#2ecc71" : "#3498db";
  const chipBg = isDiagnostic ? "rgba(46,204,113,0.12)" : "rgba(52,152,219,0.12)";

  const handleFile = async (file: File) => {
    if (!file.type.startsWith("image/")) return;
    setPreview(URL.createObjectURL(file));
    setUploading(true);
    setError(null);
    setAiGrade(null);

    try {
      const fd = new FormData();
      fd.append("file", file);
      fd.append("assessment_id", assessmentId);
      fd.append("slot_name", spec.slot_name);
      fd.append("photo_type", spec.photo_type);
      if (spec.ai_prompt) fd.append("ai_prompt", spec.ai_prompt);

      const r = await fetch(`${API_URL}/api/uploads`, { method: "POST", headers: authHeaders, body: fd });
      if (!r.ok) throw new Error("Upload failed");
      const data = await r.json();
      const url = data.url ?? data.photo_url ?? data.file_url;
      if (data.ai_grade) setAiGrade(data.ai_grade);
      onCapture({ slot_name: spec.slot_name, photo_type: spec.photo_type, photo_url: url, ai_grade: data.ai_grade ?? null });
    } catch {
      setError("Upload failed — tap to retry");
      setPreview(null);
    } finally {
      setUploading(false);
    }
  };

  const triggerCapture = () => {
    if (disabled || uploading) return;
    inputRef.current?.click();
  };

  return (
    <div className="flex flex-col gap-2 w-full">
      <div className="flex items-center gap-2">
        <span
          className="text-xs font-bold px-2.5 py-1 rounded-full"
          style={{ color: chipColor, background: chipBg }}
        >
          {isDiagnostic ? "📸" : "📋"} {chipLabel}
        </span>
      </div>

      <button
        onClick={triggerCapture}
        disabled={disabled}
        className="w-full rounded-2xl overflow-hidden transition-all active:scale-95 relative"
        style={{ border: borderStyle, minHeight: "180px", background: "#0f1117" }}
      >
        {preview ? (
          <>
            <img src={preview} alt="captured" className="w-full h-full object-cover" style={{ minHeight: "180px" }} />
            {uploading && (
              <div className="absolute inset-0 flex items-center justify-center" style={{ background: "rgba(0,0,0,.6)" }}>
                <div className="w-8 h-8 border-2 border-white border-t-transparent rounded-full animate-spin" />
              </div>
            )}
            {aiGrade && (
              <div className="absolute bottom-2 left-2 right-2 px-3 py-1.5 rounded-xl text-xs font-bold text-white" style={{ background: "rgba(0,0,0,.75)" }}>
                AI: {aiGrade}
              </div>
            )}
          </>
        ) : (
          <div className="flex flex-col items-center justify-center gap-3 p-6" style={{ minHeight: "180px" }}>
            <div className="text-4xl opacity-40">{isDiagnostic ? "📸" : "📋"}</div>
            <p className="text-sm text-center font-medium" style={{ color: chipColor }}>{spec.instruction}</p>
            {spec.ai_prompt && (
              <p className="text-xs text-center italic" style={{ color: "rgba(240,240,240,.45)" }}>AI will evaluate this photo</p>
            )}
          </div>
        )}
      </button>

      {error && (
        <p className="text-xs text-center font-medium" style={{ color: "#e74c3c" }}>{error}</p>
      )}

      {preview && !uploading && (
        <button
          onClick={triggerCapture}
          className="text-xs font-medium text-center py-2"
          style={{ color: "#3498db" }}
        >
          Retake photo
        </button>
      )}

      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        capture="environment"
        className="hidden"
        onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFile(f); e.target.value = ""; }}
      />
    </div>
  );
}
