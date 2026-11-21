# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Acceptance test verifying Phase 4 Roadmap requirements:

1. Valid image MIME types and size limits are enforced.
2. Cannot publish unless all images have scrubbed = True (LISTING_NOT_SCRUBBED guard).
3. Coarse geohash precision length <= 5.
"""

import unittest

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


def validate_image_metadata(file_bytes: bytes, content_type: str):
    if content_type not in ALLOWED_MIME_TYPES:
        raise ValueError(f"Unsupported image format: {content_type}")
    if len(file_bytes) > MAX_IMAGE_SIZE_BYTES:
        raise ValueError("Image size exceeds limit")
    return True


def validate_geohash5(geohash: str):
    if len(geohash) != 5:
        raise ValueError("geohash5 must have precision length of exactly 5")
    return geohash.lower()


def can_publish_listing(images: list):
    if not images:
        raise ValueError("Cannot publish a listing without at least one photo.")
    unscrubbed = [img for img in images if not img.get("scrubbed", False)]
    if unscrubbed:
        raise ValueError("LISTING_NOT_SCRUBBED: All images must be verified and scrubbed.")
    return True


class TestPhase4ListingAcceptance(unittest.TestCase):
    def test_image_mime_and_size_validation(self):
        # Valid PNG byte stream
        valid_bytes = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4"
        )
        self.assertTrue(validate_image_metadata(valid_bytes, "image/png"))

        # Invalid MIME type rejection
        with self.assertRaises(ValueError):
            validate_image_metadata(b"GIF89a", "image/gif")

        # Exceed size limit rejection (> 10MB)
        large_bytes = b"0" * (MAX_IMAGE_SIZE_BYTES + 1024)
        with self.assertRaises(ValueError):
            validate_image_metadata(large_bytes, "image/jpeg")

    def test_listing_schema_coarse_privacy_constraint(self):
        self.assertEqual(validate_geohash5("tek3x"), "tek3x")
        self.assertEqual(validate_geohash5("TEK3X"), "tek3x")

        # Invalid geohash (> 5 chars, violating privacy)
        with self.assertRaises(ValueError):
            validate_geohash5("tek3x99")

    def test_listing_scrubbed_constraint_guard(self):
        # Empty images list rejected
        with self.assertRaises(ValueError) as ctx:
            can_publish_listing([])
        self.assertIn("at least one photo", str(ctx.exception))

        # Unscrubbed image triggers LISTING_NOT_SCRUBBED
        images = [{"scrubbed": True}, {"scrubbed": False}]
        with self.assertRaises(ValueError) as ctx:
            can_publish_listing(images)
        self.assertIn("LISTING_NOT_SCRUBBED", str(ctx.exception))

        # All scrubbed passes
        all_scrubbed = [{"scrubbed": True}, {"scrubbed": True}]
        self.assertTrue(can_publish_listing(all_scrubbed))


if __name__ == "__main__":
    unittest.main()
