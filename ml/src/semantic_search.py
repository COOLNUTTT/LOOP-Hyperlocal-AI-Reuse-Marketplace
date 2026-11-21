# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Multilingual Semantic Search, Query Parser, and Image Similarity Engine.

Supports:
1. 384-d text embeddings (English + Hinglish concept projection).
2. 512-d image embeddings for search-by-image and "similar items".
3. Natural-language query parser extracting price ceilings (e.g. "under 3000",
   "3000 ke andar") and coarse place/area names (e.g. "near Wakad").
4. Cosine similarity ranking and FTS baseline comparison.
"""

import hashlib
import math
import re
from decimal import Decimal
from typing import Any, Dict, List, Optional

TEXT_EMBED_DIM = 384
IMAGE_EMBED_DIM = 512

# Hinglish -> English semantic normalization lexicon
HINGLISH_MAP = {
    "kitab": "book textbook",
    "kitaab": "book textbook",
    "padhai": "study engineering",
    "mez": "table desk",
    "kursi": "chair",
    "gadda": "mattress",
    "bistar": "mattress",
    "naya": "new like_new pristine",
    "nayi": "new like_new pristine",
    "purana": "used fair",
    "purani": "used fair",
    "sasta": "cheap budget affordable",
    "sasti": "cheap budget affordable",
    "kam": "under below",
    "andar": "under below",
    "paas": "near around",
    "ke": "",
    "mein": "in",
    "me": "in",
    "chahiye": "",
    "dikhao": "",
    "baja": "guitar",
    "gana": "guitar",
}

# Semantic concept clusters for 384-d projection
CONCEPT_GROUPS = [
    ["calculator", "casio", "fx-991ex", "scientific", "solar", "math", "engineering"],
    ["laptop", "dell", "hp", "lenovo", "macbook", "computer", "ssd", "ram"],
    ["headphones", "earphones", "sony", "boat", "bluetooth", "audio", "music"],
    ["monitor", "screen", "display", "hdmi", "vga"],
    ["keyboard", "mouse", "usb", "wireless"],
    ["table", "desk", "study", "wood", "ikea", "furniture", "workstation"],
    ["chair", "ergonomic", "featherlite", "seat", "office"],
    ["bookshelf", "shelf", "rack", "storage"],
    ["mattress", "bed", "foam", "wakefit", "sleep"],
    ["book", "textbook", "grewal", "pearson", "edition", "syllabus", "exam", "gate"],
    ["guitar", "acoustic", "yamaha", "fender", "strings", "music"],
    ["badminton", "racket", "yonex", "shuttle", "sports"],
    ["board", "game", "chess", "monopoly", "cards"],
]


def parse_natural_query(query: str) -> Dict[str, Any]:
    """Parse natural-language English/Hinglish query into structured SQL filters + clean text.

    Example: "study table under 3000 near Wakad"
    -> {"clean_query": "study table", "price_max": Decimal("3000"), "area_name": "Wakad"}
    """
    if not query:
        return {"clean_query": "", "price_max": None, "area_name": None}

    raw = query.strip()
    price_max: Optional[Decimal] = None
    area_name: Optional[str] = None

    # 1. Extract price ceiling: "under 3000", "below 1500", "<= 2000", "3000 ke andar", "3000 se kam"
    price_patterns = [
        r"(?:under|below|less\s+than|max|<=|<)\s*(?:rs\.?|₹)?\s*(\d{2,6})",
        r"(?:rs\.?|₹)?\s*(\d{2,6})\s*(?:ke\s+andar|se\s+kam|tak)",
    ]
    cleaned = raw
    for pat in price_patterns:
        m = re.search(pat, cleaned, flags=re.IGNORECASE)
        if m:
            price_max = Decimal(m.group(1))
            cleaned = (cleaned[: m.start()] + " " + cleaned[m.end() :]).strip()
            break

    # 2. Extract place: "near Wakad", "in Lohegaon", "around Charholi", "Wakad ke paas"
    place_patterns = [
        r"(?:near|in|around|at)\s+([A-Za-z][A-Za-z0-9\s]{1,25}?)(?=\s+(?:under|below|for|$)|$)",
        r"([A-Za-z][A-Za-z0-9]{1,25})\s+(?:ke\s+paas|mein|me)\b",
    ]
    for pat in place_patterns:
        m = re.search(pat, cleaned, flags=re.IGNORECASE)
        if m:
            candidate = m.group(1).strip()
            if candidate.lower() not in {"good", "new", "like", "fair", "cheap"}:
                area_name = candidate
                cleaned = (cleaned[: m.start()] + " " + cleaned[m.end() :]).strip()
                break

    # 3. Normalize Hinglish tokens
    tokens = re.findall(r"[A-Za-z0-9_\-]+", cleaned.lower())
    normalized_tokens = []
    for tok in tokens:
        if tok in HINGLISH_MAP:
            mapped = HINGLISH_MAP[tok]
            if mapped:
                normalized_tokens.extend(mapped.split())
        else:
            normalized_tokens.append(tok)

    clean_query = " ".join(normalized_tokens).strip()
    return {
        "clean_query": clean_query,
        "price_max": price_max,
        "area_name": area_name,
    }


def _normalize_vec(vec: List[float]) -> List[float]:
    norm = math.sqrt(sum(x * x for x in vec))
    if norm == 0.0:
        return vec
    return [x / norm for x in vec]


def embed_text(text: str) -> List[float]:
    """Generate a 384-d normalized semantic embedding for English/Hinglish text."""
    vec = [0.0] * TEXT_EMBED_DIM
    if not text:
        return vec

    parsed = parse_natural_query(text)
    norm_text = parsed["clean_query"] or text.lower()
    tokens = re.findall(r"[a-z0-9_\-]+", norm_text.lower())

    # 1. Concept cluster projection (first 13 * 16 = 208 dims)
    for g_idx, group in enumerate(CONCEPT_GROUPS):
        overlap = sum(1 for t in tokens if any(t in kw or kw in t for kw in group))
        if overlap > 0:
            base = g_idx * 16
            for offset in range(16):
                vec[base + offset] += float(overlap) * 1.5

    # 2. Deterministic token n-gram hashing into remaining dims (208..383)
    for tok in tokens:
        h = int(hashlib.md5(tok.encode("utf-8")).hexdigest(), 16)
        idx = 208 + (h % (TEXT_EMBED_DIM - 208))
        vec[idx] += 1.0

    return _normalize_vec(vec)


def embed_image(image_hint: str) -> List[float]:
    """Generate a 512-d normalized image embedding from image signature/context."""
    vec = [0.0] * IMAGE_EMBED_DIM
    if not image_hint:
        return vec

    tokens = re.findall(r"[a-z0-9_\-]+", image_hint.lower())
    for g_idx, group in enumerate(CONCEPT_GROUPS):
        overlap = sum(1 for t in tokens if any(t in kw or kw in t for kw in group))
        if overlap > 0:
            base = g_idx * 24
            for offset in range(24):
                vec[base + offset] += float(overlap) * 1.5

    for tok in tokens:
        h = int(hashlib.sha256(tok.encode("utf-8")).hexdigest(), 16)
        idx = 312 + (h % (IMAGE_EMBED_DIM - 312))
        vec[idx] += 1.0

    return _normalize_vec(vec)


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Compute cosine similarity between two equal-length vectors."""
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    na = math.sqrt(sum(a * a for a in vec_a))
    nb = math.sqrt(sum(b * b for b in vec_b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)
