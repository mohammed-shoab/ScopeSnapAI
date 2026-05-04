"use client";

import { useState } from "react";
import PhotoSlot, { PhotoSlotSpec, PhotoResult } from "./PhotoSlot";

export interface AnswerRecord {
  step_id: string;
  question_text: string;
  answer_display: string;  // human-readable answer summary
}

interface FaultCardResultProps {
  cardId: number;
  cardName: string;
  resolutionPath: AnswerRecord[];
  photoSlots: PhotoSlotSpec[];
  assessmentId: string;
  authHeaders: Record<string, string>;
  onAllPhotosCaptured: (photos: PhotoResult[]) => void;
  onSkip: () => void;
}

export default function FaultCardResult({
  cardId,
  cardName,
  resolutionPath,
  photoSlots,
  assessmentId,
  authHeaders,
  onAllPhotosCaptured,
  onSkip,
}: FaultCardResultProps) {
  const [capturedPhotos, setCapturedPhotos] = useState<PhotoResult[]>([]);
  const requiredSlots = photoSlots.filter(s => s.photo_type === "diagnostic");
  const evidenceSlots = photoSlots.filter(s => s.photo_type === "evidence");

  const allRequired = requiredSlots.length === 0 || capturedPhotos.filter(p => p.photo_type === "diagnostic").length >= requiredSlots.length;

  const handleCaptured = (result: PhotoResult) => {
    setCapturedPhotos(prev => {
      const next = [...prev.filter(p => p.slot_name !== result.slot_name), result];
      return next;
    });
  };

  return (
    <div className="flex flex-col gap-5 w-full">
      {/* Resolution banner */}
      <div
        className="flex items-center gap-4 px-5 py-4 rounded-2xl"
        style={{ background: "rgba(46,204,113,0.12)", border: "2px solid #2ecc71" }}
      >
        <div
          className="w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0 text-2xl font-black"
          style={{ background: "#2ecc71", color: "#0f1117" }}
        >
          {cardId}
        </div>
        <div>
          <p className="text-xs font-bold uppercase tracking-widest mb-0.5" style={{ color: "#2ecc71" }}>
            Diagnosis Resolved
          </p>
          <p className="text-lg font-extrabold text-white leading-tight">{cardName}</p>
        </div>
      </div>

      {/* Diagnosis chain */}
      {resolutionPath.length > 0 && (
        <div className="rounded-xl p-4 space-y-2" style={{ background: "#16213e" }}>
          <p className="text-xs font-bold uppercase tracking-widest mb-2" style={{ color: "#7a8299" }}>
            Diagnosis Path
          </p>
          {resolutionPath.map((step, i) => (
            <div key={i} className="flex gap-3 text-sm">
              <span className="text-text-secondary flex-shrink-0 font-mono text-xs pt-0.5">{i + 1}.</span>
              <div className="flex-1 min-w-0">
                <span className="text-text-secondary">{step.question_text} </span>
                <span className="font-bold text-white">{step.answer_display}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Photo slots */}
      {photoSlots.length > 0 && (
        <div className="flex flex-col gap-4">
          <p className="text-sm font-bold text-text-secondary">
            {requiredSlots.length > 0 ? "Capture diagnostic photo(s) to continue:" : "Evidence photos for homeowner PDF:"}
          </p>
          {[...requiredSlots, ...evidenceSlots].map((slot) => (
            <PhotoSlot
              key={slot.slot_name}
              spec={slot}
              assessmentId={assessmentId}
              authHeaders={authHeaders}
              onCapture={handleCaptured}
            />
          ))}
        </div>
      )}

      {/* Actions */}
      <div className="flex flex-col gap-3">
        <button
          onClick={() => onAllPhotosCaptured(capturedPhotos)}
          disabled={!allRequired && photoSlots.length > 0}
          className="w-full py-4 rounded-2xl text-white font-extrabold text-base transition-all active:scale-95 disabled:opacity-40"
          style={{ background: "linear-gradient(135deg, #1a8754 0%, #159a5e 100%)", boxShadow: "0 4px 14px rgba(26,135,84,.35)" }}
        >
          Generate Estimate
        </button>
        <button
          onClick={onSkip}
          className="w-full py-3 rounded-2xl font-semibold text-sm transition-all active:scale-95"
          style={{ color: "#7a8299", background: "transparent" }}
        >
          Skip photos, generate estimate anyway
        </button>
      </div>
    </div>
  );
}
