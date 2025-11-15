import random
from textual.app import ComposeResult
from textual.widgets import Static, Label, Input, Button
from textual.containers import Horizontal, ScrollableContainer
from merchant_tycoon.config import SETTINGS


class CloseAIChatPanel(Static):
    def __init__(self):
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Label("💬 Close AI", classes="panel-title")
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
            # AI reply
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
