# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Fraud, Duplicate-Image, Price-Anomaly, and Scam-Text Detection Engine.

All detections produce human-readable reasons for the human-in-the-loop
moderation queue. No listing is auto-removed without a moderator decision.
"""

from __future__ import annotations

import math
import re
from decimal import Decimal
from typing import Any, Dict, List, Optional

from ml.src.price_estimator import CATEGORY_FALLBACK_MEDIANS, SUBTYPE_MEDIANS
from ml.src.semantic_search import cosine_similarity

# Weighted logistic-regression-style n-gram weights for scam text detection
SCAM_NGRAM_WEIGHTS: Dict[str, float] = {
    "advance payment": 2.4,
    "pay first": 2.2,
    "token amount": 2.0,
    "booking amount": 1.8,
    "scan qr": 2.5,
    "upi pin": 2.8,
    "receive money": 1.6,
    "whatsapp": 1.3,
    "telegram": 1.4,
    "urgent": 0.9,
    "courier": 1.1,
    "army": 1.5,
    "customs": 1.8,
    "lottery": 2.5,
    "free gift": 1.7,
    "click link": 2.2,
}
SCAM_BIAS = -1.8


class FraudDetector:
    @staticmethod
    def phash_hamming_distance(hash_a: str, hash_b: str) -> int:
        """Compute Hamming distance between two hex perceptual hashes."""
        if not hash_a or not hash_b or len(hash_a) != len(hash_b):
            return 999
        try:
            xor_val = int(hash_a, 16) ^ int(hash_b, 16)
            return xor_val.bit_count()
        except ValueError:
            return 999

    @staticmethod
    def check_duplicate_image(
        phash_a: str,
        phash_b: str,
        emb_a: Optional[List[float]] = None,
        emb_b: Optional[List[float]] = None,
        phash_threshold: int = 6,
        clip_threshold: float = 0.90,
    ) -> Dict[str, Any]:
        """Two-stage duplicate/stolen image check: pHash -> CLIP embedding re-check."""
        dist = FraudDetector.phash_hamming_distance(phash_a, phash_b)
        if dist > phash_threshold:
            return {"is_duplicate": False, "phash_distance": dist, "clip_similarity": 0.0, "reason": None}

        if emb_a and emb_b:
            sim = cosine_similarity(emb_a, emb_b)
            is_dup = sim >= clip_threshold
        else:
            sim = 1.0 - (dist / 64.0)
            is_dup = True

        reason = (
            f"Potential duplicate/stolen image detected (pHash distance={dist}, "
            f"visual similarity={sim:.2f})."
            if is_dup
            else None
        )
        return {
            "is_duplicate": is_dup,
            "phash_distance": dist,
            "clip_similarity": round(sim, 4),
            "reason": reason,
        }

    @staticmethod
    def check_price_anomaly(
        price_ask: Optional[Decimal],
        category: str,
        subtype: Optional[str] = None,
        listing_type: str = "sell",
    ) -> Dict[str, Any]:
        """Flag extreme underpricing (< 0.25x median) or overpricing (> 3.5x median)."""
        if listing_type == "donate" or price_ask is None or price_ask <= 0:
            return {"is_anomaly": False, "reason": None}

        key = (subtype or "").strip().lower()
        median = SUBTYPE_MEDIANS.get(key) or CATEGORY_FALLBACK_MEDIANS.get(
            category.strip().lower(), Decimal("1000.00")
        )
        ratio = float(price_ask) / float(median)

        if ratio < 0.25:
            return {
                "is_anomaly": True,
                "ratio": round(ratio, 2),
                "reason": f"Price anomaly: asking ₹{price_ask} is {ratio:.2f}x of ₹{median} median (suspiciously low).",
            }
        if ratio > 3.5:
            return {
                "is_anomaly": True,
                "ratio": round(ratio, 2),
                "reason": f"Price anomaly: asking ₹{price_ask} is {ratio:.2f}x of ₹{median} median (abnormally high).",
            }
        return {"is_anomaly": False, "ratio": round(ratio, 2), "reason": None}

    @staticmethod
    def classify_scam_text(text: str) -> Dict[str, Any]:
        """TF-IDF / Logistic-Regression-style scam text classifier with human-readable reason."""
        if not text:
            return {"is_scam": False, "score": 0.0, "matched_terms": [], "reason": None}

        lower = text.lower()
        logit = SCAM_BIAS
        matched = []
        for phrase, weight in SCAM_NGRAM_WEIGHTS.items():
            if re.search(r"\b" + re.escape(phrase) + r"\b", lower):
                logit += weight
                matched.append(phrase)

        prob = 1.0 / (1.0 + math.exp(-logit))
        is_scam = prob >= 0.50
        reason = (
            f"Scam-text risk ({prob:.0%}): matched suspicious phrases [{', '.join(matched)}]."
            if is_scam
            else None
        )
        return {
            "is_scam": is_scam,
            "score": round(prob, 4),
            "matched_terms": matched,
            "reason": reason,
        }
