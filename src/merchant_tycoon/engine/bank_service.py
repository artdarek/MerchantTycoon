import random
from typing import TYPE_CHECKING

from merchant_tycoon.model import BankTransaction, Loan

if TYPE_CHECKING:
    from merchant_tycoon.engine.contracts import GameStateLike


class BankService:
    """Service for handling banking operations and loans"""

    def __init__(self, state: "GameStateLike"):
        self.state = state
        # Loan interest (offer of the day) — APR for new loans
        self.loan_apr_today = 0.10

    def get_bank_daily_rate(self) -> float:
        """Return today's bank daily rate derived from APR on a 365-day basis."""
        bank = self.state.bank
        try:
            annual = float(getattr(bank, "interest_rate_annual", 0.02))
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
            self.state.bank.interest_rate_annual = random.uniform(0.01, 0.03)
        except Exception:
            self.state.bank.interest_rate_annual = 0.02
        # Randomize today's loan APR offer (used only for NEW loans created today)
        try:
            self.loan_apr_today = random.uniform(0.01, 0.20)
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
                    )
                )
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
        if amount > 10000:
            return False, "Maximum loan is $10,000"

        # Determine today's APR offer
        try:
            apr = float(getattr(self, "loan_apr_today", 0.10))
        except Exception:
            apr = 0.10

        # Determine commission based on current unpaid loans BEFORE creating new one
        unpaid_loans = sum(1 for ln in getattr(self.state, "loans", []) if getattr(ln, "remaining", 0) > 0)
        fee_rate = 0.30 if unpaid_loans >= 10 else 0.10
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
        )
        self.state.loans.append(loan)

        # Apply funds to cash and sync aggregate debt
        self.state.cash += amount
        self._sync_total_debt()
        return True, (
            f"Loan approved! Received ${amount:,}. "
            f"Commission: ${fee:,} ({fee_rate*100:.0f}%). "
            f"Total to repay: ${total_to_repay:,} (APR {apr*100:.2f}%)."
        )

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

    def accrue_loan_interest(self) -> None:
        """Apply daily interest to all active loans.
        Called during day advancement (travel).
        """
        if self.state.loans:
            for loan in self.state.loans:
                if getattr(loan, 'remaining', 0) > 0:
                    # Determine daily rate from this loan's APR
                    try:
                        apr = float(getattr(loan, 'rate_annual', 0.10))
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
