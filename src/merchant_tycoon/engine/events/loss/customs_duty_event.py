"""Customs duty event handler - pay fee based on inventory value."""

import random
from typing import Optional, Tuple

from merchant_tycoon.engine.events.base import BaseEventHandler, EventType
from merchant_tycoon.engine.events.context import EventContext
from merchant_tycoon.config import SETTINGS


class CustomsDutyEventHandler(BaseEventHandler):
    """Customs duty event - pay percentage of inventory value as customs fee.

    Event details:
    - Fee calculated as percentage (5-15%) of total inventory value
    - Uses initial_goods_prices to calculate inventory worth
    - Minimum fee: $1
    - Deducted from cash (can go negative)
    """

    @property
    def event_type(self) -> EventType:
        return "loss"

    @property
    def default_weight(self) -> float:
        return 6.0

    def can_trigger(self, context: EventContext) -> bool:
        """Can trigger if player has inventory with value."""
        if not context.state.inventory:
            return False
        # Check if inventory has any value
        total_value = self._calculate_inventory_value(context)
        return total_value > 0

    def trigger(self, context: EventContext) -> Optional[Tuple[str, EventType]]:
        """Execute customs duty event."""
        if not context.state.inventory:
            return None

        # Calculate total inventory value
        value = self._calculate_inventory_value(context)
        if value <= 0:
            return None

        # Calculate customs duty (5-15% of inventory value)
        lo, hi = SETTINGS.events.customs_duty_pct
        rate = random.uniform(lo, hi)
        fee = max(1, int(value * rate))

        # Deduct from cash
        context.state.cash -= fee

        return (
            f"🧾 CUSTOMS DUTY! Paid ${fee:,} ({int(rate*100)}%) on your goods.",
            "loss"
        )

    def _calculate_inventory_value(self, context: EventContext) -> int:
        """Calculate total value of inventory using initial prices.

        Args:
            context: Event context with state and prices

        Returns:
            Total inventory value
        """
        total = 0
        for good, qty in (context.state.inventory or {}).items():
            price = int(context.initial_goods_prices.get(good, 0))
            if price > 0 and qty > 0:
                total += price * qty
        return total
