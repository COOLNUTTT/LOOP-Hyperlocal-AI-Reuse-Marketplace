# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Acceptance test verifying Phase 13 Handover, Reviews & Trust Score:

1. Trade completes only after both buyer and seller confirm.
2. Expired/incorrect OTP rejected and rate-limited (> 5 attempts -> 429).
3. Review without completed handover -> 403 Forbidden.
4. Trust breakdown sums exactly to the displayed total_score.
5. Chat-safety warnings and rule-based negotiation helper.
"""

import sys
import types
import unittest
import uuid
from datetime import datetime, timedelta, timezone
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
    fastapi_mod.status = types.SimpleNamespace(
        HTTP_400_BAD_REQUEST=400,
        HTTP_403_FORBIDDEN=403,
        HTTP_429_TOO_MANY_REQUESTS=429,
    )
    sys.modules["fastapi"] = fastapi_mod

from app.services.handover_service import MAX_OTP_ATTEMPTS, HandoverService
from app.services.safety_helper import SafetyAndNegotiationHelper
from app.services.trust_service import TrustService


class MockHandover:
    def __init__(self, buyer_id, seller_id, otp_hash, otp_expires_at):
        self.id = uuid.uuid4()
        self.buyer_id = buyer_id
        self.seller_id = seller_id
        self.otp_hash = otp_hash
        self.otp_expires_at = otp_expires_at
        self.otp_attempts = 0
        self.buyer_confirmed = False
        self.seller_confirmed = False
        self.status = "pending"
        self.completed_at = None


class TestPhase13HandoverTrustAcceptance(unittest.TestCase):
    def setUp(self):
        self.buyer_id = uuid.uuid4()
        self.seller_id = uuid.uuid4()

    def test_both_sides_confirmation_completes_handover(self):
        """Trade completes only after both buyer and seller confirm."""
        otp_code, otp_hash, expires_at = HandoverService.generate_otp()
        handover = MockHandover(self.buyer_id, self.seller_id, otp_hash, expires_at)

        # Buyer confirms first -> status = buyer_confirmed (not completed)
        HandoverService.verify_and_confirm(handover, self.buyer_id, otp_code)
        self.assertTrue(handover.buyer_confirmed)
        self.assertFalse(handover.seller_confirmed)
        self.assertEqual(handover.status, "buyer_confirmed")

        # Seller confirms second -> status = completed
        HandoverService.verify_and_confirm(handover, self.seller_id, otp_code)
        self.assertTrue(handover.seller_confirmed)
        self.assertEqual(handover.status, "completed")
        self.assertIsNotNone(handover.completed_at)

    def test_expired_and_incorrect_otp_rate_limited(self):
        """Expired/incorrect OTP rejected and rate-limited after MAX_OTP_ATTEMPTS."""
        otp_code, otp_hash, expires_at = HandoverService.generate_otp()
        handover = MockHandover(self.buyer_id, self.seller_id, otp_hash, expires_at)

        # 1. Incorrect OTP increments attempts
        for _ in range(MAX_OTP_ATTEMPTS):
            with self.assertRaises(HTTPException) as ctx:
                HandoverService.verify_and_confirm(handover, self.buyer_id, "000000")
            self.assertEqual(ctx.exception.status_code, 400)

        # 2. Next attempt -> 429 rate limited
        with self.assertRaises(HTTPException) as ctx:
            HandoverService.verify_and_confirm(handover, self.buyer_id, otp_code)
        self.assertEqual(ctx.exception.status_code, 429)

        # 3. Expired OTP -> 400
        expired_time = datetime.now(timezone.utc) - timedelta(minutes=1)
        expired_handover = MockHandover(self.buyer_id, self.seller_id, otp_hash, expired_time)
        with self.assertRaises(HTTPException) as ctx:
            HandoverService.verify_and_confirm(expired_handover, self.buyer_id, otp_code)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("OTP_EXPIRED", ctx.exception.detail)

    def test_review_gated_on_completed_handover(self):
        """Review without completed handover -> 403 Forbidden."""
        _, otp_hash, expires_at = HandoverService.generate_otp()
        pending_handover = MockHandover(self.buyer_id, self.seller_id, otp_hash, expires_at)

        with self.assertRaises(HTTPException) as ctx:
            TrustService.validate_review_allowed(pending_handover, self.buyer_id)
        self.assertEqual(ctx.exception.status_code, 403)

        # Completed handover allows review
        pending_handover.status = "completed"
        TrustService.validate_review_allowed(pending_handover, self.buyer_id)

    def test_trust_breakdown_sums_to_total_score(self):
        """Trust breakdown components must sum exactly to total_score."""
        res = TrustService.compute_trust_breakdown(
            is_verified=True,
            completed_trades=4,
            ratings=[5, 4, 5],
            upheld_flags=0,
        )
        breakdown_sum = round(sum(res["breakdown"].values()), 2)
        self.assertEqual(res["total_score"], breakdown_sum)
        self.assertGreater(res["total_score"], 70.0)

    def test_chat_safety_and_negotiation_helper(self):
        """Verify scam keyword warnings and rule-based negotiation helper."""
        warnings = SafetyAndNegotiationHelper.check_chat_safety(
            "Please send advance payment on WhatsApp and scan QR code to receive."
        )
        self.assertGreaterEqual(len(warnings), 2)

        neg = SafetyAndNegotiationHelper.suggest_negotiation_range(
            price_low=Decimal("700"),
            price_likely=Decimal("850"),
            price_high=Decimal("1050"),
            price_ask=Decimal("900"),
        )
        self.assertIsNotNone(neg["suggested_offer"])
        self.assertIn("₹", neg["suggestion"])


if __name__ == "__main__":
    unittest.main()
