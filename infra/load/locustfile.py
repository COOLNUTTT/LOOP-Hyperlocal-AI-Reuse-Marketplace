# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Locust Load & Throughput Testing Harness (`infra/load/locustfile.py`).

Simulates concurrent campus marketplace users across the core read, search,
ONNX AI inference, and algorithmic swap endpoints (`ROADMAP.md` Phase 18, `AGENTS.md` §3).

Usage:
    locust -f infra/load/locustfile.py --headless -u 50 -r 10 --run-time 30s --host http://localhost:8000
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List

try:
    from locust import HttpUser, between, task  # type: ignore[import-not-found]
except ImportError:

    class HttpUser:  # type: ignore[no-redef]
        """Fallback base class when locust is not imported."""

        client: Any = None

    def between(min_wait: float, max_wait: float) -> Callable[..., Any]:
        """Return wait-time descriptor."""
        return lambda: (min_wait, max_wait)

    def task(weight: int = 1) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Attach locust task weight metadata to a method."""

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            fn._locust_task_weight = weight  # type: ignore[attr-defined]
            return fn

        return decorator


LOAD_TEST_SLA_TARGETS: Dict[str, float] = {
    "p50_max_ms": 50.0,
    "p95_max_ms": 1000.0,
    "error_rate_max": 0.0,
}


class LOOPMarketplaceUser(HttpUser):
    """Simulated campus student browsing, searching, pricing, and listing items on LOOP."""

    wait_time = between(0.5, 2.0)

    @task(5)
    def browse_listings_semantic_hinglish(self) -> None:
        """High-frequency discovery query with Hinglish price & place parsing."""
        if self.client is not None:
            self.client.get(
                "/api/v1/listings",
                params={"q": "study table under 3000 near Wakad", "mode": "semantic"},
            )

    @task(3)
    def estimate_conformal_price(self) -> None:
        """Medium-frequency split-conformal price & fair-deal badge calculation."""
        if self.client is not None:
            self.client.post(
                "/api/v1/ai/price-estimate",
                json={
                    "category": "electronics",
                    "subtype": "scientific calculator",
                    "brand": "Casio",
                    "condition": "good",
                    "price_ask": "850.00",
                },
            )

    @task(2)
    def analyze_photos_snap_to_list(self) -> None:
        """Full Snap-to-List ONNX CPU pipeline (recognition + CORAL condition + conformal price)."""
        if self.client is not None:
            self.client.post(
                "/api/v1/ai/analyze-photos",
                json={
                    "image_urls": [
                        "https://loop.campus/uploads/casio_fx991ex_scrubbed_1.jpg",
                        "https://loop.campus/uploads/casio_fx991ex_scrubbed_2.jpg",
                    ]
                },
            )

    @task(2)
    def check_onnx_and_health(self) -> None:
        """Health & ONNX runtime parity probe."""
        if self.client is not None:
            self.client.get("/api/v1/health")
            self.client.get("/api/v1/ai/onnx-status")

    @task(1)
    def enumerate_swap_cycles(self) -> None:
        """Algorithmic <=3-way barter cycle enumeration."""
        if self.client is not None:
            self.client.get("/api/v1/swap/cycles")


def get_registered_load_tasks() -> List[Dict[str, Any]]:
    """Return metadata for all registered Locust load tasks for verification tests."""
    tasks: List[Dict[str, Any]] = []
    for attr_name in dir(LOOPMarketplaceUser):
        attr = getattr(LOOPMarketplaceUser, attr_name)
        weight = getattr(attr, "_locust_task_weight", None)
        if weight is not None:
            tasks.append({"name": attr_name, "weight": int(weight)})
    return sorted(tasks, key=lambda x: (-x["weight"], x["name"]))
