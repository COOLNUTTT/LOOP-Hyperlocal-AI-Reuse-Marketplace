// Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"use client";

import React, { useState, useRef, useEffect } from "react";
import {
  ShieldCheck,
  Plus,
  Trash2,
  RefreshCw,
  CheckCircle2,
  Lock,
  Cpu,
  Maximize2,
  Minimize2,
} from "lucide-react";
import {
  BoundingBox,
  QualityReport,
  analyzeImageQuality,
  applyCanvasPixelation,
} from "@/lib/scrubber";
import { runOnDeviceOnnxPipeline } from "@/lib/onnxClient";

interface ScrubberPreviewProps {
  imageSrc: string;
  onScrubbedComplete: (scrubbedDataUrl: string, boxes: BoundingBox[]) => void;
  className?: string;
}

export const InteractiveScrubberPreview: React.FC<ScrubberPreviewProps> = ({
  imageSrc,
  onScrubbedComplete,
  className = "",
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [boxes, setBoxes] = useState<BoundingBox[]>([
    {
      id: "auto-1",
      x: 0.25,
      y: 0.2,
      w: 0.35,
      h: 0.35,
      label: "face",
      source: "auto",
    },
  ]);
  const [quality, setQuality] = useState<QualityReport | null>(null);
  const [onnxMeta, setOnnxMeta] = useState<{
    latencyMs: number;
    executionProvider: string;
    modelCached: boolean;
  } | null>(null);
  const [isPixelated, setIsPixelated] = useState(false);

  useEffect(() => {
    loadImage();
  }, [imageSrc]);

  const loadImage = () => {
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.onload = () => {
      const canvas = canvasRef.current;
      if (!canvas) return;
      canvas.width = img.naturalWidth || 600;
      canvas.height = img.naturalHeight || 450;
      const ctx = canvas.getContext("2d");
      if (ctx) {
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      }

      // Run quality check + on-device ONNX graph inference
      analyzeImageQuality(img).then(async (baseReport) => {
        const onnxRes = await runOnDeviceOnnxPipeline(baseReport);
        setQuality(onnxRes.quality);
        setOnnxMeta({
          latencyMs: onnxRes.latencyMs,
          executionProvider: onnxRes.executionProvider,
          modelCached: onnxRes.modelCached,
        });
      });
    };
    img.src = imageSrc;
  };

  const handleAddBox = () => {
    const newBox: BoundingBox = {
      id: `box-${Date.now()}`,
      x: 0.3,
      y: 0.3,
      w: 0.3,
      h: 0.25,
      label: "custom",
      source: "user",
    };
    setBoxes((prev) => [...prev, newBox]);
    setIsPixelated(false);
  };

  const handleResizeBox = (id: string, delta: number) => {
    setBoxes((prev) =>
      prev.map((b) => {
        if (b.id !== id) return b;
        const nextW = Math.max(0.1, Math.min(1 - b.x, Math.round((b.w + delta) * 100) / 100));
        const nextH = Math.max(0.1, Math.min(1 - b.y, Math.round((b.h + delta) * 100) / 100));
        return { ...b, w: nextW, h: nextH };
      })
    );
    setIsPixelated(false);
  };

  const handleRemoveBox = (id: string) => {
    setBoxes((prev) => prev.filter((b) => b.id !== id));
    setIsPixelated(false);
  };

  const handleApplyScrub = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    // Apply irreversible pixelation on canvas
    const scrubbedData = applyCanvasPixelation(canvas, boxes);
    setIsPixelated(true);
    onScrubbedComplete(scrubbedData, boxes);
  };

  return (
    <div
      className={`space-y-4 rounded-xl border border-slate-200 bg-white p-4 shadow-sm ${className}`}
    >
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 pb-3">
        <div>
          <h3 className="text-sm font-bold text-slate-900 flex items-center gap-1.5">
            <Lock className="h-4 w-4 text-emerald-600" />
            <span>On-Device Privacy Scrubber</span>
          </h3>
          <p className="text-[11px] text-slate-500">
            Detected sensitive areas are permanently blurred on your device before upload.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-1.5">
          {onnxMeta && (
            <span className="inline-flex items-center gap-1 rounded-full border border-indigo-200 bg-indigo-50 px-2 py-0.5 text-[10px] font-semibold text-indigo-800">
              <Cpu className="h-3 w-3" />
              <span>
                {onnxMeta.executionProvider} • {onnxMeta.latencyMs} ms
              </span>
            </span>
          )}
          {quality && (
            <span
              className={`rounded-full px-2.5 py-0.5 text-[11px] font-semibold ${
                quality.qualityScore >= 0.8
                  ? "bg-emerald-50 text-emerald-800 border border-emerald-200"
                  : "bg-amber-50 text-amber-800 border border-amber-200"
              }`}
            >
              Sharpness: {quality.sharpness} ({quality.recommendation})
            </span>
          )}
        </div>
      </div>

      {/* Canvas Viewport */}
      <div className="relative mx-auto flex max-w-md items-center justify-center overflow-hidden rounded-lg bg-slate-900">
        <canvas ref={canvasRef} className="max-h-72 w-full object-contain" />

        {/* Overlay Interactive Boxes when not yet permanently pixelated */}
        {!isPixelated &&
          boxes.map((b) => (
            <div
              key={b.id}
              style={{
                left: `${b.x * 100}%`,
                top: `${b.y * 100}%`,
                width: `${b.w * 100}%`,
                height: `${b.h * 100}%`,
              }}
              className="absolute border-2 border-dashed border-red-500 bg-red-500/20 rounded flex items-start justify-between p-1 cursor-move"
            >
              <span className="rounded bg-red-600 px-1 py-0.2 text-[9px] font-bold text-white uppercase">
                {b.label} ({b.source})
              </span>
              <div className="flex items-center gap-0.5">
                <button
                  type="button"
                  onClick={() => handleResizeBox(b.id, -0.05)}
                  className="rounded bg-black/70 p-0.5 text-white hover:bg-black"
                  title="Shrink Box"
                >
                  <Minimize2 className="h-3 w-3" />
                </button>
                <button
                  type="button"
                  onClick={() => handleResizeBox(b.id, 0.05)}
                  className="rounded bg-black/70 p-0.5 text-white hover:bg-black"
                  title="Expand Box"
                >
                  <Maximize2 className="h-3 w-3" />
                </button>
                <button
                  type="button"
                  onClick={() => handleRemoveBox(b.id)}
                  className="rounded bg-black/70 p-0.5 text-white hover:bg-black"
                  title="Remove Box"
                >
                  <Trash2 className="h-3 w-3" />
                </button>
              </div>
            </div>
          ))}
      </div>

      {/* Control Buttons */}
      <div className="flex flex-wrap items-center justify-between gap-2 pt-1">
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleAddBox}
            className="flex items-center gap-1 rounded-lg border border-slate-300 bg-white px-2.5 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors"
          >
            <Plus className="h-3.5 w-3.5" />
            <span>Add Redaction Box</span>
          </button>
          <button
            type="button"
            onClick={loadImage}
            className="flex items-center gap-1 rounded-lg border border-slate-200 px-2 py-1.5 text-xs text-slate-600 hover:bg-slate-50"
            title="Reset Canvas"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            <span>Reset</span>
          </button>
        </div>

        <button
          type="button"
          onClick={handleApplyScrub}
          className={`flex items-center gap-1.5 rounded-lg px-4 py-2 text-xs font-bold transition-all shadow-sm ${
            isPixelated
              ? "bg-emerald-600 text-white"
              : "bg-slate-900 text-white hover:bg-slate-800"
          }`}
        >
          {isPixelated ? (
            <>
              <CheckCircle2 className="h-4 w-4" />
              <span>Pixelation Applied</span>
            </>
          ) : (
            <>
              <ShieldCheck className="h-4 w-4 text-emerald-400" />
              <span>Burn Irreversible Pixelation</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default InteractiveScrubberPreview;
