"""Lotto system configuration settings."""

from dataclasses import dataclass


@dataclass(frozen=True)
class LottoSettings:
    """Configuration for the daily lottery system.

    Attributes:
        number_range_max: Maximum number in lottery range (1 to this value)
        numbers_per_ticket: How many numbers on each ticket (default: 6)
        ticket_price: One-time cost to purchase a new ticket
        ticket_renewal_cost: Daily cost to keep ticket active
        max_tickets: Maximum tickets player can own (0 = unlimited)
        payouts: Prize amounts for matching 2-6 numbers
    """

    # Number range and ticket configuration
    number_range_max: int = 12
    numbers_per_ticket: int = 6

    # Pricing
    ticket_price: int = 10
    ticket_renewal_cost: int = 10

    # Limits
    max_tickets: int = 0  # 0 = unlimited

    # Payouts by number of matches
    payouts: dict[int, int] = None

    def __post_init__(self):
        """Initialize default payout structure if not provided."""
        if self.payouts is None:
            object.__setattr__(self, "payouts", {
                2: 10,
                3: 100,
                4: 1_000,
                5: 1_000_000,
                6: 10_000_000,
            })