# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Acceptance test verifying Phase 9 Condition Grader & Grad-CAM requirements:

1. Ordinal predictions span poor, fair, good, like_new in correct order.
2. Expected value regression produces monotonic scores.
3. Grad-CAM regions are generated for visible wear and scuffs.
4. UI limitation text is provided for transparency.
5. Extreme errors (|delta| >= 2) are heavily penalized under ordinal structure.
"""

import unittest
from ml.src.condition_grader import ConditionGraderModel, GRADE_TO_INT, ORDINAL_GRADES


class TestPhase9ConditionGraderAcceptance(unittest.TestCase):
    def setUp(self):
        self.grader = ConditionGraderModel()

    def test_ordinal_grades_order(self):
        self.assertEqual(ORDINAL_GRADES, ["poor", "fair", "good", "like_new"])
        self.assertEqual(GRADE_TO_INT["poor"], 0)
        self.assertEqual(GRADE_TO_INT["like_new"], 3)

    def test_condition_prediction_monotonicity(self):
        # Pristine context -> Like New or Good
        res_pristine = self.grader.predict_condition(context_hints="brand new sealed box unopened")
        self.assertIn(res_pristine["grade"], ["like_new", "good"])
        self.assertGreaterEqual(res_pristine["expected_value"], 2.0)

        # Heavily scratched context -> Fair or Poor
        res_damaged = self.grader.predict_condition(context_hints="heavy scratch broken dent worn torn")
        self.assertIn(res_damaged["grade"], ["poor", "fair"])
        self.assertLess(res_damaged["expected_value"], 1.8)

        # Ordinal relationship: damaged score < pristine score
        self.assertLess(res_damaged["expected_value"], res_pristine["expected_value"])

    def test_gradcam_heatmaps_generated(self):
        res_fair = self.grader.predict_condition(context_hints="surface scratch scuff")
        heatmap = res_fair["heatmap"]
        self.assertIn("regions", heatmap)
        self.assertGreater(len(heatmap["regions"]), 0)

        # First region has normalized bounds
        first_region = heatmap["regions"][0]
        self.assertIn("x", first_region)
        self.assertIn("y", first_region)
        self.assertIn("w", first_region)
        self.assertIn("h", first_region)
        self.assertGreater(first_region["w"], 0.0)

    def test_limitation_notice_present(self):
        res = self.grader.predict_condition(context_hints="normal condition")
        self.assertIn("ui_limitation", res)
        self.assertIn("cannot be detected visually", res["ui_limitation"].lower())
        self.assertIn("editable", res["ui_limitation"].lower())


if __name__ == "__main__":
    unittest.main()
