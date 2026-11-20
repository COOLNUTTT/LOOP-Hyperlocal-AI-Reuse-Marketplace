// Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"use client";

import React, { useState } from "react";
import Link from "next/link";
import { MessageSquare, ShieldCheck, Tag, ArrowRight, Clock, User, AlertCircle } from "lucide-react";

// Mock active threads
const DEMO_THREADS = [
  {
    listing_id: "demo-listing-1",
    listing_title: "Casio fx-991EX ClassWiz Engineering Calculator",
    listing_price: 850,
    other_user_id: "user-rohan",
    other_user_name: "Rohan K.",
    other_user_verified: true,
    last_message_body: "Hi! Yes, it's still available. We can meet near the library.",
    last_message_at: "10m ago",
    unread_count: 1,
  },
  {
    listing_id: "demo-listing-2",
    listing_title: "IKEA Micke Compact Study Table with Cable Outlet",
    listing_price: 2400,
    other_user_id: "user-aditi",
    other_user_name: "Aditi S.",
    other_user_verified: true,
    last_message_body: "Can you do ₹2200 if I pick it up tomorrow afternoon?",
    last_message_at: "2h ago",
    unread_count: 0,
  },
];

export default function ChatInboxPage() {
  const [threads, setThreads] = useState(DEMO_THREADS);

  return (
    <div className="mx-auto max-w-2xl px-2 py-4 space-y-5 sm:px-4">
      <div className="flex items-center justify-between border-b border-slate-200 pb-3">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-slate-900">Messages & Negotiations</h1>
          <p className="text-xs text-slate-500">Real-time chats with verified campus community members</p>
        </div>
        <span className="flex items-center gap-1 text-xs font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200">
          <ShieldCheck className="h-3.5 w-3.5" />
          <span>Encrypted Threads</span>
        </span>
      </div>

      <div className="space-y-3">
        {threads.map((thread) => (
          <Link
            key={thread.listing_id}
            href={`/chat/${thread.listing_id}`}
            className="flex items-center justify-between rounded-xl border border-slate-200 bg-white p-4 shadow-sm hover:border-slate-300 hover:shadow-md transition-all"
          >
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-slate-900 text-white font-bold text-sm">
                {thread.other_user_name.charAt(0)}
              </div>
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <h3 className="font-bold text-slate-900 text-sm">{thread.other_user_name}</h3>
                  {thread.other_user_verified && (
                    <span className="rounded-full bg-emerald-50 px-1.5 py-0.2 text-[10px] font-semibold text-emerald-800">
                      Verified
                    </span>
                  )}
                  <span className="text-[11px] text-slate-400">• {thread.last_message_at}</span>
                </div>
                <p className="text-xs font-medium text-slate-700 line-clamp-1">{thread.listing_title}</p>
                <p className="text-xs text-slate-500 line-clamp-1">{thread.last_message_body}</p>
              </div>
            </div>

            <div className="flex flex-col items-end gap-1.5 pl-3">
              <span className="text-xs font-bold text-slate-900">₹{thread.listing_price}</span>
              {thread.unread_count > 0 && (
                <span className="flex h-5 w-5 items-center justify-center rounded-full bg-slate-900 text-[10px] font-bold text-white">
                  {thread.unread_count}
                </span>
              )}
            </div>
          </Link>
        ))}

        {threads.length === 0 && (
          <div className="rounded-xl border border-dashed border-slate-200 bg-white p-8 text-center space-y-2">
            <MessageSquare className="mx-auto h-8 w-8 text-slate-400" />
            <p className="text-sm font-semibold text-slate-700">No active conversations</p>
            <p className="text-xs text-slate-500">
              Browse listings to chat with sellers or negotiate fair campus trades.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
