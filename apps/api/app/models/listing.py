# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Listing and listing images database models with RLS support."""

import enum
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base


class ListingType(str, enum.Enum):
    SELL = "sell"
    DONATE = "donate"
    SWAP = "swap"


class ListingStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    RESERVED = "reserved"
    COMPLETED = "completed"
    REMOVED = "removed"


class Category(str, enum.Enum):
    ELECTRONICS = "electronics"
    FURNITURE = "furniture"
    BOOKS = "books"
    HOBBIES = "hobbies"


class ConditionGrade(str, enum.Enum):
    LIKE_NEW = "like_new"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


class FairDealGrade(str, enum.Enum):
    GREAT = "great"
    FAIR = "fair"
    OVERPRICED = "overpriced"


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seller_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    community_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("communities.id", ondelete="SET NULL"), nullable=True, index=True
    )

    type: Mapped[str] = mapped_column(String(20), default=ListingType.SELL.value, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    subtype: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    brand: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Condition
    condition: Mapped[str] = mapped_column(String(20), nullable=False)
    condition_ai: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    condition_conf: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Pricing
    price_ask: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    price_low: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    price_likely: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    price_high: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    price_ai_likely: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    fair_deal: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Additional attributes & location (coarse only)
    attributes: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    area_name: Mapped[str] = mapped_column(String(100), nullable=False)
    geohash5: Mapped[str] = mapped_column(String(5), nullable=False, index=True)

    status: Mapped[str] = mapped_column(
        String(20), default=ListingStatus.DRAFT.value, nullable=False, index=True
    )
    views: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    saves: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    data_origin: Mapped[str] = mapped_column(String(20), default="real", nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    images: Mapped[list["ListingImage"]] = relationship(
        "ListingImage", back_populates="listing", cascade="all, delete-orphan", order_by="ListingImage.order"
    )


class ListingImage(Base):
    __tablename__ = "listing_images"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("listings.id", ondelete="CASCADE"), nullable=False, index=True
    )
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    scrub_boxes: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list, nullable=False)
    scrubbed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    phash: Mapped[Optional[int]] = mapped_column(Numeric(20, 0), nullable=True)
    heatmap_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    listing: Mapped["Listing"] = relationship("Listing", back_populates="images")
