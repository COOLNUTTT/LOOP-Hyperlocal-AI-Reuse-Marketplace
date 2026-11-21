# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Phase 19 (Track A) Acceptance Tests: Real ONNX Graphs, Notebooks & Runtime Wiring."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient
from ml.src.condition_grader import condition_grader
from ml.src.config_loader import load_thresholds, load_training_config
from ml.src.onnx_exporter import (
    EXPORTS_DIR,
    WEB_MODELS_DIR,
    execute_onnx_graph_tensors,
    export_all_onnx_models,
    get_model_definitions,
    parse_onnx_graph_spec,
)
from ml.src.price_estimator import price_estimator
from ml.src.privacy_scrubber import PrivacyScrubberDetector
from ml.src.product_recognition import product_recognizer
from ml.src.quality_checker import QualityAssessmentService

from app.main import app
from app.ml_runtime.onnx_runtime import onnx_engine

REPO_ROOT = Path(__file__).resolve().parents[3]
client = TestClient(app)


def test_thresholds_and_training_configs_load() -> None:
    """Verify `ml/configs/thresholds.yaml` and `training_config.yaml` exist and load."""
    thresholds = load_thresholds()
    assert thresholds["product_recognition"]["confidence_threshold"] == 0.80
    assert thresholds["condition_grader"]["confidence_threshold"] == 0.70
    assert thresholds["price_estimator"]["conformal_alpha"] == 0.20
    assert thresholds["quality_checker"]["blur_threshold"] == 100.0

    train_cfg = load_training_config()
    assert train_cfg["onnx_export"]["opset_version"] == 17
    assert train_cfg["experiment"]["seeds"] == [42, 101, 202]


def test_all_five_onnx_models_exported_and_parity_under_1e3() -> None:
    """Verify all 5 `.onnx` files exist and achieve `max_abs_diff < 1e-3` parity (AGENTS.md §7)."""
    manifest = export_all_onnx_models()
    assert manifest["all_parity_passed"] is True
    assert manifest["opset_version"] == 17

    expected_keys = {
        "quality_mobilenet_v3",
        "scrubber_detector",
        "product_recognition_probe",
        "condition_ordinal_coral",
        "price_quantile_lgbm",
    }
    assert set(manifest["models"].keys()) == expected_keys

    definitions = get_model_definitions()
    for key in expected_keys:
        meta = manifest["models"][key]
        onnx_file = EXPORTS_DIR / meta["filename"]
        assert onnx_file.exists(), f"Missing exported ONNX file: {onnx_file}"
        assert onnx_file.stat().st_size > 100
        assert meta["parity_verified"] is True
        assert meta["max_abs_diff"] < 1e-3

        # Re-parse raw binary and verify forward-pass parity directly
        spec = parse_onnx_graph_spec(onnx_file.read_bytes())
        assert spec["model_name"] == key
        ref_out = execute_onnx_graph_tensors(definitions[key], definitions[key]["test_input"])
        engine_res = onnx_engine.run_inference(key, definitions[key]["test_input"])
        max_diff = max(abs(a - b) for a, b in zip(ref_out, engine_res["output"], strict=True))
        assert max_diff < 1e-3
        assert engine_res["model_backend"] == "onnxruntime-cpu"

    # Browser public models for onnxruntime-web
    assert (WEB_MODELS_DIR / "quality_mobilenet_v3.onnx").exists()
    assert (WEB_MODELS_DIR / "scrubber_detector.onnx").exists()


def test_ml_services_wired_to_onnx_runtime() -> None:
    """Verify recognition, condition, price, quality, and scrubber execute via ONNX runtime."""
    rec = product_recognizer.predict_from_features("Casio fx-991EX scientific calculator")
    assert rec["model_backend"] == "onnxruntime-cpu"
    assert rec["onnx_model"] == "product_recognition_probe.onnx"
    assert rec["category"]["value"] == "electronics"

    cond = condition_grader.predict_condition(context_hints="minor mark normal wear")
    assert cond["model_backend"] == "onnxruntime-cpu"
    assert cond["onnx_model"] == "condition_ordinal_coral.onnx"
    assert cond["grade"] in ("poor", "fair", "good", "like_new")

    price = price_estimator.estimate_price(
        category="electronics",
        subtype="scientific calculator",
        brand="Casio",
        condition="good",
    )
    assert price["model_backend"] == "onnxruntime-cpu"
    assert price["onnx_model"] == "price_quantile_lgbm.onnx"
    assert price["low"] < price["likely"] < price["high"]

    qual = QualityAssessmentService.assess_quality_heuristics(b"sample_image_bytes")
    assert qual["model_backend"] == "onnxruntime-cpu"
    assert qual["onnx_model"] == "quality_mobilenet_v3.onnx"

    is_safe, leaks = PrivacyScrubberDetector.inspect_image_for_unscrubbed_sensitive_data(
        b"header UNSCRUBBED_TEST_FACE footer"
    )
    assert is_safe is False
    assert leaks[0]["onnx_model"] == "scrubber_detector.onnx"


def test_api_onnx_status_and_analyze_endpoints() -> None:
    """Verify `GET /api/v1/ai/onnx-status` and `POST /api/v1/ai/analyze-photos`."""
    status_resp = client.get("/api/v1/ai/onnx-status")
    assert status_resp.status_code == 200
    body = status_resp.json()
    assert body["status"] == "ready"
    assert body["all_parity_passed"] is True
    assert len(body["models"]) == 5

    analyze_resp = client.post(
        "/api/v1/ai/analyze-photos",
        json={"image_urls": ["https://loop.campus/uploads/casio_calculator_scrubbed.jpg"]},
    )
    assert analyze_resp.status_code == 200
    data = analyze_resp.json()
    assert data["category"]["value"] == "electronics"
    low_p = float(data["price"]["low"])
    likely_p = float(data["price"]["likely"])
    high_p = float(data["price"]["high"])
    assert low_p < likely_p < high_p


def test_colab_notebooks_and_web_worker_exist() -> None:
    """Verify training notebooks (`ml/notebooks/*.ipynb`) and web ONNX worker files exist."""
    notebooks_dir = REPO_ROOT / "ml" / "notebooks"
    expected_notebooks = [
        "01_quality_and_scrubber_onnx.ipynb",
        "02_product_recognition_and_condition_coral.ipynb",
        "03_price_lightgbm_conformal_shap.ipynb",
    ]
    for nb_name in expected_notebooks:
        nb_path = notebooks_dir / nb_name
        assert nb_path.exists(), f"Missing notebook: {nb_path}"
        parsed = json.loads(nb_path.read_text(encoding="utf-8"))
        assert parsed["nbformat"] == 4
        assert len(parsed["cells"]) >= 2

    web_onnx = REPO_ROOT / "apps" / "web" / "lib" / "onnxClient.ts"
    web_worker = REPO_ROOT / "apps" / "web" / "lib" / "scrubber.worker.ts"
    assert web_onnx.exists()
    assert web_worker.exists()
    assert "loop-onnx-models-v1" in web_onnx.read_text(encoding="utf-8")
