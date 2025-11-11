from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Good:
    """Represents a tradeable good"""
    name: str
    base_price: int
    price_variance: float = 0.3  # 30% variance
    # Classification
    type: str = "standard"   # "standard" | "luxury"
    category: str = "electronics"  # e.g., "electronics" | "jewelry"
