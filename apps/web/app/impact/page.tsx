// Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"use client";

import React, { useState } from "react";
import Link from "next/link";
import { ArrowLeft, BookOpen, Cpu, Leaf, Recycle } from "lucide-react";

interface SensitivityRow {
  displacement_factor: number;
  label: string;
  co2_kg: number;
  weight_kg: number;
}

interface CitationItem {
  category: string;
  subtype: string;
  embodied_co2_kg: number;
  weight_kg: number;
  source: string;
  year: number;
}

const SENSITIVITY_ROWS: SensitivityRow[] = [
  {
    displacement_factor: 0.3,
    label: "Conservative Lower Bound (d = 0.30)",
    co2_kg: 162.4,
    weight_kg: 13.8,
  },
  {
    displacement_factor: 0.45,
    label: "Moderate Substitution (d = 0.45)",
    co2_kg: 243.5,
    weight_kg: 20.7,
  },
  {
    displacement_factor: 0.55,
    label: "Central Reference Baseline (d = 0.55)",
    co2_kg: 297.7,
    weight_kg: 25.3,
  },
  {
    displacement_factor: 0.7,
    label: "High Substitution (d = 0.70)",
    co2_kg: 378.8,
    weight_kg: 32.2,
  },
  {
    displacement_factor: 0.8,
    label: "Optimistic Upper Bound (d = 0.80)",
    co2_kg: 433.0,
    weight_kg: 36.8,
  },
];

const CITED_FACTORS: CitationItem[] = [
  {
    category: "Electronics",
    subtype: "Laptop (14-inch)",
    embodied_co2_kg: 210.0,
    weight_kg: 1.8,
    source: "Dell & Apple Product Environmental Reports (LCA Median)",
    year: 2024,
  },
  {
    category: "Furniture",
    subtype: "Study Table / Desk",
    embodied_co2_kg: 45.0,
    weight_kg: 14.5,
    source: "FIRA Furniture Industry Research Association Desk Footprint Study",
    year: 2022,
  },
  {
    category: "Books",
    subtype: "Academic Textbook",
    embodied_co2_kg: 4.2,
    weight_kg: 0.85,
    source: "Book Industry Study Group & Carbon Trust Publishing LCA",
    year: 2022,
  },
  {
    category: "Hobbies",
    subtype: "Commuter Bicycle",
    embodied_co2_kg: 135.0,
    weight_kg: 13.5,
    source: "Trek & European Cyclists Federation Aluminum Bicycle LCA",
    year: 2023,
  },
];

