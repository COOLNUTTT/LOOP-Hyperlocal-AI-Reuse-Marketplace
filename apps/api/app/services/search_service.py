# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Service layer for semantic multilingual search, image search, similar items & saved searches."""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, List, Tuple

from ml.src.semantic_search import (
    cosine_similarity,
    embed_image,
    embed_text,
    parse_natural_query,
)


class SearchService:
    @staticmethod
    def build_listing_text(listing: Any) -> str:
        """Build searchable text representation of a listing."""
        parts = [
            getattr(listing, "title", "") or "",
            getattr(listing, "subtype", "") or "",
            getattr(listing, "brand", "") or "",
            getattr(listing, "category", "") or "",
            getattr(listing, "description", "") or "",
            getattr(listing, "area_name", "") or "",
        ]
        return " ".join(p for p in parts if p).strip()

    @staticmethod
    def rank_listings_semantic(
        listings: List[Any],
        query: str,
        top_k: int = 20,
    ) -> Tuple[List[Any], Dict[str, Any]]:
        """Parse query, apply extracted price/place filters, and rank by 384-d cosine similarity."""
        parsed = parse_natural_query(query)
        clean_q = parsed["clean_query"]
        price_max = parsed["price_max"]
        area_name = parsed["area_name"]

        filtered = []
        for item in listings:
            if price_max is not None:
                ask = getattr(item, "price_ask", None)
                if ask is not None and Decimal(str(ask)) > price_max:
                    continue
            if area_name is not None:
                item_area = (getattr(item, "area_name", "") or "").lower()
                if area_name.lower() not in item_area:
                    continue
            filtered.append(item)

        if not clean_q:
            return filtered[:top_k], parsed

        q_vec = embed_text(clean_q)
        scored = []
        for item in filtered:
            item_text = SearchService.build_listing_text(item)
            item_vec = embed_text(item_text)
            sim = cosine_similarity(q_vec, item_vec)
            scored.append((sim, item))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored[:top_k]], parsed

    @staticmethod
    def rank_listings_fts(
        listings: List[Any],
        query: str,
        top_k: int = 20,
    ) -> List[Any]:
        """Baseline keyword FTS matching (case-insensitive substring/token overlap)."""
        if not query:
            return listings[:top_k]

        tokens = [t.lower() for t in query.strip().split() if len(t) > 1]
        scored = []
        for item in listings:
            text = SearchService.build_listing_text(item).lower()
            hits = sum(1 for t in tokens if t in text)
            if hits > 0:
                scored.append((hits, item))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored[:top_k]]

    @staticmethod
    def search_by_image(
        listings: List[Any],
        image_hint: str,
        top_k: int = 10,
    ) -> List[Any]:
        """Rank active listings by 512-d image embedding cosine similarity."""
        q_vec = embed_image(image_hint)
        scored = []
        for item in listings:
            item_text = SearchService.build_listing_text(item)
            item_vec = embed_image(item_text)
            sim = cosine_similarity(q_vec, item_vec)
            scored.append((sim, item))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored[:top_k]]

    @staticmethod
    def find_similar_items(
        target_listing: Any,
        candidates: List[Any],
        top_k: int = 4,
    ) -> List[Any]:
        """Find top-k similar listings excluding the target listing itself."""
        target_id = getattr(target_listing, "id", None)
        target_vec = embed_text(SearchService.build_listing_text(target_listing))

        scored = []
        for item in candidates:
            if getattr(item, "id", None) == target_id:
                continue
            item_vec = embed_text(SearchService.build_listing_text(item))
            sim = cosine_similarity(target_vec, item_vec)
            scored.append((sim, item))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored[:top_k]]

    @staticmethod
    def matches_saved_search(listing: Any, saved_search: Any, threshold: float = 0.35) -> bool:
        """Check whether a newly published listing matches a user's saved search."""
        query_text = getattr(saved_search, "query_text", "") or ""
        filters = getattr(saved_search, "filters", {}) or {}

        # 1. Check structured filters
        if filters.get("category") and getattr(listing, "category", None) != filters["category"]:
            return False
        if filters.get("price_max") is not None:
            ask = getattr(listing, "price_ask", None)
            if ask is not None and Decimal(str(ask)) > Decimal(str(filters["price_max"])):
                return False
        if filters.get("area_name"):
            item_area = (getattr(listing, "area_name", "") or "").lower()
            if filters["area_name"].lower() not in item_area:
                return False

        # 2. Check semantic similarity
        if query_text:
            q_vec = embed_text(query_text)
            l_vec = embed_text(SearchService.build_listing_text(listing))
            if cosine_similarity(q_vec, l_vec) < threshold:
                return False

        return True
