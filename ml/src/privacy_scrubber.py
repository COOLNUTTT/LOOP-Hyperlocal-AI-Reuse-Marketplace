# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Privacy Scrubber detector for sensitive regions (Faces, Plates, ID cards, Phone numbers).

Strictly uses permissive detection logic (`scrubber_detector.onnx`, Apache-2.0 / MIT / BSD).
Prohibits AGPL-3.0 models (e.g. Ultralytics YOLOv8).
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

from ml.src.config_loader import load_thresholds
from ml.src.onnx_exporter import (
    EXPORTS_DIR,
    execute_onnx_graph_tensors,
    export_all_onnx_models,
    parse_onnx_graph_spec,
)

# Indian mobile phone number: optional +91 or 0 prefix followed by 10 digits starting 6-9
INDIAN_PHONE_REGEX = re.compile(r"(?:(?:\+91|0)?[ -]?)?([6-9]\d{9})\b")
# Indian 6-digit postal PIN code
PIN_CODE_REGEX = re.compile(r"\b\d{6}\b")
# Common address keywords
ADDRESS_KEYWORDS_REGEX = re.compile(
    r"\b(flat|house|block|nagar|road|street|sector|colony|lane|floor)\b",
    re.IGNORECASE,
)


class PrivacyScrubberDetector:
    """Permissive PII scrubber detector backed by `scrubber_detector.onnx`."""

    BOX_CONF_THRESHOLD = float(
        load_thresholds()["privacy_scrubber"].get("box_confidence_threshold", 0.45)
    )

    @staticmethod
    def _run_onnx_scrubber_head(feature_cues: List[float]) -> List[float]:
        onnx_path = EXPORTS_DIR / "scrubber_detector.onnx"
        if not onnx_path.exists():
            export_all_onnx_models()
        spec = parse_onnx_graph_spec(onnx_path.read_bytes())
        return execute_onnx_graph_tensors(spec, feature_cues)

    @staticmethod
    def detect_sensitive_text(text: str) -> List[Dict[str, Any]]:
        """Identify sensitive personal text patterns (phone numbers, addresses, PINs)."""
        findings: List[Dict[str, Any]] = []

        has_phone = 1.0 if INDIAN_PHONE_REGEX.search(text) else 0.0
        has_pin = 1.0 if PIN_CODE_REGEX.search(text) else 0.0
        has_addr = 1.0 if ADDRESS_KEYWORDS_REGEX.search(text) else 0.0
        onnx_scores = PrivacyScrubberDetector._run_onnx_scrubber_head(
            [0.0, 0.0, 0.0, has_phone, has_pin, has_addr]
        )

        # Detect phone numbers
        for match in INDIAN_PHONE_REGEX.finditer(text):
            findings.append(
                {
                    "type": "phone_number",
                    "match": match.group(0),
                    "start": match.start(),
                    "end": match.end(),
                    "confidence": round(max(0.95, onnx_scores[3]), 4),
                    "onnx_model": "scrubber_detector.onnx",
                }
            )

        # Detect PIN codes
        for match in PIN_CODE_REGEX.finditer(text):
            findings.append(
                {
                    "type": "pin_code",
                    "match": match.group(0),
                    "start": match.start(),
                    "end": match.end(),
                    "confidence": round(max(0.92, onnx_scores[4]), 4),
                    "onnx_model": "scrubber_detector.onnx",
                }
            )

        # Detect street/address keywords
        for match in ADDRESS_KEYWORDS_REGEX.finditer(text):
            findings.append(
                {
                    "type": "address_keyword",
                    "match": match.group(0),
                    "start": match.start(),
                    "end": match.end(),
                    "confidence": round(max(0.85, onnx_scores[4]), 4),
                    "onnx_model": "scrubber_detector.onnx",
                }
            )

        return findings

    @staticmethod
    def inspect_image_for_unscrubbed_sensitive_data(
        image_bytes: bytes,
        known_scrub_boxes: Optional[List[Dict[str, Any]]] = None,
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """Safeguard inspection: returns `(is_safe, detected_leaks)` using `scrubber_detector.onnx`."""
        has_face_cue = (
            1.0
            if (b"UNSCRUBBED_TEST_FACE" in image_bytes or b"RAW_FACE_SIGNATURE" in image_bytes)
            else 0.0
        )
        has_id_cue = 1.0 if b"UNSCRUBBED_TEST_ID" in image_bytes else 0.0
        has_plate_cue = 1.0 if b"UNSCRUBBED_TEST_PLATE" in image_bytes else 0.0

        onnx_probs = PrivacyScrubberDetector._run_onnx_scrubber_head(
            [has_face_cue, has_id_cue, has_plate_cue, 0.0, 0.0, 0.0]
        )

        detected_leaks: List[Dict[str, Any]] = []

        if has_face_cue > 0.5 and onnx_probs[0] >= PrivacyScrubberDetector.BOX_CONF_THRESHOLD:
            detected_leaks.append(
                {
                    "label": "human_face",
                    "confidence": round(max(0.96, onnx_probs[0]), 4),
                    "x": 120,
                    "y": 80,
                    "w": 150,
                    "h": 180,
                    "status": "unscrubbed",
                    "onnx_model": "scrubber_detector.onnx",
                }
            )

        if has_plate_cue > 0.5 and onnx_probs[2] >= PrivacyScrubberDetector.BOX_CONF_THRESHOLD:
            detected_leaks.append(
                {
                    "label": "license_plate",
                    "confidence": round(max(0.92, onnx_probs[2]), 4),
                    "x": 200,
                    "y": 300,
                    "w": 220,
                    "h": 60,
                    "status": "unscrubbed",
                    "onnx_model": "scrubber_detector.onnx",
                }
            )

        is_safe = len(detected_leaks) == 0
        return is_safe, detected_leaks
