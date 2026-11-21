# Phase 20 (Track C): Live Supabase Client Wiring, Interactive Coarse Area Map, Playwright E2E Suite & Locust Load Testing Plan

> **Goal:** Complete Track C by wiring the Next.js frontend to live Supabase Auth/Storage/Realtime (`apps/web/lib/supabaseClient.ts`) with in-chat scam safety alerts, upgrading `/browse` with an interactive zoomable geohash-5 Coarse Area Map component (`apps/web/components/CoarseAreaMap.tsx`) with OpenStreetMap ODbL attribution (`IP_AND_COMPLIANCE.md` §4), adding the 360px mobile-first Playwright E2E test suite (`apps/web/playwright.config.ts`, `apps/web/e2e/loop-journeys.spec.ts`), and adding the Locust load-testing harness (`infra/load/locustfile.py`) per `AGENTS.md` §§3, 7 and `ROADMAP.md` Phases 5, 6, 11, 13, 18.

---

## 1. Architecture & Scope

1. **Live Supabase Auth, Storage & Realtime Client (`apps/web/lib/supabaseClient.ts` & `apps/web/app/chat/[listingId]/page.tsx`):**
   - Read `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, and `NEXT_PUBLIC_API_URL` from environment configuration.
   - Implement `uploadScrubbedListingImage` with a hard client-side guard that throws `LISTING_NOT_SCRUBBED` if `isScrubbed !== true` before uploading to Supabase Storage (`listing-images` bucket).
   - Implement `subscribeToListingChat(listingId, onMessage)` using Supabase Realtime WebSocket channels (`realtime:public:messages:listing_id=eq.<id>`) when configured, with automatic `BroadcastChannel` local real-time sync in offline/CI environments.
   - Enhance `apps/web/app/chat/[listingId]/page.tsx` with live subscription wiring and real-time scam-keyword safety warnings (`UPI QR`, `advance payment`, `WhatsApp`, `OTP`) per `ROADMAP.md` Phase 13.

2. **Interactive Coarse Area Map Component (`apps/web/components/CoarseAreaMap.tsx` & `apps/web/app/browse/page.tsx`):**
   - Build an interactive, zoomable (`11x`–`14x`) and pannable coarse neighbourhood map component rendering ~5 km $\times$ 5 km geohash-5 coverage zones (`Lohegaon / Charholi [tek3x]`, `Wakad / Hinjawadi [tek30]`, `Viman Nagar [tek3y]`), interactive area cluster markers, distance radius rings, and OpenStreetMap (`© OpenStreetMap contributors, ODbL`) attribution.
   - Enforce geohash precision $\le 5$ so exact street coordinates can never be rendered.
   - Log OpenStreetMap (`ODbL`) attribution and `@playwright/test` (`Apache-2.0`) / `locust` (`MIT`) in `THIRD_PARTY_LICENSES.md`.

3. **Playwright 360px Mobile-First E2E Test Suite (`apps/web/playwright.config.ts`, `apps/web/e2e/loop-journeys.spec.ts`):**
   - Configure Playwright with a `360x800` mobile viewport (`AGENTS.md` §7) and desktop profile.
   - Implement E2E specs verifying the 4 core journeys:
     1. Snap-to-List (`/sell`: photo upload $\rightarrow$ on-device ONNX quality & privacy scrubber $\rightarrow$ AI draft review $\rightarrow$ seller correction $\rightarrow$ publish).
     2. Discovery & Coarse Map (`/browse`: category/price filters, Hinglish search, interactive geohash-5 map toggle, `/listings/[id]`).
     3. Realtime Chat with Safety Banner, Algorithmic Multi-Party Swap & Cited LCA Impact (`/chat/[listingId]`, `/swap`, `/impact`).
     4. Moderator Flag Queue & Active Learning Governance (`/admin`).

4. **Locust Load Test Suite (`infra/load/locustfile.py`):**
   - Implement `LOOPMarketplaceUser` locust load profile targeting `/api/v1/health`, `/api/v1/listings`, `/api/v1/ai/analyze-photos`, `/api/v1/ai/price-estimate`, `/api/v1/ai/onnx-status`, and `/api/v1/swap/cycles` with p50/p95 latency event hooks.

5. **Acceptance Tests (`apps/api/tests/test_phase20_hardening_and_e2e.py`):**
   - Verify all Phase 20 artifacts, geohash-5 privacy constraints, Supabase client guards, Playwright E2E spec coverage, Locust load profile validity, and licence/header compliance.

---

## 2. Task Breakdown

| id | task | status | notes |
| :--- | :--- | :--- | :--- |
| p20-task-1 | Log OpenStreetMap (`ODbL`), `@playwright/test` (`Apache-2.0`), and `locust` (`MIT`) in `THIRD_PARTY_LICENSES.md` | completed | All permissive licences logged before use |
| p20-task-2 | Implement `apps/web/lib/supabaseClient.ts` and wire `apps/web/app/chat/[listingId]/page.tsx` with Realtime + scam safety alerts | completed | Enforces `isScrubbed` upload guard + live chat warnings |
| p20-task-3 | Build interactive `apps/web/components/CoarseAreaMap.tsx` (geohash-5 zones, zoom/pan, ODbL attribution) & wire into `/browse` | completed | Strictly `geohash5.length <= 5`, zero exact pins |
| p20-task-4 | Add `apps/web/playwright.config.ts` (360px viewport), `apps/web/e2e/loop-journeys.spec.ts`, and `infra/load/locustfile.py` | completed | Covers all 3 main journeys + moderation + load test |
| p20-task-5 | Write `apps/api/tests/test_phase20_hardening_and_e2e.py`, run full test/lint/licence audits, and write `phase-20-report.md` | completed | All 5 Phase 20 acceptance tests + ruff + audits passed |
