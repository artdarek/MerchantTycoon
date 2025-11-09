from __future__ import annotations
from dataclasses import dataclass
from typing import Dict


@dataclass
class City:
    """Represents a city/location"""
    name: str
    country: str
    price_multiplier: Dict[str, float]  # Per-good multipliers
