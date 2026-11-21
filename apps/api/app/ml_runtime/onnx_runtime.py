# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""CPU ONNX Runtime Inference Engine for FastAPI (`apps/api/app/ml_runtime/onnx_runtime.py`).

Loads exported `.onnx` computation graphs from `ml/exports/` with lazy session
caching, SHA-256 verification against `ml/exports/onnx_manifest.json`, and
execution via `onnxruntime.InferenceSession` (`CPUExecutionProvider`) or the
IEEE-754 float32 ONNX binary graph evaluator when running in pure-Python mode.
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Sequence

from ml.src.onnx_exporter import (
    EXPORTS_DIR,
    execute_onnx_graph_tensors,
    export_all_onnx_models,
    parse_onnx_graph_spec,
)


class ONNXCPUInferenceEngine:
    """Lazy-cached CPU ONNX runtime engine for LOOP ML models."""

    def __init__(self, exports_dir: Path = EXPORTS_DIR) -> None:
        """Initialize the ONNX CPU runtime engine pointing to `ml/exports`."""
        self.exports_dir = exports_dir
        self._spec_cache: Dict[str, Dict[str, Any]] = {}
        self._ort_sessions: Dict[str, Any] = {}
        self._sha256_cache: Dict[str, str] = {}
        self._manifest: Dict[str, Any] | None = None

    def ensure_models_exported(self) -> Dict[str, Any]:
        """Ensure all 5 `.onnx` binaries and `onnx_manifest.json` exist on disk."""
        manifest_path = self.exports_dir / "onnx_manifest.json"
        if not manifest_path.exists():
            exported: Dict[str, Any] = dict(export_all_onnx_models(exports_dir=self.exports_dir))
            self._manifest = exported
            return exported
        if self._manifest is None:
            loaded: Dict[str, Any] = json.loads(manifest_path.read_text(encoding="utf-8"))
            self._manifest = loaded
        return self._manifest

    def get_model_path(self, model_key: str) -> Path:
        """Return the absolute path to the `.onnx` binary for `model_key`."""
        manifest = self.ensure_models_exported()
        models_meta: Dict[str, Any] = manifest.get("models", {})
        if model_key not in models_meta:
            raise KeyError(f"Unknown ONNX model key: {model_key}")
        filename: str = str(models_meta[model_key]["filename"])
        model_path = self.exports_dir / filename
        if not model_path.exists():
            export_all_onnx_models(exports_dir=self.exports_dir)
        return model_path

    def load_model(self, model_key: str) -> Dict[str, Any]:
        """Load and cache an `.onnx` binary graph and verify its SHA-256 digest."""
        if model_key in self._spec_cache:
            return self._spec_cache[model_key]

        model_path = self.get_model_path(model_key)
        raw_bytes = model_path.read_bytes()
        digest = hashlib.sha256(raw_bytes).hexdigest()

        manifest = self.ensure_models_exported()
        expected_sha = str(manifest["models"][model_key]["sha256"])
        if digest != expected_sha:
            raise ValueError(
                f"ONNX binary hash mismatch for {model_key}: expected {expected_sha}, got {digest}"
            )

        spec: Dict[str, Any] = dict(parse_onnx_graph_spec(raw_bytes))
        self._spec_cache[model_key] = spec
        self._sha256_cache[model_key] = digest

        try:
            import onnxruntime as ort  # type: ignore[import-not-found]

            self._ort_sessions[model_key] = ort.InferenceSession(
                str(model_path),
                providers=["CPUExecutionProvider"],
            )
        except ImportError:
            pass

        return spec

    def run_inference(self, model_key: str, input_vector: Sequence[float]) -> Dict[str, Any]:
        """Execute a forward pass on the cached `.onnx` model for `model_key`."""
        t0 = time.perf_counter()
        spec = self.load_model(model_key)
        model_path = self.get_model_path(model_key)
        backend_name = "onnxruntime-cpu"

        if model_key in self._ort_sessions:
            import numpy as np  # type: ignore[import-not-found]

            sess = self._ort_sessions[model_key]
            ort_out = sess.run(None, {"input": np.array([list(input_vector)], dtype=np.float32)})
            output_list: List[float] = [float(x) for x in ort_out[0][0]]
        else:
            output_list = [float(x) for x in execute_onnx_graph_tensors(spec, input_vector)]

        latency_ms = round((time.perf_counter() - t0) * 1000.0, 4)
        return {
            "model_key": model_key,
            "onnx_model": model_path.name,
            "sha256": self._sha256_cache[model_key],
            "model_backend": backend_name,
            "output": output_list,
            "latency_ms": latency_ms,
        }

    def get_runtime_health(self) -> Dict[str, Any]:
        """Return health and parity status of all exported ONNX models."""
        manifest = self.ensure_models_exported()
        models_status: Dict[str, Any] = {}
        for key, meta in manifest.get("models", {}).items():
            self.load_model(key)
            models_status[key] = {
                "filename": meta["filename"],
                "sha256": meta["sha256"],
                "size_bytes": meta["size_bytes"],
                "parity_verified": meta["parity_verified"],
                "max_abs_diff": meta["max_abs_diff"],
                "loaded": key in self._spec_cache,
            }
        return {
            "status": "ready",
            "opset_version": manifest.get("opset_version", 17),
            "all_parity_passed": manifest.get("all_parity_passed", True),
            "models": models_status,
        }


onnx_engine = ONNXCPUInferenceEngine()
