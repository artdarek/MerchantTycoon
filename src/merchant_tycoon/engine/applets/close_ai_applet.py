from __future__ import annotations

import random
from typing import List, Optional, Sequence, Tuple


class CloseAIApplet:
    """Chat logic for CloseAI app (triggers, canned replies, history).

    Applies in-game effects via injected services (bank, wallet, goods, investments, messenger).
    Keeps chat history as a list[(role, text)], typically shared with PhoneService.
    """

    def __init__(
        self,
        *,
        settings: object,
        history: Optional[List[Tuple[str, str]]] = None,
        bank_service: Optional[object] = None,
        wallet_service: Optional[object] = None,
        goods_service: Optional[object] = None,
        investments_service: Optional[object] = None,
        messenger: Optional[object] = None,
        assets_repo: Optional[object] = None,
        goods_repo: Optional[object] = None,
    ) -> None:
        self._settings = settings
        self._history: List[Tuple[str, str]] = history if history is not None else []
        self.bank_service = bank_service
        self.wallet_service = wallet_service
        self.goods_service = goods_service
        self.investments_service = investments_service
        self.messenger = messenger
        self.assets_repo = assets_repo
        self.goods_repo = goods_repo
        self._ui_dirty: bool = False

    # ----- History API -----
    @property
    def history(self) -> Sequence[Tuple[str, str]]:
        return tuple(self._history)

    # ----- Chat -----
    def process_message(self, msg: str) -> str:
        text = (msg or "").strip()
        if not text:
            return ""
        self._history.append(("user", text))

        # Try magic triggers from settings
        reply: Optional[str] = None
        summary_parts: List[str] = []
        try:
            phone_cfg = getattr(self._settings, 'phone', None)
            triggers = tuple(getattr(phone_cfg, 'close_ai_magic_triggers', ()) or ())
            normalized = text.lower()
        except Exception:
            triggers = ()
            normalized = text.lower()
        handled = False
        for trig in triggers:
            try:
                phrases_val = trig.get('phrase', '')
                if isinstance(phrases_val, (list, tuple)):
                    phrases = [str(p).strip().lower() for p in phrases_val if str(p).strip()]
                else:
                    one = str(phrases_val or '').strip()
                    phrases = [one.lower()] if one else []
                if not phrases or normalized not in phrases:
                    continue

                bank_amt = int(trig.get('bank', 0) or 0)
                title = str(trig.get('title', '') or '').strip() or 'CloseAI transfer'
                cargo_add = int(trig.get('cargo', 0) or 0)
                cash_amt = int(trig.get('cash', 0) or 0)
                # Apply effects
                if bank_amt > 0 and self.bank_service is not None:
                    try:
                        self.bank_service.credit(bank_amt, tx_type='deposit', title=title)
                        summary_parts.append(f"Bank +${bank_amt:,} ({title})")
                        self._ui_dirty = True
                    except Exception:
                        pass
                if cargo_add > 0:
                    try:
                        # Goods capacity lives on state via goods_service or attached state
                        if hasattr(self.goods_service, 'state') and hasattr(self.goods_service.state, 'max_inventory'):
                            self.goods_service.state.max_inventory = max(0, int(self.goods_service.state.max_inventory) + cargo_add)
                            summary_parts.append(f"Cargo +{cargo_add}")
                            self._ui_dirty = True
                    except Exception:
                        pass
                if cash_amt > 0 and self.wallet_service is not None:
                    try:
                        self.wallet_service.earn(cash_amt)
                        summary_parts.append(f"Cash +${cash_amt:,}")
                        self._ui_dirty = True
                    except Exception:
                        pass

                # Bulk ops configuration
                goods_granted = 0
                stocks_granted = 0
                goods_bought = 0
                stocks_bought = 0
                try:
                    grant_goods = int(trig.get('grant_goods', 0) or 0)
                except Exception:
                    grant_goods = 0
                try:
                    grant_stocks = int(trig.get('grant_stocks', 0) or 0)
                    buy_goods = int(trig.get('buy_goods', 0) or 0)
                    buy_stocks = int(trig.get('buy_stocks', 0) or 0)
                except Exception:
                    grant_stocks = 0
                    buy_goods = 0
                    buy_stocks = 0
                try:
                    grant_goods_size = max(1, int(trig.get('grant_goods_size', 1) or 1))
                    buy_goods_size = max(1, int(trig.get('buy_goods_size', 1) or 1))
                except Exception:
                    grant_goods_size = 1
                    buy_goods_size = 1
                try:
                    grant_stocks_size = max(1, int(trig.get('grant_stocks_size', 1) or 1))
                    buy_stocks_size = max(1, int(trig.get('buy_stocks_size', 1) or 1))
                except Exception:
                    grant_stocks_size = 1
                    buy_stocks_size = 1

                # Grant random goods
                if grant_goods > 0 and self.goods_repo is not None and self.goods_service is not None:
                    try:
                        goods_list = list(self.goods_repo.get_all())
                    except Exception:
                        goods_list = []
                    attempts = max(5, grant_goods * 5)
                    while goods_granted < grant_goods and attempts > 0 and goods_list:
                        attempts -= 1
                        g = random.choice(goods_list)
                        name = getattr(g, 'name', None)
                        if not name:
                            continue
                        try:
                            ok, _ = self.goods_service.grant(name, grant_goods_size)
                            if ok:
                                goods_granted += 1
                                self._ui_dirty = True
                        except Exception:
                            continue

                # Buy random goods
                if buy_goods > 0 and self.goods_repo is not None and self.goods_service is not None:
                    try:
                        goods_list = list(self.goods_repo.get_all())
                    except Exception:
                        goods_list = []
                    attempts = max(5, buy_goods * 5)
                    while goods_bought < buy_goods and attempts > 0 and goods_list:
                        attempts -= 1
                        g = random.choice(goods_list)
                        name = getattr(g, 'name', None)
                        if not name:
                            continue
                        try:
                            ok, _ = self.goods_service.buy(name, buy_goods_size)
                            if ok:
                                goods_bought += 1
                                self._ui_dirty = True
                        except Exception:
                            continue

                # Grant random stocks
                if grant_stocks > 0 and self.assets_repo is not None and self.investments_service is not None:
                    try:
                        assets = list(self.assets_repo.get_all())
                    except Exception:
                        assets = []
                    attempts = max(5, grant_stocks * 5)
                    while stocks_granted < grant_stocks and attempts > 0 and assets:
                        attempts -= 1
                        a = random.choice(assets)
                        sym = getattr(a, 'symbol', None)
                        if not sym:
                            continue
                        try:
                            ok, _ = self.investments_service.grant_asset(sym, grant_stocks_size)
                            if ok:
                                stocks_granted += 1
                                self._ui_dirty = True
                        except Exception:
                            continue

                # Buy random stocks
                if buy_stocks > 0 and self.assets_repo is not None and self.investments_service is not None:
                    try:
                        assets = list(self.assets_repo.get_all())
                    except Exception:
                        assets = []
                    attempts = max(5, buy_stocks * 5)
                    while stocks_bought < buy_stocks and attempts > 0 and assets:
                        attempts -= 1
                        a = random.choice(assets)
                        sym = getattr(a, 'symbol', None)
                        if not sym:
                            continue
                        try:
                            ok, _ = self.investments_service.buy_asset(sym, buy_stocks_size)
                            if ok:
                                stocks_bought += 1
                                self._ui_dirty = True
                        except Exception:
                            continue

                if goods_granted > 0:
                    summary_parts.append(f"Granted goods ×{goods_granted}")
                if stocks_granted > 0:
                    summary_parts.append(f"Granted stocks ×{stocks_granted}")
                if goods_bought > 0:
                    summary_parts.append(f"Bought goods ×{goods_bought}")
                if stocks_bought > 0:
                    summary_parts.append(f"Bought stocks ×{stocks_bought}")

                configured_reply = str(trig.get('response', '') or '').strip()
                summary = ", ".join(summary_parts) if summary_parts else "No changes"
                reply = configured_reply if configured_reply else f"Transfer complete. {summary}."
                self._history.append(("ai", reply))
                try:
                    if self.messenger:
                        self.messenger.info(f"CloseAI magic: {summary}", tag="phone")
                except Exception:
                    pass
                handled = True
                break
            except Exception:
                # robust to partial config / service failures
                continue

        # Fallback canned reply
        if not handled:
            try:
                phone_cfg = getattr(self._settings, 'phone', None)
                pool = list(getattr(phone_cfg, 'close_ai_responses', ()))
                reply = random.choice(pool) if pool else "Beep boop. Proceeding confidently with uncertainty."
            except Exception:
                reply = "Beep boop. Proceeding confidently with uncertainty."
            self._history.append(("ai", reply))

        return self._history[-1][1] if self._history else ""

    # ----- UI Sync -----
    def consume_ui_dirty(self) -> bool:
        dirty = self._ui_dirty
        self._ui_dirty = False
        return dirty
