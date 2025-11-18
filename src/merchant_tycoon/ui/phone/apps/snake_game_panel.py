from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, List

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static, Label, Button
from textual.containers import Horizontal


@dataclass
class Point:
    x: int
    y: int


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
    score: int = reactive(0)

    def __init__(self):
        super().__init__()
        self.snake: List[Point] = []  # head is first element
        self.dir: Tuple[int, int] = (1, 0)  # dx, dy (start moving right)
        self.food: Point | None = None
        self._timer = None

    def compose(self) -> ComposeResult:
        yield Label("🐍 SNAKE", classes="panel-title")
        yield Static("", id="snake-board")
        with Horizontal(id="snake-controls"):
            yield Button("Start", id="snake-start", variant="success")
            yield Button("Pause", id="snake-pause")
            yield Button("Restart", id="snake-restart", variant="warning")
        yield Label("Score: 0", id="snake-score")

    def on_mount(self) -> None:
        # Compute initial board size from allocated space, then start a new game
        self._update_board_dimensions()
        self._new_game()
        # Start paused; user can press Start
        self.running = False

    # --- Game lifecycle ---
    def _new_game(self) -> None:
        self.score = 0
        # Ensure board fits current panel
        self._update_board_dimensions()
        midx, midy = self.width // 2, self.height // 2
        self.snake = [Point(midx, midy), Point(midx - 1, midy)]
        self.dir = (1, 0)
        self._spawn_food()
        self._render_board()

    def _update_board_dimensions(self) -> None:
        """Resize the logical board to fit the available widget size."""
        try:
            board = self.query_one("#snake-board", Static)
            w_chars = max(8, int(getattr(board.size, "width", 0) or 0))
            h_chars = max(6, int(getattr(board.size, "height", 0) or 0))
        except Exception:
            # Fallback to defaults if size not yet available
            w_chars, h_chars = self.width * self.cell_x, self.height

        # Convert character space to cell counts; keep sane bounds
        new_w = max(12, min(80, w_chars // self.cell_x))
        new_h = max(8, min(40, h_chars))

        if new_w != self.width or new_h != self.height:
            self.width, self.height = new_w, new_h
            # If current snake no longer fits, restart to avoid invalid state
            if any(p.x >= self.width or p.y >= self.height or p.x < 0 or p.y < 0 for p in self.snake):
                self._new_game()
            else:
                self._render_board()

    def _spawn_food(self) -> None:
        import random

        taken = {(p.x, p.y) for p in self.snake}
        while True:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if (x, y) not in taken:
                self.food = Point(x, y)
                return

    def _tick(self) -> None:
        if not self.running:
            return
        # Compute next head
        dx, dy = self.dir
        head = self.snake[0]
        nx, ny = head.x + dx, head.y + dy

        # Check collisions
        if nx < 0 or ny < 0 or nx >= self.width or ny >= self.height:
            self._game_over()
            return
        if any(seg.x == nx and seg.y == ny for seg in self.snake):
            self._game_over()
            return

        # Move
        new_head = Point(nx, ny)
        self.snake.insert(0, new_head)

        # Eat?
        if self.food and self.food.x == nx and self.food.y == ny:
            self.score += 1
            self._spawn_food()
        else:
            # remove tail
            self.snake.pop()

        self._render_board()

    def _game_over(self) -> None:
        self.running = False
        if self._timer:
            try:
                self._timer.pause()
            except Exception:
                pass
        try:
            score_lbl = self.query_one("#snake-score", Label)
            score_lbl.update(f"Game Over! Final score: {self.score}")
        except Exception:
            pass

    def _render_board(self) -> None:
        # Build grid
        grid = [[" "] * self.width for _ in range(self.height)]
        # Draw food
        if self.food:
            grid[self.food.y][self.food.x] = "◆"
        # Draw snake
        for i, seg in enumerate(self.snake):
            ch = "█" if i == 0 else "■"
            grid[seg.y][seg.x] = ch
        # Convert to text rows; double-width cells for better proportions
        lines = ["".join(cell * self.cell_x for cell in row) for row in grid]
        board_text = "\n".join(lines)
        try:
            self.query_one("#snake-board", Static).update(board_text)
            self.query_one("#snake-score", Label).update(f"Score: {self.score}")
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
        key = getattr(event, "key", "")
        dx, dy = self.dir
        if key in ("left", "h") and dx != 1:
            self.dir = (-1, 0)
        elif key in ("right", "l") and dx != -1:
            self.dir = (1, 0)
        elif key in ("up", "k") and dy != 1:
            self.dir = (0, -1)
        elif key in ("down", "j") and dy != -1:
            self.dir = (0, 1)
        # If paused, allow arrow to start the game for convenience
        if not self.running and key in ("left", "right", "up", "down", "h", "j", "k", "l"):
            self.running = True
            self._ensure_timer()

    def on_resize(self, _event) -> None:  # type: ignore[override]
        # Recalculate board size whenever container resizes
        self._update_board_dimensions()
