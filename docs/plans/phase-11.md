# Phase 11: Snap-to-List Integration (M1 Vertical Slice) Implementation Plan

> **Goal:** Connect and verify the complete end-to-end Snap-to-List vertical slice (photo → on-device quality check → privacy scrub → AI draft generation → seller review & edit → publish → discovery browse) per `ROADMAP.md` Phase 11 and `DATA_MODEL_AND_API.md`:
> 1. Complete end-to-end `/ai/analyze-photos` pipeline combining product recognition, condition grading with Grad-CAM heatmap, split-conformal pricing with SHAP reasons, smart autofill attributes, and templated draft content.
> 2. Database model and Alembic migration `0004_corrections` for the `corrections` table (`id`, `listing_id`, `user_id`, `field`, `ai_value`, `user_value`, `ai_confidence`, `model_version`, `eligible_for_training`, `data_origin`, `created_at`).
> 3. Automatic correction logging on `PATCH /listings/{id}` and `/listings` when the seller edits any AI-inferred field (category, subtype, condition, or price).
> 4. Anti-poisoning eligibility filtering for training: `eligible_for_training = true` only when user is verified with completed trades or within median MAD bounds.
> 5. Smart autofill templates for specifications, defects, and attributes based on category, subtype, and condition.
> 6. Seller listing duration telemetry with client-side start/submit timestamps (`client_listing_duration_ms`).
> 7. Mobile-first `/sell` page update with full M1 vertical slice workflow, low-confidence warning prompts, and automatic correction submission.
> 8. End-to-end acceptance tests verifying the complete vertical slice and correction table ingestion.

---

### Tasks

| id | task | status | notes |
| :--- | :--- | :--- | :--- |
| p11-task-1 | Database model & Alembic migration `0004_corrections` with RLS | completed | Schema-exact `corrections` table with training eligibility |
| p11-task-2 | Correction service & auto-logging on listing edits | completed | Record delta between AI suggestions and user inputs |
| p11-task-3 | Smart autofill generator & enhanced `/ai/analyze-photos` | completed | Attributes, specs, templates & p95 latency measurement |
| p11-task-4 | Mobile-first `/sell` UX update with telemetry & low-conf prompts | completed | Full slice: photo → quality → scrub → review → publish |
| p11-task-5 | Full acceptance & E2E tests for M1 Snap-to-List slice | completed | End-to-end slice, correction logging, latency benchmark |
