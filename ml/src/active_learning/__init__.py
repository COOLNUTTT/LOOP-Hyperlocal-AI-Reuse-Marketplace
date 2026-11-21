# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Active learning package for human-in-the-loop retraining and gated promotion."""

from ml.src.active_learning.retrain import (
    DEFAULT_ACTIVE_METRICS,
    PRIMARY_METRICS,
    compute_item_hash,
    deduplicate_conflicting_corrections,
    evaluate_promotion_gate,
    filter_eligible_corrections,
    load_frozen_test_hashes,
    retrain_from_corrections,
    rollback_model_version,
    verify_no_test_set_leakage,
)

__all__ = [
    "DEFAULT_ACTIVE_METRICS",
    "PRIMARY_METRICS",
    "compute_item_hash",
    "deduplicate_conflicting_corrections",
    "evaluate_promotion_gate",
    "filter_eligible_corrections",
    "load_frozen_test_hashes",
    "retrain_from_corrections",
    "rollback_model_version",
    "verify_no_test_set_leakage",
]
