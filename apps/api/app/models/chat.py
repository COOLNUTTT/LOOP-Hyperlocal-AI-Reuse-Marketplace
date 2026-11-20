# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Chat message and moderation flag database models."""

import enum
import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base


class FlagType(str, enum.Enum):
    DUPLICATE_IMAGE = "duplicate_image"
    PRICE_ANOMALY = "price_anomaly"
    SCAM_TEXT = "scam_text"
    SENSITIVE_CONTENT = "sensitive_content"
    MANUAL_REPORT = "manual_report"


class FlagStatus(str, enum.Enum):
    OPEN = "open"
    UPHELD = "upheld"
    DISMISSED = "dismissed"


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("listings.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sender_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    receiver_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    body: Mapped[str] = mapped_column(Text, nullable=False)
    flagged_scam: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    # Relationships
    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])
    listing = relationship("Listing")


class Flag(Base):
    __tablename__ = "flags"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("listings.id", ondelete="CASCADE"), nullable=True, index=True
    )
    message_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("messages.id", ondelete="CASCADE"), nullable=True, index=True
    )
    reporter_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    flag_type: Mapped[str] = mapped_column(String(50), default=FlagType.MANUAL_REPORT.value, nullable=False)
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=FlagStatus.OPEN.value, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    resolved_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
