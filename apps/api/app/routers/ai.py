# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""FastAPI router for AI features with schema-correct stubs for Phase 4."""

from decimal import Decimal

from fastapi import APIRouter

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


@router.post("/analyze-photos", response_model=AIAnalyzePhotosResponse)
async def analyze_photos(payload: AIAnalyzePhotosRequest):
    """Stubbed photo analysis returning fixed, schema-correct predictions.

    Follows DATA_MODEL_AND_API.md §3 specifications for Phase 4.
    """
    return AIAnalyzePhotosResponse(
        category=AICategoryPrediction(
            value="electronics",
            conf=0.94,
            top3=[
                {"category": "electronics", "confidence": 0.94},
                {"category": "hobbies", "confidence": 0.04},
                {"category": "furniture", "confidence": 0.02},
            ],
        ),
        subtype="Scientific Calculator",
        brand_model=AIBrandModelPrediction(
            brand="Casio",
            model="fx-991EX ClassWiz",
        ),
        condition=AIConditionPrediction(
            grade="good",
            conf=0.88,
            heatmap_url="/demo/heatmaps/calc-sample.png",
        ),
        price=AIPricePrediction(
            low=Decimal("700.00"),
            likely=Decimal("850.00"),
            high=Decimal("1100.00"),
            reasons=[
                AIPriceReason(feature="High demand item in Engineering campus", effect="+10%"),
                AIPriceReason(feature="Minor cosmetic surface scuff on cover", effect="-5%"),
                AIPriceReason(feature="Working solar cell and pristine display", effect="+5%"),
            ],
        ),
        draft=AIDraftContent(
            title="Casio FX-991EX ClassWiz Scientific Calculator",
            description="Casio scientific calculator in good working condition. All keys respond smoothly, high-resolution LCD screen is scratch-free. Perfect for engineering mathematics and semester examinations.",
        ),
        needs_confirmation=[],
    )
