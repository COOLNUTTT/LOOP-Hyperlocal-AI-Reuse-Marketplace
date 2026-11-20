# Phase 4: Listings and Image Upload (with Stubbed AI) Implementation Plan

> **Goal:** Implement the full listings lifecycle: database schema with RLS and enums, CRUD & status transitions (draft -> active -> reserved -> completed), image upload with MIME/size validation & EXIF stripping, server-enforced scrubbed constraint (`LISTING_NOT_SCRUBBED`), schema-correct `/ai/analyze-photos` stub, seed script (`scripts/seed.py`), and the mobile-first frontend sell/create listing flow.

---

### Approved Architecture & Constraints

1. **Schema & Models:**
   - Enums: `listing_type` (`sell`, `donate`, `swap`), `listing_status` (`draft`, `active`, `reserved`, `completed`, `removed`), `category` (`electronics`, `furniture`, `books`, `hobbies`), `condition_grade` (`like_new`, `good`, `fair`, `poor`).
   - `listings` table with RLS enabled:
     - `id` (UUID PK), `seller_id` (FK `users.id`), `community_id` (FK `communities.id`, optional/nullable).
     - `type`, `category`, `subtype`, `brand`, `model`, `title`, `description`.
     - `condition` (`condition_grade`), `condition_ai`, `condition_conf` (float).
     - `price_ask`, `price_low`, `price_likely`, `price_high`, `price_ai_likely`, `fair_deal` (`great`, `fair`, `overpriced`).
     - `attributes` (JSONB), `area_name`, `geohash5` (<=5 chars), `status` (default `draft`).
     - `views`, `saves`, `created_at`, `completed_at`.
   - `listing_images` table with RLS enabled:
     - `id` (UUID PK), `listing_id` (FK `listings.id`), `storage_path`, `order`, `quality_score`, `scrub_boxes` (JSONB), `scrubbed` (bool default `false`), `phash`, `image_embedding`, `heatmap_path`.
   - Constraint: Cannot transition status to `active` (`/listings/{id}/publish`) unless **all** images associated with the listing have `scrubbed = true` and at least 1 image is attached. Returns HTTP 400 with code `LISTING_NOT_SCRUBBED`.

2. **Image Upload & Processing:**
   - Allowed MIME types: `image/jpeg`, `image/png`, `image/webp`.
   - Max file size: 10MB per image.
   - EXIF metadata stripping upon server receipt (re-encoded via PIL / pure byte processing) so GPS or device data is never retained in storage.

3. **AI Stub (`/api/v1/ai/analyze-photos`):**
   - Implements the exact schema from `DATA_MODEL_AND_API.md`:
     - `category`: `{ value, conf, top3 }`
     - `subtype`: string
     - `brand_model`: `{ brand, model }`
     - `condition`: `{ grade, conf, heatmap_url }`
     - `price`: `{ low, likely, high, reasons: [{ feature, effect }] }`
     - `draft`: `{ title, description }`
     - `needs_confirmation`: list of field strings if confidence < threshold.

4. **Frontend Sell Flow (`apps/web/app/sell/page.tsx`):**
   - Step 1: Photo selection & local preview.
   - Step 2: Quality & Privacy scrub simulation toggle (`scrubbed = true`).
   - Step 3: Trigger `/ai/analyze-photos` to autofill draft form.
   - Step 4: Review / edit category, title, condition, price.
   - Step 5: Publish listing with validation against unscrubbed images.

5. **Seed Script (`scripts/seed.py`):**
   - Generates simulated realistic listings (`data_origin='simulated'`) across the 4 categories (Electronics, Furniture, Books, Hobbies) for ADYPU community.

---

### Tasks

| id | task | status | notes |
| :--- | :--- | :--- | :--- |
| p4-task-1 | Listings & image models, Alembic migration 0002 with RLS | not_started | Enforce enums, RLS policies, geohash5 <= 5 |
| p4-task-2 | Image upload service with EXIF stripping & MIME/size validation | not_started | 10MB max, JPEG/PNG/WebP, strip GPS |
| p4-task-3 | Listings CRUD, status transitions & scrubbed-enforced publish | not_started | `LISTING_NOT_SCRUBBED` 400 error guard |
| p4-task-4 | Schema-correct `/ai/analyze-photos` stub | not_started | Match DATA_MODEL_AND_API §3 schema |
| p4-task-5 | `scripts/seed.py` database seeder | not_started | Realistic items with `data_origin='simulated'` |
| p4-task-6 | Mobile-first sell flow page (`/sell`) in Next.js web app | not_started | Multi-step photo -> AI draft -> edit -> publish |
| p4-task-7 | Full verification, test suite & acceptance report | not_started | Phase 4 acceptance criteria |
