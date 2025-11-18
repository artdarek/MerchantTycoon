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
    rewards: int = reactive(0)
    game_over: bool = reactive(False)

    def __init__(self):
        super().__init__()
        self.snake: List[Point] = []  # head is first element
        self.dir: Tuple[int, int] = (1, 0)  # dx, dy (start moving right)
        self.food: Point | None = None
        self.bonus: Point | None = None  # $ bonus position
        self.bonus_ttl: int = 0          # ticks until bonus disappears
        self.super_bonus: Point | None = None  # 'B' super bonus position
        self.super_bonus_ttl: int = 0          # ticks until super bonus disappears
        self._timer = None
        self.growth_pending: int = 0     # pending growth segments
        # Speed controls
        self.speed_bonus: float = 0.0    # extra steps per tick (accumulated)
        self.step_budget: float = 0.0    # accumulated step budget
        self.super_rewards: int = 0      # count of super bonuses collected

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
        # Compute initial board size from allocated space, then start a new game
        self._update_board_dimensions()
        self._new_game()
        # Start paused; user can press Start
        self.running = False

    # --- Game lifecycle ---
    def _new_game(self) -> None:
        self.score = 0
        self.rewards = 0
        self.game_over = False
        self.growth_pending = 0
        self.speed_bonus = 0.0
        self.step_budget = 0.0
        self.super_rewards = 0
        self.super_bonus = None
        self.super_bonus_ttl = 0
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
                # Ensure food and bonus are valid within new bounds and not colliding with snake
                def _occupied(x: int, y: int) -> bool:
                    return any(s.x == x and s.y == y for s in self.snake)

                if self.food is None or self.food.x < 0 or self.food.y < 0 or self.food.x >= self.width or self.food.y >= self.height or _occupied(self.food.x, self.food.y):
                    self._spawn_food()

                if self.bonus is not None:
                    if (
                        self.bonus.x < 0
                        or self.bonus.y < 0
                        or self.bonus.x >= self.width
                        or self.bonus.y >= self.height
                        or _occupied(self.bonus.x, self.bonus.y)
                    ):
                        # Drop invalid bonus rather than respawn immediately
                        self.bonus = None
                        self.bonus_ttl = 0
                if self.super_bonus is not None:
                    if (
                        self.super_bonus.x < 0
                        or self.super_bonus.y < 0
                        or self.super_bonus.x >= self.width
                        or self.super_bonus.y >= self.height
                        or _occupied(self.super_bonus.x, self.super_bonus.y)
                    ):
                        self.super_bonus = None
                        self.super_bonus_ttl = 0
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

    def _maybe_spawn_bonus(self) -> None:
        """Occasionally spawn a temporary $ bonus on a free cell."""
        import random

        if self.bonus is not None:
            return
        # ~2% chance per tick while running
        if random.random() < 0.02:
            taken = {(p.x, p.y) for p in self.snake}
            if self.food:
                taken.add((self.food.x, self.food.y))
            for _ in range(50):
                x = random.randint(0, self.width - 1)
                y = random.randint(0, self.height - 1)
                if (x, y) not in taken:
                    self.bonus = Point(x, y)
                    # bonus stays 5–10 seconds depending on FPS (~6fps)
                    self.bonus_ttl = random.randint(30, 60)
                    break

    def _maybe_spawn_super_bonus(self) -> None:
        """Occasionally spawn a temporary 'B' super bonus on a free cell."""
        import random

        if self.super_bonus is not None:
            return
        # Rarer than $ bonus (~0.5% chance per tick)
        if random.random() < 0.005:
            taken = {(p.x, p.y) for p in self.snake}
            if self.food:
                taken.add((self.food.x, self.food.y))
            if self.bonus:
                taken.add((self.bonus.x, self.bonus.y))
            for _ in range(50):
                x = random.randint(0, self.width - 1)
                y = random.randint(0, self.height - 1)
                if (x, y) not in taken:
                    self.super_bonus = Point(x, y)
                    self.super_bonus_ttl = random.randint(30, 60)
                    break

    def _tick(self) -> None:
        if not self.running or self.game_over:
            return
        # Accumulate step budget: 1 base step + speed bonus per timer tick
        self.step_budget += 1.0 + max(0.0, self.speed_bonus)
        steps = 0
        while self.step_budget >= 1.0 and steps < 10 and self.running and not self.game_over:
            self.step_budget -= 1.0
            steps += 1
            self._step_once()
        # Render once after applying steps this tick
        self._render_board()

    def _step_once(self) -> None:
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

        # Determine pickups
        ate_food = bool(self.food and self.food.x == nx and self.food.y == ny)
        ate_bonus = bool(self.bonus and self.bonus.x == nx and self.bonus.y == ny)
        ate_super = bool(self.super_bonus and self.super_bonus.x == nx and self.super_bonus.y == ny)

        # Food
        if ate_food:
            self.score += 1
            self.growth_pending += 1
            self._spawn_food()

        # $ bonus
        if ate_bonus:
            self.rewards += 1
            try:
                if hasattr(self.app, 'engine') and hasattr(self.app.engine, 'wallet_service'):
                    from merchant_tycoon.config import SETTINGS
                    bonus_amt = int(getattr(SETTINGS.phone, 'snake_bonus_amount', 100))
                    self.app.engine.wallet_service.earn(bonus_amt)
                    if hasattr(self.app.engine, 'messenger'):
                        self.app.engine.messenger.info(f"Snake bonus: +${bonus_amt}", tag="phone")
                if hasattr(self.app, 'refresh_all'):
                    self.app.refresh_all()
            except Exception:
                pass
            try:
                from merchant_tycoon.config import SETTINGS
                growth_add = int(getattr(SETTINGS.phone, 'snake_bonus_growth', 2))
            except Exception:
                growth_add = 2
            self.growth_pending += max(0, growth_add)
            self.bonus = None
            self.bonus_ttl = 0

        # Super bonus 'B'
        if ate_super:
            self.super_rewards += 1
            try:
                if hasattr(self.app, 'engine') and hasattr(self.app.engine, 'wallet_service'):
                    from merchant_tycoon.config import SETTINGS
                    super_amt = int(getattr(SETTINGS.phone, 'snake_super_bonus_amount', 1000))
                    self.app.engine.wallet_service.earn(super_amt)
                    if hasattr(self.app.engine, 'messenger'):
                        self.app.engine.messenger.info(f"Snake SUPER bonus: +${super_amt}", tag="phone")
                if hasattr(self.app, 'refresh_all'):
                    self.app.refresh_all()
            except Exception:
                pass
            # Grow more and speed up slightly (cap total bonus)
            try:
                from merchant_tycoon.config import SETTINGS
                growth_add_super = int(getattr(SETTINGS.phone, 'snake_super_bonus_growth', 3))
            except Exception:
                growth_add_super = 3
            self.growth_pending += max(0, growth_add_super)
            try:
                from merchant_tycoon.config import SETTINGS
                step = float(getattr(SETTINGS.phone, 'snake_super_bonus_speed_step', 0.2))
            except Exception:
                step = 0.2
            self.speed_bonus = min(self.speed_bonus + step, 3.0)
            self.super_bonus = None
            self.super_bonus_ttl = 0

        # Apply growth or trim tail
        if self.growth_pending > 0:
            self.growth_pending -= 1
        else:
            self.snake.pop()

        # Lifecycle for bonuses
        if self.bonus is None:
            self._maybe_spawn_bonus()
        else:
            self.bonus_ttl -= 1
            if self.bonus_ttl <= 0:
                self.bonus = None
                self.bonus_ttl = 0

        if self.super_bonus is None:
            self._maybe_spawn_super_bonus()
        else:
            self.super_bonus_ttl -= 1
            if self.super_bonus_ttl <= 0:
                self.super_bonus = None
                self.super_bonus_ttl = 0

    def _game_over(self) -> None:
        self.running = False
        self.game_over = True
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
        if self.food and 0 <= self.food.x < self.width and 0 <= self.food.y < self.height:
            grid[self.food.y][self.food.x] = "◆"
        # Draw snake
        for i, seg in enumerate(self.snake):
            ch = "█" if i == 0 else "■"
            grid[seg.y][seg.x] = ch
        # Draw bonus ($)
        if self.bonus and 0 <= self.bonus.x < self.width and 0 <= self.bonus.y < self.height:
            grid[self.bonus.y][self.bonus.x] = "$"
        # Draw super bonus (B)
        if self.super_bonus and 0 <= self.super_bonus.x < self.width and 0 <= self.super_bonus.y < self.height:
            grid[self.super_bonus.y][self.super_bonus.x] = "B"
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
            # Use dot separators and right-aligned score line
            self.query_one("#snake-score", Label).update(
                f"Score: {self.score} • Bonus: {self.rewards} x ${bonus_amt} • Super bonus: {self.super_rewards} x ${super_amt}"
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
        dx, dy = self.dir
        if key in ("left", "h") and dx != 1:
            self.dir = (-1, 0)
        elif key in ("right", "l") and dx != -1:
            self.dir = (1, 0)
        elif key in ("up", "k") and dy != 1:
            self.dir = (0, -1)
        elif key in ("down", "j") and dy != -1:
            self.dir = (0, 1)
        # If paused (but not game over), allow arrow to start the game for convenience
        if not self.running and not self.game_over and key in ("left", "right", "up", "down", "h", "j", "k", "l"):
            self.running = True
            self._ensure_timer()

    def on_resize(self, _event) -> None:  # type: ignore[override]
        # Recalculate board size whenever container resizes
        self._update_board_dimensions()
