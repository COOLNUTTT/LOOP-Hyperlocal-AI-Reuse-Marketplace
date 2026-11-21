// Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"use client";

import React, { use, useState, useEffect, useRef } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  Send,
  ShieldAlert,
  ShieldCheck,
  Tag,
  CheckCheck,
  AlertTriangle,
  Flag,
} from "lucide-react";

interface MessageItem {
  id: string;
  sender_id: string;
  sender_name: string;
  body: string;
  created_at: string;
  is_me: boolean;
}

export default function ChatThreadPage({
  params,
}: {
  params: Promise<{ listingId: string }>;
}) {
  const { listingId: _listingId } = use(params);
  const [messages, setMessages] = useState<MessageItem[]>([
    {
      id: "msg-1",
      sender_id: "user-rohan",
      sender_name: "Rohan K.",
      body: "Hi! Thanks for reaching out. Yes, the Casio fx-991EX is available.",
      created_at: "10:14 AM",
      is_me: false,
    },
    {
      id: "msg-2",
      sender_id: "me",
      sender_name: "Me",
      body: "Awesome! Can we meet at the campus library or cafeteria for the handover?",
      created_at: "10:16 AM",
      is_me: true,
    },
  ]);

  const [inputMessage, setInputMessage] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [showReportModal, setShowReportModal] = useState(false);
  const [reportReason, setReportReason] = useState("");
  const [reportSubmitted, setReportSubmitted] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    const newMsg: MessageItem = {
      id: `msg-${Date.now()}`,
      sender_id: "me",
      sender_name: "Me",
      body: inputMessage.trim(),
      created_at: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      is_me: true,
    };

    setMessages((prev) => [...prev, newMsg]);
    setInputMessage("");

    // Simulate real-time seller response
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          id: `msg-reply-${Date.now()}`,
          sender_id: "user-rohan",
          sender_name: "Rohan K.",
          body: "Sounds great! 4:00 PM near the library entrance works well for me.",
          created_at: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          is_me: false,
        },
      ]);
    }, 1200);
  };

  const handleQuickOffer = (amount: number) => {
    setInputMessage(`Would you consider ₹${amount} for a quick handover today?`);
  };

  const handleReport = (e: React.FormEvent) => {
    e.preventDefault();
    setReportSubmitted(true);
    setTimeout(() => {
      setShowReportModal(false);
      setReportSubmitted(false);
      setReportReason("");
    }, 1500);
  };

  return (
    <div className="mx-auto flex h-[calc(100vh-140px)] max-w-2xl flex-col rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-200 bg-white px-4 py-3">
        <div className="flex items-center gap-3">
          <Link href="/chat" className="text-slate-600 hover:text-slate-900">
            <ArrowLeft className="h-4 w-4" />
          </Link>
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-900 font-bold text-white text-xs">
              R
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <h2 className="text-xs font-bold text-slate-900">Rohan K.</h2>
                <span className="rounded bg-emerald-50 px-1.5 py-0.2 text-[10px] font-semibold text-emerald-800">
                  Verified
                </span>
              </div>
              <p className="text-[11px] text-slate-500">Casio fx-991EX (₹850)</p>
            </div>
          </div>
        </div>

        <button
          onClick={() => setShowReportModal(true)}
          className="flex items-center gap-1 rounded-lg border border-slate-200 px-2 py-1 text-[11px] font-semibold text-slate-600 hover:bg-slate-50"
          title="Report Scam or Harassment"
        >
          <Flag className="h-3 w-3 text-red-500" />
          <span>Report</span>
        </button>
      </div>

      {/* Safety Notice */}
      <div className="bg-amber-50/70 border-b border-amber-200/60 px-4 py-2 text-[11px] text-amber-900 flex items-center gap-2">
        <AlertTriangle className="h-3.5 w-3.5 text-amber-600 shrink-0" />
        <span>Campus Safety: Meet in public campus spots (library, cafeteria). Never pay advance UPI.</span>
      </div>

      {/* Message Stream */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-slate-50/50">
        {messages.map((m) => (
          <div
            key={m.id}
            className={`flex flex-col ${m.is_me ? "items-end" : "items-start"}`}
          >
            <div
              className={`max-w-[80%] rounded-2xl px-3.5 py-2 text-xs leading-relaxed shadow-sm ${
                m.is_me
                  ? "bg-slate-900 text-white rounded-br-xs"
                  : "bg-white text-slate-800 border border-slate-200 rounded-bl-xs"
              }`}
            >
              <p>{m.body}</p>
            </div>
            <span className="mt-0.5 text-[10px] text-slate-400 px-1">{m.created_at}</span>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Negotiation Actions */}
      <div className="flex items-center gap-2 border-t border-slate-100 bg-white px-3 py-1.5 text-xs overflow-x-auto">
        <span className="text-[10px] uppercase font-bold text-slate-400 shrink-0">Quick:</span>
        <button
          onClick={() => setInputMessage("Is this still available?")}
          className="whitespace-nowrap rounded-full border border-slate-200 bg-slate-50 px-2.5 py-1 text-[11px] text-slate-700 hover:bg-slate-100"
        >
          Available?
        </button>
        <button
          onClick={() => handleQuickOffer(800)}
          className="whitespace-nowrap rounded-full border border-slate-200 bg-slate-50 px-2.5 py-1 text-[11px] text-slate-700 hover:bg-slate-100"
        >
          Offer ₹800
        </button>
        <button
          onClick={() => setInputMessage("Can we meet at the campus library?")}
          className="whitespace-nowrap rounded-full border border-slate-200 bg-slate-50 px-2.5 py-1 text-[11px] text-slate-700 hover:bg-slate-100"
        >
          Meet at library
        </button>
      </div>

      {/* Input Form */}
      <form onSubmit={handleSendMessage} className="border-t border-slate-200 bg-white p-3 flex gap-2">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Type message (max 60/min rate limit)..."
          className="flex-1 rounded-xl border border-slate-300 px-3 py-2 text-xs text-slate-900 placeholder-slate-400 focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900"
        />
        <button
          type="submit"
          disabled={!inputMessage.trim()}
          className="flex items-center justify-center rounded-xl bg-slate-900 px-4 py-2 text-white hover:bg-slate-800 disabled:opacity-40 transition-colors"
        >
          <Send className="h-4 w-4" />
        </button>
      </form>

      {/* Moderation / Report Modal */}
      {showReportModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-xs p-4">
          <div className="w-full max-w-sm rounded-xl border border-slate-200 bg-white p-5 shadow-lg space-y-4">
            <div className="flex items-center gap-2">
              <ShieldAlert className="h-5 w-5 text-red-600" />
              <h3 className="text-sm font-bold text-slate-900">Report User or Listing</h3>
            </div>
            <p className="text-xs text-slate-600">
              Submit a flag to campus moderators for spam, advance payment requests, or abusive behavior.
            </p>

            {reportSubmitted ? (
              <div className="rounded-lg bg-emerald-50 p-3 text-xs text-emerald-800 flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-emerald-600" />
                <span>Flag submitted. Moderators will review within 24 hours.</span>
              </div>
            ) : (
              <form onSubmit={handleReport} className="space-y-3">
                <textarea
                  rows={3}
                  required
                  value={reportReason}
                  onChange={(e) => setReportReason(e.target.value)}
                  placeholder="Describe the issue (e.g. asked for advance UPI outside platform)..."
                  className="w-full rounded-lg border border-slate-300 p-2 text-xs text-slate-900 focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900"
                />
                <div className="flex justify-end gap-2">
                  <button
                    type="button"
                    onClick={() => setShowReportModal(false)}
                    className="rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-slate-600 hover:bg-slate-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="rounded-lg bg-red-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-red-700"
                  >
                    Submit Report
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
