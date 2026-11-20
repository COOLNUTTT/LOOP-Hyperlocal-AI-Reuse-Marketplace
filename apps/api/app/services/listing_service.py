# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Service layer for listings management, status transitions, search & discovery."""

import uuid
from decimal import Decimal
from typing import Any, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.listing import FairDealGrade, Listing, ListingImage, ListingStatus


class ListingService:
    @staticmethod
    def calculate_fair_deal_badge(
        price_ask: Optional[Decimal],
        price_likely: Optional[Decimal],
        listing_type: str,
    ) -> Optional[str]:
        """Compute fair deal classification."""
        if listing_type == "donate" or (price_ask is not None and price_ask == Decimal("0.00")):
            return FairDealGrade.GREAT.value

        if price_ask is None or price_likely is None or price_likely <= Decimal("0.00"):
            return None

        ratio = price_ask / price_likely
        if ratio <= Decimal("0.85"):
            return FairDealGrade.GREAT.value
        elif ratio <= Decimal("1.15"):
            return FairDealGrade.FAIR.value
        else:
            return FairDealGrade.OVERPRICED.value

    @staticmethod
    async def create_listing(
        db: AsyncSession,
        seller_id: uuid.UUID,
        payload_data: dict[str, Any],
    ) -> Listing:
        """Create a new listing in draft status."""
        # Calculate fair deal badge if not provided
        if not payload_data.get("fair_deal"):
            payload_data["fair_deal"] = ListingService.calculate_fair_deal_badge(
                price_ask=payload_data.get("price_ask"),
                price_likely=payload_data.get("price_likely") or payload_data.get("price_ai_likely"),
                listing_type=payload_data.get("type", "sell"),
            )

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
    async def list_listings(
        db: AsyncSession,
        q: Optional[str] = None,
        category: Optional[str] = None,
        listing_type: Optional[str] = None,
        condition: Optional[str] = None,
        price_min: Optional[Decimal] = None,
        price_max: Optional[Decimal] = None,
        area_name: Optional[str] = None,
        geohash5: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[list[Listing], int]:
        """Filter and paginate active listings."""
        stmt = select(Listing).where(Listing.status == ListingStatus.ACTIVE.value)

        if q:
            term = f"%{q.strip()}%"
            stmt = stmt.where(
                or_(
                    Listing.title.ilike(term),
                    Listing.description.ilike(term),
                    Listing.subtype.ilike(term),
                    Listing.brand.ilike(term),
                )
            )

        if category:
            stmt = stmt.where(Listing.category == category)

        if listing_type:
            stmt = stmt.where(Listing.type == listing_type)

        if condition:
            stmt = stmt.where(Listing.condition == condition)

        if price_min is not None:
            stmt = stmt.where(Listing.price_ask >= price_min)

        if price_max is not None:
            stmt = stmt.where(Listing.price_ask <= price_max)

        if area_name:
            stmt = stmt.where(Listing.area_name.ilike(f"%{area_name.strip()}%"))

        if geohash5:
            # Match 5-char geohash or prefix
            stmt = stmt.where(Listing.geohash5.startswith(geohash5.strip().lower()[:5]))

        # Count total matches
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar_one()

        # Eager load images and paginate
        stmt = (
            stmt.options(selectinload(Listing.images))
            .order_by(Listing.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        result = await db.execute(stmt)
        items = list(result.scalars().all())
        return items, total

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

        # Re-evaluate fair deal badge if price updated
        if "price_ask" in update_data:
            listing.fair_deal = ListingService.calculate_fair_deal_badge(
                price_ask=listing.price_ask,
                price_likely=listing.price_likely or listing.price_ai_likely,
                listing_type=listing.type,
            )

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
