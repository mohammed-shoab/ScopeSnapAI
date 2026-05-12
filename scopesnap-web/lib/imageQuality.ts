/**
 * imageQuality.ts — Board Session 8, Section 5B
 *
 * Client-side image quality checks run before sending photos to the OCR API.
 * Avoids wasting a Gemini call on a blurry/dark photo.
 *
 * Blur detection: Laplacian variance computed on a downsampled canvas.
 *   - Sharp image:  variance >> BLUR_THRESHOLD (typically 100–600+)
 *   - Blurry image: variance << BLUR_THRESHOLD (typically < 80)
 *
 * Brightness detection: mean pixel luminance.
 *   - Too dark  < 40  (0–255 scale)
 *   - Too bright > 230
 */

export interface ImageQualityResult {
  /** 0–100 score (100 = perfect) */
  score: number;
  blurry: boolean;
  tooDark: boolean;
  tooBright: boolean;
  /** Human-readable coaching message, or null if OK */
  message: string | null;
  /** Laplacian variance (debug) */
  laplacianVariance: number;
  /** Mean luminance 0–255 (debug) */
  meanLuminance: number;
}

// ── Thresholds (tuned for HVAC nameplate photos) ──────────────────────────────
const BLUR_THRESHOLD       = 80;    // Below = blurry
const DARK_THRESHOLD       = 40;    // Mean luminance below = too dark
const BRIGHT_THRESHOLD     = 230;   // Mean luminance above = too bright
const DOWNSAMPLE_MAX       = 320;   // Downsample to this max dimension for speed

/** Convert a File or Blob to an ImageData at capped resolution */
async function fileToImageData(file: File | Blob): Promise<ImageData> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    const url = URL.createObjectURL(file);

    img.onload = () => {
      URL.revokeObjectURL(url);
      const scale = Math.min(1, DOWNSAMPLE_MAX / Math.max(img.width, img.height));
      const w = Math.round(img.width * scale);
      const h = Math.round(img.height * scale);

      const canvas = document.createElement("canvas");
      canvas.width = w;
      canvas.height = h;
      const ctx = canvas.getContext("2d")!;
      ctx.drawImage(img, 0, 0, w, h);
      resolve(ctx.getImageData(0, 0, w, h));
    };

    img.onerror = () => {
      URL.revokeObjectURL(url);
      reject(new Error("Failed to load image for quality check"));
    };

    img.src = url;
  });
}

/** Compute mean luminance (0–255) from RGBA ImageData */
function computeMeanLuminance(data: ImageData): number {
  const { data: px, width, height } = data;
  let total = 0;
  const pixels = width * height;
  for (let i = 0; i < px.length; i += 4) {
    // BT.601 luminance
    total += 0.299 * px[i] + 0.587 * px[i + 1] + 0.114 * px[i + 2];
  }
  return total / pixels;
}

/**
 * Compute Laplacian variance — measures sharpness.
 * Applies a discrete Laplacian kernel on the grayscale image.
 * Returns variance of the response; higher = sharper.
 */
function computeLaplacianVariance(data: ImageData): number {
  const { data: px, width, height } = data;

  // Build grayscale array
  const gray = new Float32Array(width * height);
  for (let i = 0; i < gray.length; i++) {
    const base = i * 4;
    gray[i] = 0.299 * px[base] + 0.587 * px[base + 1] + 0.114 * px[base + 2];
  }

  // Laplacian kernel: [0,1,0 / 1,-4,1 / 0,1,0]
  const lap = new Float32Array((width - 2) * (height - 2));
  let n = 0;
  for (let y = 1; y < height - 1; y++) {
    for (let x = 1; x < width - 1; x++) {
      const idx = y * width + x;
      lap[n++] =
        gray[idx - width] +
        gray[idx + width] +
        gray[idx - 1] +
        gray[idx + 1] -
        4 * gray[idx];
    }
  }

  // Variance of Laplacian responses
  let mean = 0;
  for (let i = 0; i < lap.length; i++) mean += lap[i];
  mean /= lap.length;

  let variance = 0;
  for (let i = 0; i < lap.length; i++) {
    const d = lap[i] - mean;
    variance += d * d;
  }
  return variance / lap.length;
}

/**
 * Run quality checks on a photo File.
 * Returns a quality result with score and coaching message.
 */
export async function checkImageQuality(file: File | Blob): Promise<ImageQualityResult> {
  let imageData: ImageData;
  try {
    imageData = await fileToImageData(file);
  } catch {
    // If we can't decode, pass through (don't block the user)
    return {
      score: 100,
      blurry: false,
      tooDark: false,
      tooBright: false,
      message: null,
      laplacianVariance: 0,
      meanLuminance: 128,
    };
  }

  const laplacianVariance = computeLaplacianVariance(imageData);
  const meanLuminance = computeMeanLuminance(imageData);

  const blurry    = laplacianVariance < BLUR_THRESHOLD;
  const tooDark   = meanLuminance < DARK_THRESHOLD;
  const tooBright = meanLuminance > BRIGHT_THRESHOLD;

  // Score: start at 100, deduct for issues
  let score = 100;
  if (blurry)    score -= 40;
  if (tooDark)   score -= 30;
  if (tooBright) score -= 20;

  let message: string | null = null;
  if (blurry && tooDark) {
    message = "Photo is blurry and too dark — turn on your flashlight and hold steady.";
  } else if (blurry) {
    message = "Photo looks blurry — hold the camera still and tap to focus on the nameplate.";
  } else if (tooDark) {
    message = "Photo is too dark — use your flashlight to illuminate the nameplate.";
  } else if (tooBright) {
    message = "Photo is overexposed — try shading the nameplate or moving slightly.";
  }

  return { score, blurry, tooDark, tooBright, message, laplacianVariance, meanLuminance };
}
