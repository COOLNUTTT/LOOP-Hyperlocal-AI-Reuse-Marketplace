# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""FastAPI router for listings and image uploads."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.identity import User
from app.schemas.listing import (
    ListingCreateRequest,
    ListingDetailResponse,
    ListingImageResponse,
    ListingUpdateRequest,
    PublishListingResponse,
)
from app.services.image_service import ImageProcessingService
from app.services.listing_service import ListingService

router = APIRouter(prefix="/listings", tags=["listings"])


@router.post("", response_model=ListingDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_listing(
    payload: ListingCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a new listing draft."""
    data = payload.model_dump()
    listing = await ListingService.create_listing(db, current_user.id, data)
    return listing


@router.get("/{listing_id}", response_model=ListingDetailResponse)
async def get_listing(
    listing_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get listing details."""
    return await ListingService.get_listing(db, listing_id)


@router.patch("/{listing_id}", response_model=ListingDetailResponse)
async def update_listing(
    listing_id: uuid.UUID,
    payload: ListingUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update listing details."""
    data = payload.model_dump(exclude_unset=True)
    return await ListingService.update_listing(db, listing_id, current_user.id, data)


@router.post("/{listing_id}/publish", response_model=PublishListingResponse)
async def publish_listing(
    listing_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Publish a listing. Fails with 400 if any image is unscrubbed."""
    listing = await ListingService.publish_listing(db, listing_id, current_user.id)
    return PublishListingResponse(
        id=listing.id,
        status=listing.status,
        detail="Listing published successfully.",
    )


@router.post("/{listing_id}/images", response_model=ListingImageResponse)
async def upload_listing_image(
    listing_id: uuid.UUID,
    file: UploadFile = File(...),
    scrubbed: bool = Form(False),
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
):
    """Upload an image, validate format/size, strip EXIF metadata, and attach to listing."""
    file_bytes = await file.read()
    clean_bytes, content_type = ImageProcessingService.validate_and_strip_exif(
        file_bytes, file.content_type or "image/jpeg"
    )

    # In production, save to Supabase Storage; for local sandbox, store in storage path
    storage_path = f"listings/{listing_id}/{uuid.uuid4()}.jpg"

    return await ListingService.add_image(
        db=db,
        listing_id=listing_id,
        seller_id=current_user.id,
        storage_path=storage_path,
        scrubbed=scrubbed,
        quality_score=0.92,
    )
