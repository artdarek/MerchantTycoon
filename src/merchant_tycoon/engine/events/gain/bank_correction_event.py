"""Bank correction event handler - bank miscalculated, bonus interest paid."""

import random
from typing import Optional, Tuple

from merchant_tycoon.engine.events.base import BaseEventHandler, EventType
from merchant_tycoon.engine.events.context import EventContext
from merchant_tycoon.config import SETTINGS


class BankCorrectionEventHandler(BaseEventHandler):
    """Bank correction event - bank credits extra interest due to calculation error.

    Event details:
    - Requires bank account with positive balance
    - Bonus: 1-5% of current bank balance
    - Minimum bonus: configured in settings (default $10)
    - Credited to bank account via bank_service
    """

    @property
    def event_type(self) -> EventType:
        return "gain"

    @property
    def default_weight(self) -> float:
        return 4.0

    def can_trigger(self, context: EventContext) -> bool:
        """Can trigger if player has positive bank balance."""
        try:
            bal = int(getattr(context.state.bank, 'balance', 0))
        except Exception:
            bal = 0
        return bal > 0

    def trigger(self, context: EventContext) -> Optional[Tuple[str, EventType]]:
        """Execute bank correction event."""
        try:
            bal = int(getattr(context.state.bank, 'balance', 0))
        except Exception:
            bal = 0

        if bal <= 0:
            return None

        # Calculate bonus interest (1-5% of balance)
        lo, hi = SETTINGS.events.bank_correction_pct
        pct = random.uniform(lo, hi)
        amount = max(SETTINGS.events.bank_correction_min, int(bal * pct))

        # Credit to bank
        self._bank_credit(context, amount, "Interest correction from bank")

        return (
            f"🏦 BANK CORRECTION! Extra interest ${amount:,} credited to your account.",
            "gain"
        )

    def _bank_credit(
        self,
        context: EventContext,
        amount: int,
        title: str
    ) -> None:
        """Credit amount to bank account."""
        if amount <= 0:
            return

        # Use bank service if available
        if context.bank_service is not None and hasattr(context.bank_service, "credit"):
            try:
                context.bank_service.credit(int(amount), tx_type="interest", title=title)
                return
            except Exception:
                pass

        # Fallback: add to cash
        context.state.cash += int(amount)
