# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Chat-safety keyword warning rules and rule-based negotiation helper."""

from __future__ import annotations

import re
from decimal import Decimal
from typing import Any, Dict, List, Optional

SCAM_KEYWORD_RULES = [
    (
        r"\b(advance\s+payment|pay\s+first|token\s+amount|booking\s+amount)\b",
        "Never send advance payment before inspecting the item in person at a public meetup spot.",
    ),
    (
        r"\b(scan\s+qr|qr\s+code\s+to\s+receive|enter\s+upi\s+pin)\b",
        "You never need to scan a QR code or enter your UPI PIN to receive money.",
    ),
    (
        r"\b(whatsapp|telegram|text\s+me\s+on|call\s+outside)\b",
        "Keep communication inside LOOP chat so safety and handover protections remain active.",
    ),
    (
        r"\b(share\s+otp|send\s+otp|tell\s+me\s+the\s+code)\b",
        "Only share your handover OTP in person when you have verified the item.",
    ),
]


class SafetyAndNegotiationHelper:
    @staticmethod
    def check_chat_safety(message_text: str) -> List[str]:
        """Return safety warning messages if scam/risky patterns are detected."""
        if not message_text:
            return []
        warnings = []
        for pattern, warning_msg in SCAM_KEYWORD_RULES:
            if re.search(pattern, message_text, flags=re.IGNORECASE):
                warnings.append(warning_msg)
        return warnings

    @staticmethod
    def suggest_negotiation_range(
        price_low: Optional[Decimal],
        price_likely: Optional[Decimal],
        price_high: Optional[Decimal],
        price_ask: Optional[Decimal],
    ) -> Dict[str, Any]:
        """Rule-based negotiation helper based on calibrated price range."""
        if not price_likely or price_likely <= 0:
            return {
                "suggestion": "Ask the seller about item condition and meetup availability.",
                "suggested_offer": None,
            }

        low = price_low or (price_likely * Decimal("0.85"))
        high = price_high or (price_likely * Decimal("1.15"))

        if price_ask and price_ask <= low:
            return {
                "suggestion": f"Asking price (₹{price_ask}) is already a Great Deal below market range.",
                "suggested_offer": float(price_ask),
            }
        elif price_ask and price_ask > high:
            return {
                "suggestion": f"Asking price is above market range. Consider offering around ₹{price_likely}.",
                "suggested_offer": float(price_likely),
            }
        else:
            midpoint = round((float(low) + float(price_likely)) / 2.0, 2)
            return {
                "suggestion": f"Fair market range is ₹{low}–₹{high}. A polite opening offer is ₹{midpoint}.",
                "suggested_offer": midpoint,
            }
