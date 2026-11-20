# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Pydantic schemas for the AI analysis endpoint (/ai/analyze-photos)."""

import uuid
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, Field


class AICategoryPrediction(BaseModel):
    value: str
    conf: float = Field(ge=0.0, le=1.0)
    top3: list[dict[str, Any]] = []


class AIBrandModelPrediction(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None


class AIConditionPrediction(BaseModel):
    grade: str
    conf: float = Field(ge=0.0, le=1.0)
    heatmap_url: Optional[str] = None


class AIPriceReason(BaseModel):
    feature: str
    effect: str


class AIPricePrediction(BaseModel):
    low: Decimal
    likely: Decimal
    high: Decimal
    reasons: list[AIPriceReason] = []


class AIDraftContent(BaseModel):
    title: str
    description: str
    attributes: dict[str, Any] = {}


class AIAnalyzePhotosRequest(BaseModel):
    image_ids: list[uuid.UUID] = Field(default_factory=list)
    image_urls: list[str] = Field(default_factory=list)


class AIAnalyzePhotosResponse(BaseModel):
    category: AICategoryPrediction
    subtype: str
    brand_model: AIBrandModelPrediction
    condition: AIConditionPrediction
    price: AIPricePrediction
    draft: AIDraftContent
    needs_confirmation: list[str] = []
    latency_ms: Optional[float] = None
