"""Robbery event handler - lose portion of a random good from inventory."""

import random
from typing import Optional, Tuple

from merchant_tycoon.engine.events.base import BaseEventHandler, EventType
from merchant_tycoon.engine.events.context import EventContext
from merchant_tycoon.config import SETTINGS


class RobberyEventHandler(BaseEventHandler):
    """Robbery event - lose 10-30% of a random good.

    Event details:
    - Targets a random good from player's inventory
    - Loss percentage configured in SETTINGS.events.robbery_loss_pct
    - Minimum loss: 1 unit
    - Uses FIFO accounting via goods_service if available
    """

    @property
    def event_type(self) -> EventType:
        return "loss"

    @property
    def default_weight(self) -> float:
        return 8.0

    def can_trigger(self, context: EventContext) -> bool:
        """Can trigger if player has any goods in inventory."""
        return bool(context.state.inventory)

    def trigger(self, context: EventContext) -> Optional[Tuple[str, EventType]]:
        """Execute robbery event."""
        if not context.state.inventory:
            return None

        # Select random good from inventory
        good = random.choice(list(context.state.inventory.keys()))
        qty = context.state.inventory.get(good, 0)
        if qty <= 0:
            return None

        # Calculate loss (10-30% of quantity, minimum 1)
        a, b = SETTINGS.events.robbery_loss_pct
        lost = max(1, int(qty * random.uniform(a, b)))
        lost = min(lost, qty)  # Cap at available quantity

        # Apply loss via goods service (handles FIFO and lot accounting)
        try:
            if context.goods_service is not None:
                context.goods_service.record_loss_fifo(good, lost)
            else:
                # Fallback: direct inventory modification
                context.state.inventory[good] = qty - lost
        except Exception:
            # Safety fallback
            context.state.inventory[good] = max(0, qty - lost)

        # Remove good from inventory if depleted
        if context.state.inventory.get(good, 0) <= 0:
            context.state.inventory.pop(good, None)

        return (f"🚨 ROBBERY! Lost {lost}x {good}.", "loss")
