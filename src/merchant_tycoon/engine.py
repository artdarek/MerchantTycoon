import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .models import (
    PurchaseLot,
    Transaction,
    InvestmentLot,
    BankAccount,
    BankTransaction,
    Loan,
    GOODS,
    STOCKS,
    COMMODITIES,
    CRYPTO,
    CITIES,
)
from .events import TravelEventSystem


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


class GameEngine:
    """Core game logic"""

    def __init__(self):
        self.state = GameState()
        self.prices: Dict[str, int] = {}
        self.previous_prices: Dict[str, int] = {}
        self.asset_prices: Dict[str, int] = {}
        self.previous_asset_prices: Dict[str, int] = {}
        self.generate_prices()
        self.generate_asset_prices()
        self.interest_rate = 0.10  # Daily loan interest rate (will be randomized each travel)
        # Initialize bank last interest day to current day at start
        if self.state.bank.last_interest_day == 0:
            self.state.bank.last_interest_day = self.state.day
        # Ensure aggregate debt synchronized with loans list
        self._sync_total_debt()

    def randomize_daily_rates(self) -> None:
        """Randomize bank and global loan daily interest rates for the new day.
        Range: 1% to 20% (0.01 to 0.20).
        Note: Existing loans keep their own fixed `rate_daily` captured at creation.
        """
        # Randomize bank daily rate
        try:
            self.state.bank.interest_rate_daily = random.uniform(0.01, 0.20)
        except Exception:
            self.state.bank.interest_rate_daily = 0.01
        # Randomize global loan daily rate (used only for NEW loans created today)
        try:
            self.interest_rate = random.uniform(0.01, 0.20)
        except Exception:
            self.interest_rate = 0.10

    def deposit_to_bank(self, amount: int) -> tuple[bool, str]:
        """Deposit cash to bank account."""
        if amount <= 0:
            return False, "Amount must be positive"
        if amount > self.state.cash:
            return False, f"Not enough cash! Have ${self.state.cash:,}"
        self.state.cash -= amount
        bank = self.state.bank
        bank.balance += amount
        bank.transactions.append(
                BankTransaction(
                    tx_type="deposit",
                    amount=amount,
                    balance_after=bank.balance,
                    day=self.state.day,
                    title="Personal savings",
                )
            )
        return True, f"Deposited ${amount:,} to bank"

    def withdraw_from_bank(self, amount: int) -> tuple[bool, str]:
        """Withdraw cash from bank account (no overdraft)."""
        if amount <= 0:
            return False, "Amount must be positive"
        bank = self.state.bank
        if amount > bank.balance:
            return False, f"Not enough bank balance! Have ${bank.balance:,}"
        bank.balance -= amount
        self.state.cash += amount
        bank.transactions.append(
                BankTransaction(
                    tx_type="withdraw",
                    amount=amount,
                    balance_after=bank.balance,
                    day=self.state.day,
                    title="Personal withdrawal",
                )
            )
        return True, f"Withdrew ${amount:,} from bank"

    def accrue_bank_interest(self) -> None:
        """Accrue and credit daily compounding bank interest up to current day.
        Credits only whole currency units; fractional part is carried in accrued_interest.
        """
        bank = self.state.bank
        current_day = self.state.day
        # Process days strictly after last_interest_day up to current_day (inclusive step-by-step)
        days_to_process = current_day - bank.last_interest_day
        if days_to_process <= 0:
            bank.last_interest_day = current_day
            return
        rate = bank.interest_rate_daily
        for i in range(days_to_process):
            # Accrue interest on starting-of-day balance (compounding via credited amounts)
            bank.accrued_interest += bank.balance * rate
            credit = int(bank.accrued_interest)
            if credit > 0:
                bank.balance += credit
                bank.accrued_interest -= credit
                bank.transactions.append(
                    BankTransaction(
                        tx_type="interest",
                        amount=credit,
                        balance_after=bank.balance,
                        day=bank.last_interest_day + i + 1,
                        title="Daily interest",
                    )
                )
        bank.last_interest_day = current_day

    def generate_prices(self):
        """Generate random prices for current city"""
        # Save previous prices before generating new ones
        self.previous_prices = self.prices.copy()

        city = CITIES[self.state.current_city]
        for good in GOODS:
            variance = random.uniform(1 - good.price_variance, 1 + good.price_variance)
            city_mult = city.price_multiplier[good.name]
            base_price = good.base_price * city_mult * variance
            # Apply one-day modifier if present
            try:
                modifier = float(self.state.price_modifiers.get(good.name, 1.0))
            except Exception:
                modifier = 1.0
            price = int(max(1, base_price * modifier))
            self.prices[good.name] = price
        # Clear one-day modifiers after they take effect
        try:
            self.state.price_modifiers.clear()
        except Exception:
            self.state.price_modifiers = {}

    def generate_asset_prices(self):
        """Generate random prices for stocks and commodities"""
        # Save previous prices
        self.previous_asset_prices = self.asset_prices.copy()

        # Generate prices for all assets
        all_assets = STOCKS + COMMODITIES + CRYPTO
        for asset in all_assets:
            variance = random.uniform(1 - asset.price_variance, 1 + asset.price_variance)
            # For crypto with very low prices (like DOGE), use float precision
            price = asset.base_price * variance
            self.asset_prices[asset.symbol] = round(price, 2) if asset.asset_type == "crypto" and price < 10 else int(price)

    def buy(self, good_name: str, quantity: int) -> tuple[bool, str]:
        """Buy goods"""
        if good_name not in self.prices:
            return False, "Invalid item"

        price = self.prices[good_name]
        total_cost = price * quantity

        if total_cost > self.state.cash:
            return False, f"Not enough cash! Need ${total_cost}, have ${self.state.cash}"

        if not self.state.can_carry(quantity):
            available = self.state.max_inventory - self.state.get_inventory_count()
            return False, f"Not enough space! Only {available} slots available"

        self.state.cash -= total_cost
        self.state.inventory[good_name] = self.state.inventory.get(good_name, 0) + quantity

        # Record purchase lot
        city_name = CITIES[self.state.current_city].name
        lot = PurchaseLot(
            good_name=good_name,
            quantity=quantity,
            purchase_price=price,
            day=self.state.day,
            city=city_name,
        )
        self.state.purchase_lots.append(lot)

        # Record transaction
        transaction = Transaction(
            transaction_type="buy",
            good_name=good_name,
            quantity=quantity,
            price_per_unit=price,
            total_value=total_cost,
            day=self.state.day,
            city=city_name,
        )
        self.state.transaction_history.append(transaction)

        return True, f"Bought {quantity}x {good_name} for ${total_cost}"

    def sell(self, good_name: str, quantity: int) -> tuple[bool, str]:
        """Sell goods using FIFO (First In, First Out) strategy"""
        if good_name not in self.state.inventory or self.state.inventory[good_name] < quantity:
            have = self.state.inventory.get(good_name, 0)
            return False, f"Don't have enough! Have {have}x {good_name}"

        price = self.prices[good_name]
        total_value = price * quantity

        # Deduct from purchase lots using FIFO
        remaining_to_sell = quantity
        lots_to_remove = []
        for i, lot in enumerate(self.state.purchase_lots):
            if lot.good_name == good_name and remaining_to_sell > 0:
                if lot.quantity <= remaining_to_sell:
                    # Sell entire lot
                    remaining_to_sell -= lot.quantity
                    lots_to_remove.append(i)
                else:
                    # Partial sell from this lot
                    lot.quantity -= remaining_to_sell
                    remaining_to_sell = 0
                    break

        # Remove fully sold lots (in reverse order to maintain indices)
        for i in reversed(lots_to_remove):
            self.state.purchase_lots.pop(i)

        self.state.cash += total_value
        self.state.inventory[good_name] -= quantity
        if self.state.inventory[good_name] == 0:
            del self.state.inventory[good_name]

        # Record transaction
        city_name = CITIES[self.state.current_city].name
        transaction = Transaction(
            transaction_type="sell",
            good_name=good_name,
            quantity=quantity,
            price_per_unit=price,
            total_value=total_value,
            day=self.state.day,
            city=city_name,
        )
        self.state.transaction_history.append(transaction)

        return True, f"Sold {quantity}x {good_name} for ${total_value}"

    def travel(self, city_index: int) -> tuple[bool, str, Optional[tuple[str, bool]]]:
        """Travel to a new city. Returns (success, message, event_data) where event_data is (event_msg, is_positive)"""
        if city_index == self.state.current_city:
            return False, "Already in this city!", None

        self.state.current_city = city_index
        self.state.day += 1

        # Randomize daily interest rates for this new day (1%–20%)
        try:
            self.randomize_daily_rates()
        except Exception:
            pass

        # Apply per-loan interest using today's randomized loan rate
        if self.state.loans:
            for loan in self.state.loans:
                if loan.remaining > 0:
                    # Accrue using the loan's own fixed daily rate captured at creation
                    try:
                        rate = float(getattr(loan, "rate_daily", self.interest_rate))
                    except Exception:
                        rate = self.interest_rate
                    interest = int(loan.remaining * rate)
                    if interest > 0:
                        loan.remaining += interest
            # Sync aggregate debt to sum of remaining
            self._sync_total_debt()

        # Accrue bank interest for the day advance (daily compounding)
        self.accrue_bank_interest()

        # Random event (only affects goods, not investments!)
        event_data = self._random_event()

        # Generate new prices for goods and assets
        self.generate_prices()
        self.generate_asset_prices()

        city = CITIES[city_index]
        return True, f"Traveled to {city.name}, {city.country}", event_data

    def _random_event(self) -> Optional[tuple[str, bool]]:
        """Generate a weighted random travel event. Returns (message, is_positive) or None.
        Delegates to TravelEventSystem to keep engine slim.
        """
        try:
            return TravelEventSystem().trigger(self)
        except Exception:
            # Fail-safe: no event if anything goes wrong
            return None

    def take_loan(self, amount: int) -> tuple[bool, str]:
        """Take a loan from the bank. Creates a new Loan entry."""
        if amount <= 0:
            return False, "Invalid loan amount"
        if amount > 10000:
            return False, "Maximum loan is $10,000"

        # Create loan with incremental ID
        next_id = (max((ln.loan_id for ln in self.state.loans), default=0) + 1)
        loan = Loan(
            loan_id=next_id,
            principal=amount,
            remaining=amount,
            repaid=0,
            rate_daily=self.interest_rate,
            day_taken=self.state.day,
        )
        self.state.loans.append(loan)

        # Apply funds to cash and sync aggregate debt
        self.state.cash += amount
        self._sync_total_debt()
        return True, f"Loan approved! Received ${amount:,} ({int(self.interest_rate*100)}% daily interest)"

    def repay_loan_for(self, loan_id: int, amount: int) -> tuple[bool, str]:
        """Repay a specific loan by ID.
        Validates amount and cash, applies repayment to the targeted loan,
        updates aggregate debt, and returns a user-facing message.
        """
        # Basic validations
        if amount <= 0:
            return False, "Invalid amount"
        if amount > self.state.cash:
            return False, f"Not enough cash! Have ${self.state.cash:,}"
        # Find loan
        loan = next((ln for ln in self.state.loans if ln.loan_id == loan_id), None)
        if loan is None:
            return False, "Selected loan not found"
        if loan.remaining <= 0:
            return False, "This loan is already fully repaid"
        # Clamp to remaining
        pay = min(int(amount), int(loan.remaining))
        if pay <= 0:
            return False, "Nothing to repay"
        # Apply repayment
        self.state.cash -= pay
        loan.remaining -= pay
        loan.repaid += pay
        # Sync aggregate debt
        self._sync_total_debt()
        msg_suffix = " (fully repaid)" if loan.remaining == 0 else ""
        return True, f"Paid ${pay:,} towards Loan #{loan.loan_id}. Remaining: ${loan.remaining:,}{msg_suffix}"

    def repay_loan(self, amount: int) -> tuple[bool, str]:
        """Repay loan (legacy aggregate).
        Applies repayment to the oldest active loan for backward compatibility.
        """
        if amount <= 0:
            return False, "Invalid amount"
        if amount > self.state.cash:
            return False, f"Not enough cash! Have ${self.state.cash:,}"
        if self.state.debt <= 0:
            return False, "No debt to repay"
        # Pick oldest active loan
        active = [ln for ln in self.state.loans if ln.remaining > 0]
        if not active:
            return False, "No active loans to repay"
        active.sort(key=lambda ln: ln.day_taken)
        target = active[0]
        return self.repay_loan_for(target.loan_id, amount)

    def buy_asset(self, symbol: str, quantity: int) -> tuple[bool, str]:
        """Buy stocks or commodities"""
        if symbol not in self.asset_prices:
            return False, "Invalid asset"

        price = self.asset_prices[symbol]
        total_cost = price * quantity

        if total_cost > self.state.cash:
            return False, f"Not enough cash! Need ${total_cost:,}, have ${self.state.cash:,}"

        if quantity <= 0:
            return False, "Quantity must be positive"

        self.state.cash -= total_cost
        self.state.portfolio[symbol] = self.state.portfolio.get(symbol, 0) + quantity

        # Record investment lot
        lot = InvestmentLot(
            asset_symbol=symbol,
            quantity=quantity,
            purchase_price=price,
            day=self.state.day,
        )
        self.state.investment_lots.append(lot)

        return True, f"Bought {quantity}x {symbol} for ${total_cost:,}"

    def sell_asset(self, symbol: str, quantity: int) -> tuple[bool, str]:
        """Sell stocks or commodities using FIFO"""
        if symbol not in self.state.portfolio or self.state.portfolio[symbol] < quantity:
            have = self.state.portfolio.get(symbol, 0)
            return False, f"Don't have enough! Have {have}x {symbol}"

        if quantity <= 0:
            return False, "Quantity must be positive"

        price = self.asset_prices[symbol]
        total_value = price * quantity

        # Deduct from investment lots using FIFO
        remaining_to_sell = quantity
        lots_to_remove = []
        for i, lot in enumerate(self.state.investment_lots):
            if lot.asset_symbol == symbol and remaining_to_sell > 0:
                if lot.quantity <= remaining_to_sell:
                    remaining_to_sell -= lot.quantity
                    lots_to_remove.append(i)
                else:
                    lot.quantity -= remaining_to_sell
                    remaining_to_sell = 0
                    break

        # Remove fully sold lots
        for i in reversed(lots_to_remove):
            self.state.investment_lots.pop(i)

        self.state.cash += total_value
        self.state.portfolio[symbol] -= quantity
        if self.state.portfolio[symbol] == 0:
            del self.state.portfolio[symbol]

        return True, f"Sold {quantity}x {symbol} for ${total_value:,}"

    def _sync_total_debt(self) -> int:
        """Recompute aggregate debt from the loans list and assign to state.debt.
        Returns the computed total. Safe if loans list is missing or empty.
        """
        # Get loans list defensively
        try:
            loans = getattr(self.state, "loans", []) or []
        except Exception:
            loans = []
        total = 0
        try:
            for ln in loans:
                rem = getattr(ln, "remaining", 0)
                if rem and rem > 0:
                    total += int(rem)
        except Exception:
            # If anything goes wrong, keep best-effort total
            pass
        self.state.debt = int(total)
        return self.state.debt
