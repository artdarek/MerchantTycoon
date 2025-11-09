from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Asset:
    """Represents a stock or commodity"""
    name: str
    symbol: str
    base_price: int
    price_variance: float = 0.5  # 50% variance (more volatile than goods)
    asset_type: str = "stock"  # "stock" or "commodity"
