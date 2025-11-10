from __future__ import annotations
from dataclasses import dataclass


@dataclass
class PurchaseLot:
    """Represents a batch of goods purchased at a specific price"""
    good_name: str
    quantity: int
    purchase_price: int  # Price per unit
    day: int
    city: str
    ts: str = ""  # ISO datetime when lot was created
    # New fields for loss accounting (Option A)
    # initial_quantity is the number of units purchased in this lot
    # lost_quantity accumulates units lost due to events (recognized immediately)
    initial_quantity: int = 0
    lost_quantity: int = 0
