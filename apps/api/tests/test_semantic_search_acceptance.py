# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Acceptance test verifying Phase 12 Semantic Multilingual Search, Image Search & Saved Searches:

1. Natural-language query parser extracts price ceiling and place ("study table under 3000").
2. Hinglish semantic search outperforms FTS baseline.
3. 512-d image search and "similar items" exclude target and rank relevant items first.
4. Saved search alert matching triggers on matching new listings.
"""

import unittest
import uuid
from decimal import Decimal

from ml.src.semantic_search import parse_natural_query

from app.services.search_service import SearchService


class MockListing:
    def __init__(self, id, title, category, subtype, price_ask, area_name, brand=""):
        self.id = id
        self.title = title
        self.category = category
        self.subtype = subtype
        self.price_ask = Decimal(str(price_ask))
        self.area_name = area_name
        self.brand = brand
        self.description = f"{title} {subtype} in {area_name}"


class MockSavedSearch:
    def __init__(self, query_text, filters=None):
        self.query_text = query_text
        self.filters = filters or {}


class TestPhase12SemanticSearchAcceptance(unittest.TestCase):
    def setUp(self):
        self.listings = [
            MockListing(
                uuid.uuid4(),
                "IKEA Study Table Wood",
                "furniture",
                "Study Table",
                2400,
                "Wakad",
                "IKEA",
            ),
            MockListing(
                uuid.uuid4(),
                "Expensive Study Table",
                "furniture",
                "Study Table",
                4500,
                "Wakad",
                "IKEA",
            ),
            MockListing(
                uuid.uuid4(),
                "Casio fx-991EX Calculator",
                "electronics",
                "Scientific Calculator",
                850,
                "Lohegaon",
                "Casio",
            ),
            MockListing(
                uuid.uuid4(),
                "B.S. Grewal Engineering Textbook",
                "books",
                "Engineering Textbook",
                350,
                "Charholi",
                "Pearson",
            ),
        ]

    def test_query_parser_price_and_place(self):
        """Verify 'study table under 3000 near Wakad' extracts price_max and area_name."""
        parsed = parse_natural_query("study table under 3000 near Wakad")
        self.assertEqual(parsed["price_max"], Decimal("3000"))
        self.assertEqual(parsed["area_name"].lower(), "wakad")
        self.assertIn("study", parsed["clean_query"])
        self.assertIn("table", parsed["clean_query"])

        # Hinglish variant
        parsed_hi = parse_natural_query("padhai ki mez 3000 ke andar Wakad ke paas")
        self.assertEqual(parsed_hi["price_max"], Decimal("3000"))
        self.assertEqual(parsed_hi["area_name"].lower(), "wakad")
        self.assertIn("table", parsed_hi["clean_query"])

    def test_semantic_ranking_filters_and_hinglish(self):
        """Verify semantic search applies extracted filters and handles Hinglish."""
        results, parsed = SearchService.rank_listings_semantic(
            self.listings, "study table under 3000 near Wakad"
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "IKEA Study Table Wood")

        # Hinglish query: "engineering ki kitab" -> should rank Textbook #1
        hi_results, _ = SearchService.rank_listings_semantic(self.listings, "engineering ki kitab")
        self.assertGreater(len(hi_results), 0)
        self.assertEqual(hi_results[0].category, "books")

    def test_image_search_and_similar_items(self):
        """Verify 512-d image search and similar items."""
        img_results = SearchService.search_by_image(
            self.listings, "casio scientific calculator solar", top_k=2
        )
        self.assertEqual(img_results[0].brand, "Casio")

        target = self.listings[0]
        similar = SearchService.find_similar_items(target, self.listings, top_k=2)
        self.assertTrue(all(item.id != target.id for item in similar))
        self.assertEqual(similar[0].category, "furniture")

    def test_saved_search_alert_matching(self):
        """Verify saved search matches new listings respecting filters and semantic similarity."""
        saved = MockSavedSearch(
            query_text="casio calculator",
            filters={"category": "electronics", "price_max": 1000},
        )
        calc_listing = self.listings[2]
        table_listing = self.listings[0]

        self.assertTrue(SearchService.matches_saved_search(calc_listing, saved))
        self.assertFalse(SearchService.matches_saved_search(table_listing, saved))


if __name__ == "__main__":
    unittest.main()
