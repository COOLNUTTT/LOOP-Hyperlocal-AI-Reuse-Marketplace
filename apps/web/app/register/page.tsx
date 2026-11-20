// Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"use client";

import React, { useState } from "react";
import Link from "next/link";
import { UserPlus, ArrowRight, Lock, Mail, User, MapPin, AlertCircle } from "lucide-react";

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    displayName: "",
    areaName: "Lohegaon / Charholi",
    geohash5: "tek3x",
  });
  const [hasConsented, setHasConsented] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!hasConsented) {
      setError("Please review and agree to the DPDP Act Privacy Notice to proceed.");
      return;
    }

    if (formData.geohash5.length !== 5) {
      setError("Geohash must be exactly 5 characters for privacy-preserving coarse location.");
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch("/api/v1/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password,
          display_name: formData.displayName,
          area_name: formData.areaName,
          geohash5: formData.geohash5.toLowerCase(),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Registration failed. Please check your details.");
      }

      if (typeof window !== "undefined") {
        localStorage.setItem("loop_access_token", data.access_token);
        localStorage.setItem("loop_refresh_token", data.refresh_token);
        window.location.href = "/consent";
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("An unexpected error occurred during registration.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-[calc(100vh-140px)] flex-col justify-center px-2 py-6 sm:px-6">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-slate-900 text-white shadow-md">
            <UserPlus className="h-6 w-6" />
          </div>
        </div>
        <h1 className="mt-4 text-center text-2xl font-extrabold tracking-tight text-slate-900 sm:text-3xl">
          Join LOOP
        </h1>
        <p className="mt-2 text-center text-xs text-slate-600 sm:text-sm">
          Privacy-first campus marketplace for buying, selling, and swapping
        </p>
      </div>

      <div className="mt-6 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="rounded-xl border border-slate-200 bg-white px-4 py-6 shadow-sm sm:px-8">
          {error && (
            <div
              className="mb-4 flex items-center gap-2 rounded-lg bg-red-50 p-3 text-xs text-red-700"
              role="alert"
            >
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form className="space-y-4" onSubmit={handleSubmit}>
            <div>
              <label
                htmlFor="displayName"
                className="block text-xs font-semibold uppercase tracking-wider text-slate-700"
              >
                Display Name
              </label>
              <div className="relative mt-1">
                <input
                  id="displayName"
                  name="displayName"
                  type="text"
                  required
                  value={formData.displayName}
                  onChange={handleChange}
                  placeholder="Alex M."
                  className="block w-full rounded-lg border border-slate-300 px-3 py-2 pl-9 text-sm text-slate-900 placeholder-slate-400 focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900"
                />
                <User className="pointer-events-none absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
              </div>
            </div>

            <div>
              <label
                htmlFor="email"
                className="block text-xs font-semibold uppercase tracking-wider text-slate-700"
              >
                College or Personal Email
              </label>
              <div className="relative mt-1">
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="student@adypu.edu.in"
                  className="block w-full rounded-lg border border-slate-300 px-3 py-2 pl-9 text-sm text-slate-900 placeholder-slate-400 focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900"
                />
                <Mail className="pointer-events-none absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
              </div>
              <p className="mt-1 text-[11px] text-slate-500">
                Use your college email for automatic community verification.
              </p>
            </div>

            <div>
              <label
                htmlFor="password"
                className="block text-xs font-semibold uppercase tracking-wider text-slate-700"
              >
                Password (min. 8 characters)
              </label>
              <div className="relative mt-1">
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="new-password"
                  required
                  minLength={8}
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="••••••••"
                  className="block w-full rounded-lg border border-slate-300 px-3 py-2 pl-9 text-sm text-slate-900 placeholder-slate-400 focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900"
                />
                <Lock className="pointer-events-none absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label
                  htmlFor="areaName"
                  className="block text-xs font-semibold uppercase tracking-wider text-slate-700"
                >
                  Coarse Area
                </label>
                <div className="relative mt-1">
                  <input
                    id="areaName"
                    name="areaName"
                    type="text"
                    required
                    value={formData.areaName}
                    onChange={handleChange}
                    placeholder="Wakad / Hinjawadi"
                    className="block w-full rounded-lg border border-slate-300 px-3 py-2 pl-9 text-xs text-slate-900 placeholder-slate-400 focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900"
                  />
                  <MapPin className="pointer-events-none absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
                </div>
              </div>

              <div>
                <label
                  htmlFor="geohash5"
                  className="block text-xs font-semibold uppercase tracking-wider text-slate-700"
                >
                  Geohash (5 chars)
                </label>
                <input
                  id="geohash5"
                  name="geohash5"
                  type="text"
                  maxLength={5}
                  required
                  value={formData.geohash5}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2 text-xs font-mono text-slate-900 placeholder-slate-400 focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900"
                />
              </div>
            </div>

            <div className="rounded-lg bg-slate-50 p-3 text-[11px] text-slate-600">
              <span className="font-semibold text-slate-800">Privacy Guarantee:</span> LOOP never asks for or stores exact home addresses or GPS coordinates. Only neighbourhood-level geohashes are preserved.
            </div>

            <div className="flex items-start gap-2 pt-1">
              <input
                id="consent"
                type="checkbox"
                checked={hasConsented}
                onChange={(e) => setHasConsented(e.target.checked)}
                className="mt-0.5 h-4 w-4 rounded border-slate-300 text-slate-900 focus:ring-slate-900"
              />
              <label htmlFor="consent" className="text-xs text-slate-600">
                I agree to LOOP&apos;s{" "}
                <Link href="/consent" className="font-medium text-slate-900 underline">
                  DPDP Privacy Notice
                </Link>{" "}
                and acknowledge my data rights.
              </label>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="flex w-full items-center justify-center gap-2 rounded-lg bg-slate-900 py-2.5 px-4 text-sm font-semibold text-white shadow-sm hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:ring-offset-2 disabled:opacity-60 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? (
                <span>Creating account...</span>
              ) : (
                <>
                  <span>Create Account</span>
                  <ArrowRight className="h-4 w-4" />
                </>
              )}
            </button>
          </form>

          <div className="mt-6 border-t border-slate-100 pt-4 text-center">
            <p className="text-xs text-slate-600">
              Already have an account?{" "}
              <Link
                href="/login"
                className="font-semibold text-slate-900 underline hover:text-slate-800"
              >
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
