"""Flood event handler - flood destroys large portion of total inventory."""

import random
from typing import Optional, Tuple, List

from merchant_tycoon.engine.events.base import BaseEventHandler, EventType
from merchant_tycoon.engine.events.context import EventContext
from merchant_tycoon.config import SETTINGS


class FloodEventHandler(BaseEventHandler):
    """Flood event - destroys 30-60% of total inventory spread across goods.

    Event details:
    - Heavier damage than fire (30-60% vs 20-50%)
    - Damage spread across multiple goods randomly
    - Per-good loss: 40-80% of that good's quantity
    - Uses FIFO accounting via goods_service if available
    """

    @property
    def event_type(self) -> EventType:
        return "loss"

    @property
    def default_weight(self) -> float:
        return 4.0

    def can_trigger(self, context: EventContext) -> bool:
        """Can trigger if player has any goods in inventory."""
        return bool(context.state.inventory)

    def trigger(self, context: EventContext) -> Optional[Tuple[str, EventType]]:
        """Execute flood event."""
        if not context.state.inventory:
            return None

        # Calculate total units to destroy (30-60% of total inventory)
        a, b = SETTINGS.events.flood_total_pct
        to_destroy = max(1, int(context.state.get_inventory_count() * random.uniform(a, b)))

        destroyed: List[str] = []
        goods = list(context.state.inventory.keys())
        random.shuffle(goods)  # Random destruction order

        for good in goods:
            if to_destroy <= 0:
                break

            have = context.state.inventory.get(good, 0)
            if have <= 0:
                continue

            # Destroy 40-80% of this good's quantity (heavier than fire)
            a, b = SETTINGS.events.flood_per_good_pct
            destroyed_qty = min(have, max(1, int(have * random.uniform(a, b))))
            destroyed_qty = min(destroyed_qty, to_destroy)

            # Apply loss
            try:
                if context.goods_service is not None:
                    context.goods_service.record_loss_fifo(good, destroyed_qty)
                else:
                    context.state.inventory[good] = have - destroyed_qty
            except Exception:
                context.state.inventory[good] = max(0, have - destroyed_qty)

            to_destroy -= destroyed_qty
            destroyed.append(f"{destroyed_qty}x {good}")

            # Remove if depleted
            if context.state.inventory.get(good, 0) <= 0:
                context.state.inventory.pop(good, None)

        if not destroyed:
            return None

        return ("🌊 FLOOD! Destroyed " + ", ".join(destroyed) + ".", "loss")
