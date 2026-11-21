# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Acceptance tests for Phase 15 Active Learning Loop (Human-in-the-Loop):

1. Anti-poisoning eligibility rules & conflicting-correction deduplication.
2. Frozen test-set hash guard: no test-set item can appear in retraining data.
3. Gated promotion: a candidate that fails to beat the active model (or regresses a class)
   is NOT promoted; rollback restores the previous version.
4. End-to-end `retrain_from_corrections` runs from `corrections` rows for
   product_recognition, condition_grader, and price_estimator.
5. Multi-seed experiment (>=5 seeds, 3 strategies, 10% & 20% label-noise variants)
   produces an error-band SVG figure with a clearly labelled "Simulated Corrections" caption.
"""

import unittest
import uuid
from datetime import datetime, timedelta, timezone

from ml.src.active_learning.retrain import (
    DEFAULT_ACTIVE_METRICS,
    deduplicate_conflicting_corrections,
    load_frozen_test_hashes,
    retrain_from_corrections,
    rollback_model_version,
    verify_no_test_set_leakage,
)
from ml.src.eval_active_learning import REPORT_DIR, run_active_learning_experiment

from app.services.correction_service import CorrectionService
from app.services.moderation_service import ModerationService


class DummyUser:
    def __init__(
        self,
        is_verified: bool = True,
        trust_score: float = 0.8,
        completed_trades: int = 2,
        role: str = "user",
    ) -> None:
        self.id = uuid.uuid4()
        self.is_verified = is_verified
        self.trust_score = trust_score
        self.completed_trades = completed_trades
        self.role = role


class TestPhase15ActiveLearningAcceptance(unittest.TestCase):
    def test_anti_poisoning_eligibility_and_deduplication(self) -> None:
        """Verify anti-poisoning rules and conflicting correction deduplication."""
        verified_user = DummyUser(is_verified=True, completed_trades=2)
        unverified_user = DummyUser(is_verified=False, trust_score=0.1, completed_trades=0)
        zero_trade_user = DummyUser(is_verified=True, trust_score=0.9, completed_trades=0)

        # Unverified or zero-trade user rejected
        self.assertFalse(
            CorrectionService.is_eligible_for_training(unverified_user, "category", "electronics")
        )
        self.assertFalse(
            CorrectionService.is_eligible_for_training(zero_trade_user, "category", "electronics")
        )

        # Verified user with >= 1 completed trade accepted for valid price, rejected for 10x poison
        self.assertTrue(
            CorrectionService.is_eligible_for_training(
                verified_user,
                "price",
                "600.00",
                category="electronics",
                subtype="Scientific Calculator",
            )
        )
        self.assertFalse(
            CorrectionService.is_eligible_for_training(
                verified_user,
                "price",
                "50000.00",
                category="electronics",
                subtype="Scientific Calculator",
            )
        )

        # Conflicting corrections on the same listing + field keep only the latest
        shared_listing_id = uuid.uuid4()
        t1 = datetime(2026, 10, 28, 9, 0, tzinfo=timezone.utc)
        t2 = t1 + timedelta(minutes=15)
        conflicts = [
            {
                "listing_id": shared_listing_id,
                "field": "condition",
                "ai_value": "good",
                "user_value": "fair",
                "eligible_for_training": True,
                "created_at": t1,
            },
            {
                "listing_id": shared_listing_id,
                "field": "condition",
                "ai_value": "good",
                "user_value": "like_new",
                "eligible_for_training": True,
                "created_at": t2,
            },
        ]
        deduped = deduplicate_conflicting_corrections(conflicts)
        self.assertEqual(len(deduped), 1)
        self.assertEqual(deduped[0]["user_value"], "like_new")

    def test_no_test_set_item_in_retraining_data(self) -> None:
        """Verify that any frozen test-set item hash is blocked from entering retraining."""
        frozen_hashes = load_frozen_test_hashes()
        self.assertGreater(len(frozen_hashes), 0)
        sample_test_hash = "frozen_test_rec_0001_a8f5f167f44f4964e6c998dee827110c"
        self.assertIn(sample_test_hash, frozen_hashes)

        leaked_corrections = [
            {
                "listing_id": sample_test_hash,
                "field": "category",
                "ai_value": "books",
                "user_value": "electronics",
                "eligible_for_training": True,
            }
        ]
        with self.assertRaises(ValueError) as ctx:
            verify_no_test_set_leakage(leaked_corrections, frozen_hashes=frozen_hashes)
        self.assertIn("Test-set leakage detected", str(ctx.exception))

        with self.assertRaises(ValueError):
            retrain_from_corrections("product_recognition", leaked_corrections)

    def test_candidate_failing_to_beat_active_model_is_not_promoted(self) -> None:
        """Verify a candidate failing to beat the active model or regressing a class fails."""
        corrections = [
            {
                "listing_id": str(uuid.uuid4()),
                "field": "category",
                "ai_value": "books",
                "user_value": "electronics",
                "ai_confidence": 0.45,
                "eligible_for_training": True,
            }
        ]

        # 1. Candidate fails to beat active primary metric (0.9100 < 0.9260)
        regressed_primary = {
            "top1_accuracy": 0.9100,
            "macro_f1": 0.9010,
            "per_class": {
                "electronics": 0.9200,
                "furniture": 0.9100,
                "books": 0.9100,
                "hobbies": 0.9000,
            },
        }
        res_fail = retrain_from_corrections(
            model_name="product_recognition",
            corrections=corrections,
            candidate_version="v1.1.0-bad",
            candidate_metrics_override=regressed_primary,
        )
        self.assertFalse(res_fail["is_active"])
        self.assertFalse(res_fail["gate_decision"]["promoted"])
        self.assertIsNone(res_fail["promoted_at"])

        # 2. Candidate beats overall top1_accuracy (0.9310 > 0.9260) but regresses 'hobbies' by 0.04
        class_regression_candidate = {
            "top1_accuracy": 0.9310,
            "macro_f1": 0.9220,
            "per_class": {
                "electronics": 0.9600,
                "furniture": 0.9400,
                "books": 0.9500,
                "hobbies": 0.8700,  # active is 0.9140 -> 0.044 regression > 0.015 tolerance
            },
        }
        res_cls_fail = retrain_from_corrections(
            model_name="product_recognition",
            corrections=corrections,
            candidate_version="v1.1.0-skewed",
            candidate_metrics_override=class_regression_candidate,
        )
        self.assertFalse(res_cls_fail["is_active"])
        self.assertFalse(res_cls_fail["gate_decision"]["promoted"])
        self.assertEqual(res_cls_fail["gate_decision"]["regressed_class"], "hobbies")

    def test_end_to_end_retrain_and_rollback(self) -> None:
        """Verify end-to-end retraining from corrections rows across all three models."""
        corrections = [
            {
                "listing_id": f"train_item_{i}",
                "field": field,
                "ai_value": "old",
                "user_value": "new",
                "ai_confidence": 0.42,
                "eligible_for_training": True,
            }
            for i in range(6)
            for field in ("category", "subtype", "condition", "price")
        ]

        for model_name in ("product_recognition", "condition_grader", "price_estimator"):
            result = retrain_from_corrections(
                model_name=model_name,
                corrections=corrections,
                candidate_version="v1.1.0",
            )
            self.assertTrue(result["is_active"])
            self.assertTrue(result["gate_decision"]["promoted"])
            self.assertGreater(result["eligible_corrections_used"], 0)
            self.assertIsNotNone(result["promoted_at"])

        # Test rollback
        v1 = {
            "name": "product_recognition",
            "version": "v1.0.0",
            "metrics": DEFAULT_ACTIVE_METRICS["product_recognition"],
            "is_active": False,
        }
        v2 = {
            "name": "product_recognition",
            "version": "v1.1.0",
            "metrics": DEFAULT_ACTIVE_METRICS["product_recognition"],
            "is_active": True,
        }
        restored = rollback_model_version([v1, v2], "product_recognition")
        self.assertEqual(restored["version"], "v1.0.0")
        self.assertTrue(v1["is_active"])
        self.assertFalse(v2["is_active"])

        # Test admin stats aggregation
        stats = ModerationService.compute_corrections_stats(corrections)
        self.assertEqual(stats["total_corrections"], 24)
        self.assertEqual(stats["eligible_for_training"], 24)

    def test_active_learning_experiment_and_figure_caption(self) -> None:
        """Verify multi-seed experiment (>=5 seeds, 3 strategies, 10%/20% noise) and SVG caption."""
        payload = run_active_learning_experiment()
        self.assertEqual(payload["data_origin"], "simulated")
        self.assertGreaterEqual(len(payload["seeds"]), 5)
        self.assertEqual(set(payload["strategies"]), {"random", "uncertainty", "correction_stream"})
        self.assertIn("clean_0pct_noise", payload)
        self.assertIn("noise_10pct", payload)
        self.assertIn("noise_20pct", payload)

        # Correction stream at 400 corrections beats random at 400 corrections
        clean_rec = payload["clean_0pct_noise"]["product_recognition"]
        self.assertGreater(
            clean_rec["correction_stream"]["400"]["mean"],
            clean_rec["random"]["400"]["mean"],
        )

        svg_path = REPORT_DIR / "active_learning_curves_synthetic.svg"
        self.assertTrue(svg_path.exists())
        svg_text = svg_path.read_text(encoding="utf-8")
        self.assertIn("<polygon", svg_text)
        self.assertIn("Simulated Corrections", svg_text)
        self.assertIn("data_origin='simulated'", svg_text)


if __name__ == "__main__":
    unittest.main()
