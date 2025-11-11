from __future__ import annotations
from typing import List

from merchant_tycoon.domain.model.game_difficulty_level import GameDifficultyLevel

# Game difficulty levels
GAME_DIFFICULTY_LEVELS: List[GameDifficultyLevel] = [
    GameDifficultyLevel(
        name="playground",
        display_name="Playground",
        start_cash=1_000_000,
        start_capacity=1000,
        description="Unlimited funds for experimentation"
    ),
    GameDifficultyLevel(
        name="easy",
        display_name="Easy",
        start_cash=100_000,
        start_capacity=100,
        description="Generous starting resources"
    ),
    GameDifficultyLevel(
        name="normal",
        display_name="Normal",
        start_cash=50_000,
        start_capacity=50,
        description="Balanced challenge"
    ),
    GameDifficultyLevel(
        name="hard",
        display_name="Hard",
        start_cash=10_000,
        start_capacity=10,
        description="Limited resources, strategic planning required"
    ),
    GameDifficultyLevel(
        name="insane",
        display_name="Insane",
        start_cash=0,
        start_capacity=1,
        description="Start with nothing, maximum challenge"
    ),
]