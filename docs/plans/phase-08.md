# Phase 8: Product Recognition Model Implementation Plan

> **Goal:** Build and wire the product recognition pipeline per ROADMAP.md Phase 8 and ML_SPEC §2:
> 1. CLIP zero-shot baseline and trained linear probe / EfficientNet classifier architecture for the 4 core categories (`electronics`, `furniture`, `books`, `hobbies`) and ~20 campus subtypes.
> 2. Multi-photo embedding aggregation (average or max-pooling).
> 3. Dynamic confidence thresholding ($T_{\text{cat}} = 0.80$): if confidence is below threshold, flag `needs_confirmation` and return top-3 candidates.
> 4. Brand and model suggestion incorporating candidate brand lexicon and OCR text detection.
> 5. Wire the recognition engine directly into `/api/v1/ai/analyze-photos`.
> 6. Complete Model Card (`ml/model_cards/product_recognition.md`) documenting datasets, intended use, baseline vs improved metrics, ECE calibration, and limitations.
> 7. Automated acceptance tests for frozen test evaluations and ONNX parity.

---

### Tasks

| id | task | status | notes |
| :--- | :--- | :--- | :--- |
| p8-task-1 | Product recognition architecture, CLIP baseline & linear probe | in_progress | Supports 4 categories & subtypes |
| p8-task-2 | Multi-photo aggregation & brand/model extraction engine | not_started | Embedding pooling + OCR lexicon match |
| p8-task-3 | Wire real recognition engine into `/api/v1/ai/analyze-photos` | not_started | Replaces static stub with real inferencer |
| p8-task-4 | Formal Model Card (`ml/model_cards/product_recognition.md`) | not_started | Evaluated on frozen test set |
| p8-task-5 | Acceptance tests (top-1/top-5, ECE, confidence thresholding) | not_started | Phase 8 acceptance criteria |
