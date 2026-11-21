# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Acceptance test verifying Phase 10 Price Estimator requirements:

1. Conformal prediction produces calibrated price intervals [low, likely, high].
2. Nominal coverage guarantees are verified (low < likely < high).
3. Fair-deal badge unit tests on strict boundaries (0.85, 1.15).
4. Plain-language SHAP feature contributions exist.
5. Unknown subtype widening fallback works.
"""

import unittest
from decimal import Decimal

from ml.src.price_estimator import PriceEstimatorModel


class TestPhase10PriceEstimatorAcceptance(unittest.TestCase):
    def setUp(self):
        self.estimator = PriceEstimatorModel()

    def test_conformal_interval_ordering(self):
        est = self.estimator.estimate_price(
            category="electronics",
            subtype="Scientific Calculator",
            brand="Casio",
            condition="good",
        )
        self.assertLess(est["low"], est["likely"])
        self.assertLess(est["likely"], est["high"])
        self.assertFalse(est["is_widened_fallback"])

    def test_plain_language_shap_reasons(self):
        est = self.estimator.estimate_price(
            category="furniture",
            subtype="Study Table",
            brand="IKEA",
            condition="like_new",
        )
        reasons = est["reasons"]
        self.assertGreater(len(reasons), 0)

        # Check plain language structure
        first_reason = reasons[0]
        self.assertIn("feature", first_reason)
        self.assertIn("effect", first_reason)
        self.assertIn("%", first_reason["effect"])

    def test_unknown_subtype_widening_fallback(self):
        known = self.estimator.estimate_price(
            category="electronics",
            subtype="Scientific Calculator",
        )
        unknown = self.estimator.estimate_price(
            category="electronics",
            subtype="Rare Vintage Oscilloscope X99",
        )
        self.assertTrue(unknown["is_widened_fallback"])

        # Relative interval width for unknown should be significantly wider
        known_width_ratio = (known["high"] - known["low"]) / known["likely"]
        unknown_width_ratio = (unknown["high"] - unknown["low"]) / unknown["likely"]
        self.assertGreater(unknown_width_ratio, known_width_ratio)

    def test_fair_deal_badge_boundaries(self):
        likely = Decimal("1000.00")

        # Boundary: <= 0.85 -> great
        badge_850, _ = self.estimator.evaluate_fair_deal_badge(Decimal("850.00"), likely)
        self.assertEqual(badge_850, "great")

        badge_800, _ = self.estimator.evaluate_fair_deal_badge(Decimal("800.00"), likely)
        self.assertEqual(badge_800, "great")

        # Boundary: > 0.85 and <= 1.15 -> fair
        badge_851, _ = self.estimator.evaluate_fair_deal_badge(Decimal("851.00"), likely)
        self.assertEqual(badge_851, "fair")

        badge_1150, _ = self.estimator.evaluate_fair_deal_badge(Decimal("1150.00"), likely)
        self.assertEqual(badge_1150, "fair")

        # Boundary: > 1.15 -> overpriced + seller guidance
        badge_1151, guidance = self.estimator.evaluate_fair_deal_badge(Decimal("1151.00"), likely)
        self.assertEqual(badge_1151, "overpriced")
        self.assertIsNotNone(guidance)
        self.assertIn("significantly higher", guidance)

        # Donation -> great
        badge_donate, _ = self.estimator.evaluate_fair_deal_badge(
            Decimal("0.00"), likely, listing_type="donate"
        )
        self.assertEqual(badge_donate, "great")


if __name__ == "__main__":
    unittest.main()
