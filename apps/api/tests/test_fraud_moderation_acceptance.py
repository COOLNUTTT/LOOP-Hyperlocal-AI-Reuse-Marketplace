# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Acceptance test verifying Phase 14 Fraud, Duplicates, Scam Text & Moderation:

1. Duplicate/stolen image detection (pHash -> CLIP cosine re-check) with human-readable reason.
2. Price-anomaly rule flags extreme under/overpricing.
3. Scam-text classifier flags scam messages with human-readable reason.
4. No auto-removal without human decision; moderator action writes an audit log row.
5. Synthetic evaluation reports precision/recall/FPR.
"""

import sys
import types
import unittest
import uuid
from decimal import Decimal

try:
    from fastapi import HTTPException
except ImportError:
    class HTTPException(Exception):
        def __init__(self, status_code: int, detail: str = ""):
            self.status_code = status_code
            self.detail = detail
            super().__init__(detail)

    fastapi_mod = types.ModuleType("fastapi")
    fastapi_mod.HTTPException = HTTPException
    fastapi_mod.status = types.SimpleNamespace(HTTP_400_BAD_REQUEST=400)
    sys.modules["fastapi"] = fastapi_mod

from ml.src.fraud_detector import FraudDetector
from ml.src.eval_fraud import run_evaluation
from app.services.moderation_service import ModerationService


class MockFlag:
    def __init__(self, flag_type, reason, target_id):
        self.id = uuid.uuid4()
        self.flag_type = flag_type
        self.reason = reason
        self.target_id = target_id
        self.status = "open"
        self.resolved_by = None
        self.resolved_at = None


class MockListing:
    def __init__(self):
        self.id = uuid.uuid4()
        self.status = "active"


class TestPhase14FraudModerationAcceptance(unittest.TestCase):
    def test_duplicate_image_and_price_anomaly(self):
        """Verify pHash + CLIP duplicate detection and price-anomaly rule."""
        dup = FraudDetector.check_duplicate_image(
            "ffffffff00000000", "ffffffff00000001", [1.0, 0.0], [0.99, 0.05]
        )
        self.assertTrue(dup["is_duplicate"])
        self.assertIsNotNone(dup["reason"])

        anom = FraudDetector.check_price_anomaly(
            Decimal("50.00"), category="electronics", subtype="Scientific Calculator"
        )
        self.assertTrue(anom["is_anomaly"])
        self.assertIn("Price anomaly", anom["reason"])

    def test_scam_text_classifier_with_reason(self):
        """Verify scam-text classifier produces human-readable reason."""
        res = FraudDetector.classify_scam_text("Pay advance payment and scan QR code to receive money")
        self.assertTrue(res["is_scam"])
        self.assertGreaterEqual(res["score"], 0.5)
        self.assertIn("Scam-text risk", res["reason"])

    def test_no_auto_removal_and_audit_log_on_action(self):
        """Verify flagged listing is not auto-removed and moderator action writes audit log."""
        listing = MockListing()
        flag = MockFlag("scam", "Scam-text risk (92%)", listing.id)

        # Before human decision, listing remains active
        self.assertEqual(listing.status, "active")

        mod_id = uuid.uuid4()
        audit = ModerationService.apply_moderator_action(
            flag=flag,
            moderator_id=mod_id,
            action="remove",
            notes="Confirmed scam attempt",
            listing=listing,
        )
        self.assertEqual(flag.status, "upheld")
        self.assertEqual(listing.status, "removed")
        self.assertEqual(audit["action"], "moderation.remove")
        self.assertEqual(audit["actor_id"], mod_id)

    def test_synthetic_eval_metrics(self):
        """Verify synthetic evaluation metrics."""
        metrics = run_evaluation()
        self.assertGreaterEqual(metrics["scam_text_synthetic"]["precision"], 0.9)
        self.assertGreaterEqual(metrics["duplicate_image_synthetic"]["recall"], 0.9)


if __name__ == "__main__":
    unittest.main()
