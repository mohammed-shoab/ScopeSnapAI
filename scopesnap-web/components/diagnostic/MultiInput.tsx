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
                color: active ? "#fff" : "#a0a8c0",
                border: `1.5px solid ${active ? "#3498db" : "#2a2a4a"}`,
                opacity: disabled ? 0.5 : 1,
              }}
            >
              {opt.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}

// ── MultiInput component ───────────────────────────────────────────────────

export default function MultiInput({
  inputs,
  assessmentId,
  authHeaders,
  ocrNameplate,
  onSubmit,
  disabled = false,
}: MultiInputProps) {
  const photoInputs = inputs.filter(
    (i): i is { kind: "photo"; spec: PhotoSlotSpec } => i.kind === "photo"
  );
  const readingInputs = inputs.filter(
    (i): i is { kind: "reading"; spec: ReadingSpec } => i.kind === "reading"
  );
  const selectInputs = inputs.filter(
    (i): i is { kind: "visual_select"; spec: VisualSelectSpec } => i.kind === "visual_select"
  );

  // Photos are optional when readings or visual-selects exist — readings/selects drive
  // the branch_key, so submission fires as soon as those complete.
  // Photo-only multi steps (e.g. drain pan) still require all items (handled by DiagnosticFlow skip UI).
  const hasNonPhotoItems = readingInputs.length > 0 || selectInputs.length > 0;
  const totalRequired = hasNonPhotoItems
    ? readingInputs.length + selectInputs.length
    : inputs.length;

  const capturedPhotos: PhotoResult[] = new Array(photoInputs.length).fill(null);
  const capturedReadings: ReadingResult[] = new Array(readingInputs.length).fill(null);
  const capturedSelections: SelectionResult[] = new Array(selectInputs.length).fill(null);

  let photosDone = 0;
  let readingsDone = 0;
  let selectionsDone = 0;

  const trySubmit = () => {
    if (photosDone + readingsDone + selectionsDone < totalRequired) return;

    const photos = capturedPhotos.filter(Boolean);
    const readings = capturedReadings.filter(Boolean);
    const selections = capturedSelections.filter(Boolean);

    // Primary branch_key: visual_select value takes precedence, then first reading
    let branch_key: string | undefined;
    if (selections.length > 0) {
      branch_key = selections[0].value;
    } else if (readings.length > 0 && readings[0].branchKey) {
      branch_key = readings[0].branchKey;
    }

    onSubmit({ photos, readings, selections, branch_key });
  };

  return (
    <div className="flex flex-col gap-6 w-full">
      {/* Visual select sub-items rendered first — they are the primary decision */}
      {selectInputs.map((item, i) => (
        <InlineVisualSelect
          key={`select-${i}`}
          spec={item.spec}
          disabled={disabled}
          onSelect={(value) => {
            capturedSelections[i] = { slot_name: `sub_${i}`, value };
            selectionsDone = capturedSelections.filter(Boolean).length;
            trySubmit();
          }}
        />
      ))}

      {photoInputs.map((item, i) => (
        <PhotoSlot
          key={item.spec.slot_name}
          spec={item.spec}
          assessmentId={assessmentId}
          authHeaders={authHeaders}
          disabled={disabled}
          onCapture={(result) => {
            capturedPhotos[i] = result;
            photosDone = capturedPhotos.filter(Boolean).length;
            trySubmit();
          }}
        />
      ))}

      {readingInputs.map((item, i) => (
        <ReadingInput
          key={`reading-${i}`}
          spec={item.spec}
          ocrNameplate={ocrNameplate}
          disabled={disabled}
          onSubmit={(result) => {
            capturedReadings[i] = result;
            readingsDone = capturedReadings.filter(Boolean).length;
            trySubmit();
          }}
        />
      ))}
    </div>
  );
}
