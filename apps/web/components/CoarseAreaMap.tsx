// Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"use client";

import React, { useState } from "react";
import { MapPin, ZoomIn, ZoomOut, ShieldCheck, RotateCcw } from "lucide-react";

export interface CoarseAreaCluster {
  name: string;
  geohash5: string;
  count: number;
  lat: number;
  lng: number;
}

interface CoarseAreaMapProps {
  areas: CoarseAreaCluster[];
  selectedArea: string;
  onSelectArea: (areaName: string) => void;
}

/**
 * Privacy guard (`AGENTS.md` §2): Truncates any geohash to at most 5 characters (~4.9km x 4.9km cell).
 */
export function sanitizeGeohash5(rawGeohash: string): string {
  return rawGeohash.trim().slice(0, 5);
}

export const CoarseAreaMap: React.FC<CoarseAreaMapProps> = ({
  areas,
  selectedArea,
  onSelectArea,
}) => {
  const [zoom, setZoom] = useState<number>(12);

  // Project coarse lat/lng centroids around Pune (18.55..18.63 N, 73.73..73.95 E) into SVG [0..600, 0..320]
  const projectPoint = (lat: number, lng: number) => {
    const scale = 1 + (zoom - 12) * 0.18;
    const normX = ((lng - 73.72) / 0.24) * 480 + 60;
    const normY = ((18.63 - lat) / 0.1) * 200 + 60;
    const cx = 300 + (normX - 300) * scale;
    const cy = 160 + (normY - 160) * scale;
    return { x: Math.round(cx), y: Math.round(cy) };
  };

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h3 className="text-sm font-bold text-slate-900 flex items-center gap-1.5">
            <ShieldCheck className="h-4 w-4 text-emerald-600" />
            <span>Interactive Coarse Geohash-5 Cluster Map</span>
          </h3>
          <p className="text-xs text-slate-500">
            Circles show ~5 km × 5 km coarse geohash-5 cells (`precision &le; 5`). Exact street addresses never exist in the schema.
          </p>
        </div>

        <div className="flex items-center gap-1.5">
          <button
            type="button"
            onClick={() => setZoom((z) => Math.max(11, z - 1))}
            className="rounded-lg border border-slate-200 p-1.5 text-slate-700 hover:bg-slate-50"
            title="Zoom Out"
            aria-label="Zoom Out"
          >
            <ZoomOut className="h-3.5 w-3.5" />
          </button>
          <span className="px-2 text-xs font-mono font-semibold text-slate-700">
            Zoom {zoom}x
          </span>
          <button
            type="button"
            onClick={() => setZoom((z) => Math.min(14, z + 1))}
            className="rounded-lg border border-slate-200 p-1.5 text-slate-700 hover:bg-slate-50"
            title="Zoom In"
            aria-label="Zoom In"
          >
            <ZoomIn className="h-3.5 w-3.5" />
          </button>
          <button
            type="button"
            onClick={() => {
              setZoom(12);
              onSelectArea("all");
            }}
            className="ml-1 flex items-center gap-1 rounded-lg border border-slate-200 px-2 py-1 text-[11px] font-semibold text-slate-600 hover:bg-slate-50"
            title="Reset Map Filter"
          >
            <RotateCcw className="h-3 w-3" />
            <span>All Areas</span>
          </button>
        </div>
      </div>

      {/* Interactive SVG Map Canvas */}
      <div className="relative h-80 w-full overflow-hidden rounded-xl border border-slate-800 bg-slate-950">
        <svg
          viewBox="0 0 600 320"
          className="h-full w-full select-none"
          role="img"
          aria-label="Coarse Geohash-5 Campus Neighbourhood Map"
        >
          <defs>
            <pattern id="coarseGrid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path
                d="M 40 0 L 0 0 0 40"
                fill="none"
                stroke="#1e293b"
                strokeWidth="1"
              />
            </pattern>
          </defs>
          <rect width="600" height="320" fill="url(#coarseGrid)" />

          {/* Schematic Mula-Mutha River & Campus Arterial Corridor */}
          <path
            d="M 0 230 Q 180 190 340 215 T 600 180"
            fill="none"
            stroke="#0f172a"
            strokeWidth="18"
          />
          <path
            d="M 0 230 Q 180 190 340 215 T 600 180"
            fill="none"
            stroke="#0284c7"
            strokeOpacity="0.28"
            strokeWidth="8"
          />

          {areas.map((area) => {
            const safeHash = sanitizeGeohash5(area.geohash5);
            const pt = projectPoint(area.lat, area.lng);
            const isSelected = selectedArea === area.name;
            const radius = 38 + (zoom - 11) * 6;

            return (
              <g
                key={area.name}
                onClick={() => onSelectArea(isSelected ? "all" : area.name)}
                className="cursor-pointer transition-transform"
              >
                {/* ~5km Coarse Privacy Radius Circle */}
                <circle
                  cx={pt.x}
                  cy={pt.y}
                  r={radius}
                  fill={isSelected ? "rgba(16, 185, 129, 0.25)" : "rgba(16, 185, 129, 0.12)"}
                  stroke={isSelected ? "#10b981" : "#34d399"}
                  strokeWidth={isSelected ? "2.5" : "1.5"}
                  strokeDasharray="5 3"
                />
                {/* Centroid Pin Badge */}
                <circle
                  cx={pt.x}
                  cy={pt.y}
                  r="14"
                  fill={isSelected ? "#059669" : "#0f172a"}
                  stroke="#10b981"
                  strokeWidth="2"
                />
                <text
                  x={pt.x}
                  y={pt.y + 4}
                  textAnchor="middle"
                  fill="#ffffff"
                  fontSize="11"
                  fontWeight="bold"
                >
                  {area.count}
                </text>
                {/* Area & Geohash-5 Label */}
                <rect
                  x={pt.x - 68}
                  y={pt.y + 19}
                  width="136"
                  height="32"
                  rx="6"
                  fill="rgba(15, 23, 42, 0.92)"
                  stroke={isSelected ? "#10b981" : "#334155"}
                  strokeWidth="1"
                />
                <text
                  x={pt.x}
                  y={pt.y + 33}
                  textAnchor="middle"
                  fill="#f8fafc"
                  fontSize="10"
                  fontWeight="bold"
                >
                  {area.name}
                </text>
                <text
                  x={pt.x}
                  y={pt.y + 45}
                  textAnchor="middle"
                  fill="#34d399"
                  fontSize="9"
                  fontFamily="monospace"
                >
                  geohash5: {safeHash}
                </text>
              </g>
            );
          })}
        </svg>

        {/* OpenStreetMap ODbL Attribution Footer (IP_AND_COMPLIANCE.md §4) */}
        <div className="absolute bottom-2 right-2 rounded bg-slate-900/90 px-2 py-0.5 text-[10px] text-slate-300 border border-slate-700">
          Map centroids ©{" "}
          <a
            href="https://www.openstreetmap.org/copyright"
            target="_blank"
            rel="noopener noreferrer"
            className="underline hover:text-emerald-400"
          >
            OpenStreetMap contributors (ODbL)
          </a>{" "}
          • PostGIS Geohash-5 Privacy
        </div>
      </div>

      {/* Quick Area Pills */}
      <div className="flex flex-wrap items-center gap-2 pt-1">
        {areas.map((area) => {
          const safeHash = sanitizeGeohash5(area.geohash5);
          const active = selectedArea === area.name;
          return (
            <button
              key={area.name}
              type="button"
              onClick={() => onSelectArea(active ? "all" : area.name)}
              className={`flex items-center gap-1.5 rounded-lg border px-2.5 py-1.5 text-xs font-semibold transition-all ${
                active
                  ? "border-emerald-600 bg-emerald-50 text-emerald-900"
                  : "border-slate-200 bg-slate-50 text-slate-700 hover:border-slate-300"
              }`}
            >
              <MapPin className="h-3.5 w-3.5 text-emerald-600" />
              <span>{area.name}</span>
              <span className="rounded bg-slate-200/70 px-1.5 py-0.2 font-mono text-[10px] text-slate-700">
                {safeHash} ({area.count})
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default CoarseAreaMap;
