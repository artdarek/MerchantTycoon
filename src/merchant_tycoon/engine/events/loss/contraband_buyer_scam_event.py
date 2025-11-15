"""Contraband buyer scam event handler.

Triggers only if the player currently possesses contraband (in inventory or lots).
Outcome:
 - Remove ALL purchase lots containing contraband goods.
 - Remove all contraband quantities from inventory.
 - No cash is received.
Legal goods, bank and investments remain untouched.
"""

import random
from typing import Optional, Tuple, List

from merchant_tycoon.engine.events.base import BaseEventHandler, EventType
from merchant_tycoon.engine.events.context import EventContext


class ContrabandBuyerScamEventHandler(BaseEventHandler):
    @property
    def event_type(self) -> EventType:
        return "loss"

    @property
    def default_weight(self) -> float:
        # More likely than the FBI raid, but still not too common
        return 6.0

    def _has_contraband(self, context: EventContext) -> bool:
        try:
            # Inventory check
            for name, qty in (context.state.inventory or {}).items():
                if qty > 0 and context.goods_repo.is_contraband(name):
                    return True
            # Lots check
            for lot in (context.state.purchase_lots or []):
                if getattr(lot, "quantity", 0) > 0 and context.goods_repo.is_contraband(lot.good_name):
                    return True
        except Exception:
            pass
        return False

    def can_trigger(self, context: EventContext) -> bool:
        # Eligible only if the player holds any contraband
        return self._has_contraband(context)

    def trigger(self, context: EventContext) -> Optional[Tuple[str, EventType]]:
        if not self._has_contraband(context):
            return None

        contraband_goods: List[str] = []
        try:
            for name, qty in list((context.state.inventory or {}).items()):
                if qty > 0 and context.goods_repo.is_contraband(name):
                    contraband_goods.append(name)
        except Exception:
            pass

        if not contraband_goods:
            # As a fallback, inspect lots to discover contraband names
            try:
                for lot in (context.state.purchase_lots or []):
                    if getattr(lot, "quantity", 0) > 0 and context.goods_repo.is_contraband(lot.good_name):
                        if lot.good_name not in contraband_goods:
                            contraband_goods.append(lot.good_name)
            except Exception:
                pass

        # Nothing to do if we somehow couldn't detect any
        if not contraband_goods:
            return None

        # Remove all contraband quantities and purge their lots
        removed_summary: List[str] = []
        for good in contraband_goods:
            qty = int(context.state.inventory.get(good, 0))
            if qty > 0:
                try:
                    if context.goods_service is not None:
                        actually_removed = int(context.goods_service.record_loss_from_last(good, qty))
                    else:
                        actually_removed = qty
                        context.state.inventory[good] = 0
                except Exception:
                    actually_removed = qty
                    context.state.inventory[good] = 0
                removed_summary.append(f"{actually_removed}x {good}")
                if int(context.state.inventory.get(good, 0)) <= 0:
                    context.state.inventory.pop(good, None)
            # Purge purchase lots for this contraband good
            try:
                context.state.purchase_lots = [
                    lot for lot in (context.state.purchase_lots or [])
                    if lot.good_name != good
                ]
            except Exception:
                pass

        # Flavor message
        flavor_pool = [
            "The buyer disappeared with your goods. You receive nothing.",
            "Scam! The transaction was fake, and the goods are gone.",
            "Bad news. The contraband buyer ghosted you after the pickup.",
        ]
        flavor = random.choice(flavor_pool)

        # Build final message (first line concise for messenger, details for modal)
        details = ", ".join(removed_summary) if removed_summary else "All contraband lots removed."
        message = (
            "Scam: Contraband stolen without payment.\n"
            f"{flavor}\n"
            f"Lost: {details}. No cash received."
        )
        return message, "loss"

