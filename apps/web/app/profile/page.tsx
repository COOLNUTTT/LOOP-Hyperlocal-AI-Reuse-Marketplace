// Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  User,
  MapPin,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  Download,
  Trash2,
  LogOut,
  KeyRound,
  Mail,
  Building,
} from "lucide-react";
import VerifiedBadge from "@/components/VerifiedBadge";

interface UserProfile {
  id: string;
  auth_uid: string;
  display_name: string;
  area_name: string;
  geohash5: string;
  is_verified: boolean;
  role: string;
  created_at: string;
  communities: Array<{
    id: string;
    name: string;
    type: string;
    role: string;
  }>;
}

export default function ProfilePage() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  // Edit State
  const [displayName, setDisplayName] = useState("");
  const [areaName, setAreaName] = useState("");
  const [isUpdating, setIsUpdating] = useState(false);

  // Community Verification State
  const [verifyMethod, setVerifyMethod] = useState<"email_domain" | "join_code">("email_domain");
  const [joinCode, setJoinCode] = useState("");
  const [isVerifying, setIsVerifying] = useState(false);

  useEffect(() => {
    fetchProfile();
  }, []);

  const getAuthToken = () => {
    if (typeof window !== "undefined") {
      return localStorage.getItem("loop_access_token");
    }
    return null;
  };

  const fetchProfile = async () => {
    const token = getAuthToken();
    if (!token) {
      // Mock local session for initial offline test/preview if not logged in
      setProfile({
        id: "demo-user-id",
        auth_uid: "demo-auth-uid",
        display_name: "Demo Student",
        area_name: "Lohegaon / Charholi",
        geohash5: "tek3x",
        is_verified: false,
        role: "user",
        created_at: new Date().toISOString(),
        communities: [],
      });
      setDisplayName("Demo Student");
      setAreaName("Lohegaon / Charholi");
      setIsLoading(false);
      return;
    }

    try {
      const response = await fetch("/api/v1/users/me", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Unable to load profile data");
      }

      const data = await response.json();
      setProfile(data);
      setDisplayName(data.display_name);
      setAreaName(data.area_name);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Error fetching profile");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsUpdating(true);
    setError(null);
    setMessage(null);

    const token = getAuthToken();
    if (!token) {
      setMessage("Profile updated (Demo Mode)");
      setIsUpdating(false);
      return;
    }

    try {
      const response = await fetch("/api/v1/users/me", {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          display_name: displayName,
          area_name: areaName,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Failed to update profile");
      }

      const updated = await response.json();
      setProfile(updated);
      setMessage("Profile updated successfully.");
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to update profile");
      }
    } finally {
      setIsUpdating(false);
    }
  };

  const handleVerifyCommunity = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsVerifying(true);
    setError(null);
    setMessage(null);

    const token = getAuthToken();
    if (!token) {
      if (verifyMethod === "join_code" && joinCode.trim().toUpperCase() === "LOOP-DEMO-2026") {
        setProfile((prev) =>
          prev
            ? {
                ...prev,
                is_verified: true,
                communities: [
                  {
                    id: "adypu-community",
                    name: "Ajeenkya D Y Patil University",
                    type: "college",
                    role: "member",
                  },
                ],
              }
            : null
        );
        setMessage("Verified successfully for Ajeenkya D Y Patil University (Demo Mode)!");
      } else {
        setError("Invalid join code or demonstration credentials.");
      }
      setIsVerifying(false);
      return;
    }

    try {
      const response = await fetch("/api/v1/auth/verify-community", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          method: verifyMethod,
          join_code: verifyMethod === "join_code" ? joinCode.trim() : undefined,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Community verification failed");
      }

      setMessage(`Verified as a member of ${data.community_name}!`);
      fetchProfile();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Verification error");
      }
    } finally {
      setIsVerifying(false);
    }
  };

  const handleExportData = async () => {
    const token = getAuthToken();
    if (!token) {
      alert("DPDP Data Export is available for authenticated accounts.");
      return;
    }

    try {
      const response = await fetch("/api/v1/users/me/export", {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!response.ok) {
        throw new Error("Export failed");
      }

      const data = await response.json();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `loop-data-export-${new Date().toISOString().split("T")[0]}.json`;
      a.click();
    } catch (err) {
      alert("Failed to export personal data.");
    }
  };

  const handleDeleteAccount = async () => {
    const confirmText = prompt(
      "To permanently delete your account and all associated data per DPDP Act, type 'DELETE' below:"
    );

    if (confirmText !== "DELETE") return;

    const token = getAuthToken();
    if (!token) {
      alert("Account deletion is available for authenticated accounts.");
      return;
    }

    try {
      const response = await fetch("/api/v1/users/me", {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!response.ok) {
        throw new Error("Deletion failed");
      }

      localStorage.clear();
      window.location.href = "/";
    } catch (err) {
      alert("Failed to delete account. Please try again.");
    }
  };

  const handleSignOut = () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem("loop_access_token");
      localStorage.removeItem("loop_refresh_token");
      window.location.href = "/login";
    }
  };

  if (isLoading) {
    return (
      <div className="flex min-h-[300px] items-center justify-center">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-slate-900 border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl px-2 py-4 space-y-6 sm:px-4">
      {/* Header Profile Card */}
      <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-slate-900 text-white font-bold text-lg">
              {profile?.display_name ? profile.display_name.charAt(0).toUpperCase() : "U"}
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <h1 className="text-lg font-bold text-slate-900 sm:text-xl">
                  {profile?.display_name}
                </h1>
                <VerifiedBadge
                  isVerified={profile?.is_verified ?? false}
                  communityName={profile?.communities?.[0]?.name}
                  size="sm"
                />
              </div>
              <div className="flex items-center gap-1.5 mt-0.5 text-xs text-slate-500">
                <MapPin className="h-3.5 w-3.5" />
                <span>
                  {profile?.area_name} ({profile?.geohash5})
                </span>
              </div>
            </div>
          </div>

          <button
            onClick={handleSignOut}
            className="flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors self-start sm:self-auto"
          >
            <LogOut className="h-3.5 w-3.5" />
            <span>Sign Out</span>
          </button>
        </div>
      </div>

      {/* Notifications */}
      {error && (
        <div className="flex items-center gap-2 rounded-lg bg-red-50 p-3 text-xs text-red-700" role="alert">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {message && (
        <div className="flex items-center gap-2 rounded-lg bg-emerald-50 p-3 text-xs text-emerald-800" role="status">
          <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-600" />
          <span>{message}</span>
        </div>
      )}

      {/* Community Verification Card */}
      {!profile?.is_verified && (
        <div className="rounded-xl border border-amber-200 bg-amber-50/50 p-5 shadow-sm">
          <div className="flex items-center gap-2">
            <Building className="h-5 w-5 text-amber-800" />
            <h2 className="text-sm font-bold text-amber-900 sm:text-base">
              Get Campus Community Verified
            </h2>
          </div>
          <p className="mt-1 text-xs text-amber-800">
            Verify your affiliation with Ajeenkya D Y Patil University (ADYPU) or your society to
            unlock trusted swaps and seller badges.
          </p>

          <form className="mt-4 space-y-3" onSubmit={handleVerifyCommunity}>
            <div className="flex gap-4">
              <label className="flex items-center gap-1.5 text-xs font-medium text-slate-800 cursor-pointer">
                <input
                  type="radio"
                  name="method"
                  value="email_domain"
                  checked={verifyMethod === "email_domain"}
                  onChange={() => setVerifyMethod("email_domain")}
                  className="text-slate-900 focus:ring-slate-900"
                />
                <span>Confirmed @adypu.edu.in Email</span>
              </label>

              <label className="flex items-center gap-1.5 text-xs font-medium text-slate-800 cursor-pointer">
                <input
                  type="radio"
                  name="method"
                  value="join_code"
                  checked={verifyMethod === "join_code"}
                  onChange={() => setVerifyMethod("join_code")}
                  className="text-slate-900 focus:ring-slate-900"
                />
                <span>Community Join Code</span>
              </label>
            </div>

            {verifyMethod === "join_code" && (
              <div>
                <label htmlFor="joinCode" className="block text-xs font-semibold text-slate-700">
                  Enter 10-14 Character Join Code
                </label>
                <input
                  id="joinCode"
                  type="text"
                  required
                  value={joinCode}
                  onChange={(e) => setJoinCode(e.target.value)}
                  placeholder="e.g. LOOP-DEMO-2026"
                  className="mt-1 block w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs font-mono uppercase text-slate-900 placeholder-slate-400 focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900"
                />
                <p className="mt-1 text-[11px] text-slate-500">
                  Rate-limited: maximum 5 attempts per hour per account.
                </p>
              </div>
            )}

            <button
              type="submit"
              disabled={isVerifying}
              className="flex items-center justify-center gap-1.5 rounded-lg bg-slate-900 px-4 py-2 text-xs font-semibold text-white shadow-sm hover:bg-slate-800 disabled:opacity-50 transition-colors"
            >
              <ShieldCheck className="h-4 w-4" />
              <span>{isVerifying ? "Verifying..." : "Verify Affiliation"}</span>
            </button>
          </form>
        </div>
      )}

      {/* Profile Details Edit Card */}
      <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
        <h2 className="text-sm font-bold text-slate-900 sm:text-base">Profile Information</h2>
        <p className="text-xs text-slate-500">Update your public display name and general locality</p>

        <form className="mt-4 space-y-4" onSubmit={handleUpdateProfile}>
          <div>
            <label htmlFor="editDisplayName" className="block text-xs font-semibold uppercase tracking-wider text-slate-700">
              Display Name
            </label>
            <input
              id="editDisplayName"
              type="text"
              required
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900"
            />
          </div>

          <div>
            <label htmlFor="editAreaName" className="block text-xs font-semibold uppercase tracking-wider text-slate-700">
              Coarse Area Name
            </label>
            <input
              id="editAreaName"
              type="text"
              required
              value={areaName}
              onChange={(e) => setAreaName(e.target.value)}
              className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900"
            />
          </div>

          <button
            type="submit"
            disabled={isUpdating}
            className="rounded-lg bg-slate-900 px-4 py-2 text-xs font-semibold text-white shadow-sm hover:bg-slate-800 disabled:opacity-50 transition-colors"
          >
            {isUpdating ? "Saving..." : "Save Changes"}
          </button>
        </form>
      </div>

      {/* DPDP Act Compliance & Data Rights Section */}
      <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
        <h2 className="text-sm font-bold text-slate-900 sm:text-base">
          DPDP Act Privacy & Data Controls
        </h2>
        <p className="text-xs text-slate-500">
          Manage your personal data in compliance with the Digital Personal Data Protection Act, 2023.
        </p>

        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          <div className="flex flex-col justify-between rounded-lg border border-slate-100 bg-slate-50 p-4">
            <div>
              <div className="flex items-center gap-1.5 font-semibold text-slate-800 text-xs">
                <Download className="h-4 w-4 text-slate-700" />
                <span>Download My Data</span>
              </div>
              <p className="mt-1 text-[11px] text-slate-600">
                Export a machine-readable JSON copy of your profile, active listings, and community memberships.
              </p>
            </div>
            <button
              onClick={handleExportData}
              className="mt-3 flex items-center justify-center gap-1.5 rounded-lg border border-slate-300 bg-white py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-100 transition-colors"
            >
              Export JSON
            </button>
          </div>

          <div className="flex flex-col justify-between rounded-lg border border-red-100 bg-red-50/40 p-4">
            <div>
              <div className="flex items-center gap-1.5 font-semibold text-red-900 text-xs">
                <Trash2 className="h-4 w-4 text-red-600" />
                <span>Delete Account</span>
              </div>
              <p className="mt-1 text-[11px] text-red-700">
                Irreversibly delete your account, database records, and purge all uploaded photos from storage buckets.
              </p>
            </div>
            <button
              onClick={handleDeleteAccount}
              className="mt-3 flex items-center justify-center gap-1.5 rounded-lg border border-red-200 bg-white py-1.5 text-xs font-semibold text-red-700 hover:bg-red-50 transition-colors"
            >
              Erase All Data
            </button>
          </div>
        </div>

        <div className="mt-4 text-center">
          <Link href="/consent" className="text-xs font-medium text-slate-600 underline hover:text-slate-900">
            Review DPDP Privacy Notice & Data Terms
          </Link>
        </div>
      </div>
    </div>
  );
}
