# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Algorithmic environmental impact estimator with cited LCA lookup and sensitivity analysis.

Honesty label: `algorithmic` (rule-based lookup table + displacement factor range, NOT ML).

Implements ML_SPEC.md §12 and ROADMAP.md Phase 16:
- Reads cited embodied emissions (kg CO2e) and mass (kg) from `ml/data/impact_factors.csv`.
- Computes avoided CO2e and diverted waste across displacement factor range [0.30, 0.80]
  with central factor d = 0.55.
- Produces sensitivity analysis tables across d in {0.30, 0.45, 0.55, 0.70, 0.80}.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

FACTORS_CSV_PATH = Path(__file__).resolve().parents[1] / "data" / "impact_factors.csv"
DEFAULT_DISPLACEMENT_LOW = 0.30
DEFAULT_DISPLACEMENT_CENTRAL = 0.55
DEFAULT_DISPLACEMENT_HIGH = 0.80
SENSITIVITY_FACTORS: List[float] = [0.30, 0.45, 0.55, 0.70, 0.80]


def load_impact_factors(csv_path: Optional[Path] = None) -> Dict[Tuple[str, str], Dict[str, Any]]:
    """Load cited LCA impact factors keyed by `(category, subtype)`."""
    path = csv_path or FACTORS_CSV_PATH
    factors: Dict[Tuple[str, str], Dict[str, Any]] = {}
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cat = str(row["category"]).strip().lower()
            sub = str(row["subtype"]).strip().lower()
            factors[(cat, sub)] = {
                "category": cat,
                "subtype": sub,
                "embodied_co2_kg": float(row["embodied_co2_kg"]),
                "weight_kg": float(row["weight_kg"]),
                "source": str(row["source"]).strip(),
                "year": int(row["year"]),
                "confidence": str(row["confidence"]).strip(),
            }
    return factors


