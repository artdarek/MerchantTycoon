from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Transaction:
    """Represents a transaction (buy or sell)"""
    transaction_type: str  # "buy" or "sell"
    good_name: str
    quantity: int
    price_per_unit: int
    total_value: int
    day: int
    city: str
    ts: str = ""  # ISO datetime when transaction occurred
