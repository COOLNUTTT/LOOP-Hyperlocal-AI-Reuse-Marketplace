# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Database session dependency for FastAPI routes."""

import asyncio
import importlib.util
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

# If no DB URL configured in environment or greenlet unavailable, fallback to None
engine = None
async_session_factory = None
HAS_GREENLET = importlib.util.find_spec("greenlet") is not None

if HAS_GREENLET and hasattr(settings, "database_url") and settings.database_url:
    engine = create_async_engine(settings.database_url, echo=False)
    async_session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> AsyncGenerator[Optional[AsyncSession], None]:
    """Provide a database session or None when Postgres is unreachable (standalone/CI mode)."""
    if async_session_factory is None:
        yield None
        return

    session = async_session_factory()
    try:
        await asyncio.wait_for(session.connection(), timeout=1.0)
    except Exception:
        await session.close()
        yield None
        return

    try:
        yield session
    finally:
        await session.close()
