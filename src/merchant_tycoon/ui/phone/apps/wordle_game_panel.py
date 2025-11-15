from textual.app import ComposeResult
from textual.widgets import Static, Label, Input, Button
from textual.containers import Horizontal, ScrollableContainer


class WordleGamePanel(Static):
    def __init__(self):
        super().__init__()
        self.secret_word: str = ""
        self.attempts: list[str] = []

    def compose(self) -> ComposeResult:
        # Title at top
        yield Label("🧩 WORDLE GAME", classes="panel-title")
        # Attempts list fills available space
        yield ScrollableContainer(id="wordle-attempts")
        # Message (validation / success info)
        yield Label("", id="wordle-message")
        # Controls at the bottom (input + Guess on the right)
        with Horizontal(id="wordle-controls"):
            yield Input(placeholder="enter 5-letter word", id="wordle-input")
            yield Button("Guess", id="wordle-guess", variant="success")
            yield Button("Play Again", id="wordle-restart", variant="default", disabled=True)
            yield Button("Restart", id="wordle-reset", variant="default")
        # Stats panel below controls (content set in _update_stats)
        yield Label("", id="wordle-stats")

    def on_mount(self) -> None:
        self._reset_game()

    # --- game logic ---
    def _reset_game(self) -> None:
        try:
            self.secret_word = self.app.engine.wordle_repo.get_random()
        except Exception:
            self.secret_word = "apple"
        self.attempts = []
        # Load max tries from settings (default 10)
        try:
            from merchant_tycoon.config import SETTINGS
            self.max_tries = int(getattr(SETTINGS.phone, 'wordle_max_tries', 10))
        except Exception:
            self.max_tries = 10
        try:
            self.query_one("#wordle-input", Input).value = ""
            self.query_one("#wordle-input", Input).disabled = False
            self.query_one("#wordle-guess", Button).disabled = False
            self.query_one("#wordle-restart", Button).disabled = True
            self.query_one("#wordle-message", Label).update("")
            cont = self.query_one("#wordle-attempts", ScrollableContainer)
        except Exception:
            return
        try:
            cont.remove_children()
        except Exception:
            pass
        # Update stats
        self._update_stats()

    def _validate_guess(self, word: str) -> tuple[bool, str]:
        w = (word or "").strip().lower()
        if len(w) != 5 or not w.isalpha():
            return False, "Word must be exactly 5 letters (a-z)!"
        # Optionally validate against dictionary
        try:
            from merchant_tycoon.config import SETTINGS
            validate = bool(getattr(SETTINGS.phone, 'wordle_validate_in_dictionary', True))
        except Exception:
            validate = True
        if validate:
            try:
                words = set(self.app.engine.wordle_repo.get_all())
            except Exception:
                words = set()
            if w not in words:
                return False, "Word not in dictionary!"
        return True, w

    def _render_attempt(self, guess: str) -> Horizontal:
        # Build a row of 5 boxes with color coding
        row = Horizontal(classes="wordle-row")
        secret = self.secret_word
        for i, ch in enumerate(guess):
            cls = "absent"
            if i < len(secret) and ch == secret[i]:
                cls = "correct"
            elif ch in secret:
                cls = "present"
            box = Static(ch.upper(), classes=f"wordle-box {cls}")
            row.mount(box)
        return row

    def _append_attempt(self, guess: str) -> None:
        try:
            cont = self.query_one("#wordle-attempts", ScrollableContainer)
        except Exception:
            return
        row = self._render_attempt(guess)
        cont.mount(row)
        try:
            cont.scroll_end(animate=False)
        except Exception:
            pass
        self._update_stats()

    def _update_stats(self) -> None:
        try:
            stats = self.query_one("#wordle-stats", Label)
            stats.update(f"Number of tries: {len(self.attempts)} out of {getattr(self, 'max_tries', 10)}")
        except Exception:
            pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "wordle-guess":
            inp = self.query_one("#wordle-input", Input)
            ok, val = self._validate_guess(inp.value)
            if not ok:
                self.query_one("#wordle-message", Label).update(val)
                return
            # It's valid
            word = val
            self.attempts.append(word)
            self._append_attempt(word)
            if word == self.secret_word:
                self.query_one("#wordle-message", Label).update("🎉 Correct! You guessed the word!")
                inp.disabled = True
                self.query_one("#wordle-guess", Button).disabled = True
                self.query_one("#wordle-restart", Button).disabled = False
            else:
                # Check attempts cap
                if len(self.attempts) >= getattr(self, 'max_tries', 10):
                    self.query_one("#wordle-message", Label).update(f"No more tries. The word was: {self.secret_word.upper()}")
                    inp.disabled = True
                    self.query_one("#wordle-guess", Button).disabled = True
                    self.query_one("#wordle-restart", Button).disabled = False
                    return
                # Clear input for next attempt
                inp.value = ""
                self.query_one("#wordle-message", Label).update("")
        elif event.button.id == "wordle-restart":
            self._reset_game()
        elif event.button.id == "wordle-reset":
            # Always allow manual restart
            self._reset_game()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        # Enter on input triggers Guess
        try:
            btn = self.query_one("#wordle-guess", Button)
            if not btn.disabled:
                self.on_button_pressed(Button.Pressed(btn))
        except Exception:
            pass
