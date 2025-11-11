"""Domain constant: All game difficulty level presets.

This module defines the 5 difficulty levels available when starting a new game.
Each difficulty controls starting cash and cargo capacity, providing experiences
ranging from sandbox experimentation to extreme survival challenges.

Constants:
    GAME_DIFFICULTY_LEVELS: List of all 5 difficulty presets (Playground to Insane).
        Used by GameEngine during new game initialization and by NewGameModal for
        difficulty selection UI.

Difficulty Levels:
    1. Playground: $1,000,000 cash, 1000 slots - Unlimited experimentation
    2. Easy: $100,000 cash, 100 slots - Generous starting resources
    3. Normal: $50,000 cash, 50 slots - Balanced challenge (default)
    4. Hard: $10,000 cash, 10 slots - Limited resources, strategic planning required
    5. Insane: $0 cash, 1 slot - Start with nothing, maximum challenge

Difficulty Impact:
    - Starting cash: $0 (Insane) to $1,000,000 (Playground)
    - Starting capacity: 1 slot (Insane) to 1000 slots (Playground)
    - Affects initial game state only (not ongoing mechanics)
    - Players can still expand capacity and earn money at any difficulty

Examples:
    >>> from merchant_tycoon.domain.game_difficulty_levels import GAME_DIFFICULTY_LEVELS
    >>> normal = [d for d in GAME_DIFFICULTY_LEVELS if d.name == "normal"][0]
    >>> insane = GAME_DIFFICULTY_LEVELS[-1]  # Last in list
    >>> # Get difficulty by name
    >>> def get_difficulty(name: str):
    ...     return next((d for d in GAME_DIFFICULTY_LEVELS if d.name == name), None)

See Also:
    - GameDifficultyLevel: Domain model representing a single difficulty preset
    - GameEngine: Applies difficulty settings during game initialization
    - NewGameModal: UI for selecting difficulty when starting new game
"""
from __future__ import annotations
from typing import List

from merchant_tycoon.domain.model.game_difficulty_level import GameDifficultyLevel

# All game difficulty level presets (5 levels: Playground to Insane)
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