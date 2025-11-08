from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Loan:
    """Represents a single loan instance with its own rate and lifecycle.
    rate_annual is the fixed APR for this loan. accrued_interest holds
    fractional interest until whole units can be added to remaining.
    """
    loan_id: int
    principal: int
    remaining: int
    repaid: int
    day_taken: int
    # New APR-based model
    rate_annual: float = 0.10
    accrued_interest: float = 0.0
