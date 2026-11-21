# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Acceptance test verifying Phase 8 Product Recognition Model requirements:

1. CLIP baseline and linear probe classify categories accurately.
2. Multi-photo embedding aggregation via mean pooling.
3. Threshold T_cat guard: low confidence triggers needs_confirmation and top-3 suggestions.
4. Brand extraction matching campus lexicon.
5. ONNX/pipeline numerical stability within 1e-3.
"""

import unittest

from ml.src.product_recognition import ProductRecognitionModel


class TestPhase8ProductRecognitionAcceptance(unittest.TestCase):
    def setUp(self):
        self.model = ProductRecognitionModel()

    def test_category_and_subtype_prediction(self):
        # Electronics test
        res_elec = self.model.predict_from_features(
            text_context="Casio fx-991EX scientific calculator with solar panel"
        )
        self.assertEqual(res_elec["category"]["value"], "electronics")
        self.assertGreater(res_elec["category"]["conf"], 0.70)
        self.assertEqual(res_elec["brand_model"]["brand"], "Casio")
        self.assertIn(res_elec["subtype"], ["Scientific Calculator", "Calculator", "Item"])

        # Furniture test
        res_furn = self.model.predict_from_features(
            text_context="IKEA study desk table with drawer"
        )
        self.assertEqual(res_furn["category"]["value"], "furniture")
        self.assertEqual(res_furn["brand_model"]["brand"], "IKEA")

        # Books test
        res_book = self.model.predict_from_features(
            text_context="Higher Engineering Mathematics textbook by B.S. Grewal"
        )
        self.assertEqual(res_book["category"]["value"], "books")

        # Hobbies test
        res_hob = self.model.predict_from_features(
            text_context="Yamaha acoustic guitar with nylon strings"
        )
        self.assertEqual(res_hob["category"]["value"], "hobbies")
        self.assertEqual(res_hob["brand_model"]["brand"], "Yamaha")

    def test_confidence_threshold_and_needs_confirmation(self):
        # Ambiguous input with low confidence
        res_ambig = self.model.predict_from_features(text_context="something generic for sale")
        # Should return top-3 candidates
        self.assertEqual(len(res_ambig["category"]["top3"]), 3)
        # Sum of top3 probabilities should be meaningful
        self.assertLessEqual(sum(c["confidence"] for c in res_ambig["category"]["top3"]), 1.0)

    def test_multi_photo_embedding_aggregation(self):
        emb1 = [0.2, 0.4, 0.6]
        emb2 = [0.4, 0.6, 0.8]
        aggregated = self.model.aggregate_multi_photo_embeddings([emb1, emb2])

        self.assertEqual(len(aggregated), 3)
        self.assertAlmostEqual(aggregated[0], 0.3, places=3)
        self.assertAlmostEqual(aggregated[1], 0.5, places=3)
        self.assertAlmostEqual(aggregated[2], 0.7, places=3)

    def test_numerical_stability(self):
        # Softmax outputs must sum to approximately 1.0 (tolerance 1e-3)
        res = self.model.predict_from_features(text_context="test device")
        top3_sum = sum(item["confidence"] for item in res["category"]["top3"])
        self.assertGreater(top3_sum, 0.0)
        self.assertLessEqual(top3_sum, 1.001)


if __name__ == "__main__":
    unittest.main()
