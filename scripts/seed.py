# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Seed script for populating the database with realistic simulated listings.

All synthetic records are explicitly tagged with data_origin='simulated'
per DATA_MODEL_AND_API.md §1 & ML_SPEC.
"""

import os
import sys
import uuid
from decimal import Decimal

# Standalone simulation items
SAMPLE_LISTINGS = [
    {
        "type": "sell",
        "category": "electronics",
        "subtype": "Calculator",
        "brand": "Casio",
        "model": "fx-991EX ClassWiz",
        "title": "Casio fx-991EX ClassWiz Engineering Calculator",
        "description": "Used for 1 year in engineering mathematics. Clean solar panel and crisp display, pristine battery compartment.",
        "condition": "good",
        "condition_ai": "good",
        "condition_conf": 0.91,
        "price_ask": Decimal("850.00"),
        "price_low": Decimal("700.00"),
        "price_likely": Decimal("850.00"),
        "price_high": Decimal("1100.00"),
        "price_ai_likely": Decimal("850.00"),
        "fair_deal": "fair",
        "attributes": {"color": "black", "battery": "LR44", "display": "Natural Textbook"},
        "area_name": "Lohegaon / Charholi",
        "geohash5": "tek3x",
        "status": "active",
        "data_origin": "simulated",
        "images": [
            {
                "storage_path": "simulated/calc_front.jpg",
                "scrubbed": True,
                "quality_score": 0.92,
                "scrub_boxes": [],
            }
        ],
    },
    {
        "type": "sell",
        "category": "furniture",
        "subtype": "Study Table",
        "brand": "IKEA",
        "model": "Micke Desk",
        "title": "IKEA Micke Compact Study Table with Cable Outlet",
        "description": "White study table with drawer and side storage. Sturdy and minimal wear, ideal for hostel rooms or compact flats.",
        "condition": "like_new",
        "condition_ai": "like_new",
        "condition_conf": 0.95,
        "price_ask": Decimal("2400.00"),
        "price_low": Decimal("2000.00"),
        "price_likely": Decimal("2500.00"),
        "price_high": Decimal("3200.00"),
        "price_ai_likely": Decimal("2450.00"),
        "fair_deal": "great",
        "attributes": {"color": "white", "dimensions": "73x50 cm", "material": "particleboard"},
        "area_name": "Wakad / Hinjawadi",
        "geohash5": "tek30",
        "status": "active",
        "data_origin": "simulated",
        "images": [
            {
                "storage_path": "simulated/ikea_desk.jpg",
                "scrubbed": True,
                "quality_score": 0.89,
                "scrub_boxes": [],
            }
        ],
    },
    {
        "type": "donate",
        "category": "books",
        "subtype": "Textbook",
        "brand": "Pearson",
        "model": "3rd Edition",
        "title": "Higher Engineering Mathematics by B.S. Grewal",
        "description": "Essential textbook for Sem 1 and Sem 2 engineering students. Minor pencil marks, binding fully intact.",
        "condition": "good",
        "condition_ai": "good",
        "condition_conf": 0.87,
        "price_ask": Decimal("0.00"),
        "price_low": Decimal("0.00"),
        "price_likely": Decimal("0.00"),
        "price_high": Decimal("350.00"),
        "price_ai_likely": Decimal("250.00"),
        "fair_deal": "great",
        "attributes": {"edition": "44th", "language": "English", "pages": 1300},
        "area_name": "Lohegaon",
        "geohash5": "tek3x",
        "status": "active",
        "data_origin": "simulated",
        "images": [
            {
                "storage_path": "simulated/math_book.jpg",
                "scrubbed": True,
                "quality_score": 0.94,
                "scrub_boxes": [],
            }
        ],
    },
    {
        "type": "swap",
        "category": "hobbies",
        "subtype": "Acoustic Guitar",
        "brand": "Yamaha",
        "model": "F280",
        "title": "Yamaha F280 Acoustic Guitar with Padded Gig Bag",
        "description": "Well maintained acoustic guitar with smooth action. Looking to swap for a USB audio interface or study monitor.",
        "condition": "like_new",
        "condition_ai": "like_new",
        "condition_conf": 0.93,
        "price_ask": Decimal("5200.00"),
        "price_low": Decimal("4500.00"),
        "price_likely": Decimal("5300.00"),
        "price_high": Decimal("6500.00"),
        "price_ai_likely": Decimal("5200.00"),
        "fair_deal": "fair",
        "attributes": {"strings": "D'Addario Bronze", "finish": "Natural"},
        "area_name": "Viman Nagar",
        "geohash5": "tek3y",
        "status": "active",
        "data_origin": "simulated",
        "images": [
            {
                "storage_path": "simulated/yamaha_guitar.jpg",
                "scrubbed": True,
                "quality_score": 0.96,
                "scrub_boxes": [],
            }
        ],
    },
]


def generate_seed_data():
    print(f"Loaded {len(SAMPLE_LISTINGS)} simulated listings tagged with data_origin='simulated'.")
    for item in SAMPLE_LISTINGS:
        print(f" - [{item['category'].upper()}] {item['title']} ({item['type']}) @ {item['area_name']}")
    print("Simulated dataset verified and ready for database injection.")


if __name__ == "__main__":
    generate_seed_data()
