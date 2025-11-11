from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from merchant_tycoon.domain.model.bank_transaction import BankTransaction


@dataclass
class BankAccount:
    """Represents the player's bank account with deposit and interest functionality.

    The bank account provides a safe place to store cash and earn interest through
    daily compounding. Unlike inventory, bank deposits are protected from random
    events (theft, fire, etc.) making it a low-risk wealth preservation strategy.

    Attributes:
        balance: Current account balance in dollars. Can be 0 or positive.
            Increases with deposits and interest accrual, decreases with withdrawals.
        interest_rate_annual: Annual Percentage Rate (APR) for interest calculation.
            Typically 0.01-0.03 (1%-3% APR). Randomized daily within configured range.
            Converted to daily rate as: daily_rate = APR / 365
            Example: 0.02 APR = 2% annual = ~0.0055% daily
        accrued_interest: Fractional interest cents accumulated but not yet credited.
            When this reaches >= $1, it's added to balance and reset.
            Enables precise interest calculation without rounding errors.
            Example: 0.67 means $0.67 has accrued, waiting for $0.33 more
        last_interest_day: Game day number when interest was last calculated.
            Used to prevent duplicate interest accrual on the same day.
            Updated each time interest is processed.
        transactions: Complete history of all bank account activity.
            List of BankTransaction objects in chronological order.
            Includes deposits, withdrawals, and interest credits.
            Empty list for new accounts.

    Examples:
        >>> account = BankAccount(
        ...     balance=10000,
        ...     interest_rate_annual=0.02,
        ...     accrued_interest=0.0,
        ...     last_interest_day=0,
        ...     transactions=[]
        ... )
        >>> # After one day with $10,000 at 2% APR:
        >>> daily_rate = 0.02 / 365  # ~0.000055
        >>> daily_interest = 10000 * daily_rate  # ~$0.55
        >>> account.accrued_interest += daily_interest  # 0.55
        >>> # After 2 days:
        >>> account.accrued_interest += daily_interest  # 1.10
        >>> # Credit whole dollar
        >>> account.balance += 1  # 10001
        >>> account.accrued_interest = 0.10  # Keep fractional part

    Notes:
        - Interest compounds daily (not annually)
        - APR is converted to daily rate: daily_rate = APR ÷ 365
        - Fractional cents track sub-dollar amounts precisely
        - Interest only accrues on positive balances
        - Withdrawals have no penalties or fees
        - Bank balance is immune to random game events
        - Transactions list provides complete audit trail
    """
    balance: int = 0
    # Annual interest rate (APR), used to compute daily rate as APR/365.
    interest_rate_annual: float = 0.02  # Default 2% APR
    accrued_interest: float = 0.0  # Fractional interest not yet credited
    last_interest_day: int = 0  # Last day interest was calculated
    transactions: List[BankTransaction] = field(default_factory=list)
