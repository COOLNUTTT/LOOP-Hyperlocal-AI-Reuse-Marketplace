# Phase 4 Acceptance & Verification Report

**Date:** 2026-11-21  
**Phase:** Phase 4 – Listings and Image Upload (with Stubbed AI)  
**Status:** **PASSED**

---

## 1. Roadmap Acceptance Checks

| Criteria | Implementation & Evidence | Result |
| :--- | :--- | :---: |
| **Valid image accepted, invalid rejected with a clear message** | Implemented in `ImageProcessingService` (`apps/api/app/services/image_service.py`). Enforces MIME type check (`image/jpeg`, `image/png`, `image/webp`) and 10MB size ceiling. Tested in `apps/api/tests/test_listings_acceptance.py`. | **PASS** |
| **Unscrubbed publish returns `LISTING_NOT_SCRUBBED`** | Guard implemented in `ListingService.publish_listing` and validated in acceptance tests; prevents publishing active listings until all attached photos have `scrubbed = True`. | **PASS** |
| **Listing persists across API restarts & state transitions** | Modeled via SQLAlchemy in `apps/api/app/models/listing.py` (`listings` and `listing_images` tables) and managed via Alembic migration `0002_listings_and_images.py` with PostgreSQL Row Level Security (RLS). | **PASS** |
| **Edits to AI fields are saved** | `PATCH /api/v1/listings/{id}` supports partial updates of category, subtype, condition, and pricing fields. | **PASS** |
| **AI Stub endpoint available** | Schema-compliant `/api/v1/ai/analyze-photos` implemented per `DATA_MODEL_AND_API.md §3` with confidence, top-3 categories, condition, and price intervals. | **PASS** |
| **Simulated seed data ready** | `scripts/seed.py` created with listings spanning Electronics, Furniture, Books, and Hobbies, explicitly tagged with `data_origin='simulated'`. | **PASS** |
| **Mobile-first sell flow implemented** | Multi-stage `/sell` flow built in Next.js (`apps/web/app/sell/page.tsx`): photo upload → privacy scrub check → AI analysis → edit draft → publish. | **PASS** |

---

## 2. Deliverables Summary

- **Backend (`apps/api`):**
  - Models: `app/models/listing.py` (`Listing`, `ListingImage`, Enums).
  - Migration: `alembic/versions/0002_listings_and_images.py`.
  - Services: `app/services/image_service.py` (EXIF stripping and validation), `app/services/listing_service.py` (CRUD & publishing rules).
  - Routers: `app/routers/listings.py`, `app/routers/ai.py`.
  - Dependencies: `app/dependencies/database.py`.
  - Acceptance tests: `apps/api/tests/test_listings_acceptance.py`.
- **Frontend (`apps/web`):**
  - `app/sell/page.tsx`: Complete mobile-first sell page with on-device privacy scrub toggle and AI draft review.
  - `app/layout.tsx`: "Sell Item" header button and quick links.
- **Seeding (`scripts`):**
  - `scripts/seed.py`: Realistic item generator tagged with `data_origin='simulated'`.
