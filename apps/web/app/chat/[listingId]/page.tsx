// Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"use client";

import React, { use, useState, useEffect, useRef } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  Send,
  ShieldCheck,
  Tag,
  CheckCheck,
  AlertTriangle,
  Flag,
  Wifi,
} from "lucide-react";
import {
  evaluateChatSafetyWarning,
  subscribeToListingChat,
  type RealtimeChatMessage,
} from "@/lib/supabaseClient";

interface MessageItem {
  id: string;
  sender_id: string;
  sender_name: string;
  body: string;
  created_at: string;
  is_me: boolean;
  safety_warning?: string | null;
}

export default function ChatThreadPage({
  params,
}: {
  params: Promise<{ listingId: string }>;
}) {
  const { listingId } = use(params);
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
  const [realtimeMode, setRealtimeMode] = useState<string>("local-broadcast-channel");
  const [showReportModal, setShowReportModal] = useState(false);
  const [reportReason, setReportReason] = useState("");
  const [reportSubmitted, setReportSubmitted] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const publishRef = useRef<((msg: RealtimeChatMessage) => void) | null>(null);

  useEffect(() => {
    const sub = subscribeToListingChat(listingId, (incoming) => {
      const check = evaluateChatSafetyWarning(incoming.body);
      setMessages((prev) => {
        if (prev.some((m) => m.id === incoming.id)) return prev;
        return [
          ...prev,
          {
            id: incoming.id,
            sender_id: incoming.sender_id,
            sender_name: incoming.sender_name,
            body: incoming.body,
            created_at: incoming.created_at,
            is_me: false,
            safety_warning: check.warningText,
          },
        ];
      });
    });
    setRealtimeMode(sub.mode);
    publishRef.current = sub.publish;
    return () => sub.unsubscribe();
  }, [listingId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const liveDraftSafety = evaluateChatSafetyWarning(inputMessage);

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    const safety = evaluateChatSafetyWarning(inputMessage);
    const nowTime = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    const newMsg: MessageItem = {
      id: `msg-${Date.now()}`,
      sender_id: "me",
      sender_name: "Me",
      body: inputMessage.trim(),
      created_at: nowTime,
      is_me: true,
      safety_warning: safety.warningText,
    };

    setMessages((prev) => [...prev, newMsg]);
    publishRef.current?.({
      id: newMsg.id,
      listing_id: listingId,
      sender_id: newMsg.sender_id,
      sender_name: newMsg.sender_name,
      body: newMsg.body,
      created_at: nowTime,
      safety_warning: safety.warningText,
    });
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
                <span className="text-sm font-bold text-slate-900">Rohan K.</span>
                <span className="inline-flex items-center gap-0.5 rounded-full bg-emerald-50 px-1.5 py-0.2 text-[10px] font-semibold text-emerald-700 border border-emerald-200">
                  <ShieldCheck className="h-2.5 w-2.5" />
                  <span>ADYPU Verified</span>
                </span>
              </div>
              <p className="text-[11px] text-slate-500 flex items-center gap-1">
                <Wifi className="h-2.5 w-2.5 text-emerald-600" />
                <span>
                  {realtimeMode === "supabase-realtime"
                    ? "Supabase Realtime Connected"
                    : "Realtime Channel Active"}
                </span>
              </p>
            </div>
          </div>
        </div>

        <button
          type="button"
          onClick={() => setShowReportModal(true)}
          className="flex items-center gap-1 rounded-lg border border-slate-200 px-2.5 py-1.5 text-xs font-medium text-slate-600 hover:bg-red-50 hover:text-red-700 hover:border-red-200 transition-colors"
        >
          <Flag className="h-3.5 w-3.5" />
          <span>Report</span>
        </button>
      </div>

      {/* Item Context Banner */}
      <div className="flex items-center justify-between border-b border-slate-100 bg-slate-50 px-4 py-2 text-xs">
        <div className="flex items-center gap-2">
          <Tag className="h-3.5 w-3.5 text-emerald-600" />
          <span className="font-semibold text-slate-800">
            Casio fx-991EX ClassWiz Calculator
          </span>
          <span className="font-bold text-emerald-700">₹850</span>
        </div>
        <span className="rounded bg-emerald-100 px-1.5 py-0.5 text-[10px] font-semibold text-emerald-800">
          Rule-Based Fair Range: ₹775–₹1,028
        </span>
      </div>

      {/* Safety Banner */}
      <div className="flex items-center gap-2 border-b border-amber-100 bg-amber-50/70 px-4 py-1.5 text-[11px] text-amber-800">
        <AlertTriangle className="h-3.5 w-3.5 shrink-0 text-amber-600" />
        <span>
          Meet only at verified campus spots (Library / Cafeteria). Never share raw phone numbers or pay advance UPI QR requests.
        </span>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-slate-50/40">
        {messages.map((msg) => (
          <div key={msg.id} className="space-y-1">
            <div className={`flex flex-col ${msg.is_me ? "items-end" : "items-start"}`}>
              <div
                className={`max-w-[78%] rounded-2xl px-3.5 py-2 text-xs leading-relaxed shadow-xs ${
                  msg.is_me
                    ? "bg-slate-900 text-white rounded-br-xs"
                    : "bg-white text-slate-800 border border-slate-200/80 rounded-bl-xs"
                }`}
              >
                <p>{msg.body}</p>
              </div>
              <div className="mt-1 flex items-center gap-1 text-[10px] text-slate-400 px-1">
                <span>{msg.created_at}</span>
                {msg.is_me && <CheckCheck className="h-3 w-3 text-emerald-600" />}
              </div>
            </div>
            {msg.safety_warning && (
              <div className="mx-auto max-w-md rounded-lg border border-red-200 bg-red-50 px-3 py-1.5 text-[11px] font-medium text-red-800 flex items-center gap-1.5">
                <AlertTriangle className="h-3.5 w-3.5 shrink-0 text-red-600" />
                <span>{msg.safety_warning}</span>
              </div>
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Live Scam Draft Warning */}
      {liveDraftSafety.flagged && (
        <div className="border-t border-amber-200 bg-amber-50 px-4 py-2 text-[11px] font-medium text-amber-900 flex items-center gap-2">
          <AlertTriangle className="h-4 w-4 shrink-0 text-amber-600" />
          <span>{liveDraftSafety.warningText}</span>
        </div>
      )}

      {/* Rule-Based Negotiation Helper Pills */}
      <div className="flex items-center gap-1.5 border-t border-slate-100 bg-white px-4 py-2 overflow-x-auto">
        <span className="text-[10px] font-semibold text-slate-400 uppercase shrink-0">
          Rule-Based Offers:
        </span>
        {[750, 800, 850].map((amt) => (
          <button
            key={amt}
            type="button"
            onClick={() => handleQuickOffer(amt)}
            className="rounded-full border border-slate-200 bg-slate-50 px-2.5 py-1 text-[11px] font-semibold text-slate-700 hover:border-emerald-500 hover:bg-emerald-50 hover:text-emerald-800 transition-colors shrink-0"
          >
            Offer ₹{amt}
          </button>
        ))}
      </div>

      {/* Message Input Form */}
      <form
        onSubmit={handleSendMessage}
        className="flex items-center gap-2 border-t border-slate-200 bg-white p-3"
      >
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Type a message (no external phone numbers)..."
          className="flex-1 rounded-xl border border-slate-200 bg-slate-50 px-3.5 py-2 text-xs text-slate-900 focus:border-slate-900 focus:bg-white focus:outline-none"
        />
        <button
          type="submit"
          className="flex h-9 w-9 items-center justify-center rounded-xl bg-slate-900 text-white hover:bg-slate-800 transition-colors"
          title="Send Message"
        >
          <Send className="h-4 w-4" />
        </button>
      </form>

      {/* Report Modal */}
      {showReportModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="w-full max-w-sm rounded-2xl bg-white p-5 shadow-xl space-y-4">
            <h3 className="text-sm font-bold text-slate-900">Report Conversation or Listing</h3>
            {reportSubmitted ? (
              <p className="text-xs font-semibold text-emerald-700">
                Report logged to moderation queue (`manual_report`). Thank you!
              </p>
            ) : (
              <form onSubmit={handleReport} className="space-y-3">
                <textarea
                  required
                  rows={3}
                  value={reportReason}
                  onChange={(e) => setReportReason(e.target.value)}
                  placeholder="Describe the issue (e.g., asking for off-platform UPI QR payment)..."
                  className="w-full rounded-lg border border-slate-200 p-2.5 text-xs"
                />
                <div className="flex justify-end gap-2">
                  <button
                    type="button"
                    onClick={() => setShowReportModal(false)}
                    className="rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-slate-600"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="rounded-lg bg-red-600 px-3 py-1.5 text-xs font-bold text-white hover:bg-red-700"
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
