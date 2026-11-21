# Phase 19 (Track A): Real Trained ONNX Weights, Training Notebooks & Browser/API Runtime Wiring Plan

> **Goal:** Complete Track A by replacing pure-Python heuristic stubs with real exported `.onnx` computation graphs (`ml/exports/*.onnx`), reproducible Colab/Kaggle GPU training notebooks (`ml/notebooks/*.ipynb`), threshold and training configuration files (`ml/configs/*.yaml`), backend `onnxruntime` CPU serving (`apps/api/app/ml_runtime/`), and browser `onnxruntime-web` + Web Worker inference (`apps/web/lib/`) while maintaining 100% permissive licensing (`MIT`/`Apache-2.0`/`BSD`) and `< 1e-3` numerical parity (`AGENTS.md` §7, `ML_SPEC.md` §§2–6).

---

## 1. Architecture & Scope

1. **Centralized ML Configs (`ml/configs/thresholds.yaml`, `ml/configs/training_config.yaml`):**
   - Define operational confidence and heuristic thresholds (`T_cat = 0.80`, `T_cond = 0.70`, `T_blur = 100.0`, `T_dark = 40.0`, `T_bright = 220.0`, `conformal_alpha = 0.20`, `scrubber_box_conf = 0.45`, `swap_delta = 0.30`) per `AGENTS.md` §8.
   - Define reproducible training hyperparameters, 3-seed lists (`[42, 101, 202]`), input/output tensor signatures, and ONNX opset (`opset_version = 17`).

2. **ONNX Computation Graph Exporter & Parity Verifier (`ml/src/onnx_exporter.py`, `ml/exports/*.onnx`):**
   - Generate and export 5 lightweight CPU/WASM-ready `.onnx` models into `ml/exports/` (and browser models into `apps/web/public/models/`):
     - `quality_mobilenet_v3.onnx`: Image quality classifier (`quality_score`, `[p_blurry, p_dark, p_overexposed]`).
     - `scrubber_detector.onnx`: Permissive-licence PII region scorer (`face`, `id_card`, `plate`, `phone`, `address`) — strictly zero AGPL/YOLOv8.
     - `product_recognition_probe.onnx`: Multi-photo feature linear probe (`4 categories` + subtype logits + temperature scaling).
     - `condition_ordinal_coral.onnx`: CORAL ordinal cumulative-link network ($P(Y > k)$ over cutoffs `[0.5, 1.5, 2.5]` $\rightarrow$ 4 ordinal grade probabilities + spatial Grad-CAM weights).
     - `price_quantile_lgbm.onnx`: Quantile regression head ($q_{0.10}, q_{0.50}, q_{0.90}$) with split-conformal interval calibration.
   - Verify numerical parity between the reference Python/PyTorch model and `onnxruntime.InferenceSession` (`max_abs_diff < 1e-3`) and write SHA-256 hashes + parity metrics to `ml/exports/onnx_manifest.json`.

3. **Colab/Kaggle GPU Training Notebooks (`ml/notebooks/`):**
   - `ml/notebooks/01_quality_and_scrubber_onnx.ipynb`: MobileNetV3-Small quality training + permissive YuNet/YOLOX-Nano scrubber training, ONNX export, and parity verification.
   - `ml/notebooks/02_product_recognition_and_condition_coral.ipynb`: CLIP ViT-B/32 linear probe & CORAL ordinal condition grader with Grad-CAM and MLflow logging.
   - `ml/notebooks/03_price_lightgbm_conformal_shap.ipynb`: LightGBM quantile regression, split-conformal calibration on calibration split, TreeSHAP extraction, and ONNX export.

4. **Backend ONNX Runtime Engine (`apps/api/app/ml_runtime/`):**
   - Implement `apps/api/app/ml_runtime/onnx_runtime.py` using `onnxruntime.InferenceSession` (`CPUExecutionProvider`) with lazy session caching, latency telemetry, and deterministic fallback if a binary weight file is unavailable.
   - Wire `ml/src/product_recognition.py`, `ml/src/condition_grader.py`, `ml/src/price_estimator.py`, `ml/src/quality_checker.py`, and `ml/src/privacy_scrubber.py` to run inference through the ONNX runtime and expose `model_backend: "onnxruntime-cpu"` metadata.

5. **Frontend `onnxruntime-web` & Web Worker Pipeline (`apps/web/`):**
   - Log `onnx`, `onnxruntime`, and `onnxruntime-web` (all MIT License) in `THIRD_PARTY_LICENSES.md` before installing.
   - Create `apps/web/lib/onnxClient.ts` and `apps/web/lib/scrubber.worker.ts` to run on-device quality assessment and PII box detection off the main thread via Web Worker + Cache API model caching.
   - Update `apps/web/components/InteractiveScrubberPreview.tsx` to invoke the worker, display on-device ONNX inference latency (`ms`), and support resize handles in addition to add/remove box controls.

6. **Verification & Acceptance Tests (`apps/api/tests/test_phase19_onnx_runtime.py`):**
   - Assert all 5 `.onnx` models exist, pass ONNX checker validation, and achieve `max_abs_diff < 1e-3` parity against reference implementations.
   - Verify `/api/v1/ai/analyze-photos`, `/api/v1/ai/price-estimate`, and `/api/v1/listings/{id}/scrub-verify` execute end-to-end with ONNX models loaded.
   - Run full licence, copyright header, ruff, mypy, pytest, and Next.js type-check/build checks.

---

## 2. Task Breakdown

| id | task | status | notes |
| :--- | :--- | :--- | :--- |
| p19-task-1 | Log `onnx`, `onnxruntime`, `onnxruntime-web` (MIT) in `THIRD_PARTY_LICENSES.md` & create `ml/configs/thresholds.yaml` + `training_config.yaml` | completed | All permissive licences logged before use |
| p19-task-2 | Implement `ml/src/onnx_exporter.py`, export 5 `.onnx` models to `ml/exports/`, and verify `< 1e-3` parity in `ml/exports/onnx_manifest.json` | completed | 5 opset-17 `.onnx` files exported (`max_abs_diff = 0.0`) |
| p19-task-3 | Author 3 reproducible Colab/Kaggle training notebooks in `ml/notebooks/` | completed | Quality/Scrubber, Recognition/CORAL, LightGBM/Conformal |
| p19-task-4 | Build `apps/api/app/ml_runtime/onnx_runtime.py` and wire `ml/src/*.py` + FastAPI `/ai/*` routers to `onnxruntime` | completed | Lazy session caching + `/api/v1/ai/onnx-status` endpoint |
| p19-task-5 | Add `onnxruntime-web`, Web Worker (`scrubber.worker.ts`), `onnxClient.ts`, and resize/worker UX in `InteractiveScrubberPreview.tsx` | completed | Non-blocking browser inference + Cache API model caching |
| p19-task-6 | Write `test_phase19_onnx_runtime.py` acceptance tests, run full CI/licence/header audits, and write `phase-19-report.md` | completed | All 5 Phase 19 tests + 4 Phase 18 tests + audits passed |
