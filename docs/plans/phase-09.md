# Phase 9: Condition Grader with Grad-CAM Implementation Plan

> **Goal:** Build the condition grading pipeline per ROADMAP.md Phase 9 and ML_SPEC §3:
> 1. Baseline plain-CNN vs improved Ordinal Model (CORAL / cumulative-link regression with rounding) for ordinal grades: `poor` (0), `fair` (1), `good` (2), `like_new` (3).
> 2. Grad-CAM visual explainability heatmap generator highlighting detected cosmetic wear, scratches, and flaws.
> 3. Grad-CAM endpoint and overlay in UI: heatmap displays over the item photo, is toggleable/dismissible, and includes the required limitation notice (*"Some internal or functional defects cannot be detected visually; condition is editable by seller"*).
> 4. Human annotator agreement baseline (Quadratic Weighted Kappa ceiling).
> 5. Formal Model Card (`ml/model_cards/condition_grader.md`) reporting QWK, accuracy, MAE, confusion matrix, and 50-image heatmap sanity check results.
> 6. Automated acceptance tests for ordinal scoring, Grad-CAM generation, and threshold stability.

---

### Tasks

| id | task | status | notes |
| :--- | :--- | :--- | :--- |
| p9-task-1 | Ordinal condition grading engine (0..3) with expected-value scoring | in_progress | Evaluates poor, fair, good, like_new |
| p9-task-2 | Grad-CAM explainability heatmap generator | not_started | Visual wear/scratch localization |
| p9-task-3 | Interactive Grad-CAM overlay component with dismiss & limitation text | not_started | Toggleable overlay in sell & detail flows |
| p9-task-4 | Formal Model Card (`ml/model_cards/condition_grader.md`) | not_started | QWK, MAE, confusion matrix, sanity checks |
| p9-task-5 | Acceptance tests (QWK, ordinal consistency, heatmap generation) | not_started | Phase 9 acceptance criteria |
