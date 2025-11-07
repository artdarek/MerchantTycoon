import random
from typing import List, Optional

from ..models import BankTransaction, STOCKS, GOODS


class TravelEventSystem:
    """Weighted random travel events.

    Exposes a single method `trigger(engine)` that performs at most one event and
    returns a tuple (message, is_positive) or None if no event occurs.

    Notes:
    - Only goods/cash/bank and one-day price modifiers are affected by events.
    - Investments are safe; a positive dividend may be credited to bank.
    - This class is stateless; all state is taken from the provided engine instance.
    """

    def trigger(self, engine) -> Optional[tuple[str, bool]]:
        # Overall chance that any event occurs this travel
        if random.random() >= 0.25:  # 25% chance of any event
            return None

        state = engine.state
        prices = engine.prices or {}

        def inv_total_value() -> int:
            total = 0
            for g, qty in (state.inventory or {}).items():
                price = int(prices.get(g, 0))
                if price > 0 and qty > 0:
                    total += price * qty
            return total

        # Helper: bank credit
        def bank_credit(amount: int, tx_type: str = "deposit", title: str = "") -> None:
            if amount <= 0:
                return
            try:
                state.bank.balance += amount
                state.bank.transactions.append(
                    BankTransaction(
                        tx_type=tx_type if tx_type in ("deposit", "withdraw", "interest") else "deposit",
                        amount=amount,
                        balance_after=state.bank.balance,
                        day=state.day,
                        title=title or ("Deposit" if tx_type == "deposit" else ("Withdraw" if tx_type == "withdraw" else "Interest")),
                    )
                )
            except Exception:
                # Fallback to cash if bank broken
                state.cash += amount

        # Event handlers (side-effecting), each returns (message, is_positive) or None if not applicable
        # LOSS EVENTS
        def evt_robbery() -> Optional[tuple[str, bool]]:
            if not state.inventory:
                return None
            good = random.choice(list(state.inventory.keys()))
            qty = state.inventory.get(good, 0)
            if qty <= 0:
                return None
            # Smaller loss than fire/flood: 10%–40% of that good
            lost = max(1, int(qty * random.uniform(0.1, 0.4)))
            lost = min(lost, qty)
            state.inventory[good] = qty - lost
            if state.inventory[good] <= 0:
                del state.inventory[good]
            return (f"🚨 ROBBERY! Lost {lost}x {good}.", False)

        def evt_fire() -> Optional[tuple[str, bool]]:
            if not state.inventory:
                return None
            # Destroy 20%–60% of total inventory, spread across goods
            to_destroy = max(1, int(state.get_inventory_count() * random.uniform(0.2, 0.6)))
            destroyed: List[str] = []
            goods = list(state.inventory.keys())
            random.shuffle(goods)
            for g in goods:
                if to_destroy <= 0:
                    break
                have = state.inventory.get(g, 0)
                if have <= 0:
                    continue
                d = min(have, max(1, int(have * random.uniform(0.2, 0.6))))
                d = min(d, to_destroy)
                state.inventory[g] = have - d
                to_destroy -= d
                destroyed.append(f"{d}x {g}")
                if state.inventory[g] <= 0:
                    del state.inventory[g]
            if not destroyed:
                return None
            return ("🔥 WAREHOUSE FIRE! Destroyed " + ", ".join(destroyed) + ".", False)

        def evt_flood() -> Optional[tuple[str, bool]]:
            if not state.inventory:
                return None
            # Heavier than fire: 30%–80% total
            to_destroy = max(1, int(state.get_inventory_count() * random.uniform(0.3, 0.8)))
            destroyed: List[str] = []
            goods = list(state.inventory.keys())
            random.shuffle(goods)
            for g in goods:
                if to_destroy <= 0:
                    break
                have = state.inventory.get(g, 0)
                if have <= 0:
                    continue
                d = min(have, max(1, int(have * random.uniform(0.3, 0.8))))
                d = min(d, to_destroy)
                state.inventory[g] = have - d
                to_destroy -= d
                destroyed.append(f"{d}x {g}")
                if state.inventory[g] <= 0:
                    del state.inventory[g]
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
                    return (f"🛠️ DEFECTIVE BATCH! Supplier bankrupt. Lost {remove}x {g} (last lot).", False)
            return None

        def evt_customs_duty() -> Optional[tuple[str, bool]]:
            if not state.inventory:
                return None
            value = inv_total_value()
            if value <= 0:
                return None
            rate = random.uniform(0.05, 0.15)  # 5%–15% of inventory value
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
            return (f"🚔 STOLEN GOODS! Your last purchase was confiscated: lost {remove}x {g}.", False)

        def evt_cash_damage() -> Optional[tuple[str, bool]]:
            # Generic accident costing cash, scaled by current cash
            base = int(state.cash * random.uniform(0.01, 0.05))
            damage = max(50, min(2000, base))
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
            price = engine.asset_prices.get(sym, 0) or 0
            if qty <= 0 or price <= 0:
                return None
            # 0.5% – 2% of position value
            pct = random.uniform(0.005, 0.02)
            payout = max(1, int(qty * price * pct))
            # Prefer bank credit if bank exists
            bank_credit(payout, tx_type="interest", title=f"Dividend for {sym}")
            return (f"💸 DIVIDEND! {sym} paid you ${payout:,} (≈{pct*100:.1f}% of position) credited to bank.", True)

        def evt_lottery() -> Optional[tuple[str, bool]]:
            # Simulate 3/4/5/6 hits
            tier = random.choices([3, 4, 5, 6], weights=[50, 30, 15, 5], k=1)[0]
            if tier == 3:
                win = random.randint(200, 600)
            elif tier == 4:
                win = random.randint(700, 1500)
            elif tier == 5:
                win = random.randint(2000, 6000)
            else:  # 6
                win = random.randint(10000, 30000)
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
            pct = random.uniform(0.01, 0.05)
            amount = max(10, int(bal * pct))
            bank_credit(amount, tx_type="interest", title="Interest correction from bank")
            return (f"🏦 BANK CORRECTION! Extra interest ${amount:,} credited to your account.", True)

        def evt_promo_good() -> Optional[tuple[str, bool]]:
            # Promotion - price down 30%–60% for a random good (next prices)
            if not GOODS:
                return None
            good = random.choice(GOODS).name
            mult = random.uniform(0.4, 0.7)
            state.price_modifiers[good] = mult
            return (f"🏷️ PROMOTION! {good} will be cheaper today (−{int((1 - mult) * 100)}%).", True)

        def evt_oversupply() -> Optional[tuple[str, bool]]:
            # Very low price for random good
            if not GOODS:
                return None
            good = random.choice(GOODS).name
            mult = random.uniform(0.3, 0.6)
            state.price_modifiers[good] = mult
            return (f"📉 OVERSUPPLY! {good} prices plunge (−{int((1 - mult) * 100)}%).", True)

        def evt_shortage() -> Optional[tuple[str, bool]]:
            if not GOODS:
                return None
            good = random.choice(GOODS).name
            mult = random.uniform(1.8, 2.2)
            state.price_modifiers[good] = mult
            return (f"📈 SHORTAGE! {good} prices soar (≈×{mult:.1f}).", True)

        def evt_loyal_discount() -> Optional[tuple[str, bool]]:
            # Loyal customer special: 95% discount on a random good for today
            if not GOODS:
                return None
            good = random.choice(GOODS).name
            mult = 0.05  # 95% off
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

        events: List[_Evt] = [
            # Loss events
            _Evt(has_inventory, evt_robbery, 8),
            _Evt(has_inventory, evt_fire, 5),
            _Evt(has_inventory, evt_flood, 4),
            _Evt(has_any_purchase_with_inventory, evt_defective_batch, 5),
            _Evt(inv_value_positive, evt_customs_duty, 6),
            _Evt(has_last_buy_with_inventory, evt_stolen_last_buy, 5),
            _Evt(has_cash, evt_cash_damage, 4),
            # Gain events
            _Evt(holds_any_stock, evt_dividend, 6),
            _Evt(lambda: True, evt_lottery, 3),
            _Evt(bank_has_balance, evt_bank_correction, 4),
            _Evt(lambda: True, evt_promo_good, 5),
            _Evt(lambda: True, evt_oversupply, 4),
            _Evt(lambda: True, evt_shortage, 4),
            _Evt(lambda: True, evt_loyal_discount, 1),
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
