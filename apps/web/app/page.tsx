// Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
import Link from "next/link";
import { ArrowRight, ShieldCheck, RefreshCw, Sparkles, User, LogIn } from "lucide-react";

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center space-y-8 py-6 text-center sm:py-12">
      <div className="space-y-3 max-w-xl">
        <span className="inline-flex items-center gap-1.5 rounded-full bg-slate-900 px-3 py-1 text-xs font-semibold text-white">
          <Sparkles className="h-3.5 w-3.5 text-amber-300" />
          <span>Hyperlocal Campus Reuse Network</span>
        </span>
        <h1 className="text-3xl font-extrabold tracking-tight text-slate-900 sm:text-5xl">
          Buy, Sell & Swap in Your Community
        </h1>
        <p className="mx-auto max-w-md text-sm text-slate-600 sm:text-base">
          Trade pre-owned electronics, furniture, books, and hobbies with verified peers at ADYPU and nearby societies.
        </p>
      </div>

      <div className="flex flex-wrap items-center justify-center gap-3">
        <Link
          href="/register"
          className="flex items-center gap-2 rounded-lg bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-slate-800 transition-colors"
        >
          <span>Get Started</span>
          <ArrowRight className="h-4 w-4" />
        </Link>
        <Link
          href="/login"
          className="flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 shadow-sm hover:bg-slate-50 transition-colors"
        >
          <LogIn className="h-4 w-4" />
          <span>Sign In</span>
        </Link>
        <Link
          href="/profile"
          className="flex items-center gap-2 rounded-lg border border-slate-200 bg-slate-100 px-5 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-200 transition-colors"
        >
          <User className="h-4 w-4" />
          <span>Profile Demo</span>
        </Link>
      </div>

      <div className="grid w-full grid-cols-2 gap-3 sm:grid-cols-4 sm:gap-4 max-w-lg">
        {["Electronics", "Furniture", "Books", "Hobbies"].map((category) => (
          <div
            key={category}
            className="flex flex-col items-center rounded-xl border border-slate-200 bg-white p-3.5 shadow-sm hover:border-slate-300 transition-colors"
          >
            <span className="text-xs font-semibold text-slate-800">{category}</span>
          </div>
        ))}
      </div>

      {/* DPDP and Trust Highlights */}
      <div className="grid w-full max-w-lg gap-3 sm:grid-cols-2 text-left">
        <div className="rounded-xl border border-emerald-200 bg-emerald-50/70 p-4">
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-4 w-4 text-emerald-700" />
            <h2 className="text-xs font-semibold uppercase tracking-wider text-emerald-900">
              Coarse Privacy & Verification
            </h2>
          </div>
          <p className="mt-1 text-xs text-emerald-800">
            Neighbourhood-level geohashes with DPDP Act compliance. Verified campus community members.
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-4">
          <div className="flex items-center gap-2">
            <RefreshCw className="h-4 w-4 text-slate-700" />
            <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-800">
              Fair Swaps & Trade
            </h2>
          </div>
          <p className="mt-1 text-xs text-slate-600">
            Multi-way circular exchange algorithms and explainable fair-deal valuations.
          </p>
        </div>
      </div>
    </div>
  );
}
