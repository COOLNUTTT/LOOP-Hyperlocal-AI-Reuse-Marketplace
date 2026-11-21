# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Scrub-verify safeguard endpoint router."""

import uuid
from typing import Annotated, Any, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from ml.src.privacy_scrubber import PrivacyScrubberDetector
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_db_user
from app.dependencies.database import get_db
from app.models.identity import User

router = APIRouter(prefix="/listings", tags=["scrubber-safeguard"])


@router.post("/{listing_id}/scrub-verify")
async def verify_listing_photo_scrub(
    listing_id: uuid.UUID,
    file: UploadFile = File(...),
    current_user: Annotated[Optional[User], Depends(get_current_db_user)] = None,
    db: Annotated[Optional[AsyncSession], Depends(get_db)] = None,
) -> dict[str, Any]:
    """Server-side safeguard verifying uploaded images are free of unblurred faces/plates/IDs."""
    image_bytes = await file.read()

    is_safe, detected_leaks = PrivacyScrubberDetector.inspect_image_for_unscrubbed_sensitive_data(
        image_bytes=image_bytes
    )

    if not is_safe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "UNSCRUBBED_SENSITIVE_DATA_DETECTED",
                "message": (
                    "Server safeguard detected unblurred sensitive regions (faces/plates/IDs). "
                    "Please apply on-device blur before uploading."
                ),
                "detected_regions": detected_leaks,
            },
        )

    return {
        "status": "verified_safe",
        "listing_id": str(listing_id),
        "detail": (
            "Image passed server-side privacy safeguard scan. "
            "No unblurred sensitive objects detected."
        ),
    }
