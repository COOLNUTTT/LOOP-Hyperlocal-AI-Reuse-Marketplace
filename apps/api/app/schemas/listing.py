# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Pydantic schemas for listings, status transitions, and image upload."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ListingImageResponse(BaseModel):
    id: uuid.UUID
    listing_id: uuid.UUID
    storage_path: str
    order: int
    quality_score: Optional[float] = None
    scrub_boxes: list[dict[str, Any]] = []
    scrubbed: bool
    heatmap_path: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ListingCreateRequest(BaseModel):
    type: str = Field(default="sell", pattern="^(sell|donate|swap)$")
    category: str = Field(..., pattern="^(electronics|furniture|books|hobbies)$")
    subtype: Optional[str] = Field(None, max_length=100)
    brand: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=5, max_length=5000)

    condition: str = Field(..., pattern="^(like_new|good|fair|poor)$")
    condition_ai: Optional[str] = Field(None, pattern="^(like_new|good|fair|poor)$")
    condition_conf: Optional[float] = Field(None, ge=0.0, le=1.0)

    price_ask: Optional[Decimal] = Field(None, ge=0)
    price_low: Optional[Decimal] = Field(None, ge=0)
    price_likely: Optional[Decimal] = Field(None, ge=0)
    price_high: Optional[Decimal] = Field(None, ge=0)
    price_ai_likely: Optional[Decimal] = Field(None, ge=0)
    fair_deal: Optional[str] = Field(None, pattern="^(great|fair|overpriced)$")

    attributes: dict[str, Any] = Field(default_factory=dict)
    area_name: str = Field(..., min_length=2, max_length=100)
    geohash5: str = Field(..., min_length=5, max_length=5)
    community_id: Optional[uuid.UUID] = None

    # Snap-to-List AI baseline state and telemetry for active learning corrections
    ai_baseline: Optional[dict[str, Any]] = None
    client_listing_duration_ms: Optional[int] = None

    @field_validator("geohash5")
    @classmethod
    def validate_geohash5(cls, v: str) -> str:
        if len(v) != 5:
            raise ValueError("geohash5 must have precision length of exactly 5")
        return v.lower()


class ListingUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, min_length=5, max_length=5000)
    category: Optional[str] = Field(None, pattern="^(electronics|furniture|books|hobbies)$")
    subtype: Optional[str] = Field(None, max_length=100)
    brand: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    condition: Optional[str] = Field(None, pattern="^(like_new|good|fair|poor)$")
    price_ask: Optional[Decimal] = Field(None, ge=0)
    attributes: Optional[dict[str, Any]] = None
    area_name: Optional[str] = Field(None, min_length=2, max_length=100)
    geohash5: Optional[str] = Field(None, min_length=5, max_length=5)

    # Active learning corrections tracking
    ai_baseline: Optional[dict[str, Any]] = None

    @field_validator("geohash5")
    @classmethod
    def validate_geohash5(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if len(v) != 5:
                raise ValueError("geohash5 must have precision length of exactly 5")
            return v.lower()
        return v


class ListingDetailResponse(BaseModel):
    id: uuid.UUID
    seller_id: uuid.UUID
    community_id: Optional[uuid.UUID] = None
    type: str
    category: str
    subtype: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    title: str
    description: str
    condition: str
    condition_ai: Optional[str] = None
    condition_conf: Optional[float] = None
    price_ask: Optional[Decimal] = None
    price_low: Optional[Decimal] = None
    price_likely: Optional[Decimal] = None
    price_high: Optional[Decimal] = None
    price_ai_likely: Optional[Decimal] = None
    fair_deal: Optional[str] = None
    attributes: dict[str, Any] = {}
    area_name: str
    geohash5: str
    status: str
    views: int
    saves: int
    data_origin: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    images: list[ListingImageResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ListingListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[ListingDetailResponse]
    applied_filters: dict[str, Any] = {}


class PublishListingResponse(BaseModel):
    id: uuid.UUID
    status: str = "active"
    detail: str = "Listing published successfully."
