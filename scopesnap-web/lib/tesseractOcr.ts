/**
 * tesseractOcr.ts — Board Session 8, Section 6A
 *
 * Client-side OCR fallback using Tesseract.js when the Gemini API is
 * unreachable (network degraded, API outage, etc.).
 *
 * Pipeline:
 *   1. Run Tesseract on the photo → raw text
 *   2. Parse HVAC fields from raw text via regex
 *   3. Return a NameplateUnit matching the same shape as Gemini output
 *
 * Language data (~10 MB) is fetched from jsDelivr CDN on first use and
 * cached by the browser. Subsequent calls are instant.
 *
 * NOT a true offline mode — requires CDN access on first use.
 * For fully offline operation, see offlineQueue.ts (6C).
 */

// ── Types (mirror NameplateUnit from StepZeroPanel) ───────────────────────────
export interface NameplateUnit {
  model_number:        string | null;
  serial_number:       string | null;
  tonnage:             number | null;
  refrigerant:         string | null;
  factory_charge_oz:   number | null;
  rla:                 number | null;
  lra:                 number | null;
  capacitor_uf:        string | null;
  mca:                 number | null;
  mocp:                number | null;
  voltage:             string | null;
  brand_id:            string | null;
  series_id:           string | null;
  charging_method:     string | null;
  metering_device:     string | null;
  is_legacy:           boolean;
  year_of_manufacture: number | null;
  r22_alert:           boolean;
  confidence:          number;
  notes:               string | null;
}

export interface TesseractOcrResult {
  outdoor:           NameplateUnit;
  indoor:            NameplateUnit | null;
  captured_at:       string;
  capture_method:    "tesseract";
  source:            "tesseract";
  d7_brand_detected: boolean;
  d7_brand_name:     string | null;
  raw_text:          string;
}

// ── Progress callback type ────────────────────────────────────────────────────
export type OcrProgressCallback = (pct: number, status: string) => void;

// ── Singleton worker (lazy init) ──────────────────────────────────────────────
let _workerPromise: Promise<unknown> | null = null;

async function getWorker(onProgress?: OcrProgressCallback): Promise<unknown> {
  if (_workerPromise) return _workerPromise;

  _workerPromise = (async () => {
    // Dynamic import so Next.js doesn't bundle on the server
    const Tesseract = await import("tesseract.js");

    onProgress?.(5, "Loading OCR engine…");

    const worker = await Tesseract.createWorker("eng", 1, {
      workerPath: "https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/worker.min.js",
      langPath:   "https://tessdata.projectnaptha.com/4.0.0",
      corePath:   "https://cdn.jsdelivr.net/npm/tesseract.js-core@5/tesseract-core-simd-lstm.wasm.js",
      logger: (m: { status: string; progress: number }) => {
        if (m.status === "recognizing text") {
          onProgress?.(20 + Math.round(m.progress * 60), "Reading nameplate…");
        } else if (m.status.includes("load")) {
          onProgress?.(10, "Loading OCR engine…");
        }
      },
    });

    onProgress?.(20, "OCR engine ready");
    return worker;
  })();

  return _workerPromise;
}

// ── HVAC text parser ──────────────────────────────────────────────────────────

/** Known brand prefixes for model number recognition */
const BRAND_PREFIXES: Array<{ pattern: RegExp; brand: string }> = [
  { pattern: /\b(24[A-Z]{3}\d)/i,      brand: "Carrier" },
  { pattern: /\b(GSX|GAX|DSXC|ARUF)/i, brand: "Goodman" },
  { pattern: /\b(XC\d|XR\d|XB\d|4T)/i, brand: "Trane" },
  { pattern: /\b(13AJA|RA\d{2}|RH)/i,  brand: "Rheem" },
  { pattern: /\b(ML\d|XC\d|EL\d)/i,    brand: "Lennox" },
  { pattern: /\b(ARUF|ACNF|AWA)/i,     brand: "Goodman" },
  { pattern: /\b(WCA|WCB|WHA)/i,       brand: "York" },
];

/** D7 mini-split brands — flag for manual review */
const D7_BRANDS = ["mitsubishi", "daikin", "fujitsu", "lg hvac", "samsung hvac", "gree", "midea", "pioneer"];

function detectBrand(text: string): { brand: string | null; isD7: boolean } {
  const lower = text.toLowerCase();

  // Check D7 brands first
  for (const d7 of D7_BRANDS) {
    if (lower.includes(d7)) return { brand: d7, isD7: true };
  }

  // Check model prefix patterns
  for (const { pattern, brand } of BRAND_PREFIXES) {
    if (pattern.test(text)) return { brand, isD7: false };
  }

  // Check explicit brand names in text
  const knownBrands = ["Carrier", "Goodman", "Trane", "Rheem", "Lennox", "York", "Ruud", "Heil", "Bryant", "Payne", "Amana", "Daikin"];
  for (const b of knownBrands) {
    if (lower.includes(b.toLowerCase())) return { brand: b, isD7: false };
  }

  return { brand: null, isD7: false };
}

