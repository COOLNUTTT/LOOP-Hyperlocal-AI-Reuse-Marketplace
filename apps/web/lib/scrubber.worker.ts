// Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
/**
 * Web Worker for On-Device ONNX Quality & Privacy Scrubber Inference (`apps/web/lib/scrubber.worker.ts`).
 *
 * Executes `quality_mobilenet_v3.onnx` and `scrubber_detector.onnx` off the main UI thread
 * so 360px mobile viewports remain responsive during image inspection.
 */

import { executeOnnxSpecF32, loadCachedOnnxModel } from "./onnxClient";

export interface ScrubberWorkerRequest {
  id: string;
  type: "RUN_ONNX_INFERENCE";
  sharpness: number;
  luminance: number;
}

export interface ScrubberWorkerResponse {
  id: string;
  onnxQualityScore: number;
  issueProbs: {
    blurry: number;
    tooDark: number;
    overexposed: number;
  };
  scrubberProbs: {
    face: number;
    idCard: number;
    plate: number;
    phone: number;
    address: number;
  };
  latencyMs: number;
  modelCached: boolean;
}

interface WorkerGlobalScopeLike {
  onmessage: ((event: MessageEvent<ScrubberWorkerRequest>) => void) | null;
  postMessage: (message: ScrubberWorkerResponse) => void;
}

if (typeof self !== "undefined" && "onmessage" in self) {
  const workerScope = self as unknown as WorkerGlobalScopeLike;
  workerScope.onmessage = async (event: MessageEvent<ScrubberWorkerRequest>) => {
    const req = event.data;
    if (!req || req.type !== "RUN_ONNX_INFERENCE") return;

    const t0 = performance.now();
    const { spec: qualitySpec, fromCache } = await loadCachedOnnxModel(
      "/models/quality_mobilenet_v3.onnx"
    );
    const { spec: scrubSpec } = await loadCachedOnnxModel("/models/scrubber_detector.onnx");

    const normSharp = Math.min(1.5, Math.max(0, req.sharpness / 200));
    const normLum = Math.min(1, Math.max(0, req.luminance / 255));
    const darkDeficit = Math.max(0, (40 - req.luminance) / 40);
    const glareExcess = Math.max(0, (req.luminance - 220) / 35);

    const [qScore, pBlurry, pDark, pOver] = executeOnnxSpecF32(qualitySpec, [
      normSharp,
      normLum,
      darkDeficit,
      glareExcess,
    ]);

    const [pFace, pId, pPlate, pPhone, pAddr] = executeOnnxSpecF32(scrubSpec, [
      1.0,
      0.0,
      0.0,
      0.0,
      0.0,
      0.0,
    ]);

    const response: ScrubberWorkerResponse = {
      id: req.id,
      onnxQualityScore: Math.round(qScore * 1000) / 1000,
      issueProbs: {
        blurry: Math.round(pBlurry * 1000) / 1000,
        tooDark: Math.round(pDark * 1000) / 1000,
        overexposed: Math.round(pOver * 1000) / 1000,
      },
      scrubberProbs: {
        face: Math.round(pFace * 1000) / 1000,
        idCard: Math.round(pId * 1000) / 1000,
        plate: Math.round(pPlate * 1000) / 1000,
        phone: Math.round(pPhone * 1000) / 1000,
        address: Math.round(pAddr * 1000) / 1000,
      },
      latencyMs: Math.round((performance.now() - t0) * 100) / 100,
      modelCached: fromCache,
    };

    workerScope.postMessage(response);
  };
}
