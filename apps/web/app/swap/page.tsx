// Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  ArrowRight,
  CheckCircle2,
  Cpu,
  Plus,
  RefreshCw,
  ShieldCheck,
} from "lucide-react";

interface WishlistItem {
  id: string;
  want_category: string;
  want_text: string;
  max_price: number | null;
}

interface SwapEdge {
  id: string;
  giver_name: string;
  receiver_name: string;
  item_title: string;
  estimated_value: number;
  confirmed: boolean;
  is_current_user_giver: boolean;
}

interface SwapCycleCard {
  cycle_id: string;
  length: number;
  status: "proposed" | "partially_confirmed" | "confirmed";
  value_imbalance_pct: number;
  edges: SwapEdge[];
}

const INITIAL_WISHES: WishlistItem[] = [
  {
    id: "w-1",
    want_category: "books",
    want_text: "Cormen Introduction to Algorithms (CLRS 4th Ed)",
    max_price: 900,
  },
  {
    id: "w-2",
    want_category: "electronics",
    want_text: "Casio fx-991CW Scientific Calculator",
    max_price: 850,
  },
];

const INITIAL_CYCLES: SwapCycleCard[] = [
  {
    cycle_id: "cyc-3way-101",
    length: 3,
    status: "partially_confirmed",
    value_imbalance_pct: 6.2,
    edges: [
      {
        id: "prop-1",
        giver_name: "You (Hostel B)",
        receiver_name: "Aarav (Hostel A)",
        item_title: "Logitech M331 Silent Wireless Mouse",
        estimated_value: 750,
        confirmed: false,
        is_current_user_giver: true,
      },
      {
        id: "prop-2",
        giver_name: "Aarav (Hostel A)",
        receiver_name: "Priya (Society C)",
        item_title: "wooden Book Stand & Desk Organizer",
        estimated_value: 720,
        confirmed: true,
        is_current_user_giver: false,
      },
      {
        id: "prop-3",
        giver_name: "Priya (Society C)",
        receiver_name: "You (Hostel B)",
        item_title: "Cormen Introduction to Algorithms (CLRS)",
        estimated_value: 765,
        confirmed: true,
        is_current_user_giver: false,
      },
    ],
  },
];

