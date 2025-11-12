from __future__ import annotations
from dataclasses import dataclass


@dataclass
class BankTransaction:
    """Represents a single bank account transaction (deposit, withdrawal, or interest).

    Bank transactions provide a complete audit trail of all account activity,
    enabling balance verification, interest tracking, and financial reporting.
    Each transaction is immutable once created and stored chronologically.

    Attributes:
        tx_type: Type of bank transaction operation.
            Valid values:
            - "deposit": Cash moved from hand into bank (increases balance)
            - "withdraw": Cash moved from bank to hand (decreases balance)
            - "interest": Daily interest credited to account (increases balance)
            - "dividend": Stock dividend payout credited to account (increases balance)
        amount: Transaction amount in dollars. Always positive (>= 0).
            For deposits/interest: amount added to balance
            For withdrawals: amount removed from balance
        balance_after: Account balance immediately after this transaction, in dollars.
            Used for verification and balance history tracking.
            Should equal previous_balance + amount (deposit/interest) or
            previous_balance - amount (withdrawal).
        day: Game day number when this transaction occurred (e.g., 1, 2, 3...).
            Used for chronological ordering and daily summaries.
        title: Optional descriptive label for the transaction (e.g., "Dividend for GOOGL").
            Provides context for special transactions. Empty string if not specified.
        ts: ISO 8601 datetime timestamp (e.g., "2025-01-15T14:30:00").
            Provides precise timing from ClockService for audit trail.
            Empty string if timestamp not available (backward compatibility).

    Examples:
        >>> deposit = BankTransaction(
        ...     tx_type="deposit",
        ...     amount=5000,
        ...     balance_after=15000,
        ...     day=1,
        ...     title="Initial deposit",
        ...     ts="2025-01-15T10:00:00"
        ... )
        >>> interest = BankTransaction(
        ...     tx_type="interest",
        ...     amount=1,
        ...     balance_after=15001,
        ...     day=2,
        ...     title="Daily interest",
        ...     ts="2025-01-16T00:00:00"
        ... )
        >>> withdraw = BankTransaction(
        ...     tx_type="withdraw",
        ...     amount=3000,
        ...     balance_after=12001,
        ...     day=2,
        ...     title="Cash withdrawal",
        ...     ts="2025-01-16T15:30:00"
        ... )

    Notes:
        - Transactions are append-only (immutable once created)
        - Used for account history and balance verification
        - Interest transactions accumulate fractional amounts before crediting
        - balance_after enables quick balance lookup without recalculation
        - Transactions are stored in chronological order in BankAccount.transactions
    """
    tx_type: str  # "deposit" | "withdraw" | "interest"
    amount: int  # Transaction amount (always positive)
    balance_after: int  # Account balance after this transaction
    day: int  # Game day when transaction occurred
    title: str = ""  # Optional transaction description
    ts: str = ""  # ISO datetime (YYYY-MM-DDTHH:MM:SS) from ClockService
