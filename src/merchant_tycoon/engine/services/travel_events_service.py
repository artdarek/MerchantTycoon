import random
from typing import List, Optional

from merchant_tycoon.model import BankTransaction, STOCKS, GOODS
from merchant_tycoon.config import SETTINGS
from datetime import datetime


class TravelEventsService:
    """Weighted random travel events.

    Exposes a single method `trigger(engine)` that performs at most one event and
    returns a tuple (message, is_positive) or None if no event occurs.

    Notes:
    - Only goods/cash/bank and one-day price modifiers are affected by events.
    - Investments are safe; a positive dividend may be credited to bank.
    - This class is stateless; all state is taken from the provided engine instance.
    """

    def trigger(self, state, prices: dict, asset_prices: dict, bank_service=None, goods_service=None) -> Optional[tuple[str, bool]]:
        """Trigger at most one weighted random travel event.

        Parameters:
            state: Game state object with inventory, cash, bank, etc.
            prices: dict of current goods prices {good_name: price}
            asset_prices: dict of asset prices {symbol: price}
            bank_service: optional bank service to credit amounts into bank history
        """
        # Overall chance that any event occurs this travel
        if random.random() >= float(SETTINGS.events.base_probability):
            return None
        prices = prices or {}

        def inv_total_value() -> int:
            total = 0
            for g, qty in (state.inventory or {}).items():
                price = int(prices.get(g, 0))
                if price > 0 and qty > 0:
                    total += price * qty
            return total

        # Helper: bank credit via service if provided, otherwise best-effort fallback
        def bank_credit(amount: int, tx_type: str = "deposit", title: str = "") -> None:
            if amount <= 0:
                return
            if bank_service is not None and hasattr(bank_service, "credit"):
                try:
                    bank_service.credit(int(amount), tx_type=tx_type, title=title)
                    return
                except Exception:
                    pass
            # Fallback: mutate state directly
            try:
                state.bank.balance += int(amount)
                ts = (
                    getattr(getattr(bank_service, "clock", None), "now", lambda: None)()
                    if bank_service is not None else None
                )
                if ts is None:
                    ts_str = f"{getattr(state,'date','')}T{datetime.now().strftime('%H:%M:%S')}"
                else:
                    try:
                        ts_str = ts.isoformat(timespec="seconds")
                    except Exception:
                        ts_str = f"{getattr(state,'date','')}T{datetime.now().strftime('%H:%M:%S')}"
                state.bank.transactions.append(
                    BankTransaction(
                        tx_type=tx_type if tx_type in ("deposit", "withdraw", "interest") else "deposit",
                        amount=int(amount),
                        balance_after=state.bank.balance,
                        day=state.day,
                        title=title or ("Deposit" if tx_type == "deposit" else ("Withdraw" if tx_type == "withdraw" else "Interest")),
                        ts=ts_str,
                    )
                )
            except Exception:
                state.cash += int(amount)

        # Event handlers (side-effecting), each returns (message, is_positive) or None if not applicable
        # LOSS EVENTS
        def evt_robbery() -> Optional[tuple[str, bool]]:
            if not state.inventory:
                return None
            good = random.choice(list(state.inventory.keys()))
            qty = state.inventory.get(good, 0)
            if qty <= 0:
                return None
            # Smaller loss than fire/flood
            a, b = SETTINGS.events.robbery_loss_pct
            lost = max(1, int(qty * random.uniform(a, b)))
            lost = min(lost, qty)
            state.inventory[good] = qty - lost
            # Adjust lots (FIFO) to reflect loss
            try:
                if goods_service is not None:
                    goods_service._remove_from_lots_fifo(good, lost)
            except Exception:
                pass
            if state.inventory[good] <= 0:
                del state.inventory[good]
            return (f"🚨 ROBBERY! Lost {lost}x {good}.", False)

        def evt_fire() -> Optional[tuple[str, bool]]:
            if not state.inventory:
                return None
            # Destroy a portion of total inventory, spread across goods
            a, b = SETTINGS.events.fire_total_pct
            to_destroy = max(1, int(state.get_inventory_count() * random.uniform(a, b)))
            destroyed: List[str] = []
            goods = list(state.inventory.keys())
            random.shuffle(goods)
            for g in goods:
                if to_destroy <= 0:
                    break
                have = state.inventory.get(g, 0)
                if have <= 0:
                    continue
                a, b = SETTINGS.events.fire_per_good_pct
                d = min(have, max(1, int(have * random.uniform(a, b))))
                d = min(d, to_destroy)
                state.inventory[g] = have - d
                to_destroy -= d
                destroyed.append(f"{d}x {g}")
                if state.inventory[g] <= 0:
                    del state.inventory[g]
                try:
                    if goods_service is not None:
                        goods_service._remove_from_lots_fifo(g, d)
                except Exception:
                    pass
            if not destroyed:
                return None
            return ("🔥 WAREHOUSE FIRE! Destroyed " + ", ".join(destroyed) + ".", False)

        def evt_flood() -> Optional[tuple[str, bool]]:
            if not state.inventory:
                return None
            # Heavier than fire
            a, b = SETTINGS.events.flood_total_pct
            to_destroy = max(1, int(state.get_inventory_count() * random.uniform(a, b)))
            destroyed: List[str] = []
            goods = list(state.inventory.keys())
            random.shuffle(goods)
            for g in goods:
                if to_destroy <= 0:
                    break
                have = state.inventory.get(g, 0)
                if have <= 0:
                    continue
                a, b = SETTINGS.events.flood_per_good_pct
                d = min(have, max(1, int(have * random.uniform(a, b))))
                d = min(d, to_destroy)
                state.inventory[g] = have - d
                to_destroy -= d
                destroyed.append(f"{d}x {g}")
                if state.inventory[g] <= 0:
                    del state.inventory[g]
                try:
                    if goods_service is not None:
                        goods_service._remove_from_lots_fifo(g, d)
                except Exception:
                    pass
            if not destroyed:
                return None
            return ("🌊 FLOOD! Destroyed " + ", ".join(destroyed) + ".", False)

        def evt_defective_batch() -> Optional[tuple[str, bool]]:
            # Remove last purchased lot of a random good that you still hold
            lots = state.purchase_lots
            if not lots:
                return None
            goods_with_lots = [lot.good_name for lot in lots if state.inventory.get(lot.good_name, 0) > 0]
            if not goods_with_lots:
                return None
            g = random.choice(goods_with_lots)
            # find last lot of this good
            for lot in reversed(lots):
                if lot.good_name == g:
                    qty = state.inventory.get(g, 0)
                    remove = min(qty, lot.quantity)
                    if remove <= 0:
                        return None
                    state.inventory[g] = qty - remove
                    if state.inventory[g] <= 0:
                        del state.inventory[g]
                    # Remove from last lot(s) as the event targets the last purchase
                    try:
                        if goods_service is not None:
                            goods_service._remove_from_lots_from_last(g, remove)
                    except Exception:
                        pass
                    return (f"🛠️ DEFECTIVE BATCH! Supplier bankrupt. Lost {remove}x {g} (last lot).", False)
            return None

        def evt_customs_duty() -> Optional[tuple[str, bool]]:
            if not state.inventory:
                return None
            value = inv_total_value()
            if value <= 0:
                return None
            lo, hi = SETTINGS.events.customs_duty_pct
            rate = random.uniform(lo, hi)
            fee = max(1, int(value * rate))
            state.cash -= fee
            return (f"🧾 CUSTOMS DUTY! Paid ${fee:,} ({int(rate*100)}%) on your goods.", False)

        def evt_stolen_last_buy() -> Optional[tuple[str, bool]]:
            # Confiscate last purchase if exists and still held
            txs = state.transaction_history
            if not txs:
                return None
            last_buy = None
            for tx in reversed(txs):
                if tx.transaction_type == "buy":
                    last_buy = tx
                    break
            if not last_buy:
                return None
            g = last_buy.good_name
            have = state.inventory.get(g, 0)
            if have <= 0:
                return None
            remove = min(have, last_buy.quantity)
            state.inventory[g] = have - remove
            if state.inventory[g] <= 0:
                del state.inventory[g]
            # Confiscate from last buy lot(s)
            try:
                if goods_service is not None:
                    goods_service._remove_from_lots_from_last(g, remove)
            except Exception:
                pass
            return (f"🚔 STOLEN GOODS! Your last purchase was confiscated: lost {remove}x {g}.", False)

        def evt_cash_damage() -> Optional[tuple[str, bool]]:
            # Generic accident costing cash, scaled by current cash
            lo, hi = SETTINGS.events.cash_damage_pct
            base = int(state.cash * random.uniform(lo, hi))
            damage = max(SETTINGS.events.cash_damage_min, min(SETTINGS.events.cash_damage_max, base))
            if damage <= 0:
                return None
            state.cash -= damage
            return (f"💥 ACCIDENT! Paid ${damage:,} in damages.", False)

        # GAIN EVENTS
        def evt_dividend() -> Optional[tuple[str, bool]]:
            # Pay dividend for a held stock (not commodity/crypto)
            held_stocks = [sym for sym, qty in (state.portfolio or {}).items() if qty > 0 and any(s.symbol == sym for s in STOCKS)]
            if not held_stocks:
                return None
            sym = random.choice(held_stocks)
            qty = state.portfolio.get(sym, 0)
            price = (asset_prices or {}).get(sym, 0) or 0
            if qty <= 0 or price <= 0:
                return None
            # Dividend percentage of position value
            lo, hi = SETTINGS.events.dividend_pct
            pct = random.uniform(lo, hi)
            payout = max(1, int(qty * price * pct))
            # Prefer bank credit if bank exists
            bank_credit(payout, tx_type="interest", title=f"Dividend for {sym}")
            return (f"💸 DIVIDEND! {sym} paid you ${payout:,} (≈{pct*100:.1f}% of position) credited to bank.", True)

        def evt_lottery() -> Optional[tuple[str, bool]]:
            # Simulate 3/4/5/6 hits
            tier = random.choices(SETTINGS.events.lottery_tiers, weights=SETTINGS.events.lottery_weights, k=1)[0]
            low, high = SETTINGS.events.lottery_reward_ranges.get(tier, (200, 600))
            win = random.randint(low, high)
            state.cash += win
            return (f"🎟️ LOTTERY! You matched {tier} numbers and won ${win:,}!", True)

        def evt_bank_correction() -> Optional[tuple[str, bool]]:
            # Bank miscalculated interest; credit if account exists
            try:
                bal = int(getattr(state.bank, 'balance', 0))
            except Exception:
                bal = 0
            if bal <= 0:
                return None
            lo, hi = SETTINGS.events.bank_correction_pct
            pct = random.uniform(lo, hi)
            amount = max(SETTINGS.events.bank_correction_min, int(bal * pct))
            bank_credit(amount, tx_type="interest", title="Interest correction from bank")
            return (f"🏦 BANK CORRECTION! Extra interest ${amount:,} credited to your account.", True)

        def evt_promo_good() -> Optional[tuple[str, bool]]:
            # Promotion - price down 30%–60% for a random good (next prices)
            if not GOODS:
                return None
            good = random.choice(GOODS).name
            lo, hi = SETTINGS.events.promo_multiplier
            mult = random.uniform(lo, hi)
            state.price_modifiers[good] = mult
            return (f"🏷️ PROMOTION! {good} will be cheaper today (−{int((1 - mult) * 100)}%).", True)

        def evt_oversupply() -> Optional[tuple[str, bool]]:
            # Very low price for random good
            if not GOODS:
                return None
            good = random.choice(GOODS).name
            lo, hi = SETTINGS.events.oversupply_multiplier
            mult = random.uniform(lo, hi)
            state.price_modifiers[good] = mult
            return (f"📉 OVERSUPPLY! {good} prices plunge (−{int((1 - mult) * 100)}%).", True)

        def evt_shortage() -> Optional[tuple[str, bool]]:
            if not GOODS:
                return None
            good = random.choice(GOODS).name
            lo, hi = SETTINGS.events.shortage_multiplier
            mult = random.uniform(lo, hi)
            state.price_modifiers[good] = mult
            return (f"📈 SHORTAGE! {good} prices soar (≈×{mult:.1f}).", True)

        def evt_loyal_discount() -> Optional[tuple[str, bool]]:
            # Loyal customer special: 95% discount on a random good for today
            if not GOODS:
                return None
            good = random.choice(GOODS).name
            mult = SETTINGS.events.loyal_discount_multiplier
            state.price_modifiers[good] = mult
            return (f"🤝 LOYAL CUSTOMER! As a valued customer you get 95% discount on {good} (today only)!", True)

        # Build event table with explicit can/apply and weights (no side effects during can)
        class _Evt:
            def __init__(self, can_fn, apply_fn, weight: float):
                self.can = can_fn
                self.apply = apply_fn
                self.w = float(max(0.0, weight))

        def has_inventory() -> bool:
            return bool(state.inventory)

        def has_any_purchase_with_inventory() -> bool:
            return any(state.inventory.get(lot.good_name, 0) > 0 for lot in (state.purchase_lots or []))

        def has_last_buy_with_inventory() -> bool:
            txs = state.transaction_history or []
            last_buy = None
            for tx in reversed(txs):
                if tx.transaction_type == "buy":
                    last_buy = tx
                    break
            if not last_buy:
                return False
            return state.inventory.get(last_buy.good_name, 0) > 0

        def inv_value_positive() -> bool:
            return inv_total_value() > 0

        def has_cash() -> bool:
            return int(state.cash) > 0

        def holds_any_stock() -> bool:
            return any(qty > 0 and any(s.symbol == sym for s in STOCKS) for sym, qty in (state.portfolio or {}).items())

        def bank_has_balance() -> bool:
            try:
                return int(getattr(state.bank, 'balance', 0)) > 0
            except Exception:
                return False

        w = SETTINGS.events.weights
        events: List[_Evt] = [
            # Loss events
            _Evt(has_inventory, evt_robbery, w.get("robbery", 8)),
            _Evt(has_inventory, evt_fire, w.get("fire", 5)),
            _Evt(has_inventory, evt_flood, w.get("flood", 4)),
            _Evt(has_any_purchase_with_inventory, evt_defective_batch, w.get("defective_batch", 5)),
            _Evt(inv_value_positive, evt_customs_duty, w.get("customs_duty", 6)),
            _Evt(has_last_buy_with_inventory, evt_stolen_last_buy, w.get("stolen_last_buy", 5)),
            _Evt(has_cash, evt_cash_damage, w.get("cash_damage", 4)),
            # Gain events
            _Evt(holds_any_stock, evt_dividend, w.get("dividend", 6)),
            _Evt(lambda: True, evt_lottery, w.get("lottery", 3)),
            _Evt(bank_has_balance, evt_bank_correction, w.get("bank_correction", 4)),
            _Evt(lambda: True, evt_promo_good, w.get("promo", 5)),
            _Evt(lambda: True, evt_oversupply, w.get("oversupply", 4)),
            _Evt(lambda: True, evt_shortage, w.get("shortage", 4)),
            _Evt(lambda: True, evt_loyal_discount, w.get("loyal_discount", 1)),
        ]

        eligible = [e for e in events if e.w > 0 and e.can()]
        if not eligible:
            return None
        total_w = sum(e.w for e in eligible)
        pick = random.uniform(0, total_w)
        upto = 0.0
        chosen = eligible[-1]
        for e in eligible:
            upto += e.w
            if pick <= upto:
                chosen = e
                break
        return chosen.apply()
