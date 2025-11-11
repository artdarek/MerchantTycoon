from dataclasses import dataclass


@dataclass(frozen=True)
class DifficultyLevel:
    """Defines a difficulty level preset for the game"""
    name: str
    display_name: str
    start_cash: int
    start_capacity: int
    description: str