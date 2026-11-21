# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""FastAPI router for algorithmic environmental impact estimation and sensitivity reports."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends
from ml.src.impact_estimator import aggregate_impact_summary
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.identity import User
from app.models.listing import Listing

router = APIRouter(prefix="/impact", tags=["impact"])


@router.get("/me")
async def get_my_impact(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Return personal reuse environmental impact ranges, LCA sources, and sensitivity table."""
    stmt = select(Listing).where(
        Listing.seller_id == current_user.id,
        Listing.status == "completed",
    )
    res = await db.execute(stmt)
    rows = list(res.scalars().all())
    items = [
        {
            "category": getattr(r, "category", "electronics"),
            "subtype": getattr(r, "subtype", "default") or "default",
        }
        for r in rows
    ]
    return dict(aggregate_impact_summary(items))


@router.get("/community")
async def get_community_impact(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Return community-wide reuse environmental impact ranges and sensitivity analysis."""
    stmt = select(Listing).where(Listing.status == "completed").limit(500)
    res = await db.execute(stmt)
    rows = list(res.scalars().all())
    items = [
        {
            "category": getattr(r, "category", "electronics"),
            "subtype": getattr(r, "subtype", "default") or "default",
        }
        for r in rows
    ]
    summary: dict[str, Any] = dict(aggregate_impact_summary(items))
    summary["scope"] = "community"
    summary["requested_by"] = str(current_user.id)
    return summary
