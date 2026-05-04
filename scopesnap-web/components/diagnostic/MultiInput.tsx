"use client";

import PhotoSlot, { PhotoSlotSpec, PhotoResult } from "./PhotoSlot";
import ReadingInput, { ReadingSpec, ReadingResult } from "./ReadingInput";

export type MultiInputItem =
  | { kind: "photo"; spec: PhotoSlotSpec }
  | { kind: "reading"; spec: ReadingSpec };

export interface MultiInputData {
  photos: PhotoResult[];
  readings: ReadingResult[];
}

interface MultiInputProps {
  inputs: MultiInputItem[];
  assessmentId: string;
  authHeaders: Record<string, string>;
  ocrNameplate?: Record<string, unknown> | null;
  onSubmit: (data: MultiInputData) => void;
  disabled?: boolean;
}

export default function MultiInput({ inputs, assessmentId, authHeaders, ocrNameplate, onSubmit, disabled = false }: MultiInputProps) {
  const photoInputs = inputs.filter((i): i is { kind: "photo"; spec: PhotoSlotSpec } => i.kind === "photo");
  const readingInputs = inputs.filter((i): i is { kind: "reading"; spec: ReadingSpec } => i.kind === "reading");

  const totalRequired = inputs.length;
  const capturedPhotos: PhotoResult[] = new Array(photoInputs.length).fill(null);
  const capturedReadings: ReadingResult[] = new Array(readingInputs.length).fill(null);

  let photosDone = 0;
  let readingsDone = 0;

  const trySubmit = () => {
    if (photosDone + readingsDone < totalRequired) return;
    onSubmit({ photos: capturedPhotos.filter(Boolean), readings: capturedReadings.filter(Boolean) });
  };

  return (
    <div className="flex flex-col gap-6 w-full">
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
