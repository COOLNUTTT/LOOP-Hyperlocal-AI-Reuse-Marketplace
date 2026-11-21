# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Acceptance tests for Phase 17 Marketplace Simulator & Price-Drop Suggestions:

1. Same seed -> identical results (`run_marketplace_simulation`).
2. Sensitivity analysis (+/- 50% on behavioural parameters) and all 6 scale
   experiments included, with `data_origin='simulated'`.
3. All figures captioned "Synthetic" (`simulator_figures_synthetic.svg`), and
   limitation about assumed buyer behaviour written into `ml/reports/simulator/report.md`.
4. Price-drop heuristic NEVER suggests below the floor (`0.60 * predicted_low` or
   `explicit_floor`) and NEVER suggests beyond 15% per step (`drop_pct <= 15.0`).
"""

import unittest

from ml.src.price_drop import compute_price_drop_suggestion
from sim.simulator import (
    REPORT_DIR,
    run_all_simulator_experiments,
    run_marketplace_simulation,
)


class TestPhase17SimulatorPriceDropAcceptance(unittest.TestCase):
    def test_same_seed_produces_identical_results(self) -> None:
        """Verify deterministic reproducibility: same seed -> identical results."""
        run_a = run_marketplace_simulation(seed=42, n_users=200, days=25, p_fraud=0.05)
        run_b = run_marketplace_simulation(seed=42, n_users=200, days=25, p_fraud=0.05)
        run_c = run_marketplace_simulation(seed=99, n_users=200, days=25, p_fraud=0.05)

        self.assertEqual(run_a, run_b)
        self.assertEqual(run_a["data_origin"], "simulated")
        self.assertNotEqual(run_a, run_c)

    def test_price_drop_never_below_floor_or_beyond_15pct_per_step(self) -> None:
        """Verify price-drop heuristic strictly respects both floor and 15%-step guardrails."""
        # Case 1: High asking price (5000 vs likely 800) -> capped at 15% single-step drop (4250)
        res_high = compute_price_drop_suggestion(
            price_ask=5000.0,
            predicted_low=700.0,
            predicted_likely=800.0,
            days_active=14,
            views=60,
        )
        self.assertTrue(res_high["should_drop"])
        self.assertGreaterEqual(res_high["suggested_price"], res_high["floor_price"])
        self.assertGreaterEqual(res_high["suggested_price"], 5000.0 * 0.85)
        self.assertLessEqual(res_high["drop_pct"], 15.0)

        # Case 2: Asking price close to floor (ask=450, low=700 -> floor=420, 15% step=382.5)
        # Must stop at floor=420 (only 6.67% drop) and never cross below 420
        res_near_floor = compute_price_drop_suggestion(
            price_ask=450.0,
            predicted_low=700.0,
            predicted_likely=430.0,
            days_active=10,
            views=35,
        )
        self.assertEqual(res_near_floor["floor_price"], 420.0)
        self.assertGreaterEqual(res_near_floor["suggested_price"], 420.0)
        self.assertLessEqual(res_near_floor["drop_pct"], 15.0)

        # Case 3: Asking price already below floor (ask=390, floor=420) -> no drop suggested
        res_below_floor = compute_price_drop_suggestion(
            price_ask=390.0,
            predicted_low=700.0,
            predicted_likely=800.0,
            days_active=12,
            views=40,
        )
        self.assertFalse(res_below_floor["should_drop"])
        self.assertEqual(res_below_floor["drop_pct"], 0.0)

        # Case 4: Grid sweep across diverse ask/low/floor combinations
        for ask in (300.0, 600.0, 950.0, 1800.0, 12000.0):
            for low in (250.0, 500.0, 900.0, 2000.0):
                for exp_floor in (None, 400.0, 800.0):
                    out = compute_price_drop_suggestion(
                        price_ask=ask,
                        predicted_low=low,
                        predicted_likely=low * 1.2,
                        days_active=9,
                        views=30,
                        explicit_floor=exp_floor,
                    )
                    self.assertLessEqual(out["drop_pct"], 15.0 + 1e-6)
                    if ask >= out["floor_price"]:
                        self.assertGreaterEqual(out["suggested_price"], out["floor_price"])
                        self.assertGreaterEqual(out["suggested_price"], round(ask * 0.85, 2))

    def test_simulator_experiments_sensitivity_and_synthetic_captions(self) -> None:
        """Verify 6 experiments, sensitivity analysis, synthetic SVG captions, and limitation."""
        payload = run_all_simulator_experiments(seed=42)
        self.assertEqual(payload["data_origin"], "simulated")

        # Swap scaling 100 -> 10,000 users
        pop_sizes = [row["n_users"] for row in payload["swap_scaling"]]
        self.assertEqual(pop_sizes, [100, 500, 1000, 5000, 10000])
        for row in payload["swap_scaling"]:
            self.assertGreater(row["cpsat_3way_trades"], row["greedy_2way_trades"])

        # Sensitivity analysis (+/- 50%)
        sens = payload["sensitivity_analysis"]
        self.assertEqual(len(sens), 3)
        self.assertEqual([s["multiplier"] for s in sens], [0.5, 1.0, 1.5])

        # Verify SVG figure is captioned 'Synthetic' and 'data_origin=simulated'
        svg_path = REPORT_DIR / "simulator_figures_synthetic.svg"
        self.assertTrue(svg_path.exists())
        svg_text = svg_path.read_text(encoding="utf-8")
        self.assertIn("Synthetic", svg_text)
        self.assertIn("data_origin='simulated'", svg_text)

        # Verify report contains explicit limitation about assumed buyer behaviour
        report_path = REPORT_DIR / "report.md"
        self.assertTrue(report_path.exists())
        report_text = report_path.read_text(encoding="utf-8")
        self.assertIn("Assumed buyer behaviour limitation", report_text)
        self.assertIn("Synthetic", report_text)


if __name__ == "__main__":
    unittest.main()
