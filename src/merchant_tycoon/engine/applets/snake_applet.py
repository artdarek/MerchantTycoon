from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple
import random


@dataclass
class Point:
    x: int
    y: int


class SnakeApplet:
    """Core Snake game logic independent of UI framework.

    Handles movement, collisions, spawning food/bonuses and scoring.
    Timer/ticks are driven by caller via `tick()`.
    """

    def __init__(
        self,
        *,
        width: int = 24,
        height: int = 14,
        # Economic side-effects dependencies (optional):
        wallet_service: Optional[object] = None,
        messenger: Optional[object] = None,
        # Config
        bonus_amount: int = 100,
        bonus_growth: int = 2,
        super_bonus_amount: int = 1000,
        super_bonus_growth: int = 3,
        super_bonus_speed_step: float = 0.2,
        bonus_spawn_chance: float = 0.02,
        super_spawn_chance: float = 0.005,
    ) -> None:
        self.width = int(width)
        self.height = int(height)

        # Services for side-effects
        self.wallet_service = wallet_service
        self.messenger = messenger

        # Config
        self.bonus_amount = int(bonus_amount)
        self.bonus_growth = int(bonus_growth)
        self.super_bonus_amount = int(super_bonus_amount)
        self.super_bonus_growth = int(super_bonus_growth)
        self.super_bonus_speed_step = float(super_bonus_speed_step)
        self.bonus_spawn_chance = float(bonus_spawn_chance)
        self.super_spawn_chance = float(super_spawn_chance)

        # State
        self.snake: List[Point] = []  # head first
        self.dir: Tuple[int, int] = (1, 0)
        self.food: Optional[Point] = None
        self.bonus: Optional[Point] = None
        self.bonus_ttl: int = 0
        self.super_bonus: Optional[Point] = None
        self.super_bonus_ttl: int = 0
        self.growth_pending: int = 0
        self.speed_bonus: float = 0.0
        self.step_budget: float = 0.0
        self.score: int = 0
        self.rewards: int = 0
        self.super_rewards: int = 0
        self.game_over: bool = False
        self._ui_dirty: bool = False

        self.new_game()

    # ----- Lifecycle -----
    def new_game(self) -> None:
        self.score = 0
        self.rewards = 0
        self.super_rewards = 0
        self.game_over = False
        self.growth_pending = 0
        self.speed_bonus = 0.0
        self.step_budget = 0.0
        self.bonus = None
        self.bonus_ttl = 0
        self.super_bonus = None
        self.super_bonus_ttl = 0
        midx, midy = self.width // 2, self.height // 2
        self.snake = [Point(midx, midy), Point(midx - 1, midy)]
        self.dir = (1, 0)
        self._spawn_food()
        self._ui_dirty = True

    def resize(self, width: int, height: int) -> None:
        new_w = max(12, min(80, int(width)))
        new_h = max(8, min(40, int(height)))
        if new_w == self.width and new_h == self.height:
            return
        self.width, self.height = new_w, new_h
        # If snake out of bounds, start a fresh game to avoid invalid state
        if any(p.x < 0 or p.y < 0 or p.x >= self.width or p.y >= self.height for p in self.snake):
            self.new_game()
            return
        # Keep food/bonuses valid
        def _occupied(x: int, y: int) -> bool:
            return any(s.x == x and s.y == y for s in self.snake)
        if not self.food or self.food.x < 0 or self.food.y < 0 or self.food.x >= self.width or self.food.y >= self.height or _occupied(self.food.x, self.food.y):
            self._spawn_food()
        if self.bonus and (self.bonus.x < 0 or self.bonus.y < 0 or self.bonus.x >= self.width or self.bonus.y >= self.height or _occupied(self.bonus.x, self.bonus.y)):
            self.bonus = None
            self.bonus_ttl = 0
        if self.super_bonus and (self.super_bonus.x < 0 or self.super_bonus.y < 0 or self.super_bonus.x >= self.width or self.super_bonus.y >= self.height or _occupied(self.super_bonus.x, self.super_bonus.y)):
            self.super_bonus = None
            self.super_bonus_ttl = 0

    # ----- Input -----
    def turn(self, dx: int, dy: int) -> None:
        cdx, cdy = self.dir
        # prevent turning directly into the opposite direction
        if (dx, dy) == (-cdx, -cdy):
            return
        self.dir = (dx, dy)

    # ----- Tick -----
    def tick(self) -> None:
        if self.game_over:
            return
        # ~ same stepping as original panel: 1 + speed_bonus per timer tick
        self.step_budget += 1.0 + max(0.0, self.speed_bonus)
        steps = 0
        while self.step_budget >= 1.0 and steps < 10 and not self.game_over:
            self.step_budget -= 1.0
            steps += 1
            self._step_once()

    # ----- Internals -----
    def _spawn_food(self) -> None:
        taken = {(p.x, p.y) for p in self.snake}
        while True:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if (x, y) not in taken:
                self.food = Point(x, y)
                return

    def _maybe_spawn_bonus(self) -> None:
        if self.bonus is not None:
            return
        if random.random() < self.bonus_spawn_chance:
            taken = {(p.x, p.y) for p in self.snake}
            if self.food:
                taken.add((self.food.x, self.food.y))
            for _ in range(50):
                x = random.randint(0, self.width - 1)
                y = random.randint(0, self.height - 1)
                if (x, y) not in taken:
                    self.bonus = Point(x, y)
                    self.bonus_ttl = random.randint(30, 60)
                    break

    def _maybe_spawn_super_bonus(self) -> None:
        if self.super_bonus is not None:
            return
        if random.random() < self.super_spawn_chance:
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

    def _step_once(self) -> None:
        dx, dy = self.dir
        head = self.snake[0]
        nx, ny = head.x + dx, head.y + dy

        # Collisions
        if nx < 0 or ny < 0 or nx >= self.width or ny >= self.height:
            self._game_over()
            return
        if any(seg.x == nx and seg.y == ny for seg in self.snake):
            self._game_over()
            return

        # Move
        self.snake.insert(0, Point(nx, ny))

        # Pickups
        ate_food = bool(self.food and self.food.x == nx and self.food.y == ny)
        ate_bonus = bool(self.bonus and self.bonus.x == nx and self.bonus.y == ny)
        ate_super = bool(self.super_bonus and self.super_bonus.x == nx and self.super_bonus.y == ny)

        if ate_food:
            self.score += 1
            self.growth_pending += 1
            self._spawn_food()

        if ate_bonus:
            self.rewards += 1
            if self.wallet_service:
                try:
                    self.wallet_service.earn(self.bonus_amount)
                    if self.messenger:
                        self.messenger.info(f"Snake bonus: +${self.bonus_amount}", tag="phone")
                except Exception:
                    pass
            self.growth_pending += max(0, self.bonus_growth)
            self.bonus = None
            self.bonus_ttl = 0
            self._ui_dirty = True

        if ate_super:
            self.super_rewards += 1
            if self.wallet_service:
                try:
                    self.wallet_service.earn(self.super_bonus_amount)
                    if self.messenger:
                        self.messenger.info(f"Snake SUPER bonus: +${self.super_bonus_amount}", tag="phone")
                except Exception:
                    pass
            self.growth_pending += max(0, self.super_bonus_growth)
            self.speed_bonus = min(self.speed_bonus + self.super_bonus_speed_step, 3.0)
            self.super_bonus = None
            self.super_bonus_ttl = 0
            self._ui_dirty = True

        # Growth or tail trim
        if self.growth_pending > 0:
            self.growth_pending -= 1
        else:
            self.snake.pop()

        # Bonuses lifecycle
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
        self.game_over = True
        self._ui_dirty = True

    # ----- UI Sync -----
    def consume_ui_dirty(self) -> bool:
        dirty = self._ui_dirty
        self._ui_dirty = False
        return dirty
