# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Service layer for safe peer handover, curated meetup spots, and OTP/QR confirmation."""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, List, Tuple

from fastapi import HTTPException, status

CURATED_MEETUP_SPOTS: List[str] = [
    "Main Campus Library Entrance (CCTV)",
    "Student Activity Center Reception",
    "Central Canteen Courtyard",
    "Hostel Gate Security Desk",
    "Society Clubhouse Lobby (CCTV)",
]

MAX_OTP_ATTEMPTS = 5
OTP_EXPIRY_MINUTES = 15


class HandoverService:
    @staticmethod
    def get_meetup_suggestions(area_name: str = "") -> List[str]:
        """Return curated public campus/society meetup spots."""
        return list(CURATED_MEETUP_SPOTS)

    @staticmethod
    def generate_otp(expiry_minutes: int = OTP_EXPIRY_MINUTES) -> Tuple[str, str, datetime]:
        """Generate a 6-digit OTP, its SHA-256 hash, and UTC expiry timestamp."""
        otp_code = f"{secrets.randbelow(1000000):06d}"
        otp_hash = hashlib.sha256(otp_code.encode("utf-8")).hexdigest()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=expiry_minutes)
        return otp_code, otp_hash, expires_at

    @staticmethod
    def verify_and_confirm(
        handover: Any,
        actor_id: Any,
        otp_code: str,
        now: datetime | None = None,
    ) -> Any:
        """Verify OTP (checking expiry & attempt limits) and record buyer/seller confirmation.

        Transitions handover.status -> 'completed' only after BOTH buyer and seller confirm.
        """
        current_time = now or datetime.now(timezone.utc)

        if actor_id not in (handover.buyer_id, handover.seller_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the buyer or seller can confirm this handover.",
            )

        if handover.status == "completed":
            return handover

        # Check attempt limit
        if handover.otp_attempts >= MAX_OTP_ATTEMPTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="OTP_ATTEMPTS_EXCEEDED: Maximum verification attempts reached.",
            )

        # Check expiry
        expires_at = handover.otp_expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if current_time > expires_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP_EXPIRED: Handover code has expired. Please generate a new one.",
            )

        # Verify OTP hash
        candidate_hash = hashlib.sha256(otp_code.strip().encode("utf-8")).hexdigest()
        if candidate_hash != handover.otp_hash:
            handover.otp_attempts += 1
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="INVALID_OTP: Incorrect handover verification code.",
            )

        # Record confirmation for the calling party
        if actor_id == handover.buyer_id:
            handover.buyer_confirmed = True
        if actor_id == handover.seller_id:
            handover.seller_confirmed = True

        # Transition status
        if handover.buyer_confirmed and handover.seller_confirmed:
            handover.status = "completed"
            handover.completed_at = current_time
        elif handover.buyer_confirmed:
            handover.status = "buyer_confirmed"
        elif handover.seller_confirmed:
            handover.status = "seller_confirmed"

        return handover
