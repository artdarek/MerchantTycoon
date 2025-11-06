from dataclasses import dataclass
from typing import Dict, List


# Domain data models

@dataclass
class Good:
    """Represents a tradeable good"""
    name: str
    base_price: int
    price_variance: float = 0.3  # 30% variance


@dataclass
class PurchaseLot:
    """Represents a batch of goods purchased at a specific price"""
    good_name: str
    quantity: int
    purchase_price: int  # Price per unit
    day: int
    city: str


@dataclass
class Transaction:
    """Represents a transaction (buy or sell)"""
    transaction_type: str  # "buy" or "sell"
    good_name: str
    quantity: int
    price_per_unit: int
    total_value: int
    day: int
    city: str


GOODS: List[Good] = [
    Good("TV", 800),
    Good("Computer", 1200),
    Good("Printer", 300),
    Good("Phone", 600),
    Good("Camera", 400),
    Good("Laptop", 1500),
    Good("Tablet", 500),
    Good("Console", 450),
]


@dataclass
class Asset:
    """Represents a stock or commodity"""
    name: str
    symbol: str
    base_price: int
    price_variance: float = 0.5  # 50% variance (more volatile than goods)
    asset_type: str = "stock"  # "stock" or "commodity"


STOCKS: List[Asset] = [
    Asset("Google", "GOOGL", 150, 0.6, "stock"),
    Asset("Meta", "META", 80, 0.5, "stock"),
    Asset("Apple", "AAPL", 120, 0.7, "stock"),
    Asset("Microsoft", "MSFT", 200, 0.4, "stock"),
]

COMMODITIES: List[Asset] = [
    Asset("Gold", "GOLD", 1800, 0.3, "commodity"),
    Asset("Oil", "OIL", 75, 0.8, "commodity"),
    Asset("Silver", "SILV", 25, 0.4, "commodity"),
    Asset("Copper", "COPP", 8, 0.5, "commodity"),
]


@dataclass
class InvestmentLot:
    """Represents a batch of stocks/commodities purchased at a specific price"""
    asset_symbol: str
    quantity: int
    purchase_price: int
    day: int


@dataclass
class City:
    """Represents a city/location"""
    name: str
    price_multiplier: Dict[str, float]  # Per-good multipliers


CITIES: List[City] = [
    City("Warsaw", {"TV": 1.0, "Computer": 1.0, "Printer": 1.0, "Phone": 1.0,
          "Camera": 1.0, "Laptop": 1.0, "Tablet": 1.0, "Console": 1.0}),
    City("Berlin", {"TV": 0.8, "Computer": 1.2, "Printer": 0.9, "Phone": 1.1,
          "Camera": 0.85, "Laptop": 1.15, "Tablet": 0.95, "Console": 1.05}),
    City("Prague", {"TV": 1.1, "Computer": 0.9, "Printer": 1.2, "Phone": 0.95,
          "Camera": 1.1, "Laptop": 0.85, "Tablet": 1.05, "Console": 0.9}),
    City("Vienna", {"TV": 0.95, "Computer": 1.1, "Printer": 0.85, "Phone": 1.2,
          "Camera": 1.0, "Laptop": 1.05, "Tablet": 1.1, "Console": 0.95}),
    City("Budapest", {"TV": 1.2, "Computer": 0.85, "Printer": 1.1, "Phone": 0.9,
          "Camera": 1.15, "Laptop": 0.9, "Tablet": 0.85, "Console": 1.1}),
]
