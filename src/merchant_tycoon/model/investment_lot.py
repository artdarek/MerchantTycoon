from __future__ import annotations
from dataclasses import dataclass


@dataclass
class InvestmentLot:
    """Represents a batch of stocks/commodities purchased at a specific price"""
    asset_symbol: str
    quantity: int
    purchase_price: int
    day: int
