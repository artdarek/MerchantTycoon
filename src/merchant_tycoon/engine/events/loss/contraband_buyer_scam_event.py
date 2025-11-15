"""Contraband buyer scam event handler.

Triggers only if the player currently possesses contraband (in inventory or lots).
Outcome:
 - Remove N random purchase lots that contain contraband (N from settings).
 - Deduct each removed lot's quantity from inventory for its good.
 - No cash is received.
Legal goods, other lots, bank and investments remain untouched.
"""

import random
from typing import Optional, Tuple, List

from merchant_tycoon.engine.events.base import BaseEventHandler, EventType
from merchant_tycoon.engine.events.context import EventContext
from merchant_tycoon.config import SETTINGS


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

        # Build candidate list of contraband lots (with quantity > 0)
        candidates = []
        for lot in (context.state.purchase_lots or []):
            try:
                if getattr(lot, "quantity", 0) > 0 and context.goods_repo.is_contraband(lot.good_name):
                    candidates.append(lot)
            except Exception:
                continue

        if not candidates:
            return None

        # Determine how many lots to remove from settings (default 1)
        try:
            lots_to_remove = max(1, int(getattr(SETTINGS.events, 'contraband_scam_lots', 1)))
        except Exception:
            lots_to_remove = 1

        k = min(lots_to_remove, len(candidates))
        chosen = random.sample(candidates, k)

        removed_summary: List[str] = []
        for target in chosen:
            good = str(getattr(target, "good_name", ""))
            lot_qty = int(getattr(target, "quantity", 0))

            # Remove the lot entry
            try:
                context.state.purchase_lots.remove(target)
            except Exception:
                # Fallback: filter out by identity (best-effort)
                try:
                    context.state.purchase_lots = [l for l in (context.state.purchase_lots or []) if l is not target]
                except Exception:
                    pass

            # Deduct quantity from inventory for that good
            have = int(context.state.inventory.get(good, 0))
            new_have = max(0, have - lot_qty)
            if new_have > 0:
                context.state.inventory[good] = new_have
            else:
                context.state.inventory.pop(good, None)

            removed_summary.append(f"{lot_qty}x {good}")

        # Flavor message
        flavor_pool = [
            "The buyer disappeared with your goods. You receive nothing.",
            "Scam! The transaction was fake, and the goods are gone.",
            "Bad news. The contraband buyer ghosted you after the pickup.",
        ]
        flavor = random.choice(flavor_pool)

        # Build final message (first line concise for messenger, details for modal)
        details = ", ".join(removed_summary) if removed_summary else "no lots"
        message = (
            "Scam: Contraband stolen without payment.\n"
            f"{flavor}\n"
            f"Lost: {details}. No cash received."
        )
        return message, "loss"
