# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Phase 2 (Track B) Acceptance Tests: Data Collection, Deduplication, Splits & Labelling Guide."""

from __future__ import annotations

import json
from pathlib import Path

from ml.src.data_pipeline import (
    build_synthetic_dataset_records,
    compute_perceptual_hash_64,
    compute_weighted_cohens_kappa,
    hamming_distance_64,
    resolve_annotator_label,
    run_phase02_data_pipeline,
    stratified_split_by_listing,
    verify_zero_cross_split_leakage,
)

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_ethics_ownership_and_labelling_guide_exist() -> None:
    """Verify ethics/consent protocol, ownership agreement, and labelling guide exist."""
    guide_path = REPO_ROOT / "docs" / "DATA_COLLECTION_AND_LABELLING_GUIDE.md"
    ip_path = REPO_ROOT / "docs" / "IP_AND_COMPLIANCE.md"
    ls_config_path = REPO_ROOT / "ml" / "configs" / "label_studio_interface.xml"
    licenses_path = REPO_ROOT / "ml" / "data" / "LICENSES.md"

    assert guide_path.exists()
    assert ip_path.exists()
    assert ls_config_path.exists()
    assert licenses_path.exists()

    guide_text = guide_path.read_text(encoding="utf-8")
    assert "VOLUNTEER PHOTO & STAGED SCRUBBING CONSENT FORM (TEMPLATE)" in guide_text
    assert "like_new" in guide_text and "Quadratic Weighted Cohen's Kappa" in guide_text


def test_split_determinism_and_zero_cross_split_near_duplicates() -> None:
    """Verify split script is deterministic (same hash twice) and zero near-dups cross splits."""
    records_run1 = build_synthetic_dataset_records(num_listings=80, seed=42)
    records_run2 = build_synthetic_dataset_records(num_listings=80, seed=42)

    split_1 = stratified_split_by_listing(records_run1, seed=42)
    split_2 = stratified_split_by_listing(records_run2, seed=42)

    assert split_1["manifest_sha256"] == split_2["manifest_sha256"]
    assert split_1["dropped_near_duplicates"] == 4

    leakage = verify_zero_cross_split_leakage(split_1, max_hamming=6)
    assert leakage["zero_listing_overlap"] is True
    assert leakage["zero_near_duplicate_leakage"] is True
    assert leakage["cross_split_near_duplicates_found"] == 0


def test_phash_and_weighted_cohens_kappa() -> None:
    """Verify 64-bit phash Hamming distance and Quadratic Weighted Cohen's Kappa calculation."""
    h1 = compute_perceptual_hash_64(b"calculator-photo-1")
    h2 = h1 ^ 0b101  # flip 2 bits
    assert hamming_distance_64(h1, h2) == 2

    # Identical raters -> kappa = 1.0
    assert compute_weighted_cohens_kappa([0, 1, 2, 3], [0, 1, 2, 3], weights="quadratic") == 1.0
    # High agreement raters -> kappa > 0.80
    qwk = compute_weighted_cohens_kappa(
        [0, 1, 2, 3, 2, 1, 3, 0],
        [0, 1, 2, 3, 2, 2, 3, 0],
        weights="quadratic",
    )
    assert 0.80 < qwk < 1.0
    assert resolve_annotator_label(1, 3, tie_breaker_c=3) == 3


def test_full_phase02_pipeline_manifest_and_templates() -> None:
    """Verify Phase 2 pipeline generates manifest, stats report, and 50 EN/Hinglish queries."""
    summary = run_phase02_data_pipeline()
    assert summary["data_origin"] == "simulated"
    assert summary["leakage_verification"]["zero_listing_overlap"] is True
    assert summary["leakage_verification"]["zero_near_duplicate_leakage"] is True

    manifest_file = REPO_ROOT / "ml" / "data" / "manifests" / "dataset_split_manifest.json"
    report_file = REPO_ROOT / "ml" / "reports" / "data_pipeline" / "report.md"
    queries_file = REPO_ROOT / "ml" / "data" / "templates" / "search_queries_50_en_hinglish.json"
    price_tpl = REPO_ROOT / "ml" / "data" / "templates" / "local_price_observations_template.csv"

    assert manifest_file.exists()
    assert report_file.exists()
    assert queries_file.exists()
    assert price_tpl.exists()

    queries_data = json.loads(queries_file.read_text(encoding="utf-8"))
    assert queries_data["total_queries"] == 50
    assert queries_data["english_count"] == 25
    assert queries_data["hinglish_count"] == 25
