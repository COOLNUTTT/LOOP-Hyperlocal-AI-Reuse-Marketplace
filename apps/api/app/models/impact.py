# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""ORM model for environmental impact events traced to completed handovers."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.models.base import Base


class ImpactEvent(Base):
    __tablename__ = "impact_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    handover_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("handover_events.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    listing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("listings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    co2_kg_avoided: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    ewaste_kg_avoided: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    factor_source: Mapped[str] = mapped_column(String(255), nullable=False)
    assumptions: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
