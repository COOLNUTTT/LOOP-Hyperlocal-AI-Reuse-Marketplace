// Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
/**
 * Supabase Auth, Storage & Realtime Client Layer (`apps/web/lib/supabaseClient.ts`).
 *
 * Connects to hosted Supabase Storage (`listing-images` bucket) and Realtime WebSocket
 * channels (`realtime:public:messages`) when `NEXT_PUBLIC_SUPABASE_URL` and
 * `NEXT_PUBLIC_SUPABASE_ANON_KEY` are configured, with seamless `BroadcastChannel`
 * local real-time sync in offline/CI development environments.
 *
 * Non-negotiable invariant (`AGENTS.md` §2): `uploadScrubbedListingImage` rejects
 * any image where `isScrubbed !== true` with `LISTING_NOT_SCRUBBED`.
 */

export interface SupabaseRuntimeConfig {
  supabaseUrl: string;
  supabaseAnonKey: string;
  apiUrl: string;
  isLiveConfigured: boolean;
}

export interface ScrubbedUploadRequest {
  listingId: string;
  dataUrl: string;
  isScrubbed: boolean;
  redactionBoxCount: number;
}

export interface ScrubbedUploadResponse {
  storagePath: string;
  publicUrl: string;
  scrubbed: true;
  provider: "supabase-storage" | "local-scrubbed-store";
}

export interface RealtimeChatMessage {
  id: string;
  listing_id: string;
  sender_id: string;
  sender_name: string;
  body: string;
  created_at: string;
  safety_warning?: string | null;
}

export interface ChatSafetyCheck {
  flagged: boolean;
  rule: string | null;
  warningText: string | null;
}

const SCAM_PATTERNS: Array<{ rule: string; regex: RegExp; warning: string }> = [
  {
    rule: "upi_qr_receive_scam",
    regex: /\b(scan\s+qr|upi\s+qr|qr\s+code\s+to\s+receive|enter\s+upi\s+pin)\b/i,
    warning:
      "Safety Alert: You never need to scan a QR code or enter your UPI PIN to receive money.",
  },
  {
    rule: "advance_courier_fee_scam",
    regex: /\b(advance\s+payment|courier\s+charge|booking\s+token|pay\s+half\s+first|army\s+parcel)\b/i,
    warning:
      "Safety Alert: Never pay advance token or courier fees before inspecting the item in person at a verified campus meetup spot.",
  },
  {
    rule: "off_platform_contact_leak",
    regex: /\b(whatsapp\s+me|telegram\s+me|call\s+my\s+number)\b/i,
    warning:
      "Privacy Reminder: Keep negotiations inside LOOP Chat to stay protected by handover OTP verification.",
  },
  {
    rule: "premature_handover_otp",
    regex: /\b(send\s+otp|share\s+the\s+otp\s+now|tell\s+me\s+the\s+code\s+before)\b/i,
    warning:
      "Handover Guard: Only share your 6-digit Handover OTP in person after physically inspecting the item.",
  },
];

export function getSupabaseConfig(): SupabaseRuntimeConfig {
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "";
  const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
  const isLiveConfigured =
    Boolean(supabaseUrl) &&
    Boolean(supabaseAnonKey) &&
    !supabaseUrl.includes("your-project-ref");

  return {
    supabaseUrl,
    supabaseAnonKey,
    apiUrl,
    isLiveConfigured,
  };
}

/**
 * Evaluate chat message text against rule-based scam & safety heuristics (`ROADMAP.md` Phase 13).
 */
export function evaluateChatSafetyWarning(messageText: string): ChatSafetyCheck {
  for (const item of SCAM_PATTERNS) {
    if (item.regex.test(messageText)) {
      return {
        flagged: true,
        rule: item.rule,
        warningText: item.warning,
      };
    }
  }
  return {
    flagged: false,
    rule: null,
    warningText: null,
  };
}

/**
 * Upload a client-scrubbed listing photo to Supabase Storage (`listing-images` bucket).
 * Strictly blocks any unscrubbed photo (`LISTING_NOT_SCRUBBED`).
 */
