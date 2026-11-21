// Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"use client";

import React, { use, useState } from "react";
import Link from "next/link";
import {
  MapPin,
  ShieldCheck,
  Tag,
  ArrowLeft,
  MessageSquare,
  RefreshCw,
  Eye,
  Heart,
  Share2,
  CheckCircle2,
  AlertCircle,
  TrendingDown,
} from "lucide-react";
import FairDealBadge from "@/components/FairDealBadge";
import PriceDropSuggestionCard from "@/components/PriceDropSuggestionCard";
import VerifiedBadge from "@/components/VerifiedBadge";

export default function ListingDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const [isSaved, setIsSaved] = useState(false);

  // Demo representation
  const item = {
    id,
    title: "Casio fx-991EX ClassWiz Engineering Calculator",
    type: "sell",
    category: "electronics",
    subtype: "Calculator",
    brand: "Casio",
    model: "fx-991EX ClassWiz",
    description:
      "Used for 2 semesters in engineering mathematics and physics. Clean solar cell, responsive high-resolution display, and original protective case included. Free of any major scratches.",
    condition: "good",
    condition_conf: 0.91,
    price_ask: 850,
    price_low: 700,
    price_likely: 850,
    price_high: 1100,
    fair_deal: "fair",
    area_name: "Lohegaon / Charholi",
    geohash5: "tek3x",
    created_at: "2 hours ago",
    views: 48,
    seller: {
      display_name: "Rohan K.",
      is_verified: true,
      community: "Ajeenkya D Y Patil University",
      trust_score: 4.8,
    },
    attributes: {
      Color: "Black",
      Power: "Solar + LR44 Battery",
      "Functions count": "552 functions",
    },
    shaps: [
      { feature: "High-demand tool for engineering syllabus", effect: "+10%" },
      { feature: "Clean solar panel and functional display", effect: "+5%" },
      { feature: "Minor cosmetic scratches on outer slide case", effect: "-5%" },
    ],
  };

  return (
    <div className="mx-auto max-w-3xl px-2 py-4 space-y-6 sm:px-4">
      {/* Back button */}
      <div>
        <Link
          href="/browse"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-600 hover:text-slate-900"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back to Browse</span>
        </Link>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        {/* Left: Photos & Verification */}
        <div className="space-y-3">
          <div className="relative h-72 w-full overflow-hidden rounded-xl bg-slate-100 flex items-center justify-center border border-slate-200">
            <Tag className="h-16 w-16 text-slate-400" />
            <span className="absolute top-3 left-3 rounded-full bg-slate-900/85 px-2.5 py-1 text-xs font-bold uppercase tracking-wider text-white">
              {item.type}
            </span>
          </div>

          <div className="rounded-lg border border-emerald-200 bg-emerald-50/70 p-3 text-xs text-emerald-900 flex items-center gap-2">
            <ShieldCheck className="h-4 w-4 text-emerald-700 shrink-0" />
            <span>Image verified & privacy-scrubbed on-device prior to upload.</span>
          </div>
        </div>

        {/* Right: Key Details & Actions */}
        <div className="space-y-5">
          <div>
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                {item.category} • {item.subtype}
              </span>
              <span className="text-xs text-slate-400">{item.created_at}</span>
            </div>
            <h1 className="mt-1 text-xl font-extrabold text-slate-900 sm:text-2xl">
              {item.title}
            </h1>
            <div className="mt-2 flex items-center gap-1.5 text-xs text-slate-500">
              <MapPin className="h-3.5 w-3.5 text-slate-400" />
              <span>
                {item.area_name} ({item.geohash5})
              </span>
            </div>
          </div>

          {/* Pricing & Fair Deal Card */}
          <div className="rounded-xl border border-slate-200 bg-slate-50/60 p-4 space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">
                  Asking Price
                </span>
                <p className="text-2xl font-black text-slate-900">₹{item.price_ask}</p>
              </div>
              <FairDealBadge grade={item.fair_deal} />
            </div>

            <div className="border-t border-slate-200/80 pt-2 text-xs text-slate-600">
              <div className="flex justify-between">
                <span>Fair Campus Range:</span>
                <span className="font-semibold text-slate-800">
                  ₹{item.price_low} - ₹{item.price_high}
                </span>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2">
            <Link
              href={`/chat/${item.id}`}
              className="flex-1 flex items-center justify-center gap-2 rounded-xl bg-slate-900 py-3 text-xs font-bold text-white shadow-sm hover:bg-slate-800 transition-colors"
            >
              <MessageSquare className="h-4 w-4" />
              <span>Chat with Seller</span>
            </Link>
            <button
              onClick={() => setIsSaved(!isSaved)}
              className={`rounded-xl border p-3 transition-colors ${
                isSaved
                  ? "border-red-200 bg-red-50 text-red-600"
                  : "border-slate-300 bg-white text-slate-700 hover:bg-slate-50"
              }`}
              title="Save Item"
            >
              <Heart className={`h-4 w-4 ${isSaved ? "fill-current" : ""}`} />
            </button>
          </div>

          {/* Seller Profile Card */}
          <div className="rounded-xl border border-slate-200 bg-white p-3.5 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-slate-900 font-bold text-white text-sm">
                {item.seller.display_name.charAt(0)}
              </div>
              <div>
                <h4 className="text-xs font-bold text-slate-900">{item.seller.display_name}</h4>
                <p className="text-[11px] text-slate-500">Trust Rating: {item.seller.trust_score} / 5.0</p>
              </div>
            </div>
            <VerifiedBadge isVerified={item.seller.is_verified} size="sm" />
          </div>

          {/* Seller Hazard-Style Price-Drop Suggestion Card (Phase 17) */}
          <PriceDropSuggestionCard
            currentPrice={item.price_ask}
            predictedLow={item.price_low}
            predictedLikely={780}
            daysActive={8}
            views={item.views}
          />
        </div>
      </div>

      {/* Description & Valuation Explainability */}
      <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm space-y-4">
        <div>
          <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">Item Details</h2>
          <p className="mt-2 text-xs text-slate-600 leading-relaxed sm:text-sm">{item.description}</p>
        </div>

        <div className="border-t border-slate-100 pt-3">
          <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">Specifications</h3>
          <div className="mt-2 grid grid-cols-2 gap-2 sm:grid-cols-3">
            {Object.entries(item.attributes).map(([k, v]) => (
              <div key={k} className="rounded-lg bg-slate-50 p-2 text-xs">
                <span className="text-slate-400 block text-[10px] uppercase font-semibold">{k}</span>
                <span className="font-medium text-slate-800">{v}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="border-t border-slate-100 pt-3">
          <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
            Price Determination Factors
          </h3>
          <ul className="mt-2 space-y-1.5 text-xs text-slate-600">
            {item.shaps.map((s, idx) => (
              <li key={idx} className="flex justify-between items-center bg-slate-50 px-3 py-1.5 rounded-lg">
                <span>• {s.feature}</span>
                <span className="font-semibold text-slate-900">{s.effect}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
