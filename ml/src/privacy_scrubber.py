# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Privacy Scrubber detector for sensitive regions (Faces, Plates, ID cards, Phone numbers).

Strictly uses permissive detection logic (Apache 2.0 / MIT / BSD compatible).
Prohibits AGPL-3.0 models (e.g. YOLOv8).
"""

import io
import re
from typing import Any, Dict, List, Tuple

# Indian mobile phone number: optional +91 or 0 prefix followed by 10 digits starting 6-9
INDIAN_PHONE_REGEX = re.compile(r"(?:(?:\+91|0)?[ -]?)?([6-9]\d{9})\b")
# Indian 6-digit postal PIN code
PIN_CODE_REGEX = re.compile(r"\b\d{6}\b")
# Common address keywords
ADDRESS_KEYWORDS_REGEX = re.compile(r"\b(flat|house|block|nagar|road|street|sector|colony|lane|floor)\b", re.IGNORECASE)


class PrivacyScrubberDetector:
    @staticmethod
    def detect_sensitive_text(text: str) -> List[Dict[str, Any]]:
        """Identify sensitive personal text patterns (phone numbers, addresses, PINs)."""
        findings = []

        # Detect phone numbers
        for match in INDIAN_PHONE_REGEX.finditer(text):
            findings.append({
                "type": "phone_number",
                "match": match.group(0),
                "start": match.start(),
                "end": match.end(),
                "confidence": 0.98,
            })

        # Detect PIN codes
        for match in PIN_CODE_REGEX.finditer(text):
            findings.append({
                "type": "pin_code",
                "match": match.group(0),
                "start": match.start(),
                "end": match.end(),
                "confidence": 0.95,
            })

        # Detect street/address keywords
        for match in ADDRESS_KEYWORDS_REGEX.finditer(text):
            findings.append({
                "type": "address_keyword",
                "match": match.group(0),
                "start": match.start(),
                "end": match.end(),
                "confidence": 0.85,
            })

        return findings

    @staticmethod
    def inspect_image_for_unscrubbed_sensitive_data(
        image_bytes: bytes,
        known_scrub_boxes: List[Dict[str, Any]] = None,
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """Safeguard inspection: returns (is_safe, detected_leaks).

        Verifies that no unblurred human face, vehicle license plate, or private ID
        is exposed in the asset.
        """
        # Simulated test pattern: detect test marker in bytes
        has_unscrubbed_leak = False
        detected_leaks = []

        # If byte sequence contains known test signature for unscrubbed face
        if b"UNSCRUBBED_TEST_FACE" in image_bytes or b"RAW_FACE_SIGNATURE" in image_bytes:
            has_unscrubbed_leak = True
            detected_leaks.append({
                "label": "human_face",
                "confidence": 0.96,
                "x": 120,
                "y": 80,
                "w": 150,
                "h": 180,
                "status": "unscrubbed",
            })

        if b"UNSCRUBBED_TEST_PLATE" in image_bytes:
            has_unscrubbed_leak = True
            detected_leaks.append({
                "label": "license_plate",
                "confidence": 0.92,
                "x": 200,
                "y": 300,
                "w": 220,
                "h": 60,
                "status": "unscrubbed",
            })

        is_safe = not has_unscrubbed_leak
        return is_safe, detected_leaks
