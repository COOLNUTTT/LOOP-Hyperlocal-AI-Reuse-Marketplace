# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Hazard-style dynamic price-drop heuristic with floor and 15%-step guardrails (Phase 17).

Honesty label: `heuristic` / `algorithmic` (survival/hazard logistic model, NOT deep ML).

Implements ML_SPEC.md §11 and ROADMAP.md Phase 17:
- Estimates P(sale within 7 days | listing age, views, saves, chats, ask/likely price ratio).
- Trigger rule: active >= 7 days with zero offers and price above floor.
- Hard safety invariants:
  1. Never suggests a price below the floor (`max(0.60 * predicted_low, explicit_floor)`).
  2. Never suggests a drop larger than 15% in a single step (`drop_fraction <= 0.15`).
- Compares hazard heuristic vs `no_drop` and `fixed_schedule` (-10% every 7 days) baselines.
"""

from __future__ import annotations

import math
from typing import Any, Dict, Optional

MAX_STEP_DROP_FRACTION = 0.15
DEFAULT_FLOOR_LOW_MULTIPLIER = 0.60


def estimate_sale_probability_7d(
    price_ask: float,
    predicted_likely: float,
    days_active: int = 7,
    views: int = 20,
    saves: int = 1,
    chats_started: int = 0,
    category: str = "electronics",
) -> float:
    """Estimate P(sale <= 7 days) using a calibrated survival/hazard logistic function."""
    safe_likely = max(1.0, float(predicted_likely))
    price_ratio = float(price_ask) / safe_likely

    cat_offset = {
        "electronics": 0.15,
        "books": 0.20,
        "furniture": -0.10,
        "hobbies": 0.05,
    }.get(category.strip().lower(), 0.0)

    # Logit: higher price_ratio and longer staleness without offers reduce 7d sale hazard
    view_signal = min(0.6, math.log1p(max(0, views)) * 0.12)
    engagement_signal = min(0.8, saves * 0.18 + chats_started * 0.25)
    staleness_penalty = min(0.9, max(0, days_active - 3) * 0.04)

    logit = (
        1.35
        - 2.60 * (price_ratio - 1.0)
        + view_signal
        + engagement_signal
        - staleness_penalty
        + cat_offset
    )
    prob = 1.0 / (1.0 + math.exp(-max(-10.0, min(10.0, logit))))
    return round(float(prob), 4)


def compute_price_drop_suggestion(
    price_ask: float,
    predicted_low: float,
    predicted_likely: float,
    days_active: int = 7,
    views: int = 24,
    category_median_views: int = 15,
    saves: int = 1,
    chats_started: int = 0,
    offers_count: int = 0,
    min_days_active: int = 7,
    explicit_floor: Optional[float] = None,
    category: str = "electronics",
) -> Dict[str, Any]:
    """Compute a guardrail-enforced price-drop suggestion for an active listing.

    Hard invariants:
    - If `should_drop` is True (or for any returned `suggested_price` when `price_ask >= floor`):
      1. `suggested_price >= floor_price` (where `floor_price = max(0.60 * predicted_low, explicit_floor)`).
      2. `(price_ask - suggested_price) / price_ask <= 0.15 + 1e-9` (never beyond 15% per step).
    """
    ask = round(float(price_ask), 2)
    low = max(1.0, float(predicted_low))
    likely = max(low, float(predicted_likely))

    floor_price = round(
        max(DEFAULT_FLOOR_LOW_MULTIPLIER * low, float(explicit_floor or 0.0)),
        2,
    )

    p_before = estimate_sale_probability_7d(
        price_ask=ask,
        predicted_likely=likely,
        days_active=days_active,
        views=views,
        saves=saves,
        chats_started=chats_started,
        category=category,
    )

    # If already at or below floor, or not yet eligible for a drop trigger, hold price
    if ask <= floor_price or days_active < min_days_active or offers_count > 0:
        hold_price = max(ask, floor_price) if ask >= floor_price else ask
        return {
            "methodology": "heuristic_hazard",
            "methodology_label": "Algorithmic Survival/Hazard Heuristic (Not ML)",
            "should_drop": False,
            "current_price": ask,
            "suggested_price": hold_price,
            "drop_pct": 0.0,
            "floor_price": floor_price,
            "max_step_drop_pct": 15.0,
            "p_sale_7d_before": p_before,
            "p_sale_7d_after": p_before,
            "reason": {
                "summary": (
                    "Listing is already at or below the floor price guardrail."
                    if ask <= floor_price
                    else "Listing is still within initial observation window or has active offers."
                ),
                "days_active": days_active,
                "views": views,
                "floor_enforced": ask <= floor_price,
            },
        }

    # Lower bound enforces BOTH the 15% single-step cap AND the floor price simultaneously
    min_step_price = round(ask * (1.0 - MAX_STEP_DROP_FRACTION), 2)
    lower_bound = max(floor_price, min_step_price)

    # Choose lowest-regret target price toward predicted_likely bounded by [lower_bound, ask]
    desired_target = round(min(ask * 0.90, max(likely, floor_price)), 2)
    suggested_price = round(max(lower_bound, min(ask, desired_target)), 2)

    # Final clamp to guarantee hard invariants against floating-point rounding
    if suggested_price < floor_price:
        suggested_price = floor_price
    if ask > 0 and (ask - suggested_price) / ask > MAX_STEP_DROP_FRACTION:
        suggested_price = round(math.ceil(ask * (1.0 - MAX_STEP_DROP_FRACTION) * 100.0) / 100.0, 2)
        suggested_price = max(floor_price, suggested_price)

    drop_amount = max(0.0, round(ask - suggested_price, 2))
    drop_pct = round((drop_amount / ask) * 100.0, 2) if ask > 0 else 0.0
    should_drop = drop_amount >= 1.0

    p_after = estimate_sale_probability_7d(
        price_ask=suggested_price,
        predicted_likely=likely,
        days_active=days_active,
        views=views,
        saves=saves,
        chats_started=chats_started,
        category=category,
    )

    view_note = (
        f"{views} views (above category median {category_median_views})"
        if views >= category_median_views
        else f"{views} views"
    )
    summary = (
        f"No offers in {days_active} days despite {view_note}; "
        f"dropping to ₹{suggested_price:.0f} (-{drop_pct:.1f}%) raises estimated 7-day sale "
        f"chance from {int(round(p_before * 100))}% to {int(round(p_after * 100))}%."
    )

    return {
        "methodology": "heuristic_hazard",
        "methodology_label": "Algorithmic Survival/Hazard Heuristic (Not ML)",
        "should_drop": should_drop,
        "current_price": ask,
        "suggested_price": suggested_price,
        "drop_pct": drop_pct,
        "floor_price": floor_price,
        "max_step_drop_pct": 15.0,
        "p_sale_7d_before": p_before,
        "p_sale_7d_after": p_after,
        "reason": {
            "summary": summary,
            "days_active": days_active,
            "views": views,
            "category_median_views": category_median_views,
            "floor_enforced": suggested_price == floor_price,
            "step_cap_enforced": suggested_price == min_step_price,
        },
    }
