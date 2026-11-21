# Phase 20 (Track C): Live Supabase Client Wiring, Interactive Coarse Area Map, Playwright E2E Suite & Locust Load Testing Completion Report

> **Date:** November 2026  
> **Status:** Completed  
> **Scope:** Supabase Auth/Storage/Realtime Client (`apps/web/lib/supabaseClient.ts`), Live Chat Scam Safety Warnings (`apps/web/app/chat/[listingId]/page.tsx`), Interactive Coarse Geohash-5 Map Component (`apps/web/components/CoarseAreaMap.tsx`), Playwright 360px E2E Suite (`apps/web/playwright.config.ts`, `apps/web/e2e/loop-journeys.spec.ts`), Locust Load Harness (`infra/load/locustfile.py`), and Acceptance Tests (`apps/api/tests/test_phase20_hardening_and_e2e.py`)

---

## 1. Executive Summary

Phase 20 completes frontend-backend integration hardening, interactive geohash-5 map visualization, 360px mobile E2E specifications, and load-testing infrastructure:

1. **Supabase Client & In-Chat Scam Safety Warnings (`apps/web/lib/supabaseClient.ts`, `apps/web/app/chat/[listingId]/page.tsx`):**
   - `uploadScrubbedListingImage` enforces a hard client-side `LISTING_NOT_SCRUBBED` guard before uploading to Supabase Storage (`listing-images` bucket).
   - `subscribeToListingChat` connects to Supabase Realtime WebSocket channels (`realtime:public:messages`) when configured and syncs locally via `BroadcastChannel`.
   - `evaluateChatSafetyWarning` detects off-platform scam patterns (`scan qr`, `upi qr`, `advance payment`, `whatsapp`, `send otp`) and renders an immediate warning banner in the chat UI.
2. **Interactive Coarse Geohash-5 Map (`apps/web/components/CoarseAreaMap.tsx`, `apps/web/app/browse/page.tsx`):**
   - Renders zoomable (`11x`–`14x`) ~5 km $\times$ 5 km geohash-5 campus clusters (`Lohegaon / Charholi [tek3x]`, `Wakad / Hinjawadi [tek30]`, `Viman Nagar [tek3y]`) with `sanitizeGeohash5` ($\le 5$ characters) and required `© OpenStreetMap contributors (ODbL)` attribution (`IP_AND_COMPLIANCE.md` §4).
3. **Playwright 360px E2E Suite & Locust Load Testing (`apps/web/playwright.config.ts`, `apps/web/e2e/loop-journeys.spec.ts`, `infra/load/locustfile.py`):**
   - Configured Playwright for a `360x800` mobile viewport (`mobile-360px`) covering the 4 core marketplace & moderation journeys.
   - Created `infra/load/locustfile.py` (`LOOPMarketplaceUser`) load-testing the semantic discovery, conformal pricing, Snap-to-List ONNX analysis, ONNX health, and CP-SAT swap endpoints under the `p95 < 1000 ms` target.
