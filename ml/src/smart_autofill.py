# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Smart autofill specification and template generator for campus reuse items."""

from typing import Any, Dict, List, Optional

SPECIFICATION_TEMPLATES: Dict[str, Dict[str, Any]] = {
    # Electronics
    "scientific calculator": {
        "display": "High-resolution natural textbook LCD",
        "power_source": "Solar cell + backup button battery",
        "features": "Matrix calculus, statistics, equation solver",
        "included_accessories": ["Hard sliding protective case"],
    },
    "laptop": {
        "screen_size": "14-15.6 inch anti-glare display",
        "storage_type": "Solid State Drive (SSD)",
        "ram": "8GB / 16GB RAM",
        "included_accessories": ["Original OEM charging adapter"],
    },
    "headphones": {
        "connectivity": "Bluetooth 5.0 + 3.5mm AUX jack",
        "battery_life": "20-30 hours estimated",
        "mic": "Built-in hands-free microphone",
        "included_accessories": ["USB-C charging cable"],
    },
    "monitor": {
        "resolution": "1920x1080 Full HD",
        "ports": ["HDMI", "VGA / DisplayPort"],
        "mount": "VESA 100x100 compatible",
        "included_accessories": ["Power cord", "HDMI cable"],
    },
    "keyboard": {
        "switch_type": "Membrane / Mechanical tactile keys",
        "layout": "Standard QWERTY ANSI",
        "connection": "USB wired or 2.4GHz wireless dongle",
    },
    "power bank": {
        "capacity": "10000mAh / 20000mAh fast charge",
        "ports": ["Dual USB-A output", "USB-C bidirectional"],
        "protection": "Over-voltage and short circuit guard",
    },
    # Furniture
    "study table": {
        "material": "Engineered wood / Particle board with metal frame",
        "dimensions": "90-120cm length x 50-60cm width",
        "drawers": "1-2 storage shelves or drawers",
        "assembly": "Freestanding sturdy campus desk",
    },
    "ergonomic chair": {
        "lumbar_support": "Adjustable mesh back support",
        "height_mechanism": "Class-4 hydraulic gas lift",
        "wheels": "360-degree nylon caster wheels",
    },
    "bookshelf": {
        "tiers": "3 to 4 tier vertical shelving",
        "load_capacity": "15-20 kg per shelf",
    },
    "mattress": {
        "size": "Single bed (72x36 inches)",
        "thickness": "4 to 6 inches high-density foam",
        "cover": "Breathable cotton/polyester zippered cover",
    },
    # Books
    "engineering textbook": {
        "syllabus": "Engineering Degree / Diploma curriculum",
        "edition": "Standard recommended student edition",
        "language": "English",
        "markings": "Clean text with minimal highlighter notes",
    },
    "literature": {
        "format": "Paperback",
        "language": "English",
    },
    "competitive exam guide": {
        "target_exam": "GATE / CAT / GRE / Placement prep",
        "content": "Solved sample papers and previous year questions",
    },
    # Hobbies
    "acoustic guitar": {
        "type": "Full size 38-41 inch dreadnought acoustic",
        "strings": "Steel strings",
        "included_accessories": ["Gig bag cover"],
    },
    "badminton racket": {
        "frame": "Carbon graphite lightweight frame",
        "tension": "22-26 lbs string tension",
        "grip": "Synthetic sweat-absorbent grip",
    },
    "board game": {
        "players": "2 to 6 players",
        "pieces": "All cards, dice, tokens accounted for",
    },
    "yoga mat": {
        "thickness": "6mm non-slip EVA/TPE foam",
        "carry_strap": "Included elastic carry strap",
    },
}

DEFECT_DESCRIPTIONS: Dict[str, str] = {
    "like_new": "Pristine cosmetic and structural condition, zero noticeable scratches or wear.",
    "good": "Normal gentle use with minor cosmetic surface scuffs; completely functional and sturdy.",
    "fair": "Visible wear marks, scuffs or slight discoloration from campus use; fully operable.",
    "poor": "Heavy cosmetic wear, scratches, or missing minor accessories; functional but well-used.",
}


class SmartAutofillGenerator:
    """Produces templated smart attributes, specifications, and draft descriptions."""

    @staticmethod
    def generate_smart_attributes(
        category: str,
        subtype: Optional[str] = None,
        brand: Optional[str] = None,
        model: Optional[str] = None,
        condition: str = "good",
    ) -> Dict[str, Any]:
        """Generate structured specifications and attributes for the listing."""
        key = (subtype or "").strip().lower()
        template = SPECIFICATION_TEMPLATES.get(key, {})

        attributes = dict(template)
        attributes["wear_summary"] = DEFECT_DESCRIPTIONS.get(condition, DEFECT_DESCRIPTIONS["good"])
        if brand and brand.lower() != "standard":
            attributes["brand_verified"] = brand
        if model:
            attributes["model_spec"] = model

        return attributes

    @staticmethod
    def generate_draft_copy(
        category: str,
        subtype: Optional[str],
        brand: Optional[str],
        model: Optional[str],
        condition: str,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, str]:
        """Produce structured high-clarity title and description."""
        brand_name = brand if (brand and brand.lower() != "standard") else ""
        model_name = model if (model and model.lower() != "standard") else ""
        subtype_name = subtype or category.capitalize()

        parts = [p for p in [brand_name, model_name, subtype_name] if p]
        title = " ".join(parts).strip()
        if len(title) < 5:
            title = f"{subtype_name} ({category.capitalize()})"

        cond_label = condition.replace("_", " ").capitalize()
        wear_desc = DEFECT_DESCRIPTIONS.get(condition, DEFECT_DESCRIPTIONS["good"])

        desc_lines = [
            f"{title} offered for campus reuse in {cond_label} condition.",
            wear_desc,
        ]

        if attributes:
            spec_highlights = []
            for k, v in attributes.items():
                if k not in ["wear_summary", "brand_verified", "model_spec"]:
                    val_str = ", ".join(v) if isinstance(v, list) else str(v)
                    formatted_key = k.replace("_", " ").capitalize()
                    spec_highlights.append(f"• {formatted_key}: {val_str}")
            if spec_highlights:
                desc_lines.append("\nKey Specifications:")
                desc_lines.extend(spec_highlights[:4])

        desc_lines.append("\nHyperlocal peer handover available on campus.")
        return {
            "title": title[:200],
            "description": "\n".join(desc_lines)[:5000],
        }


smart_autofill = SmartAutofillGenerator()
