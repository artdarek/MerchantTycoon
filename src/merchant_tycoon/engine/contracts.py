"""
Internal engine contracts (Protocols) to decouple services and avoid
import cycles caused by concrete type hints.
"""

from __future__ import annotations

from typing import Dict, Protocol, Tuple


class GameStateLike(Protocol):
    cash: int
    debt: int
    day: int
    current_city: int
    max_inventory: int
    inventory: Dict[str, int]

    def get_inventory_count(self) -> int: ...
    def can_carry(self, amount: int = 1) -> bool: ...

    bank: object
    loans: list
    purchase_lots: list
    transaction_history: list
    price_modifiers: Dict[str, float]
    portfolio: Dict[str, int]
    investment_lots: list


class BankServiceLike(Protocol):
    def randomize_daily_rates(self) -> None: ...
    def accrue_loan_interest(self) -> None: ...
    def accrue_bank_interest(self) -> None: ...


class GoodsServiceLike(Protocol):
    prices: Dict[str, int]

    def generate_prices(self) -> None: ...
    def extend_cargo(self) -> Tuple: ...


class InvestmentsServiceLike(Protocol):
    def generate_asset_prices(self) -> None: ...


class EngineLike(Protocol):
    state: GameStateLike
    prices: Dict[str, int]
    previous_prices: Dict[str, int]
    asset_prices: Dict[str, int]
    previous_asset_prices: Dict[str, int]

    loan_apr_today: float

    def _sync_total_debt(self) -> int: ...

