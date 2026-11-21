// Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
/**
 * Playwright Browser E2E Journey Specifications (`apps/web/e2e/loop-journeys.spec.ts`).
 *
 * Covers the 3 main user journeys + moderation on a 360px mobile viewport (`ROADMAP.md` Phases 11, 18):
 * 1. Journey 1 (Snap-to-List): `/sell` -> on-device ONNX quality & privacy scrubber -> AI draft -> seller edit -> publish.
 * 2. Journey 2 (Find & Buy + Coarse Map): `/browse` -> Hinglish search & filters -> interactive Geohash-5 Map -> `/listings/[id]`.
 * 3. Journey 3 (Realtime Chat, Algorithmic Swap & Impact): `/chat/[listingId]` safety alerts, `/swap` <=3-way cycles, `/impact` LCA ranges.
 * 4. Journey 4 (Moderation & Active Learning Governance): `/admin` flag queue, model health, and active learning promotion status.
 */

export interface E2EJourneySpec {
  id: string;
  title: string;
  viewport: { width: number; height: number };
  routes: string[];
  assertions: string[];
}

export const LOOP_E2E_JOURNEYS: E2EJourneySpec[] = [
  {
    id: "journey-1-snap-to-list",
    title: "Snap-to-List Vertical Slice (Photo -> Quality -> Scrub -> AI Draft -> Correction -> Publish)",
    viewport: { width: 360, height: 800 },
    routes: ["/sell"],
    assertions: [
      "On-Device Privacy Scrubber renders redaction boxes with add, resize (-/+), and remove controls",
      "onnxruntime-web-wasm latency badge renders after image load",
      "Burn Irreversible Pixelation overwrites raw canvas pixels before upload",
      "AI Draft displays category confidence, Grad-CAM condition overlay, and split-conformal price range with top-3 SHAP reasons",
      "Editing AI-predicted category, condition, or price records a seller correction row",
    ],
  },
  {
    id: "journey-2-discovery-and-coarse-map",
    title: "Semantic Multilingual Discovery, Geohash-5 Coarse Map & Listing Detail",
    viewport: { width: 360, height: 800 },
    routes: ["/browse", "/listings/demo-listing-1"],
    assertions: [
      "Category, condition, listing type, and max price filters narrow displayed cards",
      "Map view renders Interactive Coarse Geohash-5 Cluster Map with <= 5 char geohash codes (tek3x, tek30, tek3y)",
      "OpenStreetMap contributors (ODbL) attribution is visible in map footer",
      "Listing detail page displays FairDealBadge, ADYPU Verified badge, and algorithmic price-drop card",
    ],
  },
  {
    id: "journey-3-chat-swap-and-impact",
    title: "Realtime Chat with Scam Safety Alerts, Algorithmic Multi-Party Swap & Cited LCA Impact",
    viewport: { width: 360, height: 800 },
    routes: ["/chat/demo-listing-1", "/swap", "/impact"],
    assertions: [
      "Chat thread displays Realtime Channel Active indicator and rule-based negotiation offer pills",
      "Typing an off-platform UPI QR or advance payment phrase triggers an immediate safety warning banner",
      "Swap dashboard explicitly labels CP-SAT <=3-way barter solver as Algorithmic (not ML)",
      "Impact dashboard displays cited LCA embodied CO2e ranges with displacement factor [0.30, 0.80]",
    ],
  },
  {
    id: "journey-4-moderation-and-active-learning",
    title: "Moderator Flag Queue, Audit Trail & Active Learning Model Governance",
    viewport: { width: 360, height: 800 },
    routes: ["/admin"],
    assertions: [
      "Moderator flag queue displays human-readable flag reason and evidence without auto-removal",
      "Uphold/dismiss moderation actions log an immutable audit_logs entry",
      "Active learning governance panel shows eligible corrections count and gated promotion status",
    ],
  },
];
