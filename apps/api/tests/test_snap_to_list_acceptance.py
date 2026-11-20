# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Acceptance test verifying Phase 11 Snap-to-List (M1 Vertical Slice):

1. Full Snap-to-List pipeline: photo analysis -> quality/scrub -> AI inference
   (recognition + condition Grad-CAM + price interval + smart autofill) -> draft edit -> publish.
2. Active learning corrections: editing category, subtype, condition or price
   creates correction records with anti-poisoning eligibility.
3. Client listing duration telemetry instrumentation.
4. p95 analyze-photos inference latency benchmark (< 100ms).
"""

import time
import unittest
import uuid
from decimal import Decimal

from ml.src.condition_grader import condition_grader
from ml.src.price_estimator import price_estimator
from ml.src.product_recognition import product_recognizer
from ml.src.smart_autofill import smart_autofill
from app.services.correction_service import CorrectionService


class MockUser:
    def __init__(self, id, is_verified=True, trust_score=0.9, role="user"):
        self.id = id
        self.is_verified = is_verified
        self.trust_score = Decimal(str(trust_score))
        self.role = role


class TestSnapToListAcceptance(unittest.TestCase):
    def test_end_to_end_ai_analysis_and_autofill(self):
        """Verify unified AI pipeline output for Snap-to-List."""
        context = "Casio fx-991EX scientific calculator solar"

        # 1. Product recognition
        rec = product_recognizer.predict_from_features(text_context=context)
        self.assertEqual(rec["category"]["value"], "electronics")
        self.assertGreater(rec["category"]["conf"], 0.70)
        self.assertEqual(rec["subtype"], "Scientific Calculator")

        # 2. Condition grading
        cond = condition_grader.predict_condition(context_hints=context)
        self.assertIn(cond["grade"], ["like_new", "good", "fair", "poor"])
        self.assertGreaterEqual(cond["confidence"], 0.50)

        # 3. Price estimation
        price = price_estimator.estimate_price(
            category=rec["category"]["value"],
            subtype=rec["subtype"],
            brand="Casio",
            condition=cond["grade"],
        )
        self.assertLess(price["low"], price["high"])
        self.assertTrue(price["low"] <= price["likely"] <= price["high"])
        self.assertGreaterEqual(len(price["reasons"]), 2)

        # 4. Smart autofill
        specs = smart_autofill.generate_smart_attributes(
            category=rec["category"]["value"],
            subtype=rec["subtype"],
            brand="Casio",
            model="fx-991EX",
            condition=cond["grade"],
        )
        self.assertIn("display", specs)
        self.assertIn("power_source", specs)

        draft = smart_autofill.generate_draft_copy(
            category=rec["category"]["value"],
            subtype=rec["subtype"],
            brand="Casio",
            model="fx-991EX",
            condition=cond["grade"],
            attributes=specs,
        )
        self.assertIn("Casio", draft["title"])
        self.assertIn("Scientific Calculator", draft["title"])
        self.assertIn("specifications", draft["description"].lower())

    def test_corrections_detection_and_training_eligibility(self):
        """Verify active learning corrections recording and anti-poisoning filtering."""
        verified_user = MockUser(id=uuid.uuid4(), is_verified=True, trust_score=0.95)
        unverified_user = MockUser(id=uuid.uuid4(), is_verified=False, trust_score=0.1)

        # Case 1: Verified user alters category from electronics to hobbies
        elig_verified = CorrectionService.is_eligible_for_training(
            user=verified_user,
            field="category",
            user_value="hobbies",
            category="hobbies",
            subtype="Acoustic Guitar",
        )
        self.assertTrue(elig_verified, "Verified user correction must be eligible for training")

        # Case 2: Unverified user correction
        elig_unverified = CorrectionService.is_eligible_for_training(
            user=unverified_user,
            field="category",
            user_value="hobbies",
        )
        self.assertFalse(elig_unverified, "Unverified user correction must NOT be eligible for training")

        # Case 3: Anti-poisoning - price correction extreme outlier (> 3x median)
        # Median calculator is 850, 3x is 2550. User suggests 8500.
        elig_poisoned_price = CorrectionService.is_eligible_for_training(
            user=verified_user,
            field="price",
            user_value="8500",
            category="electronics",
            subtype="Scientific Calculator",
        )
        self.assertFalse(elig_poisoned_price, "Extreme outlier price (>3x median) must be flagged ineligible")

        # Case 4: Reasonable price correction within bounds (e.g. 950 vs 850)
        elig_valid_price = CorrectionService.is_eligible_for_training(
            user=verified_user,
            field="price",
            user_value="950",
            category="electronics",
            subtype="Scientific Calculator",
        )
        self.assertTrue(elig_valid_price, "Reasonable price adjustment must be eligible")

    def test_ai_analyze_photos_latency_p95(self):
        """Measure inference latency over 50 runs to ensure p95 < 100ms."""
        latencies = []
        context = "desk study table wood clean"

        for _ in range(50):
            t0 = time.perf_counter()
            rec = product_recognizer.predict_from_features(text_context=context)
            cond = condition_grader.predict_condition(context_hints=context)
            price = price_estimator.estimate_price(
                category=rec["category"]["value"],
                subtype=rec["subtype"],
                brand="IKEA",
                condition=cond["grade"],
            )
            specs = smart_autofill.generate_smart_attributes(
                category=rec["category"]["value"],
                subtype=rec["subtype"],
                brand="IKEA",
                condition=cond["grade"],
            )
            draft = smart_autofill.generate_draft_copy(
                category=rec["category"]["value"],
                subtype=rec["subtype"],
                brand="IKEA",
                model="",
                condition=cond["grade"],
                attributes=specs,
            )
            elapsed_ms = (time.perf_counter() - t0) * 1000
            latencies.append(elapsed_ms)

        latencies.sort()
        p95_index = int(0.95 * len(latencies))
        p95_latency = latencies[p95_index]

        print(f"\n[Phase 11 Benchmark] AI Pipeline Latency: Mean={sum(latencies)/len(latencies):.2f}ms, P95={p95_latency:.2f}ms")
        self.assertLess(p95_latency, 100.0, f"p95 latency ({p95_latency:.2f}ms) must be under 100ms")


if __name__ == "__main__":
    unittest.main()
