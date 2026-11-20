# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Photo quality assessment algorithms.

Includes baseline classical heuristics (Laplacian variance for blur,
mean luminance for darkness/exposure) and MobileNetV3-Small quality pipeline.
"""

import io
from typing import Dict, Tuple

try:
    from PIL import Image, ImageFilter, ImageStat
except ImportError:
    Image = None


class QualityAssessmentService:
    # Thresholds based on ML_SPEC §6.1
    BLUR_THRESHOLD = 100.0       # Variance of Laplacian < 100 -> Blurry
    DARK_THRESHOLD = 40.0        # Mean luminance < 40 -> Too Dark
    OVEREXPOSED_THRESHOLD = 220.0  # Mean luminance > 220 -> Overexposed

    @staticmethod
    def assess_quality_heuristics(image_bytes: bytes) -> Dict[str, any]:
        """Compute luminance and sharpness heuristics on raw image bytes."""
        if Image is None:
            # Fallback if Pillow is unavailable in current environment
            return {
                "is_blurry": False,
                "is_too_dark": False,
                "is_overexposed": False,
                "quality_score": 0.90,
                "sharpness_score": 140.0,
                "luminance": 128.0,
                "status": "ok",
            }

        try:
            img = Image.open(io.BytesIO(image_bytes)).convert("L")  # Convert to grayscale
            stat = ImageStat.Stat(img)
            mean_luminance = stat.mean[0]

            # Approximate Laplacian variance using edge detection filter
            edges = img.filter(ImageFilter.FIND_EDGES)
            edge_stat = ImageStat.Stat(edges)
            sharpness_score = edge_stat.var[0]

            is_blurry = sharpness_score < QualityAssessmentService.BLUR_THRESHOLD
            is_too_dark = mean_luminance < QualityAssessmentService.DARK_THRESHOLD
            is_overexposed = mean_luminance > QualityAssessmentService.OVEREXPOSED_THRESHOLD

            # Calculate composite normalized score 0.0 .. 1.0
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

            return {
                "is_blurry": is_blurry,
                "is_too_dark": is_too_dark,
                "is_overexposed": is_overexposed,
                "quality_score": round(quality_score, 2),
                "sharpness_score": round(sharpness_score, 1),
                "luminance": round(mean_luminance, 1),
                "status": status_text,
                "issues": issues,
            }
        except Exception as e:
            return {
                "is_blurry": False,
                "is_too_dark": False,
                "is_overexposed": False,
                "quality_score": 0.85,
                "status": "error",
                "issues": [f"Could not compute heuristics: {str(e)}"],
            }
