"""FBI confiscation mega-event handler.

Triggers only if the player currently possesses contraband (in inventory or lots).
Outcome (severe penalty):
 - Cash: reduce by 75% (keep 25%)
 - Bank: balance set to 0
 - Investments: untouched
 - Inventory: remove ALL goods (legal + contraband)
 - Cargo: reset capacity to base (remove all purchased expansions)
"""

from typing import Optional, Tuple

from merchant_tycoon.engine.events.base import BaseEventHandler, EventType
from merchant_tycoon.engine.events.context import EventContext
from merchant_tycoon.config import SETTINGS


class FBIConfiscationEventHandler(BaseEventHandler):
    @property
    def event_type(self) -> EventType:
        return "loss"

    @property
    def default_weight(self) -> float:
        # Rare, very heavy penalty
        return 2.0

    def _has_contraband(self, context: EventContext) -> bool:
        try:
            for name, qty in (context.state.inventory or {}).items():
                if qty > 0 and context.goods_repo.is_contraband(name):
                    return True
            for lot in (context.state.purchase_lots or []):
                if getattr(lot, "quantity", 0) > 0 and context.goods_repo.is_contraband(lot.good_name):
                    return True
        except Exception:
            pass
        return False

    def can_trigger(self, context: EventContext) -> bool:
        # Only eligible if carrying contraband
        return self._has_contraband(context)

    def trigger(self, context: EventContext) -> Optional[Tuple[str, EventType]]:
        if not self._has_contraband(context):
            return None

        # Cash: keep 25%
        try:
            old_cash = int(getattr(context.state, "cash", 0))
            context.state.cash = max(0, int(old_cash * 0.25))
        except Exception:
            pass

        # Bank: zero-out balance
        try:
            context.state.bank.balance = 0
        except Exception:
            pass

        # Inventory: remove everything (legal + contraband)
        try:
            context.state.inventory.clear()
        except Exception:
            context.state.inventory = {}

        try:
            context.state.purchase_lots.clear()
        except Exception:
            context.state.purchase_lots = []

        # Cargo capacity: reset to base (remove expansions)
        try:
            context.state.max_inventory = int(SETTINGS.cargo.base_capacity)
        except Exception:
            pass

        # Narrative-rich modal message; concise first line for messenger
        message = (
            "FBI raid: Major assets confiscated.\n"
            "🚨 FBI RAID!\n"
            "Your contraband operation was detected.\n"
            "All goods have been confiscated.\n"
            "75% of your cash was seized, your bank account was frozen,\n"
            "and all cargo upgrades were removed.\n"
            "Investments remain untouched."
        )
        return message, "loss"

