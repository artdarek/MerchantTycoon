import random
from typing import TYPE_CHECKING, Optional

from merchant_tycoon.domain.model.bank_transaction import BankTransaction
from merchant_tycoon.domain.model.loan import Loan
from merchant_tycoon.config import SETTINGS
from datetime import datetime

if TYPE_CHECKING:
    from merchant_tycoon.engine.game_state import GameState
    from merchant_tycoon.engine.services.clock_service import ClockService
    from merchant_tycoon.engine.services.messenger_service import MessengerService


class BankService:
    """Service for handling banking operations and loans"""

    def __init__(self, state: "GameState", clock_service: "ClockService", messenger: "MessengerService"):
        self.state = state
        self.clock = clock_service
        self.messenger = messenger
        # Loan interest (offer of the day) — APR for new loans
        self.loan_apr_today = float(SETTINGS.bank.loan_default_apr)

    def get_bank_daily_rate(self) -> float:
        """Return today's bank daily rate derived from APR on a 365-day basis."""
        bank = self.state.bank
        try:
            annual = float(getattr(bank, "interest_rate_annual", SETTINGS.bank.bank_default_apr))
        except Exception:
            annual = 0.02
        return max(0.0, annual / 365.0)

    def randomize_daily_rates(self) -> None:
        """Randomize bank APR and today's loan APR offer for the new day.
        Bank APR: 1% to 3% (0.01 to 0.03) — displayed as APR, accrued daily (APR/365).
        Loan APR offer for new loans: 1% to 20% (0.01 to 0.20). Existing loans keep their own APR.
        """
        # Randomize bank APR (savings interest)
        try:
            lo, hi = SETTINGS.bank.bank_apr_range
            self.state.bank.interest_rate_annual = random.uniform(lo, hi)
        except Exception:
            self.state.bank.interest_rate_annual = 0.02
        # Randomize today's loan APR offer (used only for NEW loans created today)
        try:
            lo, hi = SETTINGS.bank.loan_apr_range
            self.loan_apr_today = random.uniform(lo, hi)
        except Exception:
            self.loan_apr_today = 0.10

    def deposit_to_bank(self, amount: int) -> tuple[bool, str]:
        """Deposit cash to bank account."""
        if amount <= 0:
            return False, "Amount must be positive"
        if amount > self.state.cash:
            return False, f"Not enough cash! Have ${self.state.cash:,}"
        self.state.cash -= amount
        bank = self.state.bank
        bank.balance += amount
        ts = self.clock.now().isoformat(timespec="seconds")
        bank.transactions.append(
            BankTransaction(
                tx_type="deposit",
                amount=amount,
                balance_after=bank.balance,
                day=self.state.day,
                title="Personal savings",
                ts=ts,
            )
        )
        self.messenger.info(f"Deposited ${amount:,} to bank", tag="bank")
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
        ts = self.clock.now().isoformat(timespec="seconds")
        bank.transactions.append(
            BankTransaction(
                tx_type="withdraw",
                amount=amount,
                balance_after=bank.balance,
                day=self.state.day,
                title="Personal withdrawal",
                ts=ts,
            )
        )
        self.messenger.info(f"Withdrew ${amount:,} from bank", tag="bank")
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
        rate = self.get_bank_daily_rate()
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
                        ts=self.clock.now().isoformat(timespec="seconds")
                )
            )
        if credit > 0:
            self.messenger.info(f"Daily interest credited: ${credit:,}", tag="bank")
        bank.last_interest_day = current_day

    def take_loan(self, amount: int) -> tuple[bool, str]:
        """Take a loan from the bank. Creates a new Loan entry.
        Commission policy:
        - Base commission is 10% of the borrowed amount, added to the amount to repay.
        - If the player has 10 or more unpaid loans at the moment of taking a new one,
          the commission is 30% (higher risk).
        The commission increases the initial `remaining` to repay but does not change cash received.
        """
        if amount <= 0:
            return False, "Invalid loan amount"

        # Credit capacity check (optional)
        if getattr(SETTINGS.bank, "credit_enabled", True):
            cap_msg = self._check_credit_capacity(amount)
            if cap_msg:
                return False, cap_msg

        # Determine today's APR offer
        try:
            apr = float(getattr(self, "loan_apr_today", SETTINGS.bank.loan_default_apr))
        except Exception:
            apr = 0.10

        # Determine commission based on current unpaid loans BEFORE creating new one
        unpaid_loans = sum(1 for ln in getattr(self.state, "loans", []) if getattr(ln, "remaining", 0) > 0)
        fee_rate = (
            SETTINGS.bank.loan_high_commission_rate
            if unpaid_loans >= SETTINGS.bank.loan_high_commission_threshold
            else SETTINGS.bank.loan_base_commission_rate
        )
        fee = int(amount * fee_rate)
        total_to_repay = amount + fee

        # Create loan with incremental ID
        next_id = (max((ln.loan_id for ln in self.state.loans), default=0) + 1)
        loan = Loan(
            loan_id=next_id,
            principal=amount,
            remaining=total_to_repay,
            repaid=0,
            day_taken=self.state.day,
            rate_annual=apr,
            accrued_interest=0.0,
            ts=self.clock.now().isoformat(timespec="seconds"),
        )
        self.state.loans.append(loan)

        # Apply funds to cash and sync aggregate debt
        self.state.cash += amount
        self._sync_total_debt()
        self.messenger.info(
            f"Loan approved: ${amount:,} (fee ${fee:,}, total repay ${total_to_repay:,}, APR {apr*100:.2f}%)",
            tag="bank",
        )
        return True, (
            f"Loan approved! Received ${amount:,}. "
            f"Commission: ${fee:,} ({fee_rate*100:.0f}%). "
            f"Total to repay: ${total_to_repay:,} (APR {apr*100:.2f}%)."
        )

    # ---- Credit capacity helpers ----
    def _portfolio_value_with_haircuts(self) -> int:
        total = 0.0
        try:
            # asset_prices may be provided by engine (injected)
            prices = getattr(self, "asset_prices", {}) or {}
        except Exception:
            prices = {}
        # optional: investments_service to resolve asset types
        inv = getattr(self, "investments_service", None)
        for symbol, qty in (getattr(self.state, "portfolio", {}) or {}).items():
            try:
                price = int(prices.get(symbol, 0))
            except Exception:
                price = 0
            if price <= 0 or qty <= 0:
                continue
            asset_type = ""
            try:
                # Use assets_repo if available, fallback to investments_service
                if hasattr(self, 'assets_repo') and self.assets_repo:
                    a = self.assets_repo.get_by_symbol(symbol)
                    asset_type = getattr(a, "asset_type", "") if a else ""
                elif inv is not None:
                    a = inv.get_asset(symbol) if hasattr(inv, 'get_asset') else None
                    asset_type = getattr(a, "asset_type", "") if a else ""
            except Exception:
                asset_type = ""
            if asset_type == "stock":
                hc = float(getattr(SETTINGS.bank, "credit_haircut_stock", 0.8))
            elif asset_type == "commodity":
                hc = float(getattr(SETTINGS.bank, "credit_haircut_commodity", 0.7))
            elif asset_type == "crypto":
                hc = float(getattr(SETTINGS.bank, "credit_haircut_crypto", 0.5))
            else:
                hc = 0.0
            total += qty * price * hc
        return int(total)

    def compute_wealth(self) -> int:
        """Compute player's wealth used for credit capacity: cash + bank + haircut(portfolio)."""
        wealth = 0
        # Cash with haircut
        try:
            cash = int(getattr(self.state, "cash", 0))
        except Exception:
            cash = 0
        try:
            cash_hc = float(getattr(SETTINGS.bank, "credit_haircut_cash", 0.5))
        except Exception:
            cash_hc = 0.5
        wealth += int(max(0, cash) * max(0.0, cash_hc))
        try:
            wealth += int(getattr(self.state.bank, "balance", 0))
        except Exception:
            pass
        wealth += self._portfolio_value_with_haircuts()
        # Optionally include goods inventory value (disabled by default)
        # Not implemented unless SETTINGS.bank.credit_include_goods_inventory is True
        return int(max(0, wealth))

    def compute_credit_limits(self) -> tuple[int, int, int]:
        """Return (wealth, max_total_debt, max_new_loan) based on config and current debt."""
        wealth = self.compute_wealth()
        lev = float(getattr(SETTINGS.bank, "credit_leverage_factor", 0.8))
        base = int(getattr(SETTINGS.bank, "credit_base_allowance", 0))
        max_total = int(wealth * lev) + base
        cur_debt = int(getattr(self.state, "debt", 0))
        max_new = max(0, max_total - cur_debt)
        return wealth, max_total, max_new

    def _check_credit_capacity(self, requested_amount: int) -> Optional[str]:
        """Return message if requested_amount exceeds capacity; otherwise None."""
        _, max_total, max_new = self.compute_credit_limits()
        if requested_amount > max_new:
            return (
                f"Requested amount ${requested_amount:,} exceeds credit capacity. "
                f"Max new loan: ${max_new:,}; Total cap: ${max_total:,}."
            )
        return None

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
        self.messenger.info(
            f"Paid ${pay:,} towards Loan #{loan.loan_id}. Remaining: ${loan.remaining:,}",
            tag="bank",
        )
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

    def accrue_loan_interest(self) -> None:
        """Apply daily interest to all active loans.
        Called during day advancement (travel).
        """
        if self.state.loans:
            for loan in self.state.loans:
                if getattr(loan, 'remaining', 0) > 0:
                    # Determine daily rate from this loan's APR
                    try:
                        apr = float(getattr(loan, 'rate_annual', SETTINGS.bank.loan_default_apr))
                    except Exception:
                        apr = 0.10
                    daily_rate = max(0.0, apr / 365.0)
                    # Accrue fractional interest then credit whole units to remaining
                    try:
                        loan.accrued_interest = float(getattr(loan, 'accrued_interest', 0.0))
                    except Exception:
                        loan.accrued_interest = 0.0
                    loan.accrued_interest += loan.remaining * daily_rate
                    credit = int(loan.accrued_interest)
                    if credit > 0:
                        loan.remaining += credit
                        loan.accrued_interest -= credit
            # Sync aggregate debt to sum of remaining
            self._sync_total_debt()

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

    # Utility to credit bank balance with a labeled transaction (does not touch cash)
    def credit(self, amount: int, tx_type: str = "deposit", title: str = "") -> None:
        """Credit amount to bank account with a transaction record.

        Args:
            amount: Amount to credit (must be positive)
            tx_type: Transaction type ("deposit", "withdraw", "interest", "dividend")
            title: Transaction title/description
        """
        if amount <= 0:
            return
        bank = self.state.bank
        bank.balance += int(amount)
        # Validate tx_type, default to "interest" for unknown types
        valid_types = ("deposit", "withdraw", "interest", "dividend")
        tx_type = tx_type if tx_type in valid_types else "interest"
        bank.transactions.append(
            BankTransaction(
                tx_type=tx_type,
                amount=int(amount),
                balance_after=bank.balance,
                day=self.state.day,
                title=title or ("Interest" if tx_type == "interest" else "Dividend" if tx_type == "dividend" else ""),
                ts=self.clock.now().isoformat(timespec="seconds")
            )
        )
