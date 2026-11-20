// Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"use client";

import React from "react";
import { CheckCircle2, ShieldCheck, AlertCircle } from "lucide-react";

interface VerifiedBadgeProps {
  isVerified: boolean;
  communityName?: string;
  className?: string;
  size?: "sm" | "md" | "lg";
}

export const VerifiedBadge: React.FC<VerifiedBadgeProps> = ({
  isVerified,
  communityName,
  className = "",
  size = "md",
}) => {
  if (!isVerified) {
    return (
      <span
        className={`inline-flex items-center gap-1 rounded-full bg-slate-100 font-medium text-slate-600 ${
          size === "sm"
            ? "px-2 py-0.5 text-xs"
            : size === "lg"
              ? "px-3 py-1.5 text-sm"
              : "px-2.5 py-1 text-xs"
        } ${className}`}
        aria-label="Community unverified"
      >
        <AlertCircle className={size === "sm" ? "h-3 w-3" : "h-3.5 w-3.5"} />
        <span>Unverified</span>
      </span>
    );
  }

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full bg-emerald-50 font-medium text-emerald-800 ring-1 ring-inset ring-emerald-600/20 ${
        size === "sm"
          ? "px-2 py-0.5 text-xs"
          : size === "lg"
            ? "px-3 py-1.5 text-sm"
            : "px-2.5 py-1 text-xs"
      } ${className}`}
      aria-label={`Verified Member ${communityName ? `of ${communityName}` : ""}`}
    >
      <ShieldCheck className={size === "sm" ? "h-3.5 w-3.5" : "h-4 w-4"} text-emerald-600 />
      <span className="font-semibold">Verified Member</span>
      {communityName && (
        <span className="text-emerald-700 font-normal border-l border-emerald-300 pl-1.5">
          {communityName}
        </span>
      )}
    </span>
  );
};

export default VerifiedBadge;
