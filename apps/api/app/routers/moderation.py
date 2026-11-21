# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""FastAPI router for moderator flag queue, audit logging, model health, and active learning."""

import uuid
from datetime import datetime, timezone
from typing import Annotated, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from ml.src.active_learning.retrain import (
    DEFAULT_ACTIVE_METRICS,
    evaluate_promotion_gate,
)
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_db_user
from app.dependencies.database import get_db
from app.models.audit import AuditLog
from app.models.chat import Flag
from app.models.corrections import Correction
from app.models.identity import User
from app.models.listing import Listing
from app.models.model_version import ModelVersion
from app.services.moderation_service import ModerationService

router = APIRouter(prefix="/admin", tags=["moderation"])


class ModerationActionRequest(BaseModel):
    action: str = Field(..., pattern="^(uphold|dismiss|remove|warn)$")
    notes: str = Field(default="", max_length=500)


class ModelPromoteRequest(BaseModel):
    version: str = Field(..., min_length=1, max_length=50)
    candidate_metrics: dict[str, Any] = Field(default_factory=dict)
    trained_on_hash: str = Field(default="manual_promotion_hash", max_length=128)
    notes: str = Field(default="", max_length=500)


def _require_moderator(user: User) -> None:
    if getattr(user, "role", "user") not in {"admin", "moderator"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Moderator or admin privileges required.",
        )


@router.get("/flags")
async def list_flag_queue(
    current_user: Annotated[User, Depends(get_current_db_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    flag_status: str = "open",
) -> list[Any]:
    """Return moderation flag queue with human-readable reasons."""
    _require_moderator(current_user)
    stmt = select(Flag).where(Flag.status == flag_status).order_by(Flag.created_at.desc())
    res = await db.execute(stmt)
    return list(res.scalars().all())


@router.post("/flags/{flag_id}/action")
@router.post("/flags/{flag_id}/resolve")
async def moderate_flag(
    flag_id: uuid.UUID,
    payload: ModerationActionRequest,
    current_user: Annotated[User, Depends(get_current_db_user)],
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
    current_user: Annotated[User, Depends(get_current_db_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Return confidence histograms and drift indicators for active models."""
    _require_moderator(current_user)
    stmt = select(Listing.condition_conf).where(Listing.condition_conf.isnot(None)).limit(500)
    res = await db.execute(stmt)
    confs = [float(c) for c in res.scalars().all() if c is not None]
    return ModerationService.compute_model_health(confs)


@router.get("/corrections/stats")
async def get_corrections_stats(
    current_user: Annotated[User, Depends(get_current_db_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Return active learning corrections counts per field and anti-poisoning breakdown."""
    _require_moderator(current_user)
    stmt = select(Correction).order_by(Correction.created_at.desc()).limit(1000)
    res = await db.execute(stmt)
    rows = list(res.scalars().all())
    return ModerationService.compute_corrections_stats(rows)


@router.get("/models")
async def list_model_versions(
    current_user: Annotated[User, Depends(get_current_db_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[Any]:
    """Return tracked active and candidate model_versions."""
    _require_moderator(current_user)
    stmt = select(ModelVersion).order_by(ModelVersion.created_at.desc()).limit(100)
    res = await db.execute(stmt)
    return list(res.scalars().all())


@router.post("/models/{name}/promote")
async def promote_model_version(
    name: str,
    payload: ModelPromoteRequest,
    current_user: Annotated[User, Depends(get_current_db_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Promote a candidate model version ONLY if it passes the frozen test-set promotion gate."""
    _require_moderator(current_user)

    if name not in DEFAULT_ACTIVE_METRICS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown model name '{name}'.",
        )

    stmt = (
        select(ModelVersion)
        .where(ModelVersion.name == name, ModelVersion.is_active.is_(True))
        .order_by(ModelVersion.created_at.desc())
    )
    res = await db.execute(stmt)
    active_row = res.scalars().first()
    active_metrics = (
        dict(active_row.metrics) if active_row is not None else dict(DEFAULT_ACTIVE_METRICS[name])
    )

    gate = evaluate_promotion_gate(
        model_name=name,
        active_metrics=active_metrics,
        candidate_metrics=payload.candidate_metrics or active_metrics,
    )

    if not gate["promoted"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(gate["reason"]),
        )

    if active_row is not None:
        active_row.is_active = False

    now = datetime.now(timezone.utc)
    promoted_row = ModelVersion(
        name=name,
        version=payload.version,
        onnx_path=f"ml/exports/{name}_{payload.version}.onnx",
        metrics=payload.candidate_metrics,
        baseline_metrics=active_metrics,
        trained_on_hash=payload.trained_on_hash,
        is_active=True,
        promoted_at=now,
        notes=payload.notes or str(gate["reason"]),
    )
    db.add(promoted_row)

    audit_row = AuditLog(
        actor_id=current_user.id,
        action="model.promote",
        target_type="model_version",
        target_id=promoted_row.id,
        details={
            "model_name": name,
            "version": payload.version,
            "improvement": gate["improvement"],
            "reason": gate["reason"],
        },
    )
    db.add(audit_row)
    await db.commit()

    return {
        "status": "promoted",
        "model_name": name,
        "version": payload.version,
        "gate": gate,
    }


@router.post("/models/{name}/rollback")
async def rollback_active_model(
    name: str,
    current_user: Annotated[User, Depends(get_current_db_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Roll back a model to its most recent previous version and record an audit log."""
    _require_moderator(current_user)

    stmt = (
        select(ModelVersion)
        .where(ModelVersion.name == name)
        .order_by(ModelVersion.created_at.desc())
        .limit(10)
    )
    res = await db.execute(stmt)
    versions = list(res.scalars().all())
    if len(versions) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot rollback '{name}': fewer than 2 versions exist.",
        )

    current_active = versions[0]
    previous_version = versions[1]
    current_active.is_active = False
    previous_version.is_active = True
    previous_version.promoted_at = datetime.now(timezone.utc)

    audit_row = AuditLog(
        actor_id=current_user.id,
        action="model.rollback",
        target_type="model_version",
        target_id=previous_version.id,
        details={
            "model_name": name,
            "rolled_back_from": current_active.version,
            "restored_version": previous_version.version,
        },
    )
    db.add(audit_row)
    await db.commit()

    return {
        "status": "rolled_back",
        "model_name": name,
        "restored_version": previous_version.version,
    }