function parseModelNumber(text: string): string | null {
  // HVAC model numbers: 6-20 alphanumeric chars, often start with digits or letters
  // Examples: 24VNA636A003, GSX160361, 4TTR4036E1000A
  const patterns = [
    /MODEL[:\s#]*([A-Z0-9\-]{6,20})/i,
    /MOD[:\s#]*([A-Z0-9\-]{6,20})/i,
    /M\/N[:\s#]*([A-Z0-9\-]{6,20})/i,
    // Standalone model-like strings (uppercase letters + digits, 8-16 chars)
    /\b([A-Z]{2,5}\d{3,6}[A-Z0-9]{0,8})\b/,
  ];
  for (const p of patterns) {
    const m = text.match(p);
    if (m?.[1] && m[1].length >= 6) return m[1].toUpperCase();
  }
  return null;
}

function parseSerialNumber(text: string): string | null {
  const patterns = [
    /SERIAL[:\s#]*([A-Z0-9]{6,20})/i,
    /SER[:\s#]*([A-Z0-9]{6,20})/i,
    /S\/N[:\s#]*([A-Z0-9]{6,20})/i,
    /SN[:\s#]*([A-Z0-9]{8,20})/i,
  ];
  for (const p of patterns) {
    const m = text.match(p);
    if (m?.[1]) return m[1].toUpperCase();
  }
  return null;
}

function parseTonnage(text: string, modelNumber: string | null): number | null {
  // Explicit "X TON" or "X.X TON"
  const tonMatch = text.match(/(\d+\.?\d*)\s*TON/i);
  if (tonMatch) return parseFloat(tonMatch[1]);

  // BTU: 36000 BTU = 3 ton
  const btuMatch = text.match(/(\d{5,6})\s*BTU/i);
  if (btuMatch) {
    const btu = parseInt(btuMatch[1]);
    if (btu >= 12000 && btu <= 72000) return Math.round(btu / 12000);
  }

  // Extract from model number — position 5-7 often = 024-060 (thousands of BTU)
  // e.g. 24ACC636 → "36" = 36000 BTU = 3 ton
  if (modelNumber) {
    const mnBtu = modelNumber.match(/(\d{2,3})(?:[A-Z]\d{3})?$/);
    if (mnBtu) {
      const code = parseInt(mnBtu[1]);
      if (code >= 18 && code <= 60 && code % 6 === 0) {
        return code / 12; // 36 → 3 ton
      }
    }
  }

  return null;
}

function parseRefrigerant(text: string, year: number | null): string | null {
  if (/R-?22\b/i.test(text))   return "R-22";
  if (/R-?454B/i.test(text))   return "R-454B";
  if (/R-?32\b/i.test(text))   return "R-32";
  if (/R-?410A?/i.test(text))  return "R-410A";
  if (/R-?407C/i.test(text))   return "R-407C";

  // Infer from year if present
  if (year !== null) {
    if (year < 2010)  return "R-22";
    if (year >= 2023) return "R-454B";
    return "R-410A";
  }

  return null;
}

function parseYear(text: string, serialNumber: string | null): number | null {
  // Explicit year in text
  const yearMatch = text.match(/\b(19[89]\d|20[012]\d)\b/);
  if (yearMatch) {
    const yr = parseInt(yearMatch[1]);
    if (yr >= 1980 && yr <= new Date().getFullYear()) return yr;
  }

  // Carrier/Bryant/Payne serial: position 3-6 = week+year (e.g. 2219E = week 22, year 2019)
  if (serialNumber && /^\d{4}[A-Z]\d/.test(serialNumber)) {
    const yr = parseInt(serialNumber.substring(2, 4));
    if (yr >= 0 && yr <= 99) {
      return yr <= 30 ? 2000 + yr : 1900 + yr;
    }
  }

  // Goodman: first letter = decade (A=2001, B=2002…)
  if (serialNumber && /^[A-Z]\d{9}$/.test(serialNumber)) {
    const code = serialNumber.charCodeAt(0) - "A".charCodeAt(0);
    return 2001 + code;
  }

  return null;
}

function parseAmps(text: string, label: string): number | null {
  const p = new RegExp(label + "[:\\s]*([\\d.]+)\\s*A?", "i");
  const m = text.match(p);
  return m ? parseFloat(m[1]) : null;
}

function parseVoltage(text: string): string | null {
  // e.g. "208/230-1-60", "460-3-60", "115/1/60"
  const m = text.match(/\b(1[01]\d|2[023]\d|460|575)[\/\-]?\s*([13])[\/\-]?\s*60\b/);
  if (m) return `${m[1]}/${m[2]}/60`;

  const m2 = text.match(/VOLTAGE[:\s]*([0-9\/\-]+)/i);
  if (m2) return m2[1];

  return null;
}

function parseCapacitor(text: string): string | null {
  // e.g. "35+5 MFD", "45/5 uf"
  const m = text.match(/(\d+[\/\+]\d+)\s*(?:MFD|UF|µF)/i)
    || text.match(/CAP(?:ACITOR)?[:\s]*([0-9\/\+.]+\s*(?:MFD|UF))/i);
  return m ? m[1] : null;
}

function parseChargingMethod(text: string): { method: string | null; device: string | null } {
  if (/SUPERHEAT/i.test(text) || /PISTON/i.test(text) || /FIXED.ORIFICE/i.test(text)) {
    return { method: "superheat", device: "piston" };
  }
  if (/SUBCOOL/i.test(text) || /TXV/i.test(text) || /EXV/i.test(text)) {
    return { method: "subcooling", device: "TXV" };
  }
  return { method: null, device: null };
}

function parseFactoryCharge(text: string): number | null {
  const m = text.match(/FACTORY\s*CHARGE[:\s]*([0-9.]+)\s*OZ/i)
    || text.match(/CHARGE[:\s]*([0-9.]+)\s*OZ/i)
    || text.match(/([0-9.]+)\s*OZ\s*R-?[0-9]/i);
  return m ? parseFloat(m[1]) : null;
}

/** Main parser: converts raw Tesseract text → NameplateUnit */
export function parseHvacText(rawText: string): NameplateUnit {
  const text = rawText.replace(/\s+/g, " ").trim();

  const modelNumber  = parseModelNumber(text);
  const serialNumber = parseSerialNumber(text);
  const year         = parseYear(text, serialNumber);
  const refrigerant  = parseRefrigerant(text, year);
  const { brand }    = detectBrand(text);
  const { method, device } = parseChargingMethod(text);

  const r22Alert = refrigerant === "R-22";
  const isLegacy = (year !== null && year < 2010) || r22Alert;

  // Confidence: how many fields did we extract?
  const extracted = [modelNumber, serialNumber, refrigerant, year].filter(Boolean).length;
  const confidence = Math.min(85, 40 + extracted * 12); // 40–76%

  return {
    model_number:        modelNumber,
    serial_number:       serialNumber,
    tonnage:             parseTonnage(text, modelNumber),
    refrigerant,
    factory_charge_oz:   parseFactoryCharge(text),
    rla:                 parseAmps(text, "RLA"),
    lra:                 parseAmps(text, "LRA"),
    capacitor_uf:        parseCapacitor(text),
    mca:                 parseAmps(text, "MCA"),
    mocp:                parseAmps(text, "MOCP") || parseAmps(text, "HACR"),
    voltage:             parseVoltage(text),
    brand_id:            brand,
    series_id:           modelNumber ? modelNumber.substring(0, 6) : null,
    charging_method:     method,
    metering_device:     device,
    is_legacy:           isLegacy,
    year_of_manufacture: year,
    r22_alert:           r22Alert,
    confidence,
    notes:               "Extracted by local OCR — verify fields",
  };
}

// ── Public API ────────────────────────────────────────────────────────────────

/**
 * Run Tesseract OCR on an image file and parse HVAC fields.
 *
 * @param outdoorFile  - Required outdoor nameplate photo
 * @param indoorFile   - Optional indoor nameplate photo
 * @param onProgress   - Progress callback (0–100, status string)
 */
export async function runTesseractOcr(
  outdoorFile: File | Blob,
  indoorFile?: File | Blob | null,
  onProgress?: OcrProgressCallback,
): Promise<TesseractOcrResult> {
  onProgress?.(0, "Starting local OCR…");

  // Lazy-load worker
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const worker = await getWorker(onProgress) as any;

  onProgress?.(20, "Reading outdoor nameplate…");

  // Run OCR on outdoor photo
  const outdoorResult = await worker.recognize(outdoorFile);
  const outdoorText   = outdoorResult.data.text as string;

  onProgress?.(70, "Parsing nameplate fields…");

  const outdoorUnit = parseHvacText(outdoorText);
  const { brand, isD7 } = detectBrand(outdoorText);

  let indoorUnit: NameplateUnit | null = null;

  if (indoorFile) {
    onProgress?.(75, "Reading indoor nameplate…");
    const indoorResult = await worker.recognize(indoorFile);
    indoorUnit = parseHvacText(indoorResult.data.text as string);
    onProgress?.(90, "Parsing indoor fields…");
  }

  onProgress?.(100, "Done");

  return {
    outdoor:           outdoorUnit,
    indoor:            indoorUnit,
    captured_at:       new Date().toISOString(),
    capture_method:    "tesseract",
    source:            "tesseract",
    d7_brand_detected: isD7,
    d7_brand_name:     isD7 ? (brand || null) : null,
    raw_text:          outdoorText,
  };
}

/**
 * Release the Tesseract worker to free memory.
 * Call this when the user navigates away from the assess page.
 */
export async function terminateTesseractWorker(): Promise<void> {
  if (!_workerPromise) return;
  try {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const worker = await _workerPromise as any;
    await worker.terminate();
  } catch {
    // ignore
  } finally {
    _workerPromise = null;
  }
}
