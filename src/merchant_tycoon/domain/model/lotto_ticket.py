"""Lotto ticket domain model."""

from dataclasses import dataclass
from typing import List


@dataclass
class LottoTicket:
    """Represents a single lottery ticket owned by the player.

    Attributes:
        numbers: List of 6 unique numbers chosen for this ticket
        purchase_day: Day number when ticket was purchased
        active: Whether ticket is currently active (eligible for draws)
    """

    numbers: List[int]
    purchase_day: int
    active: bool = True
    # Aggregates for UI and analytics
    total_cost: int = 0        # includes initial buy + renewals actually paid
    total_reward: int = 0      # sum of payouts won by this ticket

    def __post_init__(self):
        """Validate ticket data after initialization."""
        if not isinstance(self.numbers, list):
            raise ValueError("Ticket numbers must be a list")
        if len(self.numbers) != 6:
            raise ValueError(f"Ticket must have exactly 6 numbers, got {len(self.numbers)}")
        if len(set(self.numbers)) != 6:
            raise ValueError("Ticket numbers must be unique")
        if any(n < 1 for n in self.numbers):
            raise ValueError("All ticket numbers must be >= 1")

    def matches(self, drawn_numbers: List[int]) -> int:
        """Count how many numbers on this ticket match the drawn numbers.

        Args:
            drawn_numbers: List of drawn numbers from daily draw

        Returns:
            Count of matching numbers (0-6)
        """
        return len(set(self.numbers) & set(drawn_numbers))

    def to_dict(self) -> dict:
        """Convert ticket to dictionary for serialization."""
        return {
            "numbers": self.numbers,
            "purchase_day": self.purchase_day,
            "active": self.active,
            "total_cost": int(getattr(self, "total_cost", 0) or 0),
            "total_reward": int(getattr(self, "total_reward", 0) or 0),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LottoTicket":
        """Create ticket from dictionary (deserialization)."""
        return cls(
            numbers=data["numbers"],
            purchase_day=data["purchase_day"],
            active=data.get("active", True),
            total_cost=int(data.get("total_cost", 0) or 0),
            total_reward=int(data.get("total_reward", 0) or 0),
        )
