# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Pydantic schemas for realtime chat and user moderation reporting."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class MessageCreateRequest(BaseModel):
    listing_id: uuid.UUID
    receiver_id: uuid.UUID
    body: str = Field(..., min_length=1, max_length=2000)


class MessageResponse(BaseModel):
    id: uuid.UUID
    listing_id: uuid.UUID
    sender_id: uuid.UUID
    receiver_id: uuid.UUID
    body: str
    flagged_scam: bool
    read_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ThreadSummaryResponse(BaseModel):
    listing_id: uuid.UUID
    listing_title: str
    listing_price: Optional[float] = None
    other_user_id: uuid.UUID
    other_user_name: str
    other_user_verified: bool
    last_message_body: str
    last_message_at: datetime
    unread_count: int = 0


class ReportUserRequest(BaseModel):
    target_user_id: Optional[uuid.UUID] = None
    listing_id: Optional[uuid.UUID] = None
    message_id: Optional[uuid.UUID] = None
    reason: str = Field(..., min_length=5, max_length=1000)
    flag_type: str = Field(default="manual_report", pattern="^(manual_report|scam_text|price_anomaly)$")


class ReportResponse(BaseModel):
    id: uuid.UUID
    status: str = "open"
    detail: str = "Report submitted to moderators successfully."
