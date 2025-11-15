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

    def _contraband_lot_count(self, context: EventContext) -> int:
        count = 0
        try:
            for lot in (context.state.purchase_lots or []):
                if getattr(lot, "quantity", 0) > 0 and context.goods_repo.is_contraband(lot.good_name):
                    count += 1
        except Exception:
            return 0
        return count

    def can_trigger(self, context: EventContext) -> bool:
        # Only eligible if carrying at least N contraband lots (configurable)
        try:
            min_lots = int(getattr(SETTINGS.events, "fbi_min_contraband_lots", 3))
        except Exception:
            min_lots = 3
        return self._contraband_lot_count(context) >= max(1, min_lots)

    def trigger(self, context: EventContext) -> Optional[Tuple[str, EventType]]:
        try:
            min_lots = int(getattr(SETTINGS.events, "fbi_min_contraband_lots", 3))
        except Exception:
            min_lots = 3
        if self._contraband_lot_count(context) < max(1, min_lots):
            return None

        # Cash: keep configured percentage
        try:
            keep_pct = float(getattr(SETTINGS.events, "fbi_cash_keep_pct", 0.25))
            keep_pct = max(0.0, min(1.0, keep_pct))
            old_cash = int(getattr(context.state, "cash", 0))
            context.state.cash = max(0, int(old_cash * keep_pct))
        except Exception:
            pass

        # Bank: apply reduction percentage via bank_service withdrawal with custom title.
        try:
            red_pct = float(getattr(SETTINGS.events, "fbi_bank_reduction_pct", 1.0))
            red_pct = max(0.0, min(1.0, red_pct))
            old_bal = int(getattr(context.state.bank, "balance", 0))
            reduce_amt = max(0, int(old_bal * red_pct))
            if reduce_amt > 0:
                if context.bank_service is not None:
                    # Use withdraw function but don't credit wallet; label the transaction
                    context.bank_service.withdraw_from_bank(reduce_amt, title="FBI confiscated", credit_wallet=False)
                else:
                    # Fallback: direct adjust (no wallet credit)
                    new_bal = max(0, int(old_bal - reduce_amt))
                    context.state.bank.balance = new_bal
        except Exception:
            red_pct = 1.0

        # Inventory: optionally remove everything (legal + contraband)
        try:
            remove_all = bool(getattr(SETTINGS.events, "fbi_remove_all_goods", True))
        except Exception:
            remove_all = True
        if remove_all:
            try:
                context.state.inventory.clear()
            except Exception:
                context.state.inventory = {}
            try:
                context.state.purchase_lots.clear()
            except Exception:
                context.state.purchase_lots = []

        # Cargo capacity: reset to a fraction of base capacity
        try:
            pct = float(getattr(SETTINGS.events, "fbi_cargo_capacity_pct", 1.0))
            pct = max(0.0, pct)
            base = int(getattr(SETTINGS.cargo, "base_capacity", 50))
            context.state.max_inventory = max(0, int(base * pct))
        except Exception:
            pct = 1.0

        # Narrative-rich modal message; concise first line for messenger
        # Build dynamic message summarizing penalties
        seized_cash_pct = int(round((1.0 - keep_pct) * 100))
        bank_red_pct = int(round(red_pct * 100))
        cargo_pct_str = f"{int(round(pct * 100))}% of base" if pct != 1.0 else "base capacity"
        inv_line = "All goods have been confiscated." if remove_all else "Inventory was inspected but not seized."

        message = (
            "FBI raid: Major assets confiscated.\n"
            "🚨 FBI RAID!\n"
            "Your contraband operation was detected.\n"
            f"{inv_line}\n"
            f"{seized_cash_pct}% of your cash was seized; bank balance reduced by {bank_red_pct}%.\n"
            f"Cargo capacity reset to {cargo_pct_str}.\n"
            "Investments remain untouched."
        )
        return message, "loss"
