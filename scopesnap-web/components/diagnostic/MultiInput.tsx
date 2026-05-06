"use client";

import { useState } from "react";
import PhotoSlot, { PhotoSlotSpec, PhotoResult } from "./PhotoSlot";
import ReadingInput, { ReadingSpec, ReadingResult } from "./ReadingInput";

// ── Sub-item type definitions ──────────────────────────────────────────────

export interface VisualSelectSpec {
  question_text: string;
  options: { value: string; label: string }[];
}

export interface SelectionResult {
  slot_name: string;
  value: string;
}

export type MultiInputItem =
  | { kind: "photo"; spec: PhotoSlotSpec }
  | { kind: "reading"; spec: ReadingSpec }
  | { kind: "visual_select"; spec: VisualSelectSpec };

export interface MultiInputData {
  photos: PhotoResult[];
  readings: ReadingResult[];
  selections: SelectionResult[];
  /** Primary routing key — from visual_select value or first reading branch_key. */
  branch_key?: string;
}

interface MultiInputProps {
  inputs: MultiInputItem[];
  assessmentId: string;
  authHeaders: Record<string, string>;
  ocrNameplate?: Record<string, unknown> | null;
  onSubmit: (data: MultiInputData) => void;
  disabled?: boolean;
}

// ── Inline visual-select picker (used inside multi steps) ─────────────────

function InlineVisualSelect({
  spec,
  disabled,
  onSelect,
}: {
  spec: VisualSelectSpec;
  disabled: boolean;
  onSelect: (value: string) => void;
}) {
  const [selected, setSelected] = useState<string | null>(null);

  const pick = (value: string) => {
    if (disabled) return;
    setSelected(value);
    onSelect(value);
  };

  return (
    <div className="flex flex-col gap-2 w-full">
      {spec.question_text && (
        <p className="text-sm font-semibold text-white">{spec.question_text}</p>
      )}
      <div className="flex flex-wrap gap-3">
        {spec.options.map((opt) => {
          const active = selected === opt.value;
          return (
            <button
              key={opt.value}
              onClick={() => pick(opt.value)}
              disabled={disabled}
              className="px-5 py-2.5 rounded-2xl font-semibold text-sm transition-all"
              style={{
                background: active ? "#3498db" : "#16213e",
                color: a