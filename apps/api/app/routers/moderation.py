# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""FastAPI router for moderator flag queue, audit logging, and model health."""

import uuid
from typing import Annotated, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.audit import AuditLog
from app.models.chat import Flag
from app.models.identity import User
from app.models.listing import Listing
from app.services.moderation_service import ModerationService

router = APIRouter(prefix="/admin", tags=["moderation"])


class ModerationActionRequest(BaseModel):
    action: str = Field(..., pattern="^(uphold|dismiss|remove|warn)$")
    notes: str = Field(default="", max_length=500)


def _require_moderator(user: User) -> None:
    if getattr(user, "role", "user") not in {"admin", "moderator"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Moderator or admin privileges required.",
        )


@router.get("/flags")
async def list_flag_queue(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    flag_status: str = "open",
) -> list[Any]:
    """Return moderation flag queue with human-readable reasons."""
    _require_moderator(current_user)
    stmt = select(Flag).where(Flag.status == flag_status).order_by(Flag.created_at.desc())
    res = await db.execute(stmt)
    return list(res.scalars().all())


@router.post("/flags/{flag_id}/action")
async def moderate_flag(
    flag_id: uuid.UUID,
    payload: ModerationActionRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """Execute a moderator decision (uphold/dismiss/remove/warn) and write an audit_logs row."""
    _require_moderator(current_user)

    stmt = select(Flag).where(Flag.id == flag_id)
    res = await db.execute(stmt)
    flag = res.scalar_one_or_none()
    if not flag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flag not found.")

    listing: Optional[Listing] = None
    if flag.listing_id is not None:
        l_stmt = select(Listing).where(Listing.id == flag.listing_id)
        l_res = await db.execute(l_stmt)
        listing = l_res.scalar_one_or_none()

    audit_payload = ModerationService.apply_moderator_action(
        flag=flag,
        moderator_id=current_user.id,
        action=payload.action,
        notes=payload.notes,
        listing=listing,
    )
    audit_row = AuditLog(**audit_payload)
    db.add(audit_row)
    await db.commit()
    return {"status": "ok", "flag_status": flag.status, "audit_action": audit_row.action}


@router.get("/model-health")
async def get_model_health(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Return confidence histograms and drift indicators for active models."""
    _require_moderator(current_user)
    stmt = select(Listing.condition_conf).where(Listing.condition_conf.isnot(None)).limit(500)
    res = await db.execute(stmt)
    confs = [float(c) for c in res.scalars().all() if c is not None]
    return ModerationService.compute_model_health(confs)
