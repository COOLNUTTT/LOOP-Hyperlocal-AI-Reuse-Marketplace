# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""FastAPI router for saved searches and alert matching."""

import uuid
from datetime import datetime
from typing import Annotated, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from ml.src.semantic_search import embed_text, parse_natural_query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.identity import User
from app.models.saved_search import SavedSearch

router = APIRouter(prefix="/saved-searches", tags=["saved-searches"])


class SavedSearchCreateRequest(BaseModel):
    query_text: str = Field(..., min_length=2, max_length=200)
    filters: dict[str, Any] = Field(default_factory=dict)


class SavedSearchResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    query_text: str
    filters: dict[str, Any]
    last_notified_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


@router.post("", response_model=SavedSearchResponse, status_code=status.HTTP_201_CREATED)
async def create_saved_search(
    payload: SavedSearchCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SavedSearch:
    """Save a search query with parsed filters and 384-d embedding for alerts."""
    parsed = parse_natural_query(payload.query_text)
    merged_filters = dict(payload.filters)
    if parsed.get("price_max") is not None and "price_max" not in merged_filters:
        merged_filters["price_max"] = float(parsed["price_max"])
    if parsed.get("area_name") and "area_name" not in merged_filters:
        merged_filters["area_name"] = parsed["area_name"]

    vec = embed_text(payload.query_text)

    saved = SavedSearch(
        user_id=current_user.id,
        query_text=payload.query_text,
        filters=merged_filters,
        query_embedding=vec,
    )
    db.add(saved)
    await db.commit()
    await db.refresh(saved)
    return saved


@router.get("", response_model=list[SavedSearchResponse])
async def list_saved_searches(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[SavedSearch]:
    """List current user's saved searches."""
    stmt = (
        select(SavedSearch)
        .where(SavedSearch.user_id == current_user.id)
        .order_by(SavedSearch.created_at.desc())
    )
    res = await db.execute(stmt)
    return list(res.scalars().all())


@router.delete("/{search_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_saved_search(
    search_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a saved search owned by the current user."""
    stmt = select(SavedSearch).where(
        SavedSearch.id == search_id, SavedSearch.user_id == current_user.id
    )
    res = await db.execute(stmt)
    saved = res.scalar_one_or_none()
    if not saved:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved search not found.")
    await db.delete(saved)
    await db.commit()
