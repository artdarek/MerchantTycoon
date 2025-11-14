"""Defective batch event handler - supplier bankrupt, lose last purchased lot."""

import random
from typing import Optional, Tuple

from merchant_tycoon.engine.events.base import BaseEventHandler, EventType
from merchant_tycoon.engine.events.context import EventContext


class DefectiveBatchEventHandler(BaseEventHandler):
    """Defective batch event - supplier went bankrupt, lose last lot of random good.

    Event details:
    - Selects random good that player currently holds
    - Finds the last (most recent) purchase lot for that good
    - Removes up to the lot quantity (capped by current inventory)
    - Uses record_loss_from_last() for proper lot accounting
    """

    @property
    def event_type(self) -> EventType:
        return "loss"

    @property
    def default_weight(self) -> float:
        return 5.0

    def can_trigger(self, context: EventContext) -> bool:
        """Can trigger if player has purchase lots with inventory."""
        lots = context.state.purchase_lots
        if not lots:
            return False
        # Check if any lot's good is still in inventory
        return any(context.state.inventory.get(lot.good_name, 0) > 0 for lot in lots)

    def trigger(self, context: EventContext) -> Optional[Tuple[str, EventType]]:
        """Execute defective batch event."""
        lots = context.state.purchase_lots
        if not lots:
            return None

        # Get goods that have lots and are still in inventory
        goods_with_lots = [
            lot.good_name for lot in lots
            if context.state.inventory.get(lot.good_name, 0) > 0
        ]

        if not goods_with_lots:
            return None

        # Select random good
        good = random.choice(goods_with_lots)

        # Find last (most recent) lot of this good
        for lot in reversed(lots):
            if lot.good_name == good:
                qty = context.state.inventory.get(good, 0)
                remove = min(qty, lot.quantity)
                if remove <= 0:
                    return None

                # Apply loss from last lot
                try:
                    if context.goods_service is not None:
                        context.goods_service.record_loss_from_last(good, remove)
                    else:
                        context.state.inventory[good] = max(0, qty - remove)
                except Exception:
                    context.state.inventory[good] = max(0, qty - remove)

                # Remove if depleted
                if context.state.inventory.get(good, 0) <= 0:
                    context.state.inventory.pop(good, None)

                return (
                    f"🛠️ DEFECTIVE BATCH! Supplier bankrupt. Lost {remove}x {good} (last lot).",
                    "loss"
                )

        return None
