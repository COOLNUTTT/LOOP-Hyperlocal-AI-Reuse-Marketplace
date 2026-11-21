# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Master figure and report generator for the LOOP research paper (PAPER_PLAN.md §4).

Regenerates all report figures and tables from deterministic logged runs and writes
`ml/reports/figure_manifest.json` mapping every figure #1..#8 in ML_SPEC §15 to its
source run script, data_origin, and SHA-256 file hash.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

from ml.src.eval_active_learning import run_active_learning_experiment
from ml.src.eval_fraud import run_evaluation as run_fraud_evaluation
from ml.src.eval_semantic_search import EVAL_QUERIES, _rank_semantic, evaluate_subset
from ml.src.eval_system_validation import run_three_journeys_and_load_benchmark
from ml.src.eval_user_study_and_ablations import run_user_study_analysis_and_ablations
from sim.simulator import run_all_simulator_experiments

REPORTS_ROOT = Path(__file__).resolve().parent


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def generate_all_figures_and_manifest() -> Dict[str, Any]:
    """Run all logged evaluation scripts and produce `ml/reports/figure_manifest.json`."""
    run_active_learning_experiment()
    _ = evaluate_subset(EVAL_QUERIES, _rank_semantic)
    run_fraud_evaluation()
    run_all_simulator_experiments(seed=42)
    run_user_study_analysis_and_ablations(seed=42)
    run_three_journeys_and_load_benchmark(iterations=100)

    figure_entries: List[Dict[str, Any]] = [
        {
            "figure_number": 1,
            "title": "Active learning: accuracy/QWK/MAPE vs corrections (3 strategies, 5-seed error bands)",
            "phase": "Phase 15",
            "generator_script": "ml/src/eval_active_learning.py",
            "artifact_path": "ml/reports/active_learning/active_learning_curves_synthetic.svg",
            "data_origin": "simulated",
        },
        {
            "figure_number": 2,
            "title": "On-device vs server latency + size/upload trade-off",
            "phase": "Phase 7",
            "generator_script": "ml/src/quality_checker.py",
            "artifact_path": "ml/reports/ondevice_vs_server/report.md",
            "data_origin": "simulated",
        },
        {
            "figure_number": 3,
            "title": "Scrubber per-class recall/precision + residual leak rate",
            "phase": "Phase 7",
            "generator_script": "ml/src/privacy_scrubber.py",
            "artifact_path": "ml/model_cards/privacy_scrubber.md",
            "data_origin": "simulated",
        },
        {
            "figure_number": 4,
            "title": "Price: split-conformal 80% interval coverage + plain-language SHAP",
            "phase": "Phase 10",
            "generator_script": "ml/src/price_estimator.py",
            "artifact_path": "ml/model_cards/price_estimator.md",
            "data_origin": "simulated",
        },
        {
            "figure_number": 5,
            "title": "Condition grading: confusion matrix, QWK + Grad-CAM saliency",
            "phase": "Phase 9",
            "generator_script": "ml/src/condition_grader.py",
            "artifact_path": "ml/model_cards/condition_grader.md",
            "data_origin": "simulated",
        },
        {
            "figure_number": 6,
            "title": "Semantic search: Recall@k and NDCG@10 vs FTS baseline (English vs Hinglish)",
            "phase": "Phase 12",
            "generator_script": "ml/src/eval_semantic_search.py",
            "artifact_path": "ml/reports/semantic_search/report.md",
            "data_origin": "simulated",
        },
        {
            "figure_number": 7,
            "title": "Simulator: swap scaling (100->10k), trust AUC, fraud PR curves, price-drop TTS",
            "phase": "Phase 17",
            "generator_script": "sim/simulator.py",
            "artifact_path": "ml/reports/simulator/simulator_figures_synthetic.svg",
            "data_origin": "simulated",
        },
        {
            "figure_number": 8,
            "title": "User-study statistical pipeline verification (Simulated cohort; Live study: TBD)",
            "phase": "Phase 18",
            "generator_script": "ml/src/eval_user_study_and_ablations.py",
            "artifact_path": "ml/reports/user_study/user_study_figure_synthetic.svg",
            "data_origin": "simulated",
        },
    ]

    repo_root = REPORTS_ROOT.parents[1]
    for entry in figure_entries:
        full_path = repo_root / entry["artifact_path"]
        if full_path.exists():
            entry["sha256"] = _sha256_file(full_path)
            entry["exists"] = True
        else:
            entry["sha256"] = None
            entry["exists"] = False

    manifest = {
        "paper_tag": "paper-v1",
        "reproducible": True,
        "all_figures_present": all(bool(e["exists"]) for e in figure_entries),
        "figures": figure_entries,
    }
    manifest_path = REPORTS_ROOT / "figure_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    generate_all_figures_and_manifest()
