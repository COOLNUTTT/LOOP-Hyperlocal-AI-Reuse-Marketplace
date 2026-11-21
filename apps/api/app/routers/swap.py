# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""FastAPI router for wishlists and algorithmic multi-party swap proposals."""

import uuid
from decimal import Decimal
from typing import Annotated, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from ml.src.semantic_search import embed_text
from pydantic import BaseModel, Field
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_db_user
from app.dependencies.database import get_db
from app.models.identity import User
from app.models.swap import SwapCycle, SwapProposal, Wishlist
from app.services.swap_service import SwapService

router = APIRouter(tags=["swap"])


class WishlistCreateRequest(BaseModel):
    want_category: str = Field(..., pattern="^(electronics|furniture|books|hobbies)$")
    want_text: str = Field(..., min_length=2, max_length=300)
    max_price: Optional[Decimal] = Field(default=None, ge=Decimal("0"))


@router.post("/wishlists", status_code=status.HTTP_201_CREATED)
async def create_wishlist_item(
    payload: WishlistCreateRequest,
    current_user: Annotated[User, Depends(get_current_db_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Create a user wishlist entry with 384-d semantic embedding for swap graph matching."""
    emb = embed_text(f"{payload.want_text} {payload.want_category}")
    row = Wishlist(
        user_id=current_user.id,
        want_category=payload.want_category,
        want_text=payload.want_text,
        want_embedding=emb,
        max_price=payload.max_price,
        active=True,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return {
        "id": str(row.id),
        "user_id": str(row.user_id),
        "want_category": row.want_category,
        "want_text": row.want_text,
        "max_price": float(row.max_price) if row.max_price is not None else None,
        "active": row.active,
        "methodology": "algorithmic",
    }


@router.get("/wishlists")
async def list_my_wishlists(
    current_user: Annotated[User, Depends(get_current_db_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[Any]:
    """List active wishlist wants for the authenticated user."""
    stmt = (
        select(Wishlist)
        .where(Wishlist.user_id == current_user.id, Wishlist.active.is_(True))
        .order_by(Wishlist.created_at.desc())
    )
    res = await db.execute(stmt)
    return list(res.scalars().all())


@router.get("/swap/proposals")
async def list_my_swap_proposals(
    current_user: Annotated[User, Depends(get_current_db_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """List multi-party swap proposals involving the current user (labelled algorithmic)."""
    stmt = select(SwapProposal).where(
        or_(
            SwapProposal.giver_user_id == current_user.id,
            SwapProposal.receiver_user_id == current_user.id,
        )
    )
    res = await db.execute(stmt)
    proposals = list(res.scalars().all())
    return {
        "methodology": "algorithmic",
        "methodology_label": "Algorithmic Graph Cycle Set-Packing (CP-SAT, length <= 3, Not ML)",
        "proposals": proposals,
    }


@router.post("/swap/proposals/{proposal_id}/confirm")
async def confirm_swap_proposal(
    proposal_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_db_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Confirm the user's edge in a swap cycle; cycle confirms only when all parties confirm."""
    p_stmt = select(SwapProposal).where(SwapProposal.id == proposal_id)
    p_res = await db.execute(p_stmt)
    proposal = p_res.scalar_one_or_none()
    if proposal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Swap proposal not found."
        )

    c_stmt = select(SwapCycle).where(SwapCycle.id == proposal.cycle_id)
    c_res = await db.execute(c_stmt)
    cycle = c_res.scalar_one_or_none()
    if cycle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Swap cycle not found.")

    all_stmt = select(SwapProposal).where(SwapProposal.cycle_id == cycle.id)
    all_res = await db.execute(all_stmt)
    all_proposals = list(all_res.scalars().all())

    outcome = SwapService.confirm_proposal_and_check_cycle(
        target_proposal=proposal,
        confirming_user_id=current_user.id,
        cycle=cycle,
        all_cycle_proposals=all_proposals,
    )
    await db.commit()
    return outcome
