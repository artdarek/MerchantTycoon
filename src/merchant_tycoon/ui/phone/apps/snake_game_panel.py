from __future__ import annotations

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widgets import Static, Label, Button
from textual.containers import Horizontal
from merchant_tycoon.engine.applets.snake_service import SnakeService


class SnakeGamePanel(Static):
    """Very simple Snake game for the aiPhone screen.

    - Arrow keys control movement
    - Eat food to grow and increase score
    - Hitting walls or yourself ends the game
    """

    # Board size tuned to fit nicely in phone screen
    width: int = 24
    height: int = 14
    cell_x: int = 2  # how many characters per cell horizontally

    # Reactive state for auto-refreshing UI
    running: bool = reactive(False)
    game_over: bool = reactive(False)

    def __init__(self):
        super().__init__()
        self._timer = None
        self.service: SnakeService | None = None

    def compose(self) -> ComposeResult:
        yield Label("🐍 SNAKE", classes="panel-title")
        # Score line above the gameplay area, right-aligned via CSS
        yield Label("", id="snake-score")
        yield Static("", id="snake-board")
        with Horizontal(id="snake-controls"):
            yield Button("Start", id="snake-start", variant="success")
            yield Button("Pause", id="snake-pause", variant="warning")
            yield Button("Restart", id="snake-restart", variant="error")

    def on_mount(self) -> None:
        # Bind service from engine
        try:
            self.service = getattr(self.app.engine, 'snake_service', None)
        except Exception:
            self.service = None
        self._update_board_dimensions()
        self._new_game()
        # Start paused; user can press Start
        self.running = False

    # --- Game lifecycle ---
    def _new_game(self) -> None:
        if self.service is None:
            # create a local service as fallback
            self.service = SnakeService(width=self.width, height=self.height)
        else:
            self.service.resize(self.width, self.height)
        self.service.new_game()
        # sync reactive flags for UI
        self.game_over = False
        self._render_board()

    def _update_board_dimensions(self) -> None:
        """Resize the logical board to fit the available widget size."""
        try:
            board = self.query_one("#snake-board", Static)
            w_chars = max(8, int(getattr(board.size, "width", 0) or 0))
            h_chars = max(6, int(getattr(board.size, "height", 0) or 0))
        except Exception:
            w_chars, h_chars = self.width * self.cell_x, self.height

        new_w = max(12, min(80, w_chars // self.cell_x))
        new_h = max(8, min(40, h_chars))
        if new_w != self.width or new_h != self.height:
            self.width, self.height = new_w, new_h
            if self.service:
                self.service.resize(self.width, self.height)
            self._render_board()

    # removed: spawning handled by service

    # removed: spawning handled by service

    # removed: spawning handled by service

    def _tick(self) -> None:
        if not self.running or self.game_over:
            return
        if self.service:
            self.service.tick()
            self.game_over = bool(self.service.game_over)
            try:
                if self.service.consume_ui_dirty() and hasattr(self.app, 'refresh_all'):
                    self.app.refresh_all()
            except Exception:
                pass
        self._render_board()

    # removed: single-step logic handled by service

    # removed: game over handled inside service, UI reflects via flags/label

    def _render_board(self) -> None:
        svc = self.service
        # Build grid
        grid = [[" "] * self.width for _ in range(self.height)]
        # Draw food
        if svc and svc.food and 0 <= svc.food.x < self.width and 0 <= svc.food.y < self.height:
            grid[svc.food.y][svc.food.x] = "◆"
        # Draw snake
        if svc:
            for i, seg in enumerate(svc.snake):
                ch = "█" if i == 0 else "■"
                grid[seg.y][seg.x] = ch
        # Draw bonus ($)
        if svc and svc.bonus and 0 <= svc.bonus.x < self.width and 0 <= svc.bonus.y < self.height:
            grid[svc.bonus.y][svc.bonus.x] = "$"
        # Draw super bonus (B)
        if svc and svc.super_bonus and 0 <= svc.super_bonus.x < self.width and 0 <= svc.super_bonus.y < self.height:
            grid[svc.super_bonus.y][svc.super_bonus.x] = "B"
        # Convert to text rows; double-width cells for better proportions
        lines = ["".join(cell * self.cell_x for cell in row) for row in grid]
        board_text = "\n".join(lines)
        try:
            from merchant_tycoon.config import SETTINGS
            bonus_amt = int(getattr(SETTINGS.phone, 'snake_bonus_amount', 100))
            super_amt = int(getattr(SETTINGS.phone, 'snake_super_bonus_amount', 1000))
        except Exception:
            bonus_amt, super_amt = 100, 1000
        try:
            self.query_one("#snake-board", Static).update(board_text)
            # Score line or game over message
            s = self.service
            if s and s.game_over:
                self.query_one("#snake-score", Label).update(f"Game Over! Final score: {s.score}")
            else:
                sc = s.score if s else 0
                rw = s.rewards if s else 0
                srw = s.super_rewards if s else 0
                self.query_one("#snake-score", Label).update(
                    f"Score: {sc} • Bonus: {rw} x ${bonus_amt} • Super bonus: {srw} x ${super_amt}"
                )
        except Exception:
            pass

    # --- Controls ---
    def _ensure_timer(self) -> None:
        if self._timer is None:
            # Tick ~6 times per second
            self._timer = self.set_interval(0.16, self._tick, pause=not self.running)
        else:
            # Keep timer pause state in sync
            try:
                if self.running:
                    self._timer.resume()
                else:
                    self._timer.pause()
            except Exception:
                pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "snake-start":
            if self.game_over:
                self._new_game()
            self.running = True
            self._ensure_timer()
        elif event.button.id == "snake-pause":
            self.running = False
            self._ensure_timer()
        elif event.button.id == "snake-restart":
            self.running = False
            self._ensure_timer()
            self._new_game()

    def on_key(self, event) -> None:  # type: ignore[override]
        # Arrow key handling; disallow direct opposite turns
        key = str(getattr(event, "key", "")).lower()

        # Shortcuts: S-start, P-pause, R-restart, Space-toggle pause
        if key == "s":
            if self.game_over:
                self._new_game()
            self.running = True
            self._ensure_timer()
            return
        if key == "p":
            self.running = False
            self._ensure_timer()
            return
        if key == "r":
            self.running = False
            self._ensure_timer()
            self._new_game()
            return
        if key == "space":
            if not self.game_over:
                self.running = not self.running
                self._ensure_timer()
            return
        if key in ("left", "h"):
            if self.service:
                self.service.turn(-1, 0)
        elif key in ("right", "l"):
            if self.service:
                self.service.turn(1, 0)
        elif key in ("up", "k"):
            if self.service:
                self.service.turn(0, -1)
        elif key in ("down", "j"):
            if self.service:
                self.service.turn(0, 1)
        # If paused (but not game over), allow arrow to start the game for convenience
        if not self.running and not self.game_over and key in ("left", "right", "up", "down", "h", "j", "k", "l"):
            self.running = True
            self._ensure_timer()

    def on_resize(self, _event) -> None:  # type: ignore[override]
        # Recalculate board size whenever container resizes
        self._update_board_dimensions()
