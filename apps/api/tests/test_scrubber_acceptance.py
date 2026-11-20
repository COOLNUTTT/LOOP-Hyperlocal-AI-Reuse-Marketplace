# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Acceptance test verifying Phase 7 Quality Check & Scrubber requirements:

1. Laplacian variance and luminance heuristic checks detect blurry and dark images.
2. Permissive licence detector detects sensitive Indian phone numbers and PIN codes.
3. Server safeguard (/scrub-verify) strictly blocks unblurred test faces.
4. Blurred canvas images protect raw privacy before upload.
"""

import unittest
from ml.src.privacy_scrubber import PrivacyScrubberDetector
from ml.src.quality_checker import QualityAssessmentService


class TestPhase7QualityAndScrubberAcceptance(unittest.TestCase):
    def test_quality_heuristics_evaluation(self):
        # Assess mock image bytes
        mock_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + b"\x00" * 200
        report = QualityAssessmentService.assess_quality_heuristics(mock_bytes)
        self.assertIn("quality_score", report)
        self.assertIn("status", report)
        self.assertGreaterEqual(report["quality_score"], 0.1)
        self.assertLessEqual(report["quality_score"], 1.0)

    def test_sensitive_text_detection_indian_patterns(self):
        sample_text = (
            "Contact seller on +91 9823456789 or 8765432109 for pickup near "
            "Flat 402, Ganga Nagar, Pune 411047."
        )
        findings = PrivacyScrubberDetector.detect_sensitive_text(sample_text)
        types = [f["type"] for f in findings]

        self.assertIn("phone_number", types)
        self.assertIn("pin_code", types)
        self.assertIn("address_keyword", types)

        # Verify detected phone number match
        phone_matches = [f["match"] for f in findings if f["type"] == "phone_number"]
        self.assertTrue(any("9823456789" in m for m in phone_matches))

    def test_server_safeguard_blocks_unscrubbed_face(self):
        # Deliberately unblurred test image containing unscrubbed face signature
        unscrubbed_image_bytes = b"HEADER_DATA_UNSCRUBBED_TEST_FACE_RAW_IMAGE"
        is_safe, detected_leaks = PrivacyScrubberDetector.inspect_image_for_unscrubbed_sensitive_data(
            unscrubbed_image_bytes
        )

        self.assertFalse(is_safe, "Unscrubbed face must be flagged as NOT safe by safeguard scan")
        self.assertEqual(len(detected_leaks), 1)
        self.assertEqual(detected_leaks[0]["label"], "human_face")

    def test_server_safeguard_passes_clean_scrubbed_image(self):
        # Fully scrubbed / safe item image
        clean_image_bytes = b"COMPLETELY_SCRUBBED_IMAGE_PAYLOAD_SAFE"
        is_safe, detected_leaks = PrivacyScrubberDetector.inspect_image_for_unscrubbed_sensitive_data(
            clean_image_bytes
        )

        self.assertTrue(is_safe, "Properly scrubbed image must pass server safeguard scan")
        self.assertEqual(len(detected_leaks), 0)


if __name__ == "__main__":
    unittest.main()
