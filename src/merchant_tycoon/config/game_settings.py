from dataclasses import dataclass


@dataclass(frozen=True)
class GameSettings:
    # Starting cash for a new game
    start_cash: int = 50000
    # Start date (ISO YYYY-MM-DD)
    start_date: str = "2025-01-01"

