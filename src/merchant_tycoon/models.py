from dataclasses import dataclass, field
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
    Good("Headphones", 150),
    Good("Smartwatch", 400),
    Good("VR Headset", 700),
    Good("Coffee Machine", 450),
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
    Asset("Amazon", "AMZN", 180, 0.6, "stock"),
    Asset("Netflix", "NFLX", 90, 0.8, "stock"),
    Asset("NVIDIA", "NVDA", 250, 0.9, "stock"),
    Asset("Tesla", "TSLA", 160, 0.8, "stock"),
    Asset("AMD", "AMD", 110, 0.7, "stock"),
    Asset("Oracle", "ORCL", 95, 0.5, "stock"),
    Asset("Adobe", "ADBE", 140, 0.6, "stock"),
    Asset("Intel", "INTC", 85, 0.6, "stock"),
]

COMMODITIES: List[Asset] = [
    Asset("Gold", "GOLD", 1800, 0.3, "commodity"),
    Asset("Oil", "OIL", 75, 0.8, "commodity"),
    Asset("Silver", "SILV", 25, 0.4, "commodity"),
    Asset("Copper", "COPP", 8, 0.5, "commodity"),
]

CRYPTO: List[Asset] = [
    Asset("Bitcoin", "BTC", 35000, 0.7, "crypto"),
    Asset("Ethereum", "ETH", 2000, 0.8, "crypto"),
    Asset("Solana", "SOL", 80, 0.9, "crypto"),
    Asset("Dogecoin", "DOGE", 5, 1.0, "crypto"),  # Price range $1-$10 (base 5, variance 1.0)
]


@dataclass
class InvestmentLot:
    """Represents a batch of stocks/commodities purchased at a specific price"""
    asset_symbol: str
    quantity: int
    purchase_price: int
    day: int


@dataclass
class BankTransaction:
    """Represents a bank transaction"""
    tx_type: str  # "deposit" | "withdraw" | "interest"
    amount: int
    balance_after: int
    day: int
    title: str = ""


@dataclass
class BankAccount:
    """Represents player's bank account"""
    balance: int = 0
    # Legacy daily rate kept for backward compatibility with old saves/UI.
    interest_rate_daily: float = 0.0005
    # New: annual interest rate (APR), used to compute daily rate as APR/365.
    interest_rate_annual: float = 0.02
    accrued_interest: float = 0.0
    last_interest_day: int = 0
    transactions: List[BankTransaction] = field(default_factory=list)


@dataclass
class Loan:
    """Represents a single loan instance with its own rate and lifecycle.
    rate_annual is the fixed APR for this loan (preferred). Legacy rate_daily is kept for backward compatibility.
    accrued_interest holds fractional interest until whole units can be added to remaining.
    """
    loan_id: int
    principal: int
    remaining: int
    repaid: int
    rate_daily: float
    day_taken: int
    # New APR-based model
    rate_annual: float = 0.10
    accrued_interest: float = 0.0


@dataclass
class City:
    """Represents a city/location"""
    name: str
    country: str
    price_multiplier: Dict[str, float]  # Per-good multipliers


CITIES: List[City] = [
    City("Warsaw", "Poland", {"TV": 1.0, "Computer": 1.0, "Printer": 1.0, "Phone": 1.0,
          "Camera": 1.0, "Laptop": 1.0, "Tablet": 1.0, "Console": 1.0,
          "Headphones": 1.0, "Smartwatch": 1.0, "VR Headset": 1.0, "Coffee Machine": 1.0}),
    City("Berlin", "Germany", {"TV": 0.8, "Computer": 1.2, "Printer": 0.9, "Phone": 1.1,
          "Camera": 0.85, "Laptop": 1.15, "Tablet": 0.95, "Console": 1.05,
          "Headphones": 0.85, "Smartwatch": 1.1, "VR Headset": 0.9, "Coffee Machine": 1.05}),
    City("Prague", "Czech Republic", {"TV": 1.1, "Computer": 0.9, "Printer": 1.2, "Phone": 0.95,
          "Camera": 1.1, "Laptop": 0.85, "Tablet": 1.05, "Console": 0.9,
          "Headphones": 1.15, "Smartwatch": 0.95, "VR Headset": 1.2, "Coffee Machine": 0.9}),
    City("Vienna", "Austria", {"TV": 0.95, "Computer": 1.1, "Printer": 0.85, "Phone": 1.2,
          "Camera": 1.0, "Laptop": 1.05, "Tablet": 1.1, "Console": 0.95,
          "Headphones": 0.9, "Smartwatch": 1.15, "VR Headset": 1.05, "Coffee Machine": 0.8}),
    City("Budapest", "Hungary", {"TV": 1.2, "Computer": 0.85, "Printer": 1.1, "Phone": 0.9,
          "Camera": 1.15, "Laptop": 0.9, "Tablet": 0.85, "Console": 1.1,
          "Headphones": 1.2, "Smartwatch": 0.85, "VR Headset": 1.1, "Coffee Machine": 1.15}),
    City("Paris", "France", {"TV": 0.9, "Computer": 1.15, "Printer": 0.95, "Phone": 1.05,
          "Camera": 1.2, "Laptop": 1.1, "Tablet": 1.0, "Console": 0.85,
          "Headphones": 0.95, "Smartwatch": 1.2, "VR Headset": 0.85, "Coffee Machine": 0.75}),
    City("London", "United Kingdom", {"TV": 0.85, "Computer": 1.25, "Printer": 1.0, "Phone": 1.15,
          "Camera": 0.9, "Laptop": 1.2, "Tablet": 1.05, "Console": 0.95,
          "Headphones": 1.0, "Smartwatch": 1.1, "VR Headset": 1.15, "Coffee Machine": 1.1}),
    City("Rome", "Italy", {"TV": 1.05, "Computer": 0.95, "Printer": 1.15, "Phone": 0.9,
          "Camera": 1.15, "Laptop": 0.9, "Tablet": 0.95, "Console": 1.0,
          "Headphones": 1.1, "Smartwatch": 0.9, "VR Headset": 1.0, "Coffee Machine": 0.7}),
    City("Amsterdam", "Netherlands", {"TV": 0.95, "Computer": 1.1, "Printer": 0.9, "Phone": 1.05,
          "Camera": 0.95, "Laptop": 1.15, "Tablet": 1.1, "Console": 1.05,
          "Headphones": 0.85, "Smartwatch": 1.05, "VR Headset": 1.1, "Coffee Machine": 0.85}),
    City("Barcelona", "Spain", {"TV": 1.15, "Computer": 0.85, "Printer": 1.05, "Phone": 0.95,
          "Camera": 1.05, "Laptop": 0.95, "Tablet": 0.9, "Console": 1.15,
          "Headphones": 1.05, "Smartwatch": 0.95, "VR Headset": 0.9, "Coffee Machine": 0.9}),
    City("Stockholm", "Sweden", {"TV": 0.75, "Computer": 1.3, "Printer": 0.85, "Phone": 1.2,
          "Camera": 0.8, "Laptop": 1.25, "Tablet": 1.15, "Console": 0.9,
          "Headphones": 0.8, "Smartwatch": 1.25, "VR Headset": 1.05, "Coffee Machine": 1.05}),
]