def lookup_item_factor(
    category: str,
    subtype: Optional[str] = None,
    factors: Optional[Dict[Tuple[str, str], Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Return the cited LCA factor entry for `(category, subtype)` with category fallback."""
    table = factors if factors is not None else load_impact_factors()
    cat_norm = (category or "electronics").strip().lower()
    sub_norm = (subtype or "default").strip().lower()

    if (cat_norm, sub_norm) in table:
        return table[(cat_norm, sub_norm)]
    if (cat_norm, "default") in table:
        return table[(cat_norm, "default")]
    return table[("electronics", "default")]


def estimate_item_impact(
    category: str,
    subtype: Optional[str] = None,
    displacement_low: float = DEFAULT_DISPLACEMENT_LOW,
    displacement_central: float = DEFAULT_DISPLACEMENT_CENTRAL,
    displacement_high: float = DEFAULT_DISPLACEMENT_HIGH,
) -> Dict[str, Any]:
    """Compute range-based avoided CO2e and material mass diverted for a single reused item."""
    factor = lookup_item_factor(category=category, subtype=subtype)
    embodied = float(factor["embodied_co2_kg"])
    weight = float(factor["weight_kg"])

    return {
        "methodology": "algorithmic",
        "category": factor["category"],
        "subtype": factor["subtype"],
        "embodied_co2_kg": embodied,
        "item_weight_kg": weight,
        "displacement_factor_range": [displacement_low, displacement_high],
        "displacement_factor_central": displacement_central,
        "co2_kg_avoided_low": round(embodied * displacement_low, 3),
        "co2_kg_avoided_central": round(embodied * displacement_central, 3),
        "co2_kg_avoided_high": round(embodied * displacement_high, 3),
        "weight_kg_diverted_low": round(weight * displacement_low, 3),
        "weight_kg_diverted_central": round(weight * displacement_central, 3),
        "weight_kg_diverted_high": round(weight * displacement_high, 3),
        "factor_source": factor["source"],
        "source_year": factor["year"],
        "confidence": factor["confidence"],
        "methodology_doc": "docs/IMPACT_METHOD.md",
    }


def generate_sensitivity_table(
    items: Iterable[Dict[str, Any]],
    displacement_grid: Optional[List[float]] = None,
) -> List[Dict[str, Any]]:
    """Generate a sensitivity table varying `reuse_displacement_factor` across [0.30 .. 0.80]."""
    grid = displacement_grid or SENSITIVITY_FACTORS
    item_list = list(items)
    factors = load_impact_factors()

    total_embodied_co2 = 0.0
    total_raw_weight = 0.0
    for item in item_list:
        f = lookup_item_factor(
            category=str(item.get("category", "electronics")),
            subtype=str(item.get("subtype", "default")),
            factors=factors,
        )
        total_embodied_co2 += float(f["embodied_co2_kg"])
        total_raw_weight += float(f["weight_kg"])

    rows: List[Dict[str, Any]] = []
    for d in grid:
        rows.append(
            {
                "displacement_factor": round(d, 2),
                "assumption_label": (
                    "Conservative (30%)"
                    if d <= 0.30
                    else ("Central Baseline (55%)" if abs(d - 0.55) < 1e-3 else f"d = {int(d * 100)}%")
                ),
                "total_co2_kg_avoided": round(total_embodied_co2 * d, 2),
                "total_weight_kg_diverted": round(total_raw_weight * d, 2),
            }
        )
    return rows


def aggregate_impact_summary(items: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate avoided CO2e ranges, per-category breakdown, cited sources, and sensitivity table."""
    item_list = list(items)
    co2_low = 0.0
    co2_central = 0.0
    co2_high = 0.0
    wt_low = 0.0
    wt_central = 0.0
    wt_high = 0.0

    per_category: Dict[str, Dict[str, Any]] = {}
    citations: Dict[str, Dict[str, Any]] = {}

    for item in item_list:
        est = estimate_item_impact(
            category=str(item.get("category", "electronics")),
            subtype=str(item.get("subtype", "default")),
        )
        co2_low += est["co2_kg_avoided_low"]
        co2_central += est["co2_kg_avoided_central"]
        co2_high += est["co2_kg_avoided_high"]
        wt_low += est["weight_kg_diverted_low"]
        wt_central += est["weight_kg_diverted_central"]
        wt_high += est["weight_kg_diverted_high"]

        cat = est["category"]
        if cat not in per_category:
            per_category[cat] = {
                "count": 0,
                "co2_kg_avoided_range": [0.0, 0.0],
                "co2_kg_avoided_central": 0.0,
                "weight_kg_diverted_central": 0.0,
            }
        per_category[cat]["count"] += 1
        per_category[cat]["co2_kg_avoided_range"][0] = round(
            per_category[cat]["co2_kg_avoided_range"][0] + est["co2_kg_avoided_low"], 2
        )
        per_category[cat]["co2_kg_avoided_range"][1] = round(
            per_category[cat]["co2_kg_avoided_range"][1] + est["co2_kg_avoided_high"], 2
        )
        per_category[cat]["co2_kg_avoided_central"] = round(
            per_category[cat]["co2_kg_avoided_central"] + est["co2_kg_avoided_central"], 2
        )
        per_category[cat]["weight_kg_diverted_central"] = round(
            per_category[cat]["weight_kg_diverted_central"] + est["weight_kg_diverted_central"], 2
        )

        src_key = est["factor_source"]
        citations[src_key] = {
            "source": src_key,
            "year": est["source_year"],
            "confidence": est["confidence"],
        }

    return {
        "methodology": "algorithmic",
        "methodology_label": "Algorithmic LCA Lookup & Displacement Range Estimator (Not ML)",
        "methodology_doc": "docs/IMPACT_METHOD.md",
        "completed_reuses_count": len(item_list),
        "co2_kg_avoided_range": [round(co2_low, 2), round(co2_high, 2)],
        "co2_kg_avoided_central": round(co2_central, 2),
        "weight_kg_diverted_range": [round(wt_low, 2), round(wt_high, 2)],
        "weight_kg_diverted_central": round(wt_central, 2),
        "displacement_factor_range": [DEFAULT_DISPLACEMENT_LOW, DEFAULT_DISPLACEMENT_HIGH],
        "displacement_factor_central": DEFAULT_DISPLACEMENT_CENTRAL,
        "per_category": per_category,
        "sensitivity_table": generate_sensitivity_table(item_list),
        "cited_sources": list(citations.values()),
    }
