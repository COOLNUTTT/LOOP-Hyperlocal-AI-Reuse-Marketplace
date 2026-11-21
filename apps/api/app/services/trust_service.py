# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Service layer for gated peer reviews and transparent trust score breakdown."""

from __future__ import annotations

from typing import Any, Dict, List

from fastapi import HTTPException, status


class TrustService:
    @staticmethod
    def validate_review_allowed(handover: Any, reviewer_id: Any) -> None:
        """Gate reviews on completed handover; raise 403 otherwise."""
        if not handover or getattr(handover, "status", None) != "completed":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "REVIEW_NOT_ALLOWED: Reviews can only be submitted after a completed handover."
                ),
            )
        if reviewer_id not in (handover.buyer_id, handover.seller_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only handover participants can leave a review.",
            )

    @staticmethod
    def compute_trust_breakdown(
        is_verified: bool,
        completed_trades: int,
        ratings: List[int],
        upheld_flags: int = 0,
    ) -> Dict[str, Any]:
        """Compute additive trust score (0..100) with visible component breakdown."""
        verified_pts = 25.0 if is_verified else 0.0
        trades_pts = round(min(max(completed_trades, 0) * 5.0, 35.0), 2)

        if ratings:
            avg_rating = sum(ratings) / len(ratings)
            review_pts = round((avg_rating / 5.0) * 30.0, 2)
        else:
            review_pts = 15.0  # Neutral prior for new members

        safety_pts = round(max(0.0, 10.0 - max(upheld_flags, 0) * 5.0), 2)
        total_score = round(verified_pts + trades_pts + review_pts + safety_pts, 2)

        return {
            "total_score": total_score,
            "breakdown": {
                "verified_community": verified_pts,
                "completed_trades": trades_pts,
                "review_rating": review_pts,
                "safety_record": safety_pts,
            },
        }
