# Phase 16: Swap Engine & Impact Dashboard Implementation Plan

> **Goal:** Implement the algorithmic multi-party swap engine (wishlists, directed compatibility graph builder, cycle enumeration $\le 3$ + vertex-disjoint set-packing solver vs. greedy 2-way baseline, multi-party proposal confirmation & per-edge handovers) and the cited environmental impact estimator (`ml/data/impact_factors.csv`, range estimation, sensitivity analysis, `docs/IMPACT_METHOD.md`, and `/impact` endpoints/UI) per `ROADMAP.md` Phase 16 and `ML_SPEC.md` §10 & §12:
> 1. Database Models & Alembic Migration `0008_swap_and_impact.py` (`apps/api/app/models/swap.py`, `apps/api/app/models/impact.py`):
>    - `wishlists`, `swap_cycles`, `swap_proposals` (with `UNIQUE(cycle_id, giver_user_id)`), and `impact_events` tables with Row Level Security (`RLS`).
> 2. Algorithmic Swap Engine (`ml/src/swap_engine.py`, `apps/api/app/services/swap_service.py`):
>    - Directed compatibility graph builder matching seller's swap listing to another user's wishlist (`category` match + embedding cosine similarity $\ge \tau$ + value mismatch within tolerance $\delta$).
>    - Cycle enumeration for lengths $k \in \{2, 3\}$ and maximum-weight vertex-disjoint cycle packing solver (CP-SAT / exact branch-and-bound set packing) maximising matched users, plus a `greedy_2way` baseline solver for comparison.
>    - Multi-party confirmation logic: a cycle transitions from `proposed` $\rightarrow$ `partially_confirmed` $\rightarrow$ `confirmed` **only when all participants confirm**, generating per-edge handover records upon full confirmation.
> 3. Algorithmic Impact Estimator & Methodology (`ml/data/impact_factors.csv`, `ml/src/impact_estimator.py`, `docs/IMPACT_METHOD.md`):
>    - Cited factor table (`ml/data/impact_factors.csv`) with `category`, `subtype`, `embodied_co2_kg`, `weight_kg`, `source`, `year`, `confidence`.
>    - Range-based avoided emissions ($\text{embodied\_CO}_2 \times d$ for displacement factor $d \in [0.3, 0.8]$, central $d = 0.55$) and sensitivity analysis table across $d \in \{0.30, 0.45, 0.55, 0.70, 0.80\}$.
> 4. API Routers & Mobile-First UI (`apps/api/app/routers/swap.py`, `apps/api/app/routers/impact.py`, `apps/web/app/swap/page.tsx`, `apps/web/app/impact/page.tsx`):
>    - `POST /wishlists`, `GET /wishlists`, `GET /swap/proposals`, `POST /swap/proposals/{id}/confirm`.
>    - `GET /impact/me` and `GET /impact/community`.
>    - Mobile-first (`360px` responsive) `/swap` and `/impact` pages explicitly labelling both features as **Algorithmic (Rule-Based / Graph Optimization — Not ML)** per Non-Negotiable Principle #3.
> 5. Automated Acceptance Tests (`apps/api/tests/test_swap_impact_acceptance.py`), Phase 16 Completion Report (`docs/plans/phase-16-report.md`), and full CI verification.

---

### Tasks

| id | task | status | notes |
| :--- | :--- | :--- | :--- |
| p16-task-1 | `Wishlist`, `SwapCycle`, `SwapProposal`, `ImpactEvent` models & migration `0008_swap_and_impact` | completed | RLS enabled on all 4 tables |
| p16-task-2 | Algorithmic swap graph builder, $\le 3$-cycle set-packing solver, greedy 2-way baseline & all-party confirmation | completed | Per-edge value tolerance & handovers |
| p16-task-3 | Cited `ml/data/impact_factors.csv`, impact range & sensitivity engine, and `docs/IMPACT_METHOD.md` | completed | Traceable LCA citations & sensitivity table |
| p16-task-4 | Swap & Impact API routers (`/wishlists`, `/swap/*`, `/impact/*`) and Next.js `/swap` & `/impact` pages | completed | Explicitly labelled Algorithmic in UI & API |
| p16-task-5 | Acceptance tests, Phase 16 completion report & full CI pipeline verification | completed | All Phase 16 acceptance criteria passed |
