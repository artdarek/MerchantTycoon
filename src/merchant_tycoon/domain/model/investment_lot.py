from __future__ import annotations
from dataclasses import dataclass


@dataclass
class InvestmentLot:
    """Represents a batch of financial assets purchased at a specific price point.

    Investment lots track stocks, commodities, and cryptocurrencies using FIFO
    (First In, First Out) accounting. Unlike goods, investments are protected from
    random events and provide safe long-term wealth accumulation.

    Attributes:
        asset_symbol: Trading ticker symbol of the asset (e.g., "GOOGL", "BTC", "GOLD").
            Must match a valid Asset.symbol from the ASSETS constant.
        quantity: Current remaining units/shares in this lot. Decreases when assets
            are sold via FIFO or direct lot selection. Must be >= 0.
        purchase_price: Price paid per unit when this lot was acquired, in dollars.
            Used to calculate profit/loss when selling. Fixed at purchase time.
            Examples: $150 per GOOGL share, $35000 per BTC.
        day: Game day number when this lot was purchased (e.g., 1, 2, 3...).
            Used for tracking lot age, holding period, and FIFO ordering.
        ts: ISO 8601 datetime timestamp when the lot was created (e.g., "2025-01-15T14:30:00").
            Used for unique identification, precise ordering, and sell-from-lot operations.
            Empty string if not set (backward compatibility).
        days_held: Number of days this lot has been held. Incremented daily.
            Used to determine dividend eligibility based on minimum holding period.
            Starts at 0 when lot is created.

    Examples:
        >>> google_lot = InvestmentLot(
        ...     asset_symbol="GOOGL",
        ...     quantity=100,
        ...     purchase_price=150,
        ...     day=1,
        ...     ts="2025-01-15T10:00:00"
        ... )
        >>> # After selling 40 shares FIFO
        >>> google_lot.quantity = 60
        >>> # Calculate profit if current price is $180
        >>> profit = (180 - google_lot.purchase_price) * google_lot.quantity
        >>> # = $30 * 60 = $1,800

    Notes:
        - Lots are consumed FIFO when selling (oldest lots first)
        - Investment lots are never affected by random events (fire, theft, etc.)
        - Empty lots (quantity=0) are typically removed from portfolio
        - Buy/sell transactions incur commission fees (separate from lot tracking)
        - ts field enables sell-from-lot functionality for non-FIFO sales
        - Multiple lots of the same asset can exist with different purchase prices
    """
    asset_symbol: str
    quantity: int
    purchase_price: int  # Price per unit when purchased
    day: int
    ts: str = ""  # ISO datetime when lot was created
    days_held: int = 0  # Days held, incremented daily for dividend eligibility
