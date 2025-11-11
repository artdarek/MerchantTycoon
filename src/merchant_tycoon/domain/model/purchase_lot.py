from __future__ import annotations
from dataclasses import dataclass


@dataclass
class PurchaseLot:
    """Represents a batch of goods purchased at a specific price point.

    Purchase lots implement FIFO (First In, First Out) inventory accounting,
    allowing precise profit/loss calculation and loss tracking for each batch.
    When goods are sold, the oldest lots are used first to calculate profits.

    Attributes:
        good_name: Name of the product purchased (e.g., "TV", "Ferrari").
            Must match a valid Good.name from the GOODS constant.
        quantity: Current remaining units in this lot. Decreases as goods are sold
            or lost to events. Must be >= 0.
        purchase_price: Price paid per unit when this lot was acquired, in dollars.
            Used to calculate profit/loss when selling. Fixed at purchase time.
        day: Game day number when this lot was purchased (e.g., 1, 2, 3...).
            Used for tracking lot age and FIFO ordering.
        city: Name of the city where this lot was purchased (e.g., "Warsaw", "London").
            Informational field for tracking purchase location.
        ts: ISO 8601 datetime timestamp when the lot was created (e.g., "2025-01-15T14:30:00").
            Used for unique identification and precise ordering. Empty string if not set.
        initial_quantity: Original number of units purchased in this lot.
            Remains constant and used to calculate total investment and loss percentages.
            Default 0 for backward compatibility with old saves.
        lost_quantity: Cumulative units lost to random events (fire, theft, etc.).
            Increases when losses occur, used for accounting and P/L reporting.
            Default 0 means no losses have occurred yet.

    Examples:
        >>> lot = PurchaseLot(
        ...     good_name="TV",
        ...     quantity=10,
        ...     purchase_price=800,
        ...     day=1,
        ...     city="Warsaw",
        ...     ts="2025-01-15T10:00:00",
        ...     initial_quantity=10,
        ...     lost_quantity=0
        ... )
        >>> # After selling 3 TVs
        >>> lot.quantity = 7  # 7 remaining
        >>> # After fire event destroys 2 TVs
        >>> lot.quantity = 5
        >>> lot.lost_quantity = 2

    Notes:
        - Lots are consumed FIFO when selling (oldest lots first)
        - Lost quantities are immediately recognized and reduce inventory
        - initial_quantity should be set equal to quantity at creation
        - Empty lots (quantity=0) are typically removed from inventory
        - ts field enables precise lot identification for sell-from-lot operations
    """
    good_name: str
    quantity: int
    purchase_price: int  # Price per unit when purchased
    day: int
    city: str
    ts: str = ""  # ISO datetime when lot was created
    # Loss accounting fields
    # initial_quantity is the number of units purchased in this lot
    # lost_quantity accumulates units lost due to events (recognized immediately)
    initial_quantity: int = 0
    lost_quantity: int = 0