export async function uploadScrubbedListingImage(
  req: ScrubbedUploadRequest
): Promise<ScrubbedUploadResponse> {
  if (!req.isScrubbed) {
    throw new Error(
      "LISTING_NOT_SCRUBBED: Raw unscrubbed photos cannot leave the device or upload to Supabase Storage."
    );
  }

  const cfg = getSupabaseConfig();
  const objectPath = `listings/${req.listingId}/scrubbed-${Date.now()}.jpg`;

  if (cfg.isLiveConfigured && typeof fetch !== "undefined") {
    try {
      const blobResp = await fetch(req.dataUrl);
      const blob = await blobResp.blob();
      const uploadUrl = `${cfg.supabaseUrl.replace(/\/$/, "")}/storage/v1/object/listing-images/${objectPath}`;
      const res = await fetch(uploadUrl, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${cfg.supabaseAnonKey}`,
          apikey: cfg.supabaseAnonKey,
          "Content-Type": "image/jpeg",
          "x-upsert": "true",
        },
        body: blob,
      });

      if (res.ok) {
        return {
          storagePath: objectPath,
          publicUrl: `${cfg.supabaseUrl.replace(/\/$/, "")}/storage/v1/object/public/listing-images/${objectPath}`,
          scrubbed: true,
          provider: "supabase-storage",
        };
      }
    } catch {
      // Fallback to local scrubbed data URL when offline
    }
  }

  return {
    storagePath: objectPath,
    publicUrl: req.dataUrl,
    scrubbed: true,
    provider: "local-scrubbed-store",
  };
}

/**
 * Subscribe to real-time messages for `listingId` via Supabase Realtime WebSocket
 * and browser `BroadcastChannel`.
 */
export function subscribeToListingChat(
  listingId: string,
  onMessage: (msg: RealtimeChatMessage) => void
): {
  mode: "supabase-realtime" | "local-broadcast-channel";
  publish: (msg: RealtimeChatMessage) => void;
  unsubscribe: () => void;
} {
  const cfg = getSupabaseConfig();
  const channelName = `loop-chat-thread-${listingId}`;
  let bc: BroadcastChannel | null = null;
  let ws: WebSocket | null = null;

  if (typeof window !== "undefined" && "BroadcastChannel" in window) {
    bc = new BroadcastChannel(channelName);
    bc.onmessage = (ev: MessageEvent<RealtimeChatMessage>) => {
      if (ev.data && ev.data.id) {
        onMessage(ev.data);
      }
    };
  }

  if (cfg.isLiveConfigured && typeof window !== "undefined" && "WebSocket" in window) {
    try {
      const wsBase = cfg.supabaseUrl.replace(/^http/, "ws").replace(/\/$/, "");
      const wsUrl = `${wsBase}/realtime/v1/websocket?apikey=${encodeURIComponent(
        cfg.supabaseAnonKey
      )}&vsn=1.0.0`;
      ws = new WebSocket(wsUrl);
      ws.onopen = () => {
        ws?.send(
          JSON.stringify({
            topic: `realtime:public:messages:listing_id=eq.${listingId}`,
            event: "phx_join",
            payload: {},
            ref: "1",
          })
        );
      };
      ws.onmessage = (event) => {
        try {
          const packet = JSON.parse(String(event.data));
          const record = packet?.payload?.record;
          if (record && record.body) {
            onMessage({
              id: String(record.id),
              listing_id: String(record.listing_id || listingId),
              sender_id: String(record.sender_id || "peer"),
              sender_name: String(record.sender_name || "Campus Peer"),
              body: String(record.body),
              created_at: new Date().toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
              }),
            });
          }
        } catch {
          // Ignore heartbeat frames
        }
      };
    } catch {
      ws = null;
    }
  }

  return {
    mode: cfg.isLiveConfigured ? "supabase-realtime" : "local-broadcast-channel",
    publish: (msg: RealtimeChatMessage) => {
      bc?.postMessage(msg);
    },
    unsubscribe: () => {
      bc?.close();
      ws?.close();
    },
  };
}
