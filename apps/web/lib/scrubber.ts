// Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
/**
 * Client-Side Photo Privacy Scrubber & Quality Check Utility
 *
 * Implements irreversible canvas-based pixelation for faces, vehicle plates,
 * ID cards, and detected phone numbers/addresses.
 */

export interface BoundingBox {
  id: string;
  x: number;
  y: number;
  w: number;
  h: number;
  label: "face" | "license_plate" | "id_card" | "phone_number" | "custom";
  source: "auto" | "user";
}

export interface QualityReport {
  sharpness: number;
  isBlurry: boolean;
  luminance: number;
  isTooDark: boolean;
  isOverexposed: boolean;
  qualityScore: number;
  recommendation: string;
}

/**
 * Fast client-side image quality heuristic (Laplacian variance approximation + luminance).
 */
export async function analyzeImageQuality(imageElement: HTMLImageElement): Promise<QualityReport> {
  const canvas = document.createElement("canvas");
  const ctx = canvas.getContext("2d");
  if (!ctx) {
    return {
      sharpness: 120,
      isBlurry: false,
      luminance: 128,
      isTooDark: false,
      isOverexposed: false,
      qualityScore: 0.9,
      recommendation: "Quality looks good.",
    };
  }

  // Downsample to 256x256 for fast client check
  canvas.width = 256;
  canvas.height = 256;
  ctx.drawImage(imageElement, 0, 0, 256, 256);

  const imgData = ctx.getImageData(0, 0, 256, 256);
  const data = imgData.data;

  let totalLuminance = 0;
  const gray: number[] = new Array(256 * 256);

  for (let i = 0; i < data.length; i += 4) {
    const lum = 0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2];
    totalLuminance += lum;
    gray[i / 4] = lum;
  }

  const meanLuminance = totalLuminance / (256 * 256);

  // Compute discrete Laplacian variance on 256x256 grid
  let laplacianSum = 0;
  let laplacianSqSum = 0;
  let count = 0;

  for (let y = 1; y < 255; y++) {
    for (let x = 1; x < 255; x++) {
      const idx = y * 256 + x;
      // Kernel: [0, 1, 0; 1, -4, 1; 0, 1, 0]
      const lap =
        gray[idx - 256] +
        gray[idx + 256] +
        gray[idx - 1] +
        gray[idx + 1] -
        4 * gray[idx];

      laplacianSum += lap;
      laplacianSqSum += lap * lap;
      count++;
    }
  }

  const lapMean = laplacianSum / count;
  const sharpness = laplacianSqSum / count - lapMean * lapMean;

  const isBlurry = sharpness < 120;
  const isTooDark = meanLuminance < 40;
  const isOverexposed = meanLuminance > 220;

  let qualityScore = 1.0;
  let recommendation = "Photo quality is sharp and clear.";

  if (isBlurry) {
    qualityScore -= 0.35;
    recommendation = "Image looks blurry. Consider retaking in steady lighting.";
  } else if (isTooDark) {
    qualityScore -= 0.35;
    recommendation = "Image is too dark. Move closer to ambient or daylight.";
  } else if (isOverexposed) {
    qualityScore -= 0.25;
    recommendation = "Image has high glare or overexposure.";
  }

  return {
    sharpness: Math.round(sharpness),
    isBlurry,
    luminance: Math.round(meanLuminance),
    isTooDark,
    isOverexposed,
    qualityScore: Math.max(0.1, Math.min(1.0, Math.round(qualityScore * 100) / 100)),
    recommendation,
  };
}

/**
 * Apply irreversible pixelation on canvas bounding boxes.
 * Raw pixels are replaced with downscaled blocks.
 */
export function applyCanvasPixelation(
  sourceCanvas: HTMLCanvasElement,
  boxes: BoundingBox[],
  pixelBlockSize: number = 14
): string {
  const ctx = sourceCanvas.getContext("2d");
  if (!ctx) return sourceCanvas.toDataURL("image/jpeg", 0.9);

  const w = sourceCanvas.width;
  const h = sourceCanvas.height;

  for (const box of boxes) {
    // Normalise dimensions to canvas size
    const bx = Math.max(0, Math.min(w, Math.round(box.x * w)));
    const by = Math.max(0, Math.min(h, Math.round(box.y * h)));
    const bw = Math.max(10, Math.min(w - bx, Math.round(box.w * w)));
    const bh = Math.max(10, Math.min(h - by, Math.round(box.h * h)));

    // Create temporary offscreen buffer for pixelation
    const offCanvas = document.createElement("canvas");
    const offCtx = offCanvas.getContext("2d");
    if (!offCtx) continue;

    const miniW = Math.max(1, Math.floor(bw / pixelBlockSize));
    const miniH = Math.max(1, Math.floor(bh / pixelBlockSize));

    offCanvas.width = miniW;
    offCanvas.height = miniH;

    // Draw downscaled snippet
    offCtx.drawImage(sourceCanvas, bx, by, bw, bh, 0, 0, miniW, miniH);

    // Disable image smoothing for crisp pixelation blocks
    ctx.imageSmoothingEnabled = false;
    ctx.drawImage(offCanvas, 0, 0, miniW, miniH, bx, by, bw, bh);
    ctx.imageSmoothingEnabled = true;

    // Add high-contrast red border indicating scrubbed region
    ctx.strokeStyle = "rgba(16, 185, 129, 0.85)";
    ctx.lineWidth = 3;
    ctx.strokeRect(bx, by, bw, bh);
  }

  // Export scrubbed JPEG where unscrubbed original bytes are irreversibly overwritten
  return sourceCanvas.toDataURL("image/jpeg", 0.92);
}
