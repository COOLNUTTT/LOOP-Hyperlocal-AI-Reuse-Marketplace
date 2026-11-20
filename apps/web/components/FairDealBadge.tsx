// Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"use client";

import React from "react";
import { Sparkles, CheckCircle2, TrendingUp, HelpCircle } from "lucide-react";

interface FairDealBadgeProps {
  grade?: "great" | "fair" | "overpriced" | string | null;
  priceAsk?: number | string | null;
  priceLikely?: number | string | null;
  priceRange?: { low: number; high: number } | null;
  className?: string;
  showExplanation?: boolean;
}

export const FairDealBadge: React.FC<FairDealBadgeProps> = ({
  grade,
  priceAsk,
  priceLikely,
  priceRange,
  className = "",
  showExplanation = false,
}) => {
  if (!grade) {
    return null;
  }

  const normalized = grade.toLowerCase();

  const badgeConfig = {
    great: {
      label: "Great Deal",
      bgColor: "bg-emerald-50",
      textColor: "text-emerald-800",
      ringColor: "ring-emerald-600/20",
      icon: Sparkles,
      iconColor: "text-emerald-600",
      desc: "Priced 15%+ below estimated fair market value for the campus.",
    },
    fair: {
      label: "Fair Market Deal",
      bgColor: "bg-sky-50",
      textColor: "text-sky-800",
      ringColor: "ring-sky-600/20",
      icon: CheckCircle2,
      iconColor: "text-sky-600",
      desc: "Within ±15% of estimated fair campus market value.",
    },
    overpriced: {
      label: "Above Market",
      bgColor: "bg-amber-50",
      textColor: "text-amber-800",
      ringColor: "ring-amber-600/20",
      icon: TrendingUp,
      iconColor: "text-amber-600",
      desc: "Asking price is higher than standard community transactions.",
    },
  };

  const config = badgeConfig[normalized as keyof typeof badgeConfig] || badgeConfig.fair;
  const IconComponent = config.icon;

  return (
    <div className={`inline-flex flex-col gap-1 ${className}`}>
      <span
        className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ring-inset ${config.bgColor} ${config.textColor} ${config.ringColor}`}
        title={config.desc}
      >
        <IconComponent className={`h-3.5 w-3.5 ${config.iconColor}`} />
        <span>{config.label}</span>
      </span>

      {showExplanation && (
        <div className="mt-1 rounded-lg border border-slate-200 bg-slate-50 p-2.5 text-[11px] text-slate-600">
          <p className="font-semibold text-slate-800 flex items-center gap-1">
            <HelpCircle className="h-3 w-3 text-slate-500" />
            <span>Campus Valuation Transparency</span>
          </p>
          <p className="mt-0.5">{config.desc}</p>
          {priceLikely && (
            <div className="mt-1 flex items-center justify-between text-slate-500 border-t border-slate-200/60 pt-1">
              <span>Fair Market Estimate:</span>
              <span className="font-bold text-slate-900">₹{priceLikely}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default FairDealBadge;
