# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""FastAPI router for AI recognition, condition grading & conformal pricing."""

import time
from decimal import Decimal
from typing import Any, Optional

from fastapi import APIRouter
from ml.src.condition_grader import condition_grader
from ml.src.price_drop import compute_price_drop_suggestion
from ml.src.price_estimator import price_estimator
from ml.src.product_recognition import product_recognizer
from ml.src.smart_autofill import smart_autofill
from pydantic import BaseModel, Field

from app.schemas.ai import (
    AIAnalyzePhotosRequest,
    AIAnalyzePhotosResponse,
    AIBrandModelPrediction,
    AICategoryPrediction,
    AIConditionPrediction,
    AIDraftContent,
    AIPricePrediction,
    AIPriceReason,
)

router = APIRouter(prefix="/ai", tags=["ai"])


class StandalonePriceEstimateRequest(BaseModel):
    category: str
    subtype: Optional[str] = None
    brand: Optional[str] = None
    condition: str = "good"
    price_ask: Optional[Decimal] = None


class StandalonePriceEstimateResponse(BaseModel):
    low: Decimal
    likely: Decimal
    high: Decimal
    fair_deal_badge: str
    seller_guidance: Optional[str] = None
    conformal_coverage: str
    reasons: list[AIPriceReason] = []


@router.post("/price-estimate", response_model=StandalonePriceEstimateResponse)
async def get_price_estimate(
    payload: StandalonePriceEstimateRequest,
) -> StandalonePriceEstimateResponse:
    """Estimate calibrated price bounds with SHAP reasons and fair-deal badge."""
    est = price_estimator.estimate_price(
        category=payload.category,
        subtype=payload.subtype,
        brand=payload.brand,
        condition=payload.condition,
    )

    badge, guidance = price_estimator.evaluate_fair_deal_badge(
        price_ask=payload.price_ask,
        price_likely=est["likely"],
    )

    return StandalonePriceEstimateResponse(
        low=est["low"],
        likely=est["likely"],
        high=est["high"],
        fair_deal_badge=badge,
        seller_guidance=guidance,
        conformal_coverage=est["conformal_coverage"],
        reasons=[AIPriceReason(feature=r["feature"], effect=r["effect"]) for r in est["reasons"]],
    )


@router.post("/analyze-photos", response_model=AIAnalyzePhotosResponse)
async def analyze_photos(payload: AIAnalyzePhotosRequest) -> AIAnalyzePhotosResponse:
    """Product recognition, condition grading, split-conformal pricing & smart autofill."""
    start_time = time.perf_counter()
    context_text = (
        " ".join(payload.image_urls) if payload.image_urls else "electronics calculator casio"
    )

    # 1. Product recognition
    rec_result = product_recognizer.predict_from_features(text_context=context_text)
    top_cat = rec_result["category"]["value"]
    top_conf = rec_result["category"]["conf"]
    subtype = rec_result["subtype"]
    brand = rec_result["brand_model"]["brand"] or "Casio"
    model = rec_result["brand_model"]["model"] or "fx-991EX ClassWiz"

    # 2. Condition grading (ordinal expected-value with Grad-CAM)
    cond_result = condition_grader.predict_condition(context_hints=context_text)

    # 3. Calibrated price estimation
    price_result = price_estimator.estimate_price(
        category=top_cat,
        subtype=subtype,
        brand=brand,
        condition=cond_result["grade"],
    )

    # 4. Smart autofill specifications & templated draft
    smart_specs = smart_autofill.generate_smart_attributes(
        category=top_cat,
        subtype=subtype,
        brand=brand,
        model=model,
        condition=cond_result["grade"],
    )

    draft_copy = smart_autofill.generate_draft_copy(
        category=top_cat,
        subtype=subtype,
        brand=brand,
        model=model,
        condition=cond_result["grade"],
        attributes=smart_specs,
    )

    needs_confirmation = list(rec_result["needs_confirmation"])
    if cond_result["confidence"] < 0.70:
        needs_confirmation.append("condition")
    if price_result.get("is_widened_fallback"):
        needs_confirmation.append("price_interval_widened")

    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

    return AIAnalyzePhotosResponse(
        category=AICategoryPrediction(
            value=top_cat,
            conf=top_conf,
            top3=rec_result["category"]["top3"],
        ),
        subtype=subtype,
        brand_model=AIBrandModelPrediction(
            brand=brand,
            model=model,
        ),
        condition=AIConditionPrediction(
            grade=cond_result["grade"],
            conf=cond_result["confidence"],
            heatmap_url="/demo/heatmaps/calc-sample.png",
        ),
        price=AIPricePrediction(
            low=price_result["low"],
            likely=price_result["likely"],
            high=price_result["high"],
            reasons=[
                AIPriceReason(feature=r["feature"], effect=r["effect"])
                for r in price_result["reasons"]
            ],
        ),
        draft=AIDraftContent(
            title=draft_copy["title"],
            description=draft_copy["description"],
            attributes=smart_specs,
        ),
        needs_confirmation=needs_confirmation,
        latency_ms=latency_ms,
    )


class PriceDropRequest(BaseModel):
    price_ask: float = Field(default=950.0, gt=0)
    predicted_low: float = Field(default=700.0, gt=0)
    predicted_likely: float = Field(default=820.0, gt=0)
    days_active: int = Field(default=8, ge=0)
    views: int = Field(default=32, ge=0)
    saves: int = Field(default=1, ge=0)
    chats_started: int = Field(default=0, ge=0)
    offers_count: int = Field(default=0, ge=0)
    category: str = Field(default="electronics")


@router.post("/price-drop/{listing_id}")
async def suggest_price_drop(
    listing_id: str,
    payload: Optional[PriceDropRequest] = None,
) -> dict[str, Any]:
    """Compute hazard-style price-drop suggestion with floor and 15%-step guardrails."""
    req = payload or PriceDropRequest()
    result: dict[str, Any] = dict(
        compute_price_drop_suggestion(
            price_ask=req.price_ask,
            predicted_low=req.predicted_low,
            predicted_likely=req.predicted_likely,
            days_active=req.days_active,
            views=req.views,
            saves=req.saves,
            chats_started=req.chats_started,
            offers_count=req.offers_count,
            category=req.category,
        )
    )
    result["listing_id"] = listing_id
    return result
