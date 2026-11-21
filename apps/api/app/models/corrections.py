# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Active learning corrections model for tracking seller overrides on AI predictions."""

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base


class CorrectionField(str, enum.Enum):
    CATEGORY = "category"
    SUBTYPE = "subtype"
    CONDITION = "condition"
    PRICE = "price"


class Correction(Base):
    __tablename__ = "corrections"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("listings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    field: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    ai_value: Mapped[str] = mapped_column(Text, nullable=False)
    user_value: Mapped[str] = mapped_column(Text, nullable=False)
    ai_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    model_version: Mapped[str] = mapped_column(String(50), default="v1.0.0", nullable=False)
    eligible_for_training: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, index=True
    )
    data_origin: Mapped[str] = mapped_column(String(20), default="real", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    # Relationships
    listing = relationship("Listing", backref="corrections")
    user = relationship("User", backref="corrections")
