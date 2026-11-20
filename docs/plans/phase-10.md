# Phase 10: Price Estimator and Fair-Deal Badge Implementation Plan

> **Goal:** Build the price estimation and valuation explainability pipeline per ROADMAP.md Phase 10 and ML_SPEC §4:
> 1. LightGBM quantile regression ($q=0.10, 0.50, 0.90$) + Split-Conformal Calibration guaranteeing nominal 80% coverage intervals `[price_low, price_high]`.
> 2. Baselines comparison: category median, linear regression, and random forest.
> 3. SHAP local explainability: plain-language top-3 feature contribution explanations (e.g. *"Brand 'Casio' and pristine condition raised the estimate by ₹150"*).
> 4. Fallback widening and "low confidence" flagging for rare or unknown subtypes.
> 5. Seller guidance alert when asking price significantly exceeds the upper conformal bound.
> 6. Model Card (`ml/model_cards/price_estimator.md`) detailing MAE, MAPE, median APE, interval coverage (80% target), width, and category breakdowns.
> 7. Automated acceptance tests for conformal coverage, SHAP extraction, boundary badge classification, and fallback interval widening.

---

### Tasks

| id | task | status | notes |
| :--- | :--- | :--- | :--- |
| p10-task-1 | Price estimation engine with split-conformal calibration & SHAP | in_progress | Predicts low, likely, high & plain-language reasons |
| p10-task-2 | Dedicated price estimation endpoint `POST /api/v1/ai/price-estimate` | not_started | Standalone valuation API |
| p10-task-3 | Seller pricing guidance & above-market warning UI in `/sell` flow | not_started | Alert when ask > 1.25x likely |
| p10-task-4 | Formal Model Card (`ml/model_cards/price_estimator.md`) | not_started | MAE, MAPE, conformal coverage vs baselines |
| p10-task-5 | Acceptance tests (conformal coverage, SHAP reasons, boundary unit tests) | not_started | Phase 10 acceptance criteria |
