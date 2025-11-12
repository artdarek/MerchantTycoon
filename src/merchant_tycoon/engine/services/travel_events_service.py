import random
from typing import TYPE_CHECKING, List, Optional, Callable, Tuple

from merchant_tycoon.domain.model.bank_transaction import BankTransaction
from merchant_tycoon.domain.model.city import City
from merchant_tycoon.config import SETTINGS
from datetime import datetime

if TYPE_CHECKING:
    from merchant_tycoon.repositories import AssetsRepository, GoodsRepository


class TravelEventsService:
    """Weighted random travel events.

    Exposes a single method `trigger(engine)` that performs at most one event and
    returns a tuple (message, is_positive) or None if no event occurs.

    Notes:
    - Only goods/cash/bank and one-day price modifiers are affected by events.
    - Investments are safe; a positive dividend may be credited to bank.
    - This class requires repository instances for event generation.
    """

    def __init__(self, assets_repository: "AssetsRepository", goods_repository: "GoodsRepository"):
        """Initialize TravelEventsService with required repositories.

        Args:
            assets_repository: Repository for asset lookups in dividend events.
            goods_repository: Repository for goods lookups in event generation.
        """
        self.assets_repo = assets_repository
        self.goods_repo = goods_repository

    def trigger(self, state, prices: dict, asset_prices: dict, city: Optional[City] = None, bank_service=None, goods_service=None) -> List[Tuple[str, bool]]:
        """Trigger multiple weighted random travel events based on city configuration.

        Parameters:
            state: Game state object with inventory, cash, bank, etc.
            prices: dict of current goods prices {good_name: price}
            asset_prices: dict of asset prices {symbol: price}
            city: Optional City object with travel_events config (defaults to 0-2 for both)
            bank_service: optional bank service to credit amounts into bank history
            goods_service: optional goods service for loss accounting

        Returns:
            List of event tuples (message, is_positive). Empty list if no events occur.
        """
        # Overall chance that any event occurs this travel
        if random.random() >= float(SETTINGS.events.base_probability):
            return []
        prices = prices or {}

        def _all_goods_names() -> list[str]:
            try:
                return [g.name for g in self.goods_repo.get_all()]
            except Exception:
                return []

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
            # Apply loss via goods service (handles inventory and lots + loss accounting)
            try:
                if goods_service is not None:
                    goods_service.record_loss_fifo(good, lost)
                else:
                    state.inventory[good] = qty - lost
            except Exception:
                state.inventory[good] = max(0, qty - lost)
            if state.inventory.get(good, 0) <= 0:
                state.inventory.pop(good, None)
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
                try:
                    if goods_service is not None:
                        goods_service.record_loss_fifo(g, d)
                    else:
                        state.inventory[g] = have - d
                except Exception:
                    state.inventory[g] = max(0, have - d)
                to_destroy -= d
                destroyed.append(f"{d}x {g}")
                if state.inventory.get(g, 0) <= 0:
                    state.inventory.pop(g, None)
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
                try:
                    if goods_service is not None:
                        goods_service.record_loss_fifo(g, d)
                    else:
                        state.inventory[g] = have - d
                except Exception:
                    state.inventory[g] = max(0, have - d)
                to_destroy -= d
                destroyed.append(f"{d}x {g}")
                if state.inventory.get(g, 0) <= 0:
                    state.inventory.pop(g, None)
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
                    try:
                        if goods_service is not None:
                            goods_service.record_loss_from_last(g, remove)
                        else:
                            state.inventory[g] = max(0, qty - remove)
                    except Exception:
                        state.inventory[g] = max(0, qty - remove)
                    if state.inventory.get(g, 0) <= 0:
                        state.inventory.pop(g, None)
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
            try:
                if goods_service is not None:
                    goods_service.record_loss_from_last(g, remove)
                else:
                    state.inventory[g] = max(0, have - remove)
            except Exception:
                state.inventory[g] = max(0, have - remove)
            if state.inventory.get(g, 0) <= 0:
                state.inventory.pop(g, None)
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
            stock_symbols = self.assets_repo.get_stock_symbols()
            held_stocks = [sym for sym, qty in (state.portfolio or {}).items() if qty > 0 and sym in stock_symbols]
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
            goods = _all_goods_names()
            if not goods:
                return None
            good = random.choice(goods)
            lo, hi = SETTINGS.events.promo_multiplier
            mult = random.uniform(lo, hi)
            state.price_modifiers[good] = mult

            # Show price before and after promotion
            old_price = prices.get(good, 0)
            new_price = int(old_price * mult) if old_price > 0 else 0
            discount_pct = int((1 - mult) * 100)

            if old_price > 0 and new_price > 0:
                return (f"🏷️ PROMOTION! {good} price drops from ${old_price:,} to ${new_price:,} (−{discount_pct}%).", True)
            else:
                return (f"🏷️ PROMOTION! {good} will be cheaper today (−{discount_pct}%).", True)

        def evt_oversupply() -> Optional[tuple[str, bool]]:
            # Very low price for random good
            goods = _all_goods_names()
            if not goods:
                return None
            good = random.choice(goods)
            lo, hi = SETTINGS.events.oversupply_multiplier
            mult = random.uniform(lo, hi)
            state.price_modifiers[good] = mult

            # Show price before and after
            old_price = prices.get(good, 0)
            new_price = int(old_price * mult) if old_price > 0 else 0
            discount_pct = int((1 - mult) * 100)

            if old_price > 0 and new_price > 0:
                return (f"📉 OVERSUPPLY! {good} price crashes from ${old_price:,} to ${new_price:,} (−{discount_pct}%).", True)
            else:
                return (f"📉 OVERSUPPLY! {good} prices plunge (−{discount_pct}%).", True)

        def evt_shortage() -> Optional[tuple[str, bool]]:
            goods = _all_goods_names()
            if not goods:
                return None
            good = random.choice(goods)
            lo, hi = SETTINGS.events.shortage_multiplier
            mult = random.uniform(lo, hi)
            state.price_modifiers[good] = mult

            # Show price before and after
            old_price = prices.get(good, 0)
            new_price = int(old_price * mult) if old_price > 0 else 0

            if old_price > 0 and new_price > 0:
                return (f"📈 SHORTAGE! {good} price surges from ${old_price:,} to ${new_price:,} (≈×{mult:.1f}).", True)
            else:
                return (f"📈 SHORTAGE! {good} prices soar (≈×{mult:.1f}).", True)

        def evt_loyal_discount() -> Optional[tuple[str, bool]]:
            # Loyal customer special: 95% discount on a random good for today
            goods = _all_goods_names()
            if not goods:
                return None
            good = random.choice(goods)
            mult = SETTINGS.events.loyal_discount_multiplier
            state.price_modifiers[good] = mult

            # Show price before and after
            old_price = prices.get(good, 0)
            new_price = int(old_price * mult) if old_price > 0 else 0

            if old_price > 0 and new_price > 0:
                return (f"🤝 LOYAL CUSTOMER! 95% discount on {good}: ${old_price:,} → ${new_price:,} (today only)!", True)
            else:
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
            stock_symbols = self.assets_repo.get_stock_symbols()
            return any(qty > 0 and sym in stock_symbols for sym, qty in (state.portfolio or {}).items())

        def bank_has_balance() -> bool:
            try:
                return int(getattr(state.bank, 'balance', 0)) > 0
            except Exception:
                return False

        w = SETTINGS.events.weights

        # Separate events into loss and gain categories
        loss_events: List[_Evt] = [
            _Evt(has_inventory, evt_robbery, w.get("robbery", 8)),
            _Evt(has_inventory, evt_fire, w.get("fire", 5)),
            _Evt(has_inventory, evt_flood, w.get("flood", 4)),
            _Evt(has_any_purchase_with_inventory, evt_defective_batch, w.get("defective_batch", 5)),
            _Evt(inv_value_positive, evt_customs_duty, w.get("customs_duty", 6)),
            _Evt(has_last_buy_with_inventory, evt_stolen_last_buy, w.get("stolen_last_buy", 5)),
            _Evt(has_cash, evt_cash_damage, w.get("cash_damage", 4)),
        ]

        gain_events: List[_Evt] = [
            _Evt(holds_any_stock, evt_dividend, w.get("dividend", 6)),
            _Evt(lambda: True, evt_lottery, w.get("lottery", 3)),
            _Evt(bank_has_balance, evt_bank_correction, w.get("bank_correction", 4)),
            _Evt(lambda: True, evt_promo_good, w.get("promo", 5)),
            _Evt(lambda: True, evt_oversupply, w.get("oversupply", 4)),
            _Evt(lambda: True, evt_shortage, w.get("shortage", 4)),
            _Evt(lambda: True, evt_loyal_discount, w.get("loyal_discount", 1)),
        ]

        # Get city config (default to 0-2 for both if city not provided)
        if city and hasattr(city, 'travel_events'):
            cfg = city.travel_events
            loss_min, loss_max = cfg.loss_min, cfg.loss_max
            gain_min, gain_max = cfg.gain_min, cfg.gain_max
        else:
            loss_min, loss_max = 0, 2
            gain_min, gain_max = 0, 2

        # Helper to select weighted event without replacement
        def select_event(event_pool: List[_Evt], used_events: set) -> Optional[Tuple[str, bool]]:
            eligible = [e for e in event_pool if e.w > 0 and e.can() and e.apply not in used_events]
            if not eligible:
                return None
            total_w = sum(e.w for e in eligible)
            if total_w <= 0:
                return None
            pick = random.uniform(0, total_w)
            upto = 0.0
            chosen = eligible[-1]
            for e in eligible:
                upto += e.w
                if pick <= upto:
                    chosen = e
                    break
            result = chosen.apply()
            if result:
                used_events.add(chosen.apply)
            return result

        # Generate multiple events
        selected_events: List[Tuple[str, bool]] = []
        used_events: set = set()

        # Select loss events
        loss_count = random.randint(loss_min, loss_max)
        for _ in range(loss_count):
            result = select_event(loss_events, used_events)
            if result:
                selected_events.append(result)

        # Select gain events
        gain_count = random.randint(gain_min, gain_max)
        for _ in range(gain_count):
            result = select_event(gain_events, used_events)
            if result:
                selected_events.append(result)

        # Shuffle all events for variety
        random.shuffle(selected_events)
        return selected_events
