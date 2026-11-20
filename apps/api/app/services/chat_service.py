# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Service layer for chat messages, threads, and block/report actions."""

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.chat import Flag, FlagStatus, FlagType, Message
from app.models.identity import User
from app.models.listing import Listing
from app.services.chat_rate_limiter import chat_rate_limiter


class ChatService:
    @staticmethod
    async def send_message(
        db: AsyncSession,
        sender_id: uuid.UUID,
        listing_id: uuid.UUID,
        receiver_id: uuid.UUID,
        body: str,
    ) -> Message:
        """Send message in listing thread with 60/min rate limiting."""
        # Enforce rate limit (Roadmap constraint: 60/min)
        if not chat_rate_limiter.check_and_record(str(sender_id)):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Maximum 60 messages per minute allowed.",
            )

        if sender_id == receiver_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot message yourself.",
            )

        msg = Message(
            listing_id=listing_id,
            sender_id=sender_id,
            receiver_id=receiver_id,
            body=body.strip(),
        )
        db.add(msg)
        await db.commit()
        await db.refresh(msg)
        return msg

    @staticmethod
    async def get_thread_messages(
        db: AsyncSession,
        listing_id: uuid.UUID,
        user_id: uuid.UUID,
        other_user_id: Optional[uuid.UUID] = None,
    ) -> List[Message]:
        """Fetch messages between participants in a listing thread."""
        stmt = (
            select(Message)
            .where(
                Message.listing_id == listing_id,
                or_(
                    Message.sender_id == user_id,
                    Message.receiver_id == user_id,
                ),
            )
            .order_by(Message.created_at.asc())
        )

        if other_user_id:
            stmt = stmt.where(
                or_(
                    (Message.sender_id == user_id) & (Message.receiver_id == other_user_id),
                    (Message.sender_id == other_user_id) & (Message.receiver_id == user_id),
                )
            )

        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def create_report(
        db: AsyncSession,
        reporter_id: uuid.UUID,
        reason: str,
        listing_id: Optional[uuid.UUID] = None,
        message_id: Optional[uuid.UUID] = None,
        flag_type: str = FlagType.MANUAL_REPORT.value,
    ) -> Flag:
        """Create a manual moderation report / flag."""
        flag = Flag(
            reporter_id=reporter_id,
            listing_id=listing_id,
            message_id=message_id,
            flag_type=flag_type,
            reason=reason.strip(),
            status=FlagStatus.OPEN.value,
        )
        db.add(flag)
        await db.commit()
        await db.refresh(flag)
        return flag


chat_service = ChatService()
