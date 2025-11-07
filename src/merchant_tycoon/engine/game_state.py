from dataclasses import dataclass, field
from typing import Dict, List

from ..models import (
    PurchaseLot,
    Transaction,
    InvestmentLot,
    BankAccount,
    Loan,
)


@dataclass
class GameState:
    """Player's game state"""

    cash: int = 5000
    debt: int = 0
    day: int = 1
    current_city: int = 0
    inventory: Dict[str, int] = field(default_factory=dict)
    max_inventory: int = 50
    purchase_lots: List[PurchaseLot] = field(default_factory=list)
    transaction_history: List[Transaction] = field(default_factory=list)
    # Investment portfolio
    portfolio: Dict[str, int] = field(default_factory=dict)  # {symbol: quantity}
    investment_lots: List[InvestmentLot] = field(default_factory=list)
    # Bank account
    bank: BankAccount = field(default_factory=BankAccount)
    # Loans (multi-loan support)
    loans: List[Loan] = field(default_factory=list)
    # One-day price modifiers for specific goods (applied on next price generation)
    price_modifiers: Dict[str, float] = field(default_factory=dict)

    def get_inventory_count(self) -> int:
        return sum(self.inventory.values())

    def can_carry(self, amount: int = 1) -> bool:
        return self.get_inventory_count() + amount <= self.max_inventory

    def get_lots_for_good(self, good_name: str) -> List[PurchaseLot]:
        """Get all purchase lots for a specific good"""
        return [lot for lot in self.purchase_lots if lot.good_name == good_name]

    def get_investment_lots_for_asset(self, symbol: str) -> List[InvestmentLot]:
        """Get all investment lots for a specific asset"""
        return [lot for lot in self.investment_lots if lot.asset_symbol == symbol]
