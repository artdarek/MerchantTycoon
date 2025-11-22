from dataclasses import dataclass, field
from typing import Dict, List, Optional

from merchant_tycoon.domain.model.purchase_lot import PurchaseLot
from merchant_tycoon.domain.model.transaction import Transaction
from merchant_tycoon.domain.model.investment_lot import InvestmentLot
from merchant_tycoon.domain.model.bank_account import BankAccount
from merchant_tycoon.domain.model.loan import Loan
from merchant_tycoon.domain.model.lotto_ticket import LottoTicket
from merchant_tycoon.domain.model.lotto_draw import LottoDraw
from merchant_tycoon.domain.model.lotto_win_history import LottoWinHistory
from typing import Optional, Dict


@dataclass
class GameState:
    """Player's game state"""

    cash: int = 5000
    debt: int = 0
    day: int = 1
    # ISO date for in-game calendar (YYYY-MM-DD). Engine keeps it in sync with `day`.
    date: str = ""
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
    # Rolling price history for goods: {good_name: [prices...]}
    price_history: Dict[str, List[int]] = field(default_factory=dict)
    # Lotto system
    lotto_tickets: List[LottoTicket] = field(default_factory=list)
    lotto_today_draw: Optional[LottoDraw] = None
    lotto_win_history: List[LottoWinHistory] = field(default_factory=list)
    # Lotto daily aggregates (reset at start of a new day draw)
    lotto_today_cost: int = 0
    lotto_today_payout: int = 0
    # Investment trading unlock tracking
    investments_unlocked: bool = False  # Once unlocked, stays unlocked forever
    peak_wealth: int = 0  # Highest wealth ever achieved (cash + bank + portfolio value)

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

    def check_and_update_peak_wealth(self, current_wealth: int, threshold: int) -> bool:
        """Check if player reached wealth threshold to unlock investments.

        Updates peak_wealth and investments_unlocked if threshold is reached.

        Args:
            current_wealth: Current total wealth (cash + bank + portfolio)
            threshold: Minimum wealth required to unlock (0 = disabled)

        Returns:
            True if investments were just unlocked (transition from locked to unlocked)
        """
        # If already unlocked, nothing to do
        if self.investments_unlocked:
            return False

        # If feature disabled (threshold <= 0), auto-unlock
        if threshold <= 0:
            self.investments_unlocked = True
            return False

        # Update peak wealth
        if current_wealth > self.peak_wealth:
            self.peak_wealth = current_wealth

        # Check if threshold reached
        if self.peak_wealth >= threshold:
            self.investments_unlocked = True
            return True  # Just unlocked!

        return False

    # ---- Wealth helpers ----
    def calculate_total_wealth(self, asset_prices: Optional[Dict[str, int]] = None) -> int:
        """Calculate total wealth (gross, excluding debt).

        Wealth = cash + bank_balance + portfolio_value

        Args:
            asset_prices: Optional price map for assets used to value the portfolio.

        Returns:
            Total wealth in currency units
        """
        cash = int(getattr(self, "cash", 0))
        bank_balance = int(getattr(self.bank, "balance", 0))

        portfolio_value = 0
        try:
            portfolio = getattr(self, "portfolio", {}) or {}
            prices = asset_prices or {}
            for symbol, qty in portfolio.items():
                price = int(prices.get(symbol, 0))
                portfolio_value += int(qty) * price
        except Exception:
            pass

        return cash + bank_balance + portfolio_value
