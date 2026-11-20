# Phase 5: Discovery: Browse, Filters, Geo-Search, Map Implementation Plan

> **Goal:** Implement the complete discovery journey for listings: category browsing, multi-criteria filtering (category, type: sell/donate/swap, condition, price range, distance/coarse area), pagination, map view with area-level coarse markers, listing detail page with the fair-deal badge and price breakdown, and automated filter/geo acceptance tests.

---

### Approved Architecture & Constraints

1. **Backend Filtering & Discovery API (`GET /api/v1/listings`):**
   - Query Parameters:
     - `q`: string search across title and description.
     - `category`: `electronics | furniture | books | hobbies`.
     - `type`: `sell | donate | swap`.
     - `condition`: `like_new | good | fair | poor`.
     - `price_min`, `price_max`: numeric range.
     - `area_name` or `geohash5`: coarse area search.
     - `limit`, `offset`: pagination controls (default limit 20, max 100).
   - Only returns listings in `status = 'active'`.
   - Returns total count, paginated listings, and applied filters summary.

2. **Fair-Deal Badge Logic:**
   - Evaluates listing ask price relative to estimated fair market likely price:
     - `ask <= likely * 0.85` or `type == 'donate'` -> **Great Deal** (green badge).
     - `likely * 0.85 < ask <= likely * 1.15` -> **Fair Deal** (slate/blue badge).
     - `ask > likely * 1.15` -> **Overpriced / Above Market** (amber/orange badge).

3. **Frontend Discovery & Browse Pages (`apps/web`):**
   - `/browse` (or `/explore`):
     - Filter sidebar & mobile filter drawer (Category, Type, Condition, Price Slider/Inputs, Coarse Area).
     - Results grid with image thumbnails, price, condition, coarse locality, and fair-deal badges.
     - Toggle between **Grid View** and **Map View**.
     - Map View uses coarse, neighbourhood-level points (e.g. Lohegaon / Charholi, Wakad, Viman Nagar) with zero exact addresses.
   - `/listings/[id]`:
     - Clean, responsive detail page.
     - Photo carousel/gallery.
     - Prominent Fair-Deal badge with price range explainability card.
     - Seller info with `VerifiedBadge` and coarse locality.
     - Action buttons: "Chat with Seller" (prepares Phase 6), "Propose Swap" (prepares Phase 16).

---

### Tasks

| id | task | status | notes |
| :--- | :--- | :--- | :--- |
| p5-task-1 | Discovery query service with filters, pagination & fair-deal evaluation | in_progress | Supports q, category, type, condition, price, geohash |
| p5-task-2 | API endpoint `GET /listings` and `GET /listings/{id}` enhancement | not_started | Eager load images and seller community badge |
| p5-task-3 | Fair-deal badge UI component with price explainability | not_started | Great / Fair / Overpriced badge states |
| p5-task-4 | Mobile-first Browse page with filter drawer & coarse Map View toggle | not_started | Responsive at 360px viewport |
| p5-task-5 | Listing Detail Page (`/listings/[id]`) with image gallery & seller card | not_started | Integrates FairDealBadge and VerifiedBadge |
| p5-task-6 | Full acceptance tests for filter combinations & geo privacy | not_started | Measure load and verify area-level coarse points |
