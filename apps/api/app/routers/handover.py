# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""FastAPI router for handover events, OTP confirmation, gated reviews, and trust scores."""

import uuid
from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.handover import HandoverEvent, Review
from app.models.identity import User
from app.models.listing import Listing, ListingStatus
from app.services.handover_service import HandoverService
from app.services.trust_service import TrustService

router = APIRouter(prefix="/handover", tags=["handover"])


class InitiateHandoverRequest(BaseModel):
    listing_id: uuid.UUID
    buyer_id: uuid.UUID
    meetup_spot: str = Field(..., min_length=3, max_length=200)


class InitiateHandoverResponse(BaseModel):
    id: uuid.UUID
    listing_id: uuid.UUID
    meetup_spot: str
    otp_code: str
    otp_expires_at: datetime
    status: str


class ConfirmHandoverRequest(BaseModel):
    otp_code: str = Field(..., min_length=6, max_length=6)


class HandoverStatusResponse(BaseModel):
    id: uuid.UUID
    listing_id: uuid.UUID
    buyer_confirmed: bool
    seller_confirmed: bool
    status: str
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CreateReviewRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=1000)


class ReviewResponse(BaseModel):
    id: uuid.UUID
    handover_id: uuid.UUID
    reviewer_id: uuid.UUID
    reviewee_id: uuid.UUID
    rating: int
    comment: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


@router.get("/meetup-spots", response_model=list[str])
async def get_meetup_spots(area_name: str = ""):
    """Return curated public campus/society meetup spots."""
    return HandoverService.get_meetup_suggestions(area_name)


@router.post("/initiate", response_model=InitiateHandoverResponse, status_code=status.HTTP_201_CREATED)
async def initiate_handover(
    payload: InitiateHandoverRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Initiate a handover event with a 6-digit OTP."""
    stmt = select(Listing).where(Listing.id == payload.listing_id)
    res = await db.execute(stmt)
    listing = res.scalar_one_or_none()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found.")

    otp_code, otp_hash, expires_at = HandoverService.generate_otp()
    handover = HandoverEvent(
        listing_id=listing.id,
        buyer_id=payload.buyer_id,
        seller_id=listing.seller_id,
        meetup_spot=payload.meetup_spot,
        otp_hash=otp_hash,
        otp_expires_at=expires_at,
    )
    db.add(handover)
    await db.commit()
    await db.refresh(handover)

    return InitiateHandoverResponse(
        id=handover.id,
        listing_id=handover.listing_id,
        meetup_spot=handover.meetup_spot,
        otp_code=otp_code,
        otp_expires_at=handover.otp_expires_at,
        status=handover.status,
    )


@router.post("/{handover_id}/confirm", response_model=HandoverStatusResponse)
async def confirm_handover(
    handover_id: uuid.UUID,
    payload: ConfirmHandoverRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Confirm handover with OTP. Transitions listing to completed once both confirm."""
    stmt = select(HandoverEvent).where(HandoverEvent.id == handover_id)
    res = await db.execute(stmt)
    handover = res.scalar_one_or_none()
    if not handover:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Handover event not found.")

    try:
        HandoverService.verify_and_confirm(handover, current_user.id, payload.otp_code)
    except HTTPException:
        await db.commit()
        raise

    if handover.status == "completed":
        l_stmt = select(Listing).where(Listing.id == handover.listing_id)
        l_res = await db.execute(l_stmt)
        listing = l_res.scalar_one_or_none()
        if listing:
            listing.status = ListingStatus.COMPLETED.value
            listing.completed_at = handover.completed_at

    await db.commit()
    await db.refresh(handover)
    return handover


@router.post("/{handover_id}/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    handover_id: uuid.UUID,
    payload: CreateReviewRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Submit a review gated on a completed handover."""
    stmt = select(HandoverEvent).where(HandoverEvent.id == handover_id)
    res = await db.execute(stmt)
    handover = res.scalar_one_or_none()

    TrustService.validate_review_allowed(handover, current_user.id)

    reviewee_id = handover.seller_id if current_user.id == handover.buyer_id else handover.buyer_id
    review = Review(
        handover_id=handover.id,
        reviewer_id=current_user.id,
        reviewee_id=reviewee_id,
        rating=payload.rating,
        comment=payload.comment,
    )
    db.add(review)
    await db.commit()
    await db.refresh(review)
    return review


@router.get("/users/{user_id}/trust-score")
async def get_trust_score(
    user_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Return user's trust score and visible additive breakdown."""
    u_stmt = select(User).where(User.id == user_id)
    u_res = await db.execute(u_stmt)
    user = u_res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    r_stmt = select(Review.rating).where(Review.reviewee_id == user_id)
    r_res = await db.execute(r_stmt)
    ratings = list(r_res.scalars().all())

    h_stmt = select(HandoverEvent).where(
        HandoverEvent.status == "completed",
        (HandoverEvent.buyer_id == user_id) | (HandoverEvent.seller_id == user_id),
    )
    h_res = await db.execute(h_stmt)
    completed_count = len(list(h_res.scalars().all()))

    return TrustService.compute_trust_breakdown(
        is_verified=user.is_verified,
        completed_trades=completed_count,
        ratings=ratings,
    )
