# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""ORM models for hazard-style price-drop suggestions and historical price observations."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.models.base import Base


class PriceDropSuggestion(Base):
    __tablename__ = "price_drop_suggestions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("listings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    suggested_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    reason: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    p_sale_7d_before: Mapped[float] = mapped_column(Float, nullable=False)
    p_sale_7d_after: Mapped[float] = mapped_column(Float, nullable=False)
    accepted: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )


class PriceHistory(Base):
    __tablename__ = "price_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    subtype: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    brand: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    condition: Mapped[str] = mapped_column(String(30), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    source: Mapped[str] = mapped_column(String(50), default="completed_trade", nullable=False)
    data_origin: Mapped[str] = mapped_column(String(20), default="simulated", nullable=False)
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
