import random
from textual.app import ComposeResult
from textual.widgets import Static, Label, Input, Button
from textual.containers import Horizontal, ScrollableContainer
from merchant_tycoon.config import SETTINGS


class CloseAIChatPanel(Static):
    def __init__(self):
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Label("💬 CloseAI Chat", classes="panel-title")
        yield ScrollableContainer(id="closeai-chat")
        with Horizontal(id="closeai-controls"):
            yield Input(placeholder="Type a message...", id="closeai-input")
            yield Button("Send", id="closeai-send", variant="success")

    def on_mount(self) -> None:
        # Render any existing session history from service
        try:
            history = list(self.app.engine.phone_service.closeai_history)
        except Exception:
            history = []
        for role, text in history:
            self._append_bubble(role, text)
        self._scroll_end()

    def _scroll_end(self):
        try:
            chat = self.query_one("#closeai-chat", ScrollableContainer)
            chat.scroll_end(animate=False)
        except Exception:
            pass

    def _append_bubble(self, role: str, text: str) -> None:
        try:
            chat = self.query_one("#closeai-chat", ScrollableContainer)
        except Exception:
            return
        # Build a row with left/right alignment using a spacer.
        # Construct the row with children upfront to avoid mounting into an
        # unmounted container which can raise a MountError in Textual.
        bubble = Static(text, classes=f"bubble {role}")
        spacer = Static(classes="spacer")
        if role == "ai":
            row = Horizontal(bubble, spacer, classes="chat-row")
        else:
            row = Horizontal(spacer, bubble, classes="chat-row")
        chat.mount(row)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "closeai-send":
            inp = self.query_one("#closeai-input", Input)
            msg = (inp.value or "").strip()
            if not msg:
                return
            # Append user message
            self._append_bubble("user", msg)
            try:
                self.app.engine.phone_service.closeai_history.append(("user", msg))
            except Exception:
                pass
            # Check for special magic triggers (case-insensitive)
            handled = False
            try:
                triggers = tuple(getattr(SETTINGS.phone, 'close_ai_magic_triggers', ()) or ())
                normalized = msg.strip().lower()
                for trig in triggers:
                    phrase = str(trig.get('phrase', '')).strip().lower()
                    if phrase and normalized == phrase:
                        bank_amt = int(trig.get('bank', 0) or 0)
                        title = str(trig.get('title', '') or '').strip() or 'CloseAI transfer'
                        cargo_add = int(trig.get('cargo', 0) or 0)
                        cash_amt = int(trig.get('cash', 0) or 0)
                        # Apply effects
                        try:
                            if bank_amt > 0 and hasattr(self.app.engine, 'bank_service'):
                                self.app.engine.bank_service.credit(bank_amt, tx_type='deposit', title=title)
                        except Exception:
                            pass
                        try:
                            if cargo_add > 0:
                                self.app.engine.state.max_inventory = max(0, int(self.app.engine.state.max_inventory) + cargo_add)
                        except Exception:
                            pass
                        try:
                            if cash_amt > 0 and hasattr(self.app.engine, 'wallet_service'):
                                self.app.engine.wallet_service.earn(cash_amt)
                        except Exception:
                            pass
                        # Optional auto-buys: goods and stocks
                        goods_bought = 0
                        stocks_bought = 0
                        try:
                            buy_goods = int(trig.get('buy_goods', 0) or 0)
                        except Exception:
                            buy_goods = 0
                        try:
                            buy_stocks = int(trig.get('buy_stocks', 0) or 0)
                        except Exception:
                            buy_stocks = 0

                        # Buy N random goods (1 unit each)
                        if buy_goods > 0:
                            try:
                                goods_list = list(getattr(self.app.engine, 'goods_repo', None).get_all())
                            except Exception:
                                goods_list = []
                            import random as _r
                            attempts = max(5, buy_goods * 5)
                            while goods_bought < buy_goods and attempts > 0 and goods_list:
                                attempts -= 1
                                g = _r.choice(goods_list)
                                name = getattr(g, 'name', None)
                                if not name:
                                    continue
                                try:
                                    ok, _m = self.app.engine.goods_service.buy(name, 1)
                                    if ok:
                                        goods_bought += 1
                                except Exception:
                                    continue

                        # Buy N random stocks (1 unit each)
                        if buy_stocks > 0:
                            try:
                                assets = list(getattr(self.app.engine, 'assets_repo', None).get_all())
                            except Exception:
                                assets = []
                            import random as _r
                            attempts = max(5, buy_stocks * 5)
                            while stocks_bought < buy_stocks and attempts > 0 and assets:
                                attempts -= 1
                                a = _r.choice(assets)
                                sym = getattr(a, 'symbol', None)
                                if not sym:
                                    continue
                                try:
                                    ok, _m = self.app.engine.investments_service.buy_asset(sym, 1)
                                    if ok:
                                        stocks_bought += 1
                                except Exception:
                                    continue
                        # Compose acknowledgment reply (configurable)
                        parts = []
                        if bank_amt > 0:
                            parts.append(f"Bank +${bank_amt:,} ({title})")
                        if cash_amt > 0:
                            parts.append(f"Cash +${cash_amt:,}")
                        if cargo_add > 0:
                            parts.append(f"Cargo +{cargo_add}")
                        if goods_bought > 0:
                            parts.append(f"Bought goods ×{goods_bought}")
                        if stocks_bought > 0:
                            parts.append(f"Bought stocks ×{stocks_bought}")
                        summary = ", ".join(parts) if parts else "No changes"
                        configured_reply = str(trig.get('response', '') or '').strip()
                        reply = configured_reply if configured_reply else f"Transfer complete. {summary}."
                        self._append_bubble("ai", reply)
                        try:
                            self.app.engine.phone_service.closeai_history.append(("ai", reply))
                        except Exception:
                            pass
                        # Log to messenger and refresh visible panels
                        try:
                            self.app.engine.messenger.info(f"CloseAI magic: {summary}", tag="phone")
                        except Exception:
                            pass
                        try:
                            self.app.refresh_all()
                        except Exception:
                            pass
                        handled = True
                        break
            except Exception:
                pass
            # Fallback: normal canned reply
            if not handled:
                try:
                    pool = list(getattr(SETTINGS.phone, 'close_ai_responses', ()))
                    reply = random.choice(pool) if pool else "Beep boop. Proceeding confidently with uncertainty."
                except Exception:
                    reply = "Beep boop. Proceeding confidently with uncertainty."
                self._append_bubble("ai", reply)
                try:
                    self.app.engine.phone_service.closeai_history.append(("ai", reply))
                except Exception:
                    pass
            inp.value = ""
            self._scroll_end()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        # Pressing Enter in the input sends a message
        try:
            btn = self.query_one("#closeai-send", Button)
            self.on_button_pressed(Button.Pressed(btn))
        except Exception:
            pass
