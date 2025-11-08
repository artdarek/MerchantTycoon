from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from merchant_tycoon.model.bank_transaction import BankTransaction


@dataclass
class BankAccount:
    """Represents player's bank account"""
    balance: int = 0
    # Legacy daily rate kept for backward compatibility with old saves/UI.
    interest_rate_daily: float = 0.0005
    # New: annual interest rate (APR), used to compute daily rate as APR/365.
    interest_rate_annual: float = 0.02
    accrued_interest: float = 0.0
    last_interest_day: int = 0
    transactions: List[BankTransaction] = field(default_factory=list)
