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

from .game_state import GameState
from .game_engine import GameEngine
from .bank_service import BankService
from .goods_service import GoodsService
from .investments_service import InvestmentsService
from .travel_service import TravelService
from .savegame_service import SavegameService

__all__ = [
    "GameState",
    "GameEngine",
    "BankService",
    "GoodsService",
    "InvestmentsService",
    "TravelService",
]
