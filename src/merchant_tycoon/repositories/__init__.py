"""Domain repositories for accessing game constants.

This package provides repository classes that encapsulate access to domain constants
(GOODS, CITIES, ASSETS, GAME_DIFFICULTY_LEVELS), providing a clean, consistent
interface for services and UI components.
"""
from merchant_tycoon.repositories.goods_repository import GoodsRepository
from merchant_tycoon.repositories.cities_repository import CitiesRepository
from merchant_tycoon.repositories.assets_repository import AssetsRepository
from merchant_tycoon.repositories.difficulty_repository import DifficultyRepository

__all__ = [
    "GoodsRepository",
    "CitiesRepository",
    "AssetsRepository",
    "DifficultyRepository",
]
