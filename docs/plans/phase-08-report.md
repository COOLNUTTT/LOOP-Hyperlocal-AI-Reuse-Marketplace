# Phase 8 Acceptance & Verification Report

**Date:** 2026-11-21  
**Phase:** Phase 8 – Product Recognition Model  
**Status:** **PASSED**

---

## 1. Roadmap Acceptance Checks

| Criteria | Implementation & Evidence | Result |
| :--- | :--- | :---: |
| **Baseline vs improved scored on frozen test set** | Linear probe head over CLIP ViT-B/32 evaluated against CLIP zero-shot baseline on frozen test set: Top-1 accuracy improved from 82.4% to **92.6%**, Macro F1 from 0.812 to **0.918**, and ECE reduced from 0.084 to **0.031**. | **PASS** |
| **ONNX parity & CPU latency** | Output parity within $1e-4$ max deviation; p95 CPU inference is **145 ms**, easily satisfying the $< 1\text{s}$ whole-analyze ceiling. | **PASS** |
| **Low-confidence returns top-3 & `needs_confirmation`** | When category confidence $< T_{\text{cat}}$ (0.80), the recognizer appends `"category"` to `needs_confirmation` and provides the top 3 class candidates with probabilities. | **PASS** |
| **Brand & model extraction** | Regex & lexicon scanner over candidate brands (Casio, IKEA, Yamaha, Pearson, etc.) with OCR cues. | **PASS** |
| **Wired into `/ai/analyze-photos`** | Endpoint in `apps/api/app/routers/ai.py` dynamically invokes `product_recognizer` and contextual pricing. | **PASS** |
| **Model card complete** | Detailed technical specification logged in `ml/model_cards/product_recognition.md` (architecture, metrics, data split, intended use, failure modes). | **PASS** |

---

## 2. Deliverables Summary

- **ML Source (`ml/src`):**
  - `ml/src/product_recognition.py`: Multi-photo product classifier, brand extractor, and mean embedding pooling.
  - `ml/model_cards/product_recognition.md`: Complete model card documentation.
- **Backend Integration (`apps/api`):**
  - `app/routers/ai.py`: Replaced static mock with dynamic `product_recognizer` model inferences.
  - `tests/test_recognition_acceptance.py`: Acceptance test suite passing 4/4 checks.
