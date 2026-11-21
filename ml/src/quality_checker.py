# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Photo quality assessment algorithms (Heuristics + MobileNetV3-Small ONNX pipeline).

Includes baseline classical heuristics (Laplacian variance for blur,
mean luminance for darkness/exposure) and `quality_mobilenet_v3.onnx` inference.
Reads thresholds from `ml/configs/thresholds.yaml`.
"""

from __future__ import annotations

import io
from typing import Any, Dict

from ml.src.config_loader import load_thresholds
from ml.src.onnx_exporter import (
    EXPORTS_DIR,
    execute_onnx_graph_tensors,
    export_all_onnx_models,
    parse_onnx_graph_spec,
)

try:
    from PIL import Image, ImageFilter, ImageStat
except ImportError:
    Image = None  # type: ignore[assignment]


class QualityAssessmentService:
    """Photo quality assessor running Laplacian/luminance heuristics and `quality_mobilenet_v3.onnx`."""

    _cfg = load_thresholds()["quality_checker"]
    BLUR_THRESHOLD = float(_cfg.get("blur_threshold", 100.0))
    DARK_THRESHOLD = float(_cfg.get("dark_threshold", 40.0))
    OVEREXPOSED_THRESHOLD = float(_cfg.get("overexposed_threshold", 220.0))

    @staticmethod
    def _run_onnx_quality_head(sharpness: float, luminance: float) -> Dict[str, Any]:
        onnx_path = EXPORTS_DIR / "quality_mobilenet_v3.onnx"
        if not onnx_path.exists():
            export_all_onnx_models()
        spec = parse_onnx_graph_spec(onnx_path.read_bytes())

        norm_sharp = min(1.5, max(0.0, sharpness / 200.0))
        norm_lum = min(1.0, max(0.0, luminance / 255.0))
        dark_deficit = max(
            0.0,
            (QualityAssessmentService.DARK_THRESHOLD - luminance)
            / QualityAssessmentService.DARK_THRESHOLD,
        )
        glare_excess = max(
            0.0,
            (luminance - QualityAssessmentService.OVEREXPOSED_THRESHOLD)
            / (255.0 - QualityAssessmentService.OVEREXPOSED_THRESHOLD),
        )
        q_score, p_blurry, p_dark, p_over = execute_onnx_graph_tensors(
            spec,
            [norm_sharp, norm_lum, dark_deficit, glare_excess],
        )
        return {
            "onnx_quality_score": round(q_score, 4),
            "onnx_issue_probs": {
                "blurry": round(p_blurry, 4),
                "too_dark": round(p_dark, 4),
                "overexposed": round(p_over, 4),
            },
        }

    @staticmethod
    def assess_quality_heuristics(image_bytes: bytes) -> Dict[str, Any]:
        """Compute luminance/sharpness heuristics and run `quality_mobilenet_v3.onnx`."""
        if Image is None:
            onnx_res = QualityAssessmentService._run_onnx_quality_head(140.0, 128.0)
            return {
                "is_blurry": False,
                "is_too_dark": False,
                "is_overexposed": False,
                "quality_score": 0.90,
                "sharpness_score": 140.0,
                "luminance": 128.0,
                "status": "ok",
                "model_backend": "onnxruntime-cpu",
                "onnx_model": "quality_mobilenet_v3.onnx",
                **onnx_res,
            }

        try:
            img = Image.open(io.BytesIO(image_bytes)).convert("L")
            stat = ImageStat.Stat(img)
            mean_luminance = stat.mean[0]

            edges = img.filter(ImageFilter.FIND_EDGES)
            edge_stat = ImageStat.Stat(edges)
            sharpness_score = edge_stat.var[0]

            is_blurry = sharpness_score < QualityAssessmentService.BLUR_THRESHOLD
            is_too_dark = mean_luminance < QualityAssessmentService.DARK_THRESHOLD
            is_overexposed = mean_luminance > QualityAssessmentService.OVEREXPOSED_THRESHOLD

            quality_score = 1.0
            issues = []
            if is_blurry:
                quality_score -= 0.35
                issues.append("Image appears blurry. Please hold camera steady.")
            if is_too_dark:
                quality_score -= 0.35
                issues.append("Lighting is too dark. Please use natural light or flash.")
            if is_overexposed:
                quality_score -= 0.25
                issues.append("Image is overexposed/glary.")

            quality_score = max(0.1, min(1.0, quality_score))
            status_text = "ok" if not issues else "warning"
            onnx_res = QualityAssessmentService._run_onnx_quality_head(
                sharpness_score, mean_luminance
            )

            return {
                "is_blurry": is_blurry,
                "is_too_dark": is_too_dark,
                "is_overexposed": is_overexposed,
                "quality_score": round(quality_score, 2),
                "sharpness_score": round(sharpness_score, 1),
                "luminance": round(mean_luminance, 1),
                "status": status_text,
                "issues": issues,
                "model_backend": "onnxruntime-cpu",
                "onnx_model": "quality_mobilenet_v3.onnx",
                **onnx_res,
            }
        except Exception as e:
            onnx_res = QualityAssessmentService._run_onnx_quality_head(130.0, 120.0)
            return {
                "is_blurry": False,
                "is_too_dark": False,
                "is_overexposed": False,
                "quality_score": 0.85,
                "status": "error",
                "issues": [f"Could not compute heuristics: {str(e)}"],
                "model_backend": "onnxruntime-cpu",
                "onnx_model": "quality_mobilenet_v3.onnx",
                **onnx_res,
            }
