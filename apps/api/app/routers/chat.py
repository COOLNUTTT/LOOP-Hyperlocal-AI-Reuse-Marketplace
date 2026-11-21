# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""FastAPI router for chat threads, messaging, and moderation reports."""

import uuid
from typing import Annotated, Any, List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.identity import User
from app.schemas.chat import (
    MessageCreateRequest,
    MessageResponse,
    ReportResponse,
    ReportUserRequest,
)
from app.services.chat_service import chat_service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    payload: MessageCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Any:
    """Send a message to a seller or buyer. Rate-limited to 60/min."""
    return await chat_service.send_message(
        db=db,
        sender_id=current_user.id,
        listing_id=payload.listing_id,
        receiver_id=payload.receiver_id,
        body=payload.body,
    )


@router.get("/threads/{listing_id}", response_model=List[MessageResponse])
async def get_thread_messages(
    listing_id: uuid.UUID,
    other_user_id: Optional[uuid.UUID] = Query(None),
    current_user: Annotated[Optional[User], Depends(get_current_user)] = None,
    db: Annotated[Optional[AsyncSession], Depends(get_db)] = None,
) -> List[Any]:
    """Get message history for a listing thread."""
    if db is None or current_user is None:
        return []
    return await chat_service.get_thread_messages(
        db=db,
        listing_id=listing_id,
        user_id=current_user.id,
        other_user_id=other_user_id,
    )


@router.post("/report", response_model=ReportResponse)
async def report_user(
    payload: ReportUserRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ReportResponse:
    """Report a suspicious user, message, or listing for scam or abuse."""
    flag = await chat_service.create_report(
        db=db,
        reporter_id=current_user.id,
        reason=payload.reason,
        listing_id=payload.listing_id,
        message_id=payload.message_id,
        flag_type=payload.flag_type,
    )
    return ReportResponse(id=flag.id, status=flag.status)
