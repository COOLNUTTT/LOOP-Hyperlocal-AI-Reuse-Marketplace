# Phase 17: Marketplace Simulator & Price-Drop Suggestions Implementation Plan

> **Goal:** Implement the agent-based marketplace simulator (`sim/`) with deterministic single-seed reproducibility, run the 6 scale & resilience experiments ($100 \rightarrow 10,000$ users, 2- vs 3-cycle swap gain, trust-score AUC & fake-review ring resilience, fraud PR vs `p_fraud`, cold-start heatmap, and $\pm 50\%$ behavioural sensitivity analysis), and build the hazard-style price-drop suggestion heuristic with strict floor ($\ge 0.60 \times \text{predicted\_low}$) and step ($\le 15\%$ max drop per step) guardrails, database migration, API endpoint, and seller UI card per `ROADMAP.md` Phase 17 and `ML_SPEC.md` §9 & §11:
> 1. Database Models & Alembic Migration `0009_price_drop_and_history.py` (`apps/api/app/models/price_drop.py`):
>    - `price_drop_suggestions` and `price_history` tables with Row Level Security (`RLS`).
> 2. Hazard-Style Price-Drop Heuristic (`ml/src/price_drop.py`):
>    - Estimates $P(\text{sale} \le 7\text{d} \mid \text{age, views, saves, chats, price\_ratio})$.
>    - Enforces hard invariants:
>      1. **Never below floor:** $\text{suggested\_price} \ge \text{floor}$ (default $\max(0.60 \times \text{price\_low}, 0.50 \times \text{price\_ask})$).
>      2. **Never beyond 15% per step:** $\text{suggested\_price} \ge 0.85 \times \text{price\_ask}$ (if $0.85 \times \text{price\_ask} > \text{floor}$; when current ask is already at or below floor, no drop is suggested).
> 3. Agent-Based Marketplace Simulator (`sim/configs/default.yaml`, `sim/simulator.py`, `sim/experiments.py`):
>    - Discrete-time agent simulator with `student`, `family`, `donor`, `scammer` (fraction `p_fraud`), and `reseller` agents; all randomness derived from a single `seed` (`same seed -> identical results`); every output flagged `data_origin='simulated'`.
>    - Executes all 6 experiments + $\pm 50\%$ parameter sensitivity analysis and generates `ml/reports/simulator/simulator_results_synthetic.json`, `ml/reports/simulator/simulator_figures_synthetic.svg` (all panels captioned `"Synthetic (data_origin='simulated')"`), and `ml/reports/simulator/report.md` (including explicit limitation on assumed buyer demand circularity).
> 4. Price-Drop API & Seller Listing UI Card (`apps/api/app/routers/ai.py`, `apps/web/components/PriceDropSuggestionCard.tsx`, `apps/web/app/listings/[id]/page.tsx`):
>    - `POST /api/v1/ai/price-drop/{listing_id}` endpoint returning suggestion, $P_{\text{before}}$, $P_{\text{after}}$, plain-language reason, and guardrail bounds.
>    - Responsive `PriceDropSuggestionCard` component displayed on listing detail pages, explicitly labelled **Algorithmic Hazard Heuristic (Not ML)**.
> 5. Automated Acceptance Tests (`apps/api/tests/test_simulator_pricedrop_acceptance.py`), Phase 17 Completion Report (`docs/plans/phase-17-report.md`), and full CI verification.

---

### Tasks

| id | task | status | notes |
| :--- | :--- | :--- | :--- |
| p17-task-1 | `PriceDropSuggestion` & `PriceHistory` models + migration `0009_price_drop_and_history` | completed | RLS enabled on both tables |
| p17-task-2 | Hazard-style price-drop heuristic (`ml/src/price_drop.py`) with floor & 15%-step guardrails | completed | Never below floor or >15% drop per step |
| p17-task-3 | Agent-based marketplace simulator (`sim/`), 6 experiments, $\pm 50\%$ sensitivity & synthetic SVG figures | completed | Same seed -> identical results; captioned synthetic |
| p17-task-4 | `POST /ai/price-drop/{listing_id}` endpoint & `PriceDropSuggestionCard` on seller listing UI | completed | Labelled Algorithmic Hazard Heuristic |
| p17-task-5 | Acceptance tests, Phase 17 completion report & full CI pipeline verification | completed | All Phase 17 acceptance criteria passed |
