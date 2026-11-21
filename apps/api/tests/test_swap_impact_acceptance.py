# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Acceptance tests for Phase 16 Swap Engine and Impact Dashboard:

1. Swap cycles are valid: each user gives exactly one item and receives one item;
   value difference per user is within tolerance delta; vertex-disjoint CP-SAT
   set-packing solver finds 3-way cycles that greedy 2-way baseline cannot match.
2. Swap proposals confirm ONLY when all participants in the cycle confirm, generating
   per-edge handovers upon full confirmation.
3. Impact values trace directly to cited LCA factor sources in `ml/data/impact_factors.csv`,
   report ranges (not false single-point precision), and generate a sensitivity table
   across displacement factors d in {0.30, 0.45, 0.55, 0.70, 0.80}.
4. Both the swap engine and impact estimator are explicitly labelled `algorithmic`.
"""

import unittest
import uuid
from pathlib import Path

from ml.src.impact_estimator import (
    FACTORS_CSV_PATH,
    aggregate_impact_summary,
    estimate_item_impact,
    generate_sensitivity_table,
    load_impact_factors,
)
from ml.src.swap_engine import (
    build_compatibility_graph,
    solve_swap_cycles_cpsat,
    solve_swap_cycles_greedy_2way,
    validate_swap_cycle,
)

from app.services.swap_service import SwapService


class DummyCycle:
    def __init__(self, length: int = 3) -> None:
        self.id = uuid.uuid4()
        self.length = length
        self.status = "proposed"


class DummyProposal:
    def __init__(
        self,
        cycle_id: uuid.UUID,
        giver_id: uuid.UUID,
        receiver_id: uuid.UUID,
    ) -> None:
        self.id = uuid.uuid4()
        self.cycle_id = cycle_id
        self.giver_user_id = giver_id
        self.receiver_user_id = receiver_id
        self.listing_id = uuid.uuid4()
        self.confirmed_at = None


class TestPhase16SwapImpactAcceptance(unittest.TestCase):
    def test_valid_cycles_and_cpsat_vs_greedy_2way(self) -> None:
        """Verify cycle validity (give 1, receive 1, value within tolerance) and 3-way packing."""
        # 3 users forming a directed 3-cycle: u1 -> u2 -> u3 -> u1 (no 2-way cycles exist)
        listings = [
            {
                "id": "list-1",
                "seller_id": "user-1",
                "type": "swap",
                "status": "active",
                "category": "books",
                "title": "Cormen Algorithms Textbook",
                "price_likely": 800.0,
            },
            {
                "id": "list-2",
                "seller_id": "user-2",
                "type": "swap",
                "status": "active",
                "category": "electronics",
                "title": "Casio Scientific Calculator",
                "price_likely": 760.0,
            },
            {
                "id": "list-3",
                "seller_id": "user-3",
                "type": "swap",
                "status": "active",
                "category": "furniture",
                "title": "Study Desk Lamp Organizer",
                "price_likely": 820.0,
            },
        ]
        wishlists = [
            {
                "id": "wish-2",
                "user_id": "user-2",
                "want_category": "books",
                "want_text": "Cormen Algorithms Textbook",
                "max_price": 900.0,
                "active": True,
            },
            {
                "id": "wish-3",
                "user_id": "user-3",
                "want_category": "electronics",
                "want_text": "Casio Scientific Calculator",
                "max_price": 900.0,
                "active": True,
            },
            {
                "id": "wish-1",
                "user_id": "user-1",
                "want_category": "furniture",
                "want_text": "Study Desk Lamp Organizer",
                "max_price": 900.0,
                "active": True,
            },
        ]

        graph = build_compatibility_graph(listings, wishlists, value_tolerance=0.30)
        self.assertEqual(graph["methodology"], "algorithmic")

        # Greedy 2-way baseline finds 0 matches on a pure 3-cycle
        greedy_res = solve_swap_cycles_greedy_2way(graph, value_tolerance=0.30)
        self.assertEqual(greedy_res["users_matched"], 0)

        # CP-SAT <=3-cycle set-packing solver finds the 3-way cycle (3 users matched)
        cpsat_res = solve_swap_cycles_cpsat(graph, max_cycle_length=3, value_tolerance=0.30)
        self.assertEqual(cpsat_res["methodology"], "algorithmic")
        self.assertEqual(cpsat_res["users_matched"], 3)
        self.assertEqual(len(cpsat_res["selected_cycles"]), 1)

        cycle = cpsat_res["selected_cycles"][0]
        ok, reason = validate_swap_cycle(cycle["edges"], value_tolerance=0.30)
        self.assertTrue(ok, msg=reason)

        # Verify each user gives 1 and receives 1
        givers = [e["giver_user_id"] for e in cycle["edges"]]
        receivers = [e["receiver_user_id"] for e in cycle["edges"]]
        self.assertEqual(len(set(givers)), 3)
        self.assertEqual(set(givers), set(receivers))

        # Verify an unfair cycle with 5x value mismatch is rejected
        unfair_edges = [
            {"giver_user_id": "uA", "receiver_user_id": "uB", "value": 500.0},
            {"giver_user_id": "uB", "receiver_user_id": "uA", "value": 4000.0},
        ]
        ok_unfair, _ = validate_swap_cycle(unfair_edges, value_tolerance=0.30)
        self.assertFalse(ok_unfair)

    def test_proposals_confirm_only_when_all_confirm(self) -> None:
        """Verify a swap cycle confirms and unlocks handovers ONLY when all parties confirm."""
        u1, u2, u3 = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
        cycle = DummyCycle(length=3)
        p1 = DummyProposal(cycle.id, giver_id=u1, receiver_id=u2)
        p2 = DummyProposal(cycle.id, giver_id=u2, receiver_id=u3)
        p3 = DummyProposal(cycle.id, giver_id=u3, receiver_id=u1)
        all_props = [p1, p2, p3]

        # 1. Party 1 confirms -> partially_confirmed
        res1 = SwapService.confirm_proposal_and_check_cycle(p1, u1, cycle, all_props)
        self.assertFalse(res1["all_confirmed"])
        self.assertEqual(res1["cycle_status"], "partially_confirmed")
        self.assertEqual(len(res1["per_edge_handovers"]), 0)

        # 2. Party 2 confirms -> still partially_confirmed
        res2 = SwapService.confirm_proposal_and_check_cycle(p2, u2, cycle, all_props)
        self.assertFalse(res2["all_confirmed"])
        self.assertEqual(res2["cycle_status"], "partially_confirmed")
        self.assertEqual(len(res2["per_edge_handovers"]), 0)

        # 3. Party 3 confirms -> all confirmed! Cycle status becomes 'confirmed' & handovers created
        res3 = SwapService.confirm_proposal_and_check_cycle(p3, u3, cycle, all_props)
        self.assertTrue(res3["all_confirmed"])
        self.assertEqual(res3["cycle_status"], "confirmed")
        self.assertEqual(len(res3["per_edge_handovers"]), 3)

    def test_impact_values_trace_to_factor_sources_and_sensitivity_table(self) -> None:
        """Verify impact values trace to cited LCA sources and produce a sensitivity table."""
        self.assertTrue(FACTORS_CSV_PATH.exists())
        factors = load_impact_factors()
        self.assertIn(("electronics", "laptop"), factors)

        item_impact = estimate_item_impact("electronics", "laptop")
        self.assertEqual(item_impact["methodology"], "algorithmic")
        self.assertIn("Dell & Apple", item_impact["factor_source"])
        self.assertAlmostEqual(item_impact["co2_kg_avoided_low"], 210.0 * 0.30, places=2)
        self.assertAlmostEqual(item_impact["co2_kg_avoided_central"], 210.0 * 0.55, places=2)
        self.assertAlmostEqual(item_impact["co2_kg_avoided_high"], 210.0 * 0.80, places=2)

        sample_items = [
            {"category": "electronics", "subtype": "laptop"},
            {"category": "furniture", "subtype": "study table"},
            {"category": "books", "subtype": "textbook"},
        ]
        summary = aggregate_impact_summary(sample_items)
        self.assertEqual(summary["methodology"], "algorithmic")
        self.assertEqual(summary["completed_reuses_count"], 3)
        self.assertGreaterEqual(len(summary["cited_sources"]), 3)

        sens_table = generate_sensitivity_table(sample_items)
        self.assertEqual(len(sens_table), 5)
        self.assertEqual(
            [row["displacement_factor"] for row in sens_table],
            [0.30, 0.45, 0.55, 0.70, 0.80],
        )

        method_doc = Path(__file__).resolve().parents[3] / "docs" / "IMPACT_METHOD.md"
        self.assertTrue(method_doc.exists())


if __name__ == "__main__":
    unittest.main()
