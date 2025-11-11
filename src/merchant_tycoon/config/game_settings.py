from dataclasses import dataclass


@dataclass(frozen=True)
class GameSettings:
    # Starting cash for a new game (overridden by difficulty level)
    start_cash: int = 50000
    # Start date (ISO YYYY-MM-DD)
    start_date: str = "2025-01-01"
    # Default difficulty level name
    default_difficulty: str = "normal"

