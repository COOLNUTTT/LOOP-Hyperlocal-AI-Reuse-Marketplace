# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""50-Query Evaluation Harness: Semantic Multilingual Search vs FTS Baseline.

Evaluates 25 English and 25 Hinglish queries on Recall@5, Recall@10, NDCG@10,
MRR, and query latency.
"""

import math
import time
from decimal import Decimal
from typing import Any, Dict, List

from ml.src.semantic_search import parse_natural_query, embed_text, cosine_similarity


class EvalListing:
    def __init__(self, id: str, title: str, category: str, subtype: str, price: int, area: str):
        self.id = id
        self.title = title
        self.category = category
        self.subtype = subtype
        self.price_ask = Decimal(str(price))
        self.area_name = area
        self.brand = ""
        self.description = f"{title} {subtype} in {area}"


CORPUS = [
    EvalListing("L1", "Casio fx-991EX Scientific Calculator", "electronics", "Scientific Calculator", 850, "Lohegaon"),
    EvalListing("L2", "IKEA Study Table Wood Desk", "furniture", "Study Table", 2400, "Wakad"),
    EvalListing("L3", "Ergonomic Mesh Office Chair", "furniture", "Ergonomic Chair", 3100, "Wakad"),
    EvalListing("L4", "B.S. Grewal Engineering Mathematics Textbook", "books", "Engineering Textbook", 350, "Charholi"),
    EvalListing("L5", "Yamaha F310 Acoustic Guitar", "hobbies", "Acoustic Guitar", 4800, "Lohegaon"),
    EvalListing("L6", "Yonex Carbon Badminton Racket", "hobbies", "Badminton Racket", 1100, "Viman Nagar"),
    EvalListing("L7", "Dell Inspiron 15 Laptop SSD", "electronics", "Laptop", 26000, "Wakad"),
    EvalListing("L8", "Sony Wireless Bluetooth Headphones", "electronics", "Headphones", 1400, "Lohegaon"),
    EvalListing("L9", "Wakefit Single Bed Foam Mattress", "furniture", "Mattress", 1800, "Charholi"),
    EvalListing("L10", "GATE CSE Competitive Exam Guide", "books", "Competitive Exam Guide", 400, "Lohegaon"),
]

# 50 Queries: 25 English + 25 Hinglish
EVAL_QUERIES = [
    # 25 English
    ("study table under 3000 near Wakad", ["L2"]),
    ("scientific calculator casio", ["L1"]),
    ("ergonomic chair in Wakad", ["L3"]),
    ("engineering mathematics textbook", ["L4"]),
    ("acoustic guitar yamaha", ["L5"]),
    ("badminton racket yonex", ["L6"]),
    ("dell laptop ssd", ["L7"]),
    ("bluetooth headphones under 2000", ["L8"]),
    ("single bed mattress", ["L9"]),
    ("gate exam guide book", ["L10"]),
    ("desk for study", ["L2"]),
    ("math calculator", ["L1"]),
    ("office chair", ["L3"]),
    ("college textbook", ["L4"]),
    ("music guitar", ["L5"]),
    ("sports racket", ["L6"]),
    ("computer laptop", ["L7"]),
    ("wireless earphones", ["L8"]),
    ("foam mattress", ["L9"]),
    ("competitive exam book", ["L10"]),
    ("ikea furniture near Wakad", ["L2"]),
    ("casio calculator under 1000", ["L1"]),
    ("chair below 3500", ["L3"]),
    ("grewal book", ["L4"]),
    ("yamaha guitar", ["L5"]),
    # 25 Hinglish
    ("padhai ki mez 3000 ke andar Wakad ke paas", ["L2"]),
    ("engineering ki kitab", ["L4"]),
    ("sasta calculator", ["L1"]),
    ("kursi Wakad me", ["L3"]),
    ("baja guitar", ["L5"]),
    ("padhai ke liye table", ["L2"]),
    ("naya mattress", ["L9"]),
    ("sasti kitab", ["L4", "L10"]),
    ("exam ki kitaab", ["L10"]),
    ("purana laptop", ["L7"]),
    ("gana bajane wala guitar", ["L5"]),
    ("sasta headphones", ["L8"]),
    ("padhai ka table", ["L2"]),
    ("badminton khelne ka racket", ["L6"]),
    ("bistar gadda", ["L9"]),
    ("math ka calculator", ["L1"]),
    ("office ki kursi", ["L3"]),
    ("college ki kitab", ["L4"]),
    ("bluetooth earphones sasta", ["L8"]),
    ("study mez", ["L2"]),
    ("gate ki kitaab", ["L10"]),
    ("racket sports", ["L6"]),
    ("laptop 30000 ke andar", ["L7"]),
    ("gadda Charholi me", ["L9"]),
    ("calculator Lohegaon ke paas", ["L1"]),
]


def _rank_semantic(query: str) -> List[str]:
    parsed = parse_natural_query(query)
    filtered = []
    for item in CORPUS:
        if parsed["price_max"] is not None and item.price_ask > parsed["price_max"]:
            continue
        if parsed["area_name"] is not None and parsed["area_name"].lower() not in item.area_name.lower():
            continue
        filtered.append(item)
    q_vec = embed_text(parsed["clean_query"] or query)
    scored = [(cosine_similarity(q_vec, embed_text(i.description)), i.id) for i in filtered]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [lid for _, lid in scored]


def _rank_fts(query: str) -> List[str]:
    tokens = [t.lower() for t in query.split() if len(t) > 1]
    scored = []
    for item in CORPUS:
        text = item.description.lower()
        hits = sum(1 for t in tokens if t in text)
        if hits > 0:
            scored.append((hits, item.id))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [lid for _, lid in scored]


def evaluate_subset(queries: List[tuple], rank_fn) -> Dict[str, float]:
    r5, r10, ndcg10, mrr, latencies = [], [], [], [], []
    for q, rel in queries:
        t0 = time.perf_counter()
        ranked = rank_fn(q)
        latencies.append((time.perf_counter() - t0) * 1000)

        rel_set = set(rel)
        top5 = ranked[:5]
        top10 = ranked[:10]

        r5.append(1.0 if any(x in rel_set for x in top5) else 0.0)
        r10.append(1.0 if any(x in rel_set for x in top10) else 0.0)

        # MRR
        rr = 0.0
        for idx, lid in enumerate(top10):
            if lid in rel_set:
                rr = 1.0 / (idx + 1)
                break
        mrr.append(rr)

        # NDCG@10
        dcg = sum(1.0 / math.log2(idx + 2) for idx, lid in enumerate(top10) if lid in rel_set)
        idcg = sum(1.0 / math.log2(idx + 2) for idx in range(min(len(rel_set), 10)))
        ndcg10.append(dcg / idcg if idcg > 0 else 0.0)

    n = len(queries)
    return {
        "recall_5": round(sum(r5) / n, 4),
        "recall_10": round(sum(r10) / n, 4),
        "ndcg_10": round(sum(ndcg10) / n, 4),
        "mrr": round(sum(mrr) / n, 4),
        "mean_latency_ms": round(sum(latencies) / n, 3),
    }


if __name__ == "__main__":
    en_queries = EVAL_QUERIES[:25]
    hi_queries = EVAL_QUERIES[25:]

    print("English Semantic:", evaluate_subset(en_queries, _rank_semantic))
    print("English FTS:     ", evaluate_subset(en_queries, _rank_fts))
    print("Hinglish Semantic:", evaluate_subset(hi_queries, _rank_semantic))
    print("Hinglish FTS:     ", evaluate_subset(hi_queries, _rank_fts))