export default function ImpactDashboardPage() {
  const [scope, setScope] = useState<"personal" | "community">("community");
  const multiplier = scope === "community" ? 1.0 : 0.25;

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900 pb-16">
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-3 flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <Link
              href="/browse"
              className="p-1.5 rounded-lg text-slate-600 hover:bg-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-600"
              aria-label="Back to Browse"
            >
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <div>
              <h1 className="text-base sm:text-lg font-bold text-slate-900">
                Reuse Environmental Impact Dashboard
              </h1>
              <p className="text-xs text-slate-500">
                Range-Based Embodied Carbon &amp; Waste Diversion (docs/IMPACT_METHOD.md)
              </p>
            </div>
          </div>

          <span
            className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-teal-100 text-teal-900"
            title="Rule-based lookup from cited LCA product reports multiplied by displacement factor range [0.30, 0.80]"
          >
            <Cpu className="w-3.5 h-3.5" />
            Algorithmic LCA Lookup Model (Not ML)
          </span>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 pt-5 space-y-6">
        {/* Scope Switcher */}
        <div className="flex items-center justify-between flex-wrap gap-2">
          <div className="inline-flex rounded-lg border border-slate-300 bg-white p-1">
            <button
              type="button"
              onClick={() => setScope("personal")}
              className={`px-3 py-1.5 rounded-md text-xs font-semibold ${
                scope === "personal"
                  ? "bg-emerald-600 text-white"
                  : "text-slate-700 hover:bg-slate-100"
              }`}
            >
              My Impact (/impact/me)
            </button>
            <button
              type="button"
              onClick={() => setScope("community")}
              className={`px-3 py-1.5 rounded-md text-xs font-semibold ${
                scope === "community"
                  ? "bg-emerald-600 text-white"
                  : "text-slate-700 hover:bg-slate-100"
              }`}
            >
              Campus Community (/impact/community)
            </button>
          </div>
          <span className="text-xs text-slate-500">
            Displacement Factor Range: d &isin; [0.30, 0.80] (Central d = 0.55)
          </span>
        </div>

        {/* Range Cards (No False Precision) */}
        <section className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="bg-white p-4 rounded-xl border border-emerald-200 shadow-sm space-y-1">
            <div className="flex items-center gap-1.5 text-xs font-semibold text-emerald-800">
              <Leaf className="w-4 h-4 text-emerald-600" />
              Avoided Embodied Emissions (kg CO2e)
            </div>
            <p className="text-2xl font-bold text-slate-900">
              {(162.4 * multiplier).toFixed(1)} – {(433.0 * multiplier).toFixed(1)} kg CO2e
            </p>
            <p className="text-xs text-slate-600">
              Central Estimate (d = 0.55):{" "}
              <span className="font-semibold">{(297.7 * multiplier).toFixed(1)} kg CO2e</span>
            </p>
          </div>

          <div className="bg-white p-4 rounded-xl border border-teal-200 shadow-sm space-y-1">
            <div className="flex items-center gap-1.5 text-xs font-semibold text-teal-800">
              <Recycle className="w-4 h-4 text-teal-600" />
              Material &amp; E-Waste Mass Diverted (kg)
            </div>
            <p className="text-2xl font-bold text-slate-900">
              {(13.8 * multiplier).toFixed(1)} – {(36.8 * multiplier).toFixed(1)} kg
            </p>
            <p className="text-xs text-slate-600">
              Central Estimate (d = 0.55):{" "}
              <span className="font-semibold">{(25.3 * multiplier).toFixed(1)} kg</span>
            </p>
          </div>
        </section>

        {/* Sensitivity Analysis Table */}
        <section
          aria-labelledby="sensitivity-heading"
          className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm"
        >
          <div className="px-4 py-3 bg-slate-100 border-b border-slate-200">
            <h2 id="sensitivity-heading" className="text-xs sm:text-sm font-semibold text-slate-800">
              Sensitivity Analysis Across Reuse Displacement Factor (d)
            </h2>
            <p className="text-xs text-slate-500">
              Avoided CO2e = Embodied CO2e &times; d (evaluating counterfactual new-purchase
              replacement rate)
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs sm:text-sm">
              <thead className="bg-slate-50 text-slate-600 border-b border-slate-200">
                <tr>
                  <th className="px-4 py-2.5">Displacement Assumption</th>
                  <th className="px-4 py-2.5">Avoided CO2e (kg)</th>
                  <th className="px-4 py-2.5">Diverted Mass (kg)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {SENSITIVITY_ROWS.map((row) => (
                  <tr key={row.displacement_factor}>
                    <td className="px-4 py-2.5 font-medium text-slate-800">{row.label}</td>
                    <td className="px-4 py-2.5 text-emerald-800 font-semibold">
                      {(row.co2_kg * multiplier).toFixed(1)} kg
                    </td>
                    <td className="px-4 py-2.5 text-slate-700">
                      {(row.weight_kg * multiplier).toFixed(1)} kg
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Cited LCA Factor Sources */}
        <section
          aria-labelledby="citations-heading"
          className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm"
        >
          <div className="px-4 py-3 bg-slate-100 border-b border-slate-200 flex items-center gap-1.5">
            <BookOpen className="w-4 h-4 text-emerald-600" />
            <h2 id="citations-heading" className="text-xs sm:text-sm font-semibold text-slate-800">
              Cited LCA Factor Table (ml/data/impact_factors.csv)
            </h2>
          </div>
          <div className="divide-y divide-slate-100">
            {CITED_FACTORS.map((item) => (
              <div
                key={item.subtype}
                className="px-4 py-3 flex flex-wrap items-center justify-between gap-2 text-xs"
              >
                <div>
                  <span className="font-semibold text-slate-900">
                    {item.category} — {item.subtype}
                  </span>
                  <p className="text-slate-500 mt-0.5">
                    Source: {item.source} ({item.year})
                  </p>
                </div>
                <div className="text-right font-medium text-slate-800">
                  <span>{item.embodied_co2_kg} kg CO2e</span> · <span>{item.weight_kg} kg</span>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}
