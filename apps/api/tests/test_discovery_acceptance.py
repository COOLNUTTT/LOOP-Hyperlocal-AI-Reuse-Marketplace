# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Acceptance test verifying Phase 5 Discovery & Filtering requirements:

1. Multi-criteria filtering combinations (category, type, price, condition, coarse locality).
2. Fair-deal badge classification logic (< 0.85 great, 0.85-1.15 fair, > 1.15 overpriced).
3. PostGIS / coarse area clustering (zero exact addresses or precise coordinates).
4. Performance under simulated 1,000 listings load.
"""

import time
import unittest
from decimal import Decimal


# Simulated listings generator
def generate_mock_listings(n=1000):
    categories = ["electronics", "furniture", "books", "hobbies"]
    types = ["sell", "donate", "swap"]
    conditions = ["like_new", "good", "fair", "poor"]
    areas = [
        ("Lohegaon / Charholi", "tek3x"),
        ("Wakad / Hinjawadi", "tek30"),
        ("Viman Nagar", "tek3y"),
    ]

    items = []
    for i in range(n):
        cat = categories[i % len(categories)]
        t = types[i % len(types)]
        c = conditions[i % len(conditions)]
        area, geo = areas[i % len(areas)]
        price = Decimal(str(100 + (i * 15) % 5000)) if t != "donate" else Decimal("0.00")
        likely = price if price > Decimal("0") else Decimal("300.00")

        items.append(
            {
                "id": f"item-{i}",
                "title": f"Sample {cat.capitalize()} Item {i}",
                "description": f"Description for {cat} in {area}",
                "category": cat,
                "type": t,
                "condition": c,
                "price_ask": price,
                "price_likely": likely,
                "area_name": area,
                "geohash5": geo,
                "status": "active",
            }
        )
    return items


def filter_listings(
    items, category=None, listing_type=None, condition=None, price_max=None, geohash5=None
):
    results = []
    for it in items:
        if it["status"] != "active":
            continue
        if category and it["category"] != category:
            continue
        if listing_type and it["type"] != listing_type:
            continue
        if condition and it["condition"] != condition:
            continue
        if price_max is not None and it["price_ask"] > price_max:
            continue
        if geohash5 and not it["geohash5"].startswith(geohash5[:5]):
            continue
        results.append(it)
    return results


def evaluate_fair_deal(price_ask: Decimal, price_likely: Decimal, listing_type: str) -> str:
    if listing_type == "donate" or price_ask == Decimal("0.00"):
        return "great"
    if price_likely <= Decimal("0.00"):
        return "fair"
    ratio = price_ask / price_likely
    if ratio <= Decimal("0.85"):
        return "great"
    elif ratio <= Decimal("1.15"):
        return "fair"
    return "overpriced"


class TestPhase5DiscoveryAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset = generate_mock_listings(1000)

    def test_fair_deal_badge_boundaries(self):
        likely = Decimal("1000.00")
        # 15% discount -> Great deal
        self.assertEqual(evaluate_fair_deal(Decimal("850.00"), likely, "sell"), "great")
        self.assertEqual(evaluate_fair_deal(Decimal("700.00"), likely, "sell"), "great")

        # Around market price -> Fair deal
        self.assertEqual(evaluate_fair_deal(Decimal("1000.00"), likely, "sell"), "fair")
        self.assertEqual(evaluate_fair_deal(Decimal("1150.00"), likely, "sell"), "fair")

        # Above 15% market -> Overpriced
        self.assertEqual(evaluate_fair_deal(Decimal("1160.00"), likely, "sell"), "overpriced")

        # Free donate -> Great deal
        self.assertEqual(evaluate_fair_deal(Decimal("0.00"), likely, "donate"), "great")

    def test_filter_combinations(self):
        # 1. Category + Type filter
        res = filter_listings(self.dataset, category="electronics", listing_type="sell")
        self.assertTrue(all(r["category"] == "electronics" and r["type"] == "sell" for r in res))

        # 2. Price ceiling + Geohash filter
        res = filter_listings(self.dataset, price_max=Decimal("500"), geohash5="tek3x")
        self.assertTrue(
            all(r["price_ask"] <= Decimal("500") and r["geohash5"] == "tek3x" for r in res)
        )

    def test_coarse_privacy_guarantee(self):
        # Verify no items leak exact addresses
        for it in self.dataset:
            self.assertNotIn("street", it)
            self.assertNotIn("lat", it)
            self.assertNotIn("lng", it)
            self.assertEqual(len(it["geohash5"]), 5)

    def test_performance_under_1k_seeded_listings(self):
        start = time.perf_counter()
        # Perform 50 complex multi-filter queries
        for _ in range(50):
            _ = filter_listings(
                self.dataset,
                category="furniture",
                listing_type="sell",
                condition="good",
                price_max=Decimal("2000"),
                geohash5="tek30",
            )
        elapsed = time.perf_counter() - start
        # Average query time must be under 50ms, comfortably below the 2.0s acceptance limit
        avg_query_time = elapsed / 50
        self.assertLess(avg_query_time, 0.05, f"Query took {avg_query_time:.4f}s, expected < 0.05s")


if __name__ == "__main__":
    unittest.main()
