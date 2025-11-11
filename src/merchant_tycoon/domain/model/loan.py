from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Loan:
    """Represents a single loan with fixed APR and daily interest accrual.

    Loans provide leverage for accelerated wealth building by allowing players
    to borrow money for trading opportunities. Each loan has its own fixed APR
    that persists for the life of the loan, with interest compounding daily.

    Attributes:
        loan_id: Unique identifier for this loan instance. Used for tracking
            and referencing specific loans in repayment operations.
            Typically an auto-incrementing integer (1, 2, 3...).
        principal: Original loan amount borrowed, in dollars.
            Fixed at loan creation, represents the initial debt.
            Example: $10,000 for a standard loan.
        remaining: Current outstanding balance owed on the loan, in dollars.
            Decreases with repayments, increases with interest accrual.
            Loan is fully repaid when remaining reaches $0.
        repaid: Total amount repaid so far on this loan, in dollars.
            Increases with each payment. Used for tracking payment progress.
            Formula: repaid + remaining = principal + total_interest_accrued
        day_taken: Game day number when this loan was originated (e.g., 1, 2, 3...).
            Used for calculating loan age and payment history.
        rate_annual: Fixed Annual Percentage Rate (APR) for this loan.
            Typically 0.01-0.20 (1%-20% APR), randomized at loan creation.
            Remains constant for the life of the loan even as market rates change.
            Converted to daily rate as: daily_rate = rate_annual / 365
            Example: 0.10 APR = 10% annual = ~0.027% daily
        accrued_interest: Fractional interest cents accumulated but not yet added to remaining.
            When this reaches >= $1, it's added to remaining and reset.
            Enables precise interest calculation without rounding errors.
            Example: 0.85 means $0.85 has accrued, waiting for $0.15 more
        ts: ISO 8601 datetime timestamp when the loan was taken (e.g., "2025-01-15T14:30:00").
            Provides precise origination time for record keeping.
            Empty string if not set (backward compatibility).

    Examples:
        >>> loan = Loan(
        ...     loan_id=1,
        ...     principal=10000,
        ...     remaining=10000,
        ...     repaid=0,
        ...     day_taken=1,
        ...     rate_annual=0.10,
        ...     accrued_interest=0.0,
        ...     ts="2025-01-15T10:00:00"
        ... )
        >>> # After one day with $10,000 at 10% APR:
        >>> daily_rate = 0.10 / 365  # ~0.000274
        >>> daily_interest = 10000 * daily_rate  # ~$2.74
        >>> loan.accrued_interest += daily_interest  # 2.74
        >>> # Credit whole dollars to remaining
        >>> loan.remaining += int(loan.accrued_interest)  # 10002
        >>> loan.accrued_interest = 0.74  # Keep fractional part
        >>> # After partial repayment of $5,000
        >>> loan.remaining -= 5000  # 5002
        >>> loan.repaid += 5000  # 5000

    Notes:
        - Interest compounds daily (not annually)
        - APR is fixed at loan creation, unaffected by market rate changes
        - Fractional cents track sub-dollar amounts precisely
        - Each loan is independent with its own rate and balance
        - Players can take multiple loans simultaneously
        - No penalties for early repayment
        - Loans affect credit capacity calculations
        - Daily rate formula: daily_rate = APR ÷ 365
    """
    loan_id: int
    principal: int  # Original amount borrowed
    remaining: int  # Current amount owed
    repaid: int  # Total amount repaid so far
    day_taken: int  # Game day when loan was taken
    # APR-based model for realistic interest calculation
    rate_annual: float = 0.10  # Annual Percentage Rate (10% default)
    accrued_interest: float = 0.0  # Fractional interest not yet added to remaining
    ts: str = ""  # ISO datetime when loan was taken
