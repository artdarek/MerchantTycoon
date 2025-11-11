from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Transaction:
    """Represents a goods trading transaction (buy or sell operation).

    Transactions provide a complete audit trail of all goods trading activity,
    enabling profit/loss analysis, trade history review, and accounting records.
    Each transaction captures the details of a single buy or sell action.

    Attributes:
        transaction_type: Type of transaction operation.
            Valid values:
            - "buy": Purchase of goods from the market
            - "sell": Sale of goods from inventory
        good_name: Name of the product traded (e.g., "TV", "Ferrari", "Cocaine").
            Must match a valid Good.name from the GOODS constant.
        quantity: Number of units traded in this transaction. Must be > 0.
            For buys: units added to inventory
            For sells: units removed from inventory
        price_per_unit: Market price per unit at the time of transaction, in dollars.
            Reflects the actual price paid (buy) or received (sell) per unit,
            including city multipliers and variance.
        total_value: Total transaction value in dollars (quantity × price_per_unit).
            For buys: total cost (cash deducted)
            For sells: total revenue (cash received)
            This is the gross amount before any fees or commissions.
        day: Game day number when this transaction occurred (e.g., 1, 2, 3...).
            Used for chronological ordering and performance analysis.
        city: Name of the city where this transaction took place (e.g., "Warsaw", "London").
            Important for tracking trade routes and arbitrage opportunities.
        ts: ISO 8601 datetime timestamp when the transaction occurred (e.g., "2025-01-15T14:30:00").
            Provides precise timing for audit trail and transaction history.
            Empty string if not set (backward compatibility).

    Examples:
        >>> buy_tx = Transaction(
        ...     transaction_type="buy",
        ...     good_name="TV",
        ...     quantity=10,
        ...     price_per_unit=800,
        ...     total_value=8000,
        ...     day=1,
        ...     city="Warsaw",
        ...     ts="2025-01-15T10:00:00"
        ... )
        >>> sell_tx = Transaction(
        ...     transaction_type="sell",
        ...     good_name="TV",
        ...     quantity=10,
        ...     price_per_unit=1000,
        ...     total_value=10000,
        ...     day=2,
        ...     city="London",
        ...     ts="2025-01-16T14:30:00"
        ... )
        >>> profit = sell_tx.total_value - buy_tx.total_value  # $2000 profit

    Notes:
        - Transactions are append-only (immutable once created)
        - Used for historical analysis and profit/loss calculations
        - Does not track fees or commissions (those are handled separately)
        - PurchaseLot objects provide lot-level tracking, Transaction provides transaction-level history
        - "loss" transactions may be recorded separately for event-based losses
    """
    transaction_type: str  # "buy" | "sell" | "loss"
    good_name: str
    quantity: int
    price_per_unit: int
    total_value: int
    day: int
    city: str
    ts: str = ""  # ISO datetime when transaction occurred
