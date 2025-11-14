"""Lotto draw domain model."""

from dataclasses import dataclass
from typing import List


@dataclass
class LottoDraw:
    """Represents a single daily lottery draw.

    Attributes:
        day: Day number when draw occurred
        numbers: List of 6 unique numbers drawn
    """

    day: int
    numbers: List[int]

    def __post_init__(self):
        """Validate draw data after initialization."""
        if not isinstance(self.numbers, list):
            raise ValueError("Draw numbers must be a list")
        if len(self.numbers) != 6:
            raise ValueError(f"Draw must have exactly 6 numbers, got {len(self.numbers)}")
        if len(set(self.numbers)) != 6:
            raise ValueError("Draw numbers must be unique")

    def to_dict(self) -> dict:
        """Convert draw to dictionary for serialization."""
        return {
            "day": self.day,
            "numbers": self.numbers,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LottoDraw":
        """Create draw from dictionary (deserialization)."""
        return cls(
            day=data["day"],
            numbers=data["numbers"],
        )