from __future__ import annotations
from dataclasses import dataclass


@dataclass
class BankTransaction:
    """Represents a bank transaction"""
    tx_type: str  # "deposit" | "withdraw" | "interest"
    amount: int
    balance_after: int
    day: int
    title: str = ""
    ts: str = ""  # ISO datetime (YYYY-MM-DDTHH:MM:SS) from ClockService
