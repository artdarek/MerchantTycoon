"""Stolen goods event handler - last purchase confiscated by authorities."""

import random
from typing import Optional, Tuple

from merchant_tycoon.engine.events.base import BaseEventHandler, EventType
from merchant_tycoon.engine.events.context import EventContext


class StolenGoodsEventHandler(BaseEventHandler):
    """Stolen goods event - authorities confiscate your last purchase.

    Event details:
    - Finds last 'buy' transaction from history
    - Confiscates quantity from that purchase (if still in inventory)
    - Uses record_loss_from_last() for proper lot accounting
    """

    @property
    def event_type(self) -> EventType:
        return "loss"

    @property
    def default_weight(self) -> float:
        return 5.0

    def can_trigger(self, context: EventContext) -> bool:
        """Can trigger if player has a last buy transaction with goods still held."""
        txs = context.state.transaction_history or []
        if not txs:
            return False

        # Find last buy transaction
        last_buy = None
        for tx in reversed(txs):
            if tx.transaction_type == "buy":
                last_buy = tx
                break

        if not last_buy:
            return False

        # Check if those goods are still in inventory
        return context.state.inventory.get(last_buy.good_name, 0) > 0

    def trigger(self, context: EventContext) -> Optional[Tuple[str, EventType]]:
        """Execute stolen goods event."""
        txs = context.state.transaction_history or []
        if not txs:
            return None

        # Find last buy transaction
        last_buy = None
        for tx in reversed(txs):
            if tx.transaction_type == "buy":
                last_buy = tx
                break

        if not last_buy:
            return None

        good = last_buy.good_name
        have = context.state.inventory.get(good, 0)
        if have <= 0:
            return None

        # Confiscate quantity from last purchase
        remove = min(have, last_buy.quantity)

        # Apply loss
        try:
            if context.goods_service is not None:
                context.goods_service.record_loss_from_last(good, remove)
            else:
                context.state.inventory[good] = max(0, have - remove)
        except Exception:
            context.state.inventory[good] = max(0, have - remove)

        # Remove if depleted
        if context.state.inventory.get(good, 0) <= 0:
            context.state.inventory.pop(good, None)

        return (
            f"🚔 STOLEN GOODS! Your bought stollen goods! Your last purchase was confiscated: lost {remove}x {good}.",
            "loss"
        )
