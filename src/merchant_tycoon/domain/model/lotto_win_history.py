"""Lotto win history domain model."""

from dataclasses import dataclass
from typing import List


@dataclass
class LottoWinHistory:
    """Represents a single lottery win record.

    Attributes:
        day: Day number when win occurred
        ticket_numbers: The winning ticket's numbers
        matched: How many numbers matched
        payout: Prize amount won
    """

    day: int
    ticket_numbers: List[int]
    matched: int
    payout: int

    def to_dict(self) -> dict:
        """Convert win history to dictionary for serialization."""
        return {
            "day": self.day,
            "ticket_numbers": self.ticket_numbers,
            "matched": self.matched,
            "payout": self.payout,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LottoWinHistory":
        """Create win history from dictionary (deserialization)."""
        return cls(
            day=data["day"],
            ticket_numbers=data["ticket_numbers"],
            matched=data["matched"],
            payout=data["payout"],
        )