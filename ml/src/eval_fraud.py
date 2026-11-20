# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Synthetic Evaluation for Fraud, Duplicate-Image, and Scam-Text Detection.

All test cases are explicitly labelled data_origin='synthetic'.
"""

from typing import Dict, List, Tuple
from ml.src.fraud_detector import FraudDetector

# Synthetic labelled scam-text dataset (data_origin='synthetic')
SYNTHETIC_SCAM_TEXTS: List[Tuple[str, bool, str]] = [
    ("Pay advance payment of 500 via UPI before meetup", True, "synthetic"),
    ("Scan QR code to receive money and enter UPI PIN", True, "synthetic"),
    ("Urgent! Army courier customs fee required, text me on WhatsApp", True, "synthetic"),
    ("Click link for free gift lottery prize", True, "synthetic"),
    ("Send token amount on Telegram to book the laptop", True, "synthetic"),
    ("Casio fx-991EX calculator in good condition, meetup at library", False, "synthetic"),
    ("IKEA study table for sale, minor scratch on corner", False, "synthetic"),
    ("B.S. Grewal engineering mathematics textbook 44th edition", False, "synthetic"),
    ("Yamaha F310 acoustic guitar with gig bag, negotiable", False, "synthetic"),
    ("Yonex badminton racket, used for 1 semester", False, "synthetic"),
]

# Synthetic near-duplicate image pairs (data_origin='synthetic')
SYNTHETIC_DUP_PAIRS: List[Tuple[str, str, bool, str]] = [
    ("ffffffff00000000", "ffffffff00000001", True, "synthetic"),   # 1-bit diff
    ("abcd1234abcd1234", "abcd1234abcd123f", True, "synthetic"),   # 3-bit diff
    ("1111222233334444", "1111222233334440", True, "synthetic"),   # 1-bit diff
    ("0000000000000000", "ffffffffffffffff", False, "synthetic"),  # 64-bit diff
    ("1234567890abcdef", "fedcba0987654321", False, "synthetic"),  # unrelated
    ("aaaa5555aaaa5555", "5555aaaa5555aaaa", False, "synthetic"),  # unrelated
]


def compute_metrics(y_true: List[bool], y_pred: List[bool]) -> Dict[str, float]:
    tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt and yp)
    fp = sum(1 for yt, yp in zip(y_true, y_pred) if not yt and yp)
    tn = sum(1 for yt, yp in zip(y_true, y_pred) if not yt and not yp)
    fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt and not yp)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "fpr": round(fpr, 4),
    }


def run_evaluation() -> Dict[str, Dict[str, float]]:
    scam_true = [label for _, label, _ in SYNTHETIC_SCAM_TEXTS]
    scam_pred = [FraudDetector.classify_scam_text(text)["is_scam"] for text, _, _ in SYNTHETIC_SCAM_TEXTS]

    dup_true = [label for _, _, label, _ in SYNTHETIC_DUP_PAIRS]
    dup_pred = [FraudDetector.check_duplicate_image(ha, hb)["is_duplicate"] for ha, hb, _, _ in SYNTHETIC_DUP_PAIRS]

    return {
        "scam_text_synthetic": compute_metrics(scam_true, scam_pred),
        "duplicate_image_synthetic": compute_metrics(dup_true, dup_pred),
    }


if __name__ == "__main__":
    print(run_evaluation())
