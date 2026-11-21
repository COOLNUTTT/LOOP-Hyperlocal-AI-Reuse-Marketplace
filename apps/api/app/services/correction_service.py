# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Service layer for active learning corrections and training anti-poisoning eligibility."""

from __future__ import annotations

import enum
import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Optional

from ml.src.price_estimator import CATEGORY_FALLBACK_MEDIANS, SUBTYPE_MEDIANS

if TYPE_CHECKING:
    from app.models.identity import User


class CorrectionField(str, enum.Enum):
    CATEGORY = "category"
    SUBTYPE = "subtype"
    CONDITION = "condition"
    PRICE = "price"


class CorrectionService:
    @staticmethod
    def is_eligible_for_training(
        user: Optional[User],
        field: str,
        user_value: str,
        category: Optional[str] = None,
        subtype: Optional[str] = None,
    ) -> bool:
        """Evaluate anti-poisoning eligibility rules per ML_SPEC §7:

        1. User must be verified or have positive trust score.
        2. If field is price, price correction must lie within robust bounds
           (within 3x median of category/subtype).
        """
        if not user:
            return False

        # Admin or verified user check (requires completed_trades >= 1 if set)
        completed_trades = getattr(user, "completed_trades", None)
        has_completed_trade = completed_trades is None or int(completed_trades) >= 1
        is_admin = getattr(user, "role", "user") == "admin"

        is_trusted = is_admin or (
            has_completed_trade
            and (
                getattr(user, "is_verified", False)
                or (
                    hasattr(user, "trust_score")
                    and user.trust_score
                    and float(user.trust_score) >= 0.5
                )
            )
        )

        if not is_trusted:
            return False

        # Price sanity check (bounds within 3x median)
        if field == CorrectionField.PRICE.value:
            try:
                price_val = Decimal(str(user_value))
                if price_val <= 0:
                    return False

                key = (subtype or "").strip().lower()
                median = SUBTYPE_MEDIANS.get(key)
                if not median:
                    cat_key = (category or "electronics").strip().lower()
                    median = CATEGORY_FALLBACK_MEDIANS.get(cat_key, Decimal("1000.00"))

                # Within 3x median bound
                if price_val > median * Decimal("3.0") or price_val < median * Decimal("0.2"):
                    return False
            except Exception:
                return False

        return True

    @staticmethod
    async def record_correction(
        db: Any,
        listing_id: uuid.UUID,
        user_id: uuid.UUID,
        field: str,
        ai_value: str,
        user_value: str,
        ai_confidence: Optional[float] = None,
        model_version: str = "v1.0.0",
        eligible_for_training: bool = False,
        data_origin: str = "real",
    ) -> Any:
        """Insert or update latest correction record for a listing field."""
        from app.models.corrections import Correction

        correction = Correction(
            listing_id=listing_id,
            user_id=user_id,
            field=field,
            ai_value=str(ai_value),
            user_value=str(user_value),
            ai_confidence=ai_confidence,
            model_version=model_version,
            eligible_for_training=eligible_for_training,
            data_origin=data_origin,
        )
        db.add(correction)
        await db.commit()
        await db.refresh(correction)
        return correction

    @staticmethod
    async def detect_and_record_corrections(
        db: Any,
        listing_id: uuid.UUID,
        user: Any,
        ai_state: dict[str, Any],
        user_state: dict[str, Any],
        category: Optional[str] = None,
        subtype: Optional[str] = None,
    ) -> list[Any]:
        """Compare AI predictions against final user-chosen values and log corrections."""
        recorded = []

        fields_to_check = [
            ("category", "category", "category"),
            ("subtype", "subtype", "subtype"),
            ("condition", "condition", "condition"),
            ("price", "price_likely", "price_ask"),
        ]

        for field_enum, ai_key, user_key in fields_to_check:
            ai_val = ai_state.get(ai_key)
            user_val = user_state.get(user_key)

            if ai_val is not None and user_val is not None:
                str_ai = str(ai_val).strip()
                str_user = str(user_val).strip()

                # For price comparison, format as float or decimal
                if field_enum == CorrectionField.PRICE.value:
                    try:
                        ai_num = float(str_ai)
                        user_num = float(str_user)
                        has_changed = abs(ai_num - user_num) > 1e-2
                    except ValueError:
                        has_changed = str_ai.lower() != str_user.lower()
                else:
                    has_changed = str_ai.lower() != str_user.lower()

                if has_changed:
                    eligible = CorrectionService.is_eligible_for_training(
                        user=user,
                        field=field_enum,
                        user_value=str_user,
                        category=category or user_state.get("category"),
                        subtype=subtype or user_state.get("subtype"),
                    )

                    ai_conf = ai_state.get(f"{ai_key}_conf") or ai_state.get("conf")

                    corr = await CorrectionService.record_correction(
                        db=db,
                        listing_id=listing_id,
                        user_id=user.id,
                        field=field_enum,
                        ai_value=str_ai,
                        user_value=str_user,
                        ai_confidence=float(ai_conf) if ai_conf is not None else None,
                        model_version="v1.0.0",
                        eligible_for_training=eligible,
                        data_origin=user_state.get("data_origin", "real"),
                    )
                    recorded.append(corr)

        return recorded