export default function SwapEnginePage() {
  const [wishes, setWishes] = useState<WishlistItem[]>(INITIAL_WISHES);
  const [cycles, setCycles] = useState<SwapCycleCard[]>(INITIAL_CYCLES);
  const [category, setCategory] = useState<string>("books");
  const [wantText, setWantText] = useState<string>("");
  const [maxPrice, setMaxPrice] = useState<string>("1000");
  const [notice, setNotice] = useState<string | null>(null);

  const handleAddWishlist = (e: React.FormEvent) => {
    e.preventDefault();
    if (!wantText.trim()) return;
    const newWish: WishlistItem = {
      id: `w-${Date.now()}`,
      want_category: category,
      want_text: wantText.trim(),
      max_price: maxPrice ? Number(maxPrice) : null,
    };
    setWishes((prev) => [newWish, ...prev]);
    setWantText("");
    setNotice("Wishlist added and indexed in compatibility graph.");
  };

  const handleConfirmMyEdge = (cycleId: string, edgeId: string) => {
    setCycles((prev) =>
      prev.map((cyc) => {
        if (cyc.cycle_id !== cycleId) return cyc;
        const updatedEdges = cyc.edges.map((ed) =>
          ed.id === edgeId ? { ...ed, confirmed: true } : ed
        );
        const allConfirmed = updatedEdges.every((ed) => ed.confirmed);
        return {
          ...cyc,
          edges: updatedEdges,
          status: allConfirmed ? "confirmed" : "partially_confirmed",
        };
      })
    );
    setNotice(
      "Your swap edge is confirmed! Because all 3 parties confirmed, per-edge QR/OTP handovers are now unlocked."
    );
  };

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
                Multi-Party Swap Engine
              </h1>
              <p className="text-xs text-slate-500">
                2-Way &amp; 3-Way Barter Cycles Within Value Tolerance (&delta; &le; 30%)
              </p>
            </div>
          </div>
          <span
            className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-indigo-100 text-indigo-900"
            title="Uses combinatorial cycle enumeration and CP-SAT vertex-disjoint set-packing, not ML"
          >
            <Cpu className="w-3.5 h-3.5" />
            Algorithmic (CP-SAT Graph Solver — Not ML)
          </span>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 pt-5 space-y-6">
        {notice && (
          <div
            role="status"
            className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-900 text-xs sm:text-sm flex items-start gap-2"
          >
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
            <span>{notice}</span>
          </div>
        )}

        {/* Wishlist Form */}
        <section
          aria-labelledby="wishlist-heading"
          className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-3"
        >
          <h2 id="wishlist-heading" className="text-sm font-semibold text-slate-800">
            1. My Swap Wishlists (What You Want to Receive)
          </h2>

          <form onSubmit={handleAddWishlist} className="grid grid-cols-1 sm:grid-cols-4 gap-2">
            <select
              aria-label="Wanted Category"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="px-3 py-2 rounded-lg border border-slate-300 text-xs sm:text-sm bg-white"
            >
              <option value="books">Books</option>
              <option value="electronics">Electronics</option>
              <option value="furniture">Furniture</option>
              <option value="hobbies">Hobbies &amp; Recreation</option>
            </select>
            <input
              type="text"
              placeholder="e.g., Study lamp or CLRS textbook"
              value={wantText}
              onChange={(e) => setWantText(e.target.value)}
              className="sm:col-span-2 px-3 py-2 rounded-lg border border-slate-300 text-xs sm:text-sm"
              required
            />
            <div className="flex gap-2">
              <input
                type="number"
                aria-label="Max value in INR"
                placeholder="Max ₹"
                value={maxPrice}
                onChange={(e) => setMaxPrice(e.target.value)}
                className="w-24 px-2.5 py-2 rounded-lg border border-slate-300 text-xs sm:text-sm"
              />
              <button
                type="submit"
                className="flex-1 inline-flex items-center justify-center gap-1 px-3 py-2 rounded-lg bg-emerald-600 text-white text-xs font-semibold hover:bg-emerald-700"
              >
                <Plus className="w-3.5 h-3.5" />
                Add
              </button>
            </div>
          </form>

          <div className="divide-y divide-slate-100 pt-2">
            {wishes.map((w) => (
              <div
                key={w.id}
                className="py-2 flex items-center justify-between text-xs sm:text-sm"
              >
                <div>
                  <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-medium capitalize mr-2">
                    {w.want_category}
                  </span>
                  <span className="font-medium text-slate-800">{w.want_text}</span>
                </div>
                {w.max_price && (
                  <span className="text-slate-500">Up to ₹{w.max_price}</span>
                )}
              </div>
            ))}
          </div>
        </section>

        {/* Active Swap Cycle Proposals */}
        <section aria-labelledby="cycles-heading" className="space-y-3">
          <div className="flex items-center justify-between">
            <h2
              id="cycles-heading"
              className="text-sm font-semibold text-slate-800 flex items-center gap-1.5"
            >
              <RefreshCw className="w-4 h-4 text-emerald-600" />
              2. Matched Disjoint Swap Cycles (Length &le; 3)
            </h2>
            <span className="text-xs text-slate-500">
              All participants must confirm before handovers unlock
            </span>
          </div>

          {cycles.map((cyc) => (
            <div
              key={cyc.cycle_id}
              className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-3"
            >
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-900">
                    {cyc.length}-Way Cycle
                  </span>
                  <span className="text-xs text-slate-600">
                    Value Imbalance: {cyc.value_imbalance_pct}% (within &le;30% fairness bound)
                  </span>
                </div>
                <span
                  className={`px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                    cyc.status === "confirmed"
                      ? "bg-emerald-600 text-white"
                      : "bg-amber-100 text-amber-900"
                  }`}
                >
                  {cyc.status === "confirmed"
                    ? "All Parties Confirmed — Handovers Ready"
                    : "Awaiting All-Party Confirmation"}
                </span>
              </div>

              <div className="space-y-2 pt-2 border-t border-slate-100">
                {cyc.edges.map((edge) => (
                  <div
                    key={edge.id}
                    className="p-3 rounded-lg bg-slate-50 border border-slate-200 flex flex-wrap items-center justify-between gap-2 text-xs sm:text-sm"
                  >
                    <div className="space-y-0.5">
                      <div className="flex items-center gap-1.5 font-semibold text-slate-800">
                        <span>{edge.giver_name}</span>
                        <ArrowRight className="w-3.5 h-3.5 text-slate-400" />
                        <span>{edge.receiver_name}</span>
                      </div>
                      <p className="text-slate-600">
                        Item: <span className="font-medium">{edge.item_title}</span> (~₹
                        {edge.estimated_value})
                      </p>
                    </div>

                    <div>
                      {edge.confirmed ? (
                        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-emerald-100 text-emerald-800 text-xs font-semibold">
                          <ShieldCheck className="w-3.5 h-3.5" />
                          Confirmed
                        </span>
                      ) : edge.is_current_user_giver ? (
                        <button
                          type="button"
                          onClick={() => handleConfirmMyEdge(cyc.cycle_id, edge.id)}
                          className="px-3 py-1.5 rounded-lg bg-emerald-600 text-white text-xs font-semibold hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-600"
                        >
                          Confirm My Trade Edge
                        </button>
                      ) : (
                        <span className="text-xs text-slate-500">Pending</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </section>
      </div>
    </main>
  );
}
