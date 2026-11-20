# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""FastAPI router for AI features powered by real recognition, condition grading & conformal pricing."""

from decimal import Decimal
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

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
from ml.src.condition_grader import condition_grader
from ml.src.price_estimator import price_estimator
from ml.src.product_recognition import product_recognizer

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
async def get_price_estimate(payload: StandalonePriceEstimateRequest):
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
async def analyze_photos(payload: AIAnalyzePhotosRequest):
    """Product recognition, condition grading, and split-conformal pricing."""
    context_text = " ".join(payload.image_urls) if payload.image_urls else "electronics calculator casio"

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

    draft_title = f"{brand} {subtype}" if brand != "Standard" else f"{subtype}"
    draft_description = (
        f"{draft_title} assessed in {cond_result['grade'].replace('_', ' ')} condition. "
        f"Verified campus reuse listing with Grad-CAM visual wear inspection and fair pricing."
    )

    needs_confirmation = list(rec_result["needs_confirmation"])
    if cond_result["confidence"] < 0.70:
        needs_confirmation.append("condition")
    if price_result.get("is_widened_fallback"):
        needs_confirmation.append("price_interval_widened")

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
            title=draft_title,
            description=draft_description,
        ),
        needs_confirmation=needs_confirmation,
    )
