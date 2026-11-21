# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Service layer for multi-party swap cycle confirmation and per-edge handovers."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

from fastapi import HTTPException, status


class SwapService:
    @staticmethod
    def confirm_proposal_and_check_cycle(
        target_proposal: Any,
        confirming_user_id: uuid.UUID,
        cycle: Any,
        all_cycle_proposals: List[Any],
    ) -> Dict[str, Any]:
        """Record a participant's confirmation on their swap proposal edge.

        A swap cycle transitions to `confirmed` ONLY when ALL participants confirm.
        When all confirm, generates per-edge handover specifications.
        """
        giver_id = getattr(target_proposal, "giver_user_id", None)
        if giver_id != confirming_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the item giver on this swap proposal edge may confirm it.",
            )

        now = datetime.now(timezone.utc)
        if getattr(target_proposal, "confirmed_at", None) is None:
            target_proposal.confirmed_at = now

        confirmed_count = sum(
            1 for p in all_cycle_proposals if getattr(p, "confirmed_at", None) is not None
        )
        total_edges = len(all_cycle_proposals)
        all_confirmed = total_edges >= 2 and confirmed_count == total_edges

        per_edge_handovers: List[Dict[str, Any]] = []
        if all_confirmed:
            cycle.status = "confirmed"
            for prop in all_cycle_proposals:
                per_edge_handovers.append(
                    {
                        "cycle_id": getattr(cycle, "id", None),
                        "proposal_id": getattr(prop, "id", None),
                        "listing_id": getattr(prop, "listing_id", None),
                        "seller_id": getattr(prop, "giver_user_id", None),
                        "buyer_id": getattr(prop, "receiver_user_id", None),
                        "status": "pending",
                    }
                )
        else:
            cycle.status = "partially_confirmed"

        return {
            "methodology": "algorithmic",
            "cycle_id": str(getattr(cycle, "id", "")),
            "cycle_status": cycle.status,
            "confirmed_count": confirmed_count,
            "required_confirmations": total_edges,
            "all_confirmed": all_confirmed,
            "per_edge_handovers": per_edge_handovers,
        }
