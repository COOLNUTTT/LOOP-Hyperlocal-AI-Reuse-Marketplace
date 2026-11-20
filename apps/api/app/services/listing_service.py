# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Service layer for listings management, status transitions, and publishing guards."""

import uuid
from decimal import Decimal
from typing import Any, Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.listing import Listing, ListingImage, ListingStatus


class ListingService:
    @staticmethod
    async def create_listing(
        db: AsyncSession,
        seller_id: uuid.UUID,
        payload_data: dict[str, Any],
    ) -> Listing:
        """Create a new listing in draft status."""
        listing = Listing(
            seller_id=seller_id,
            status=ListingStatus.DRAFT.value,
            **payload_data,
        )
        db.add(listing)
        await db.commit()
        await db.refresh(listing)
        return listing

    @staticmethod
    async def get_listing(
        db: AsyncSession,
        listing_id: uuid.UUID,
    ) -> Listing:
        """Retrieve listing with images eagerly loaded."""
        stmt = (
            select(Listing)
            .where(Listing.id == listing_id)
            .options(selectinload(Listing.images))
        )
        result = await db.execute(stmt)
        listing = result.scalar_one_or_none()
        if not listing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Listing not found.",
            )
        return listing

    @staticmethod
    async def update_listing(
        db: AsyncSession,
        listing_id: uuid.UUID,
        seller_id: uuid.UUID,
        update_data: dict[str, Any],
    ) -> Listing:
        """Update draft or active listing owned by seller."""
        listing = await ListingService.get_listing(db, listing_id)
        if listing.seller_id != seller_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to modify this listing.",
            )

        for key, value in update_data.items():
            if value is not None and hasattr(listing, key):
                setattr(listing, key, value)

        await db.commit()
        await db.refresh(listing)
        return listing

    @staticmethod
    async def publish_listing(
        db: AsyncSession,
        listing_id: uuid.UUID,
        seller_id: uuid.UUID,
    ) -> Listing:
        """Publish a listing. Requires all images to have scrubbed=True."""
        listing = await ListingService.get_listing(db, listing_id)
        if listing.seller_id != seller_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to publish this listing.",
            )

        if not listing.images:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot publish a listing without at least one photo.",
            )

        # Roadmap constraint: cannot publish unless all images scrubbed = true
        unscrubbed_images = [img for img in listing.images if not img.scrubbed]
        if unscrubbed_images:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="LISTING_NOT_SCRUBBED: All images must be verified and scrubbed of private faces, plates, and phone numbers before publishing.",
            )

        listing.status = ListingStatus.ACTIVE.value
        await db.commit()
        await db.refresh(listing)
        return listing

    @staticmethod
    async def add_image(
        db: AsyncSession,
        listing_id: uuid.UUID,
        seller_id: uuid.UUID,
        storage_path: str,
        scrubbed: bool = False,
        quality_score: Optional[float] = None,
        scrub_boxes: list[dict[str, Any]] = None,
    ) -> ListingImage:
        """Attach an image to a listing."""
        listing = await ListingService.get_listing(db, listing_id)
        if listing.seller_id != seller_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to attach images to this listing.",
            )

        image = ListingImage(
            listing_id=listing_id,
            storage_path=storage_path,
            order=len(listing.images),
            quality_score=quality_score,
            scrubbed=scrubbed,
            scrub_boxes=scrub_boxes or [],
        )
        db.add(image)
        await db.commit()
        await db.refresh(image)
        return image
