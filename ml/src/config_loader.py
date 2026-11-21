# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Configuration and threshold loader for LOOP ML modules (`ml/configs/*.yaml`).

Parses `thresholds.yaml` and `training_config.yaml` using PyYAML if installed,
or a deterministic built-in YAML subset parser when running in minimal environments.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

ML_DIR = Path(__file__).resolve().parents[1]
THRESHOLDS_PATH = ML_DIR / "configs" / "thresholds.yaml"
TRAINING_CONFIG_PATH = ML_DIR / "configs" / "training_config.yaml"

DEFAULT_THRESHOLDS: Dict[str, Dict[str, Any]] = {
    "product_recognition": {
        "confidence_threshold": 0.80,
        "temperature": 1.00,
        "top_k": 3,
    },
    "condition_grader": {
        "confidence_threshold": 0.70,
        "ordinal_cutoffs": [0.5, 1.5, 2.5],
        "logistic_scale": 3.0,
    },
    "price_estimator": {
        "conformal_alpha": 0.20,
        "conformal_scale": 1.12,
        "known_subtype_spread": 0.22,
        "unknown_subtype_spread": 0.45,
        "fair_deal_great_max_ratio": 0.85,
        "fair_deal_fair_max_ratio": 1.15,
    },
    "quality_checker": {
        "blur_threshold": 100.0,
        "dark_threshold": 40.0,
        "overexposed_threshold": 220.0,
    },
    "privacy_scrubber": {
        "box_confidence_threshold": 0.45,
        "pixel_block_size": 14,
        "prohibited_licenses": ["AGPL-3.0", "GPL-3.0"],
    },
    "active_learning": {
        "min_completed_trades": 1,
        "min_price_median_ratio": 0.20,
        "max_price_median_ratio": 3.00,
        "promotion_min_gain": 0.005,
        "max_class_regression": 0.020,
    },
    "swap_engine": {
        "max_cycle_length": 3,
        "value_tolerance_delta": 0.30,
    },
}


def _parse_scalar(raw: str) -> Any:
    """Parse a YAML scalar or inline list value."""
    val = raw.split("#")[0].strip()
    if not val:
        return None
    if val.startswith("[") and val.endswith("]"):
        try:
            return json.loads(val)
        except Exception:
            items = [x.strip().strip('"').strip("'") for x in val[1:-1].split(",") if x.strip()]
            parsed = []
            for item in items:
                try:
                    parsed.append(float(item) if "." in item else int(item))
                except ValueError:
                    parsed.append(item)
            return parsed
    if val.startswith(('"', "'")) and val.endswith(('"', "'")):
        return val[1:-1]
    if val.lower() == "true":
        return True
    if val.lower() == "false":
        return False
    try:
        return float(val) if "." in val else int(val)
    except ValueError:
        return val


def parse_simple_yaml(path: Path) -> Dict[str, Any]:
    """Load a 2-level YAML file using PyYAML or built-in parser."""
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore[import-untyped]

        loaded = yaml.safe_load(text)
        if isinstance(loaded, dict):
            return loaded
    except ImportError:
        pass

    result: Dict[str, Any] = {}
    current_section: str | None = None
    current_subsection: str | None = None

    for line in text.splitlines():
        stripped = line.split("#")[0].rstrip()
        if not stripped.strip():
            continue
        indent = len(stripped) - len(stripped.lstrip(" "))
        key_part, _, val_part = stripped.strip().partition(":")
        key = key_part.strip()
        val_str = val_part.strip()

        if indent == 0:
            current_section = key
            current_subsection = None
            result[current_section] = _parse_scalar(val_str) if val_str else {}
        elif indent == 2 and current_section is not None:
            if not isinstance(result.get(current_section), dict):
                result[current_section] = {}
            if val_str:
                result[current_section][key] = _parse_scalar(val_str)
                current_subsection = None
            else:
                result[current_section][key] = {}
                current_subsection = key
        elif indent >= 4 and current_section is not None and current_subsection is not None:
            sub_dict = result[current_section].get(current_subsection)
            if isinstance(sub_dict, dict):
                sub_dict[key] = _parse_scalar(val_str)

    return result


def load_thresholds(path: Path = THRESHOLDS_PATH) -> Dict[str, Dict[str, Any]]:
    """Return merged operational thresholds from `ml/configs/thresholds.yaml`."""
    merged = {k: dict(v) for k, v in DEFAULT_THRESHOLDS.items()}
    parsed = parse_simple_yaml(path)
    for section, values in parsed.items():
        if isinstance(values, dict):
            merged.setdefault(section, {}).update(values)
    return merged


def load_training_config(path: Path = TRAINING_CONFIG_PATH) -> Dict[str, Any]:
    """Return training and ONNX export settings from `ml/configs/training_config.yaml`."""
    return parse_simple_yaml(path)
