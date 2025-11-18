import random
from textual.app import ComposeResult
from textual.widgets import Static, Label, Input, Button
from textual.containers import Horizontal, ScrollableContainer
from merchant_tycoon.config import SETTINGS
from merchant_tycoon.engine.applets.close_ai_applet import CloseAIApplet


class CloseAIChatPanel(Static):
    def __init__(self):
        super().__init__()
        self.service: CloseAIApplet | None = None

    def compose(self) -> ComposeResult:
        yield Label("💬 CloseAI Chat", classes="panel-title")
        yield ScrollableContainer(id="closeai-chat")
        with Horizontal(id="closeai-controls"):
            yield Input(placeholder="Type a message...", id="closeai-input")
            yield Button("Send", id="closeai-send", variant="success")

    def on_mount(self) -> None:
        # Bind service and render any existing session history
        try:
            self.service: CloseAIApplet | None = getattr(self.app.engine, 'closeai_applet', None)
        except Exception:
            self.service = None
        try:
            history = list(self.service.history) if self.service else []
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
            # Use service to process chat and apply effects
            self._append_bubble("user", msg)
            reply = ""
            try:
                svc: CloseAIApplet | None = getattr(self, 'service', None)
                if svc is None:
                    # fallback: use engine service if available
                    svc = getattr(self.app.engine, 'closeai_applet', None)
                    self.service = svc
                if svc is not None:
                    reply = svc.process_message(msg)
                    # If chat applied any game effects, refresh global UI state
                    try:
                        if svc.consume_ui_dirty() and hasattr(self.app, 'refresh_all'):
                            self.app.refresh_all()
                    except Exception:
                        pass
                else:
                    # last resort: canned reply
                    pool = list(getattr(SETTINGS.phone, 'close_ai_responses', ()))
                    reply = random.choice(pool) if pool else "Beep boop. Proceeding confidently with uncertainty."
            except Exception:
                try:
                    pool = list(getattr(SETTINGS.phone, 'close_ai_responses', ()))
                    reply = random.choice(pool) if pool else "Beep boop. Proceeding confidently with uncertainty."
                except Exception:
                    reply = "Beep boop. Proceeding confidently with uncertainty."
            self._append_bubble("ai", reply)
            inp.value = ""
            self._scroll_end()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        # Pressing Enter in the input sends a message
        try:
            btn = self.query_one("#closeai-send", Button)
            self.on_button_pressed(Button.Pressed(btn))
        except Exception:
            pass
