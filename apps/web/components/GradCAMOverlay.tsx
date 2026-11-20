// Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"use client";

import React, { useState } from "react";
import { Sparkles, Eye, EyeOff, AlertCircle, Info, ShieldCheck } from "lucide-react";

export interface GradCAMRegion {
  x: number;
  y: number;
  w: number;
  h: number;
  intensity: number;
  defect?: string;
}

interface GradCAMOverlayProps {
  imageSrc: string;
  grade: "poor" | "fair" | "good" | "like_new" | string;
  confidence: number;
  regions?: GradCAMRegion[];
  className?: string;
}

export const GradCAMOverlay: React.FC<GradCAMOverlayProps> = ({
  imageSrc,
  grade,
  confidence,
  regions = [
    { x: 0.25, y: 0.4, w: 0.25, h: 0.2, intensity: 0.8, defect: "Cosmetic wear / scuff" },
  ],
  className = "",
}) => {
  const [showHeatmap, setShowHeatmap] = useState(true);

  const gradeColors = {
    poor: "text-red-700 bg-red-50 border-red-200",
    fair: "text-amber-800 bg-amber-50 border-amber-200",
    good: "text-sky-800 bg-sky-50 border-sky-200",
    like_new: "text-emerald-800 bg-emerald-50 border-emerald-200",
  };

  const badgeClass = gradeColors[grade.toLowerCase() as keyof typeof gradeColors] || gradeColors.good;

  return (
    <div className={`space-y-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm ${className}`}>
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
            Condition Grade:
          </span>
          <span className={`rounded-full px-2.5 py-0.5 text-xs font-bold uppercase border ${badgeClass}`}>
            {grade.replace("_", " ")}
          </span>
          <span className="text-[11px] text-slate-400">({Math.round(confidence * 100)}% conf)</span>
        </div>

        <button
          type="button"
          onClick={() => setShowHeatmap(!showHeatmap)}
          className="flex items-center gap-1.5 rounded-lg border border-slate-200 px-2.5 py-1 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors"
        >
          {showHeatmap ? <EyeOff className="h-3.5 w-3.5 text-slate-500" /> : <Eye className="h-3.5 w-3.5 text-slate-500" />}
          <span>{showHeatmap ? "Hide Heatmap" : "Show Grad-CAM Heatmap"}</span>
        </button>
      </div>

      {/* Visual Canvas / Image with Saliency Overlay */}
      <div className="relative mx-auto max-h-72 w-full overflow-hidden rounded-lg bg-slate-900 flex items-center justify-center">
        <img src={imageSrc} alt="Item Condition Inspection" className="h-full w-full object-contain" />

        {/* Grad-CAM Saliency Overlay */}
        {showHeatmap && (
          <div className="absolute inset-0 pointer-events-none">
            {regions.map((r, i) => (
              <div
                key={i}
                style={{
                  left: `${r.x * 100}%`,
                  top: `${r.y * 100}%`,
                  width: `${r.w * 100}%`,
                  height: `${r.h * 100}%`,
                }}
                className="absolute rounded-xl border-2 border-amber-400 bg-radial from-amber-500/40 via-red-500/25 to-transparent backdrop-blur-xs flex items-start justify-center p-1 animate-pulse"
              >
                {r.defect && (
                  <span className="rounded bg-black/80 px-1.5 py-0.5 text-[9px] font-bold text-amber-300 uppercase tracking-wider shadow">
                    {r.defect}
                  </span>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Explainer & Limitation Guarantee */}
      <div className="rounded-lg border border-amber-200 bg-amber-50/70 p-3 text-xs text-amber-900 space-y-1">
        <div className="flex items-center gap-1.5 font-bold">
          <Info className="h-3.5 w-3.5 text-amber-700 shrink-0" />
          <span>Grad-CAM Explainability Transparency</span>
        </div>
        <p className="text-[11px] text-amber-800 leading-normal">
          The highlighted thermal regions highlight surface wear patterns detected by the neural network.
          <strong> Notice:</strong> Some internal, mechanical, or functional defects cannot be detected visually;
          the final condition grade remains 100% editable by the seller.
        </p>
      </div>
    </div>
  );
};

export default GradCAMOverlay;
