"""
Game Engine Module

This module contains the core game logic and state management for Merchant Tycoon.

The engine is organized into specialized services:
- BankService: Banking operations and loan management
- GoodsService: Trading goods (buy/sell)
- InvestmentsService: Trading investments (stocks, commodities, crypto)
- TravelService: Travel coordination and events

GameEngine acts as a facade over these services, providing a unified API.
"""

from merchant_tycoon.engine.game_state import GameState
from merchant_tycoon.engine.game_engine import GameEngine
__all__ = [
    "GameState",
    "GameEngine",
]
