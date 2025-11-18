from textual.app import ComposeResult
from textual.widgets import Static, Label, Input, Button
from textual.containers import Horizontal, ScrollableContainer
from merchant_tycoon.engine.applets.wordle_applet import WordleApplet


class WordleGamePanel(Static):
    def __init__(self):
        super().__init__()
        self.service: WordleApplet | None = None

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
            # Make Play Again pastel orange (warning) and Restart destructive (error)
            yield Button("Play Again", id="wordle-restart", variant="warning", disabled=True)
            yield Button("Restart", id="wordle-reset", variant="error")
        # Stats panel below controls (content set in _update_stats)
        yield Label("", id="wordle-stats")

    def on_mount(self) -> None:
        # Bind service from engine and reset
        try:
            self.service = getattr(self.app.engine, "wordle_applet", None)
        except Exception:
            self.service = None
        self._reset_game()

    # --- game logic ---
    def _reset_game(self) -> None:
        if self.service is None:
            try:
                self.service = WordleApplet()
            except Exception:
                self.service = None
        if self.service:
            try:
                # Refresh settings in case they changed (optional)
                from merchant_tycoon.config import SETTINGS
                self.service.max_tries = int(getattr(SETTINGS.phone, 'wordle_max_tries', 10))
                self.service.validate_in_dictionary = bool(getattr(SETTINGS.phone, 'wordle_validate_in_dictionary', True))
            except Exception:
                pass
            self.service.reset()
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

    def _render_attempt(self, guess: str) -> Horizontal:
        """Render guess using Wordle two-pass rules for duplicates.

        Pass 1: mark greens and build remaining counts for secret.
        Pass 2: mark reds only up to remaining counts, else grey.
        """
        secret = (self.service.secret if self.service else "")[:5]
        guess = (guess or "")[:5]

        # Build counts of letters in secret
        counts: dict[str, int] = {}
        for s_ch in secret:
            counts[s_ch] = counts.get(s_ch, 0) + 1

        # First pass: mark correct and decrement counts
        marks = ["absent"] * 5
        for i in range(min(5, len(secret), len(guess))):
            if guess[i] == secret[i]:
                marks[i] = "correct"
                counts[guess[i]] -= 1

        # Second pass: mark present if available in remaining counts, else absent
        for i in range(min(5, len(secret), len(guess))):
            if marks[i] == "correct":
                continue
            ch = guess[i]
            if counts.get(ch, 0) > 0:
                marks[i] = "present"
                counts[ch] -= 1
            else:
                marks[i] = "absent"

        # Build UI boxes first, then construct row with children to avoid
        # mounting into an unmounted container which can raise MountError.
        boxes: list[Static] = []
        for i, ch in enumerate(guess):
            cls = marks[i] if i < len(marks) else "absent"
            boxes.append(Static(ch.upper(), classes=f"wordle-box {cls}"))
        return Horizontal(*boxes, classes="wordle-row")

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
            attempts = len(self.service.attempts) if self.service else 0
            max_tries = getattr(self.service, 'max_tries', getattr(self, 'max_tries', 10)) if self.service else getattr(self, 'max_tries', 10)
            stats.update(f"Number of tries: {attempts} out of {max_tries}")
        except Exception:
            pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "wordle-guess":
            inp = self.query_one("#wordle-input", Input)
            # Validate via service
            if not self.service:
                self.query_one("#wordle-message", Label).update("Service unavailable")
                return
            ok, val = self.service.validate_guess(inp.value)
            if not ok:
                self.query_one("#wordle-message", Label).update(val)
                return
            # Apply guess and render
            result = self.service.make_guess(val)
            self._append_attempt(val)
            if result.is_correct:
                self.query_one("#wordle-message", Label).update("🎉 Correct! You guessed the word!")
                inp.disabled = True
                self.query_one("#wordle-guess", Button).disabled = True
                self.query_one("#wordle-restart", Button).disabled = False
            else:
                # Check attempts cap
                if result.attempts_used >= getattr(self.service, 'max_tries', 10):
                    self.query_one("#wordle-message", Label).update(result.message or "No more tries.")
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
