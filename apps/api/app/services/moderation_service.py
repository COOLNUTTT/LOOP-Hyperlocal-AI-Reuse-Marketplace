# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Service layer for human-in-the-loop moderation, audit logging, and model health."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

from fastapi import HTTPException, status

ALLOWED_MOD_ACTIONS = {"uphold", "dismiss", "remove", "warn"}


class ModerationService:
    @staticmethod
    def apply_moderator_action(
        flag: Any,
        moderator_id: uuid.UUID,
        action: str,
        notes: str = "",
        listing: Any = None,
    ) -> Dict[str, Any]:
        """Apply a human moderator decision and return an audit log payload.

        No listing is auto-removed without a human decision.
        """
        action_norm = action.strip().lower()
        if action_norm not in ALLOWED_MOD_ACTIONS:
            allowed = sorted(ALLOWED_MOD_ACTIONS)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid moderation action: {action}. Must be one of {allowed}.",
            )

        now = datetime.now(timezone.utc)
        if action_norm in {"uphold", "remove", "warn"}:
            flag.status = "upheld"
        elif action_norm == "dismiss":
            flag.status = "dismissed"

        flag.resolved_by = moderator_id
        flag.resolved_at = now

        if action_norm == "remove" and listing is not None:
            listing.status = "removed"

        audit_entry = {
            "actor_id": moderator_id,
            "action": f"moderation.{action_norm}",
            "target_type": "flag",
            "target_id": flag.id,
            "details": {
                "flag_type": getattr(flag, "flag_type", None),
                "reason": getattr(flag, "reason", None),
                "notes": notes,
                "listing_removed": action_norm == "remove",
            },
        }
        return audit_entry

    @staticmethod
    def compute_model_health(confidences: List[float]) -> Dict[str, Any]:
        """Compute confidence histogram and drift indicator for model-health dashboard."""
        bins = {"0.0-0.5": 0, "0.5-0.7": 0, "0.7-0.85": 0, "0.85-1.0": 0}
        for c in confidences:
            if c < 0.5:
                bins["0.0-0.5"] += 1
            elif c < 0.7:
                bins["0.5-0.7"] += 1
            elif c < 0.85:
                bins["0.7-0.85"] += 1
            else:
                bins["0.85-1.0"] += 1

        mean_conf = round(sum(confidences) / len(confidences), 4) if confidences else 0.0
        low_conf_ratio = round(bins["0.0-0.5"] / len(confidences), 4) if confidences else 0.0
        drift_status = "drift_warning" if low_conf_ratio > 0.25 else "healthy"

        return {
            "sample_count": len(confidences),
            "mean_confidence": mean_conf,
            "low_confidence_ratio": low_conf_ratio,
            "drift_status": drift_status,
            "confidence_histogram": bins,
        }
