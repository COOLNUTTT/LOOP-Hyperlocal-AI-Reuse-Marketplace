// Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"use client";

import React, { useState } from "react";
import Link from "next/link";
import { ShieldCheck, CheckCircle2, ArrowRight, Lock, EyeOff, Trash2, Download } from "lucide-react";

export default function ConsentPage() {
  const [agreed, setAgreed] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleAcknowledge = () => {
    if (!agreed) return;
    setSubmitted(true);
    if (typeof window !== "undefined") {
      localStorage.setItem("loop_dpdp_consent", new Date().toISOString());
      setTimeout(() => {
        window.location.href = "/profile";
      }, 1000);
    }
  };

  return (
    <div className="mx-auto max-w-2xl px-2 py-6 sm:px-4">
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-emerald-100 text-emerald-800">
            <ShieldCheck className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-slate-900 sm:text-2xl">
              Privacy Notice & Data Rights
            </h1>
            <p className="text-xs text-slate-500">
              Aligned with the Digital Personal Data Protection (DPDP) Act, 2023
            </p>
          </div>
        </div>

        <div className="mt-6 space-y-4 text-xs text-slate-600 sm:text-sm">
          <p>
            LOOP is built with strict privacy guarantees. Before participating in your campus reuse
            network, please review how your personal data is handled:
          </p>

          <div className="grid gap-3 pt-2">
            <div className="flex gap-3 rounded-lg border border-slate-100 bg-slate-50/80 p-3.5">
              <EyeOff className="h-5 w-5 shrink-0 text-slate-700" />
              <div>
                <h2 className="font-semibold text-slate-800 text-xs sm:text-sm">
                  Coarse Location Only
                </h2>
                <p className="mt-0.5 text-xs text-slate-600">
                  We never ask for or store exact residential addresses or GPS coordinates. Only
                  broad locality names and 5-character geohashes (~5 km² area) are recorded.
                </p>
              </div>
            </div>

            <div className="flex gap-3 rounded-lg border border-slate-100 bg-slate-50/80 p-3.5">
              <Lock className="h-5 w-5 shrink-0 text-slate-700" />
              <div>
                <h2 className="font-semibold text-slate-800 text-xs sm:text-sm">
                  Client-Side Photo Privacy Scrubbing
                </h2>
                <p className="mt-0.5 text-xs text-slate-600">
                  Before any photo leaves your device, on-device AI blurs detected human faces, vehicle
                  number plates, IDs, and phone numbers. Unscrubbed originals are rejected by the
                  server.
                </p>
              </div>
            </div>

            <div className="flex gap-3 rounded-lg border border-slate-100 bg-slate-50/80 p-3.5">
              <Download className="h-5 w-5 shrink-0 text-slate-700" />
              <div>
                <h2 className="font-semibold text-slate-800 text-xs sm:text-sm">
                  Right to Data Portability
                </h2>
                <p className="mt-0.5 text-xs text-slate-600">
                  You can export your complete profile, listings, and trade history in a
                  machine-readable format at any time directly from your profile settings.
                </p>
              </div>
            </div>

            <div className="flex gap-3 rounded-lg border border-slate-100 bg-slate-50/80 p-3.5">
              <Trash2 className="h-5 w-5 shrink-0 text-slate-700" />
              <div>
                <h2 className="font-semibold text-slate-800 text-xs sm:text-sm">
                  Right to Complete Erasure (Purge)
                </h2>
                <p className="mt-0.5 text-xs text-slate-600">
                  Deleting your account immediately purges your database records and deletes all
                  uploaded photos from storage buckets, with irreversible destruction.
                </p>
              </div>
            </div>
          </div>

          <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-4">
            <h3 className="font-semibold text-emerald-900 text-xs sm:text-sm">
              Community Verification Notice
            </h3>
            <p className="mt-1 text-xs text-emerald-800">
              Your college email or join code is solely used to verify your community affiliation
              (e.g., ADYPU). Email addresses are never made public to other buyers or sellers.
            </p>
          </div>
        </div>

        <div className="mt-6 border-t border-slate-200 pt-6">
          <label className="flex items-start gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={agreed}
              onChange={(e) => setAgreed(e.target.checked)}
              className="mt-1 h-4 w-4 rounded border-slate-300 text-slate-900 focus:ring-slate-900"
            />
            <span className="text-xs text-slate-700 sm:text-sm">
              I have read and agree to the privacy policy, consent to processing my coarse locality
              for marketplace discovery, and understand my rights under the DPDP Act.
            </span>
          </label>

          <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <Link
              href="/"
              className="text-center text-xs font-medium text-slate-600 hover:text-slate-900"
            >
              Cancel & Return Home
            </Link>

            <button
              onClick={handleAcknowledge}
              disabled={!agreed || submitted}
              className="flex items-center justify-center gap-2 rounded-lg bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {submitted ? (
                <>
                  <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                  <span>Consent Recorded</span>
                </>
              ) : (
                <>
                  <span>Accept & Continue</span>
                  <ArrowRight className="h-4 w-4" />
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
