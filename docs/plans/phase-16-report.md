# Phase 16: Swap Engine & Impact Dashboard Completion Report

> **Date:** November 2026  
> **Status:** Completed  
> **Scope:** Algorithmic Multi-Party Swap Cycle Solver ($\le 3$-Way CP-SAT Set Packing vs. Greedy 2-Way Baseline), Multi-Party Proposal Confirmation & Per-Edge Handovers, Cited LCA Environmental Impact Estimator, Sensitivity Analysis, and Mobile-First Dashboards

---

## 1. Executive Summary

Phase 16 implements the algorithmic multi-party swap engine and environmental impact dashboard per `ROADMAP.md` Phase 16 and `ML_SPEC.md` §10 & §12:
1. **Database Schema & RLS (`apps/api/app/models/swap.py`, `apps/api/app/models/impact.py`, `apps/api/alembic/versions/0008_swap_and_impact.py`):**
   - Created `wishlists`, `swap_cycles`, `swap_proposals` (with `UNIQUE(cycle_id, giver_user_id)`), and `impact_events` tables with Row Level Security (`RLS`).
2. **Algorithmic Swap Engine (`ml/src/swap_engine.py`, `apps/api/app/services/swap_service.py`):**
   - Directed compatibility graph matching swap listings to user wishlists (`category` match + embedding cosine similarity $\ge \tau$ + relative value mismatch $\le \delta$).
   - Cycle enumeration for $k \in \{2, 3\}$ verifying that each user gives one item, receives one item, and stays within value tolerance $\delta$.
   - Vertex-disjoint cycle set-packing solver (`solve_swap_cycles_cpsat`) compared against `solve_swap_cycles_greedy_2way`.
   - All-party confirmation (`SwapService.confirm_proposal_and_check_cycle`): a cycle transitions to `confirmed` and generates per-edge handovers **only when all participants confirm**.
3. **Cited Environmental Impact Estimator & Methodology (`ml/data/impact_factors.csv`, `ml/src/impact_estimator.py`, `docs/IMPACT_METHOD.md`):**
   - Cataloged cited embodied carbon ($\text{kg CO}_2\text{e}$) and mass ($\text{kg}$) factors across Electronics, Furniture, Books, and Hobbies in `ml/data/impact_factors.csv`.
   - Reports range-based avoided emissions across displacement factor $d \in [0.30, 0.80]$ (central $d = 0.55$) and generates a 5-point sensitivity table ($d \in \{0.30, 0.45, 0.55, 0.70, 0.80\}$).
4. **API Routers & Mobile-First Pages (`apps/api/app/routers/swap.py`, `apps/api/app/routers/impact.py`, `apps/web/app/swap/page.tsx`, `apps/web/app/impact/page.tsx`):**
   - Implemented `POST /wishlists`, `GET /wishlists`, `GET /swap/proposals`, `POST /swap/proposals/{id}/confirm`, `GET /impact/me`, and `GET /impact/community`.
   - Explicitly labelled both features as **Algorithmic (Not ML)** in API responses and UI badges.
5. **Acceptance Testing (`apps/api/tests/test_swap_impact_acceptance.py`):**
   - All Phase 16 acceptance tests passed.
