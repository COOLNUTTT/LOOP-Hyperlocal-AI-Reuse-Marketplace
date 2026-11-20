# Phase 13: Handover, Reviews & Trust Score Implementation Plan

> **Goal:** Implement safe peer handover, OTP/QR confirmation, gated reviews, transparent trust score breakdown, chat-safety warnings, and rule-based negotiation helper per `ROADMAP.md` Phase 13:
> 1. Database models (`HandoverEvent`, `Review`) and Alembic migration `0006_handover_and_reviews` with Row Level Security (RLS).
> 2. Handover service (`apps/api/app/services/handover_service.py`) with curated public meetup-point suggestions, OTP generation with expiry & attempt limits (max 5), and both-sides confirmation transitioning listing status to `completed`.
> 3. Reviews & Trust Score service (`apps/api/app/services/trust_service.py`) gating reviews on completed handovers (returning `403` otherwise) and computing a transparent, additive trust score breakdown.
> 4. Chat-safety keyword warnings and rule-based negotiation helper (`apps/api/app/services/safety_helper.py`).
> 5. Handover & Review API router (`apps/api/app/routers/handover.py`).
> 6. Automated acceptance tests verifying both-sides confirmation, OTP expiry/rate-limiting, 403 review gate, trust score breakdown sum, and chat safety/negotiation.

---

### Tasks

| id | task | status | notes |
| :--- | :--- | :--- | :--- |
| p13-task-1 | `HandoverEvent` & `Review` models + migration `0006_handover_and_reviews` | completed | RLS for buyer/seller participants |
| p13-task-2 | Handover service (meetup spots, OTP expiry/attempts, both-sides confirm) | completed | Transitions listing to `completed` only after both confirm |
| p13-task-3 | Gated reviews & transparent trust score breakdown | completed | 403 if handover not completed; additive score breakdown |
| p13-task-4 | Chat-safety warnings, negotiation helper & handover router | completed | Scam keyword rules + price-range negotiation tips |
| p13-task-5 | Acceptance tests & Phase 13 completion report | completed | Verify all Phase 13 acceptance criteria |
