# Phase 17: Marketplace Simulator & Price-Drop Suggestions Completion Report

> **Date:** November 2026  
> **Status:** Completed (Completes Milestone **M3: Research Features**)  
> **Scope:** Discrete-Time Agent-Based Marketplace Simulator (`sim/`), 6 Scale & Resilience Experiments ($N = 100 \rightarrow 10,000$), $\pm 50\%$ Behavioural Sensitivity Analysis, Hazard-Style Price-Drop Heuristic with Hard Floor & 15%-Step Guardrails, and Seller Listing UI Card

---

## 1. Executive Summary

Phase 17 implements the agent-based marketplace simulator and dynamic price-drop heuristic per `ROADMAP.md` Phase 17 and `ML_SPEC.md` §9 & §11:
1. **Database Schema & RLS (`apps/api/app/models/price_drop.py`, `apps/api/alembic/versions/0009_price_drop_and_history.py`):**
   - Created `price_drop_suggestions` and `price_history` tables with Row Level Security (`RLS`).
2. **Hazard-Style Price-Drop Heuristic (`ml/src/price_drop.py`):**
   - Estimates $P(\text{sale} \le 7\text{d} \mid \text{age, views, saves, chats, price\_ratio})$.
   - Enforces hard safety invariants:
     1. **Floor Guardrail:** Never suggests below `max(0.60 * predicted_low, explicit_floor)`.
     2. **Step-Size Guardrail:** Never suggests a drop larger than `15%` in a single step (`suggested_price >= 0.85 * price_ask`).
3. **Agent-Based Marketplace Simulator (`sim/configs/default.yaml`, `sim/simulator.py`, `ml/reports/simulator/`):**
   - Single-seed deterministic simulation (`same seed -> identical results`) with `student`, `family`, `donor`, `reseller`, and `scammer` agents, flagging all outputs `data_origin='simulated'`.
   - Executed all 6 experiments (`swap_scaling` $100 \rightarrow 10,000$ users, 2- vs 3-cycle gain, `trust_score_resilience` under fake-review rings, `fraud_detection_scale` across $p_{\text{fraud}} \in \{0.02, 0.05, 0.10, 0.20\}$, `price_drop_comparison` vs `no_drop` and `fixed_schedule`, and `cold_start`) plus $\pm 50\%$ behavioural sensitivity analysis.
   - Generated `ml/reports/simulator/simulator_figures_synthetic.svg` (all panels captioned `"Synthetic (data_origin='simulated')"`) and `ml/reports/simulator/report.md` with the explicit buyer-demand circularity limitation.
4. **API Endpoint & Seller Listing UI Card (`apps/api/app/routers/ai.py`, `apps/web/components/PriceDropSuggestionCard.tsx`, `apps/web/app/listings/[id]/page.tsx`):**
   - Added `POST /api/v1/ai/price-drop/{listing_id}` and integrated `PriceDropSuggestionCard` on listing detail pages, explicitly labelled **Algorithmic Hazard Heuristic (Not ML)**.
5. **Acceptance Testing (`apps/api/tests/test_simulator_pricedrop_acceptance.py`):**
   - All Phase 17 acceptance tests passed.
