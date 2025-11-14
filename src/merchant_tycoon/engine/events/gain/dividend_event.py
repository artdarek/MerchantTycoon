"""Dividend event handler - random stock pays dividend (legacy event, not regular dividend system)."""

import random
from typing import Optional, Tuple

from merchant_tycoon.engine.events.base import BaseEventHandler, EventType
from merchant_tycoon.engine.events.context import EventContext
from merchant_tycoon.config import SETTINGS


class DividendEventHandler(BaseEventHandler):
    """Dividend event - random held stock pays one-time dividend (travel event bonus).

    Event details:
    - This is a BONUS dividend event (separate from regular dividend system)
    - Selects random stock from player's portfolio
    - Payout: 0.5-2% of position value
    - Credited to bank account via bank_service
    - Only stocks eligible (not commodities or crypto)

    Note: This is different from the regular dividend system which pays
    on a schedule. This is a random bonus event during travel.
    """

    @property
    def event_type(self) -> EventType:
        return "gain"

    @property
    def default_weight(self) -> float:
        return 6.0

    def can_trigger(self, context: EventContext) -> bool:
        """Can trigger if player holds any stocks."""
        stock_symbols = context.assets_repo.get_stock_symbols()
        return any(
            qty > 0 and sym in stock_symbols
            for sym, qty in (context.state.portfolio or {}).items()
        )

    def trigger(self, context: EventContext) -> Optional[Tuple[str, EventType]]:
        """Execute dividend event."""
        # Get all stock symbols
        stock_symbols = context.assets_repo.get_stock_symbols()

        # Filter to stocks player holds
        held_stocks = [
            sym for sym, qty in (context.state.portfolio or {}).items()
            if qty > 0 and sym in stock_symbols
        ]

        if not held_stocks:
            return None

        # Select random stock
        sym = random.choice(held_stocks)
        qty = context.state.portfolio.get(sym, 0)
        price = context.initial_asset_prices.get(sym, 0)

        if qty <= 0 or price <= 0:
            return None

        # Calculate dividend (0.5-2% of position value)
        lo, hi = SETTINGS.events.dividend_pct
        pct = random.uniform(lo, hi)
        payout = max(1, int(qty * price * pct))

        # Credit to bank account
        self._bank_credit(context, payout, f"Dividend for {sym}")

        return (
            f"💸 DIVIDEND! {sym} paid you ${payout:,} (≈{pct*100:.1f}% of position) credited to bank.",
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
