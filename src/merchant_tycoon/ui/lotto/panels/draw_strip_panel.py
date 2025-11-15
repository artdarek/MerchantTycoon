from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Horizontal

from merchant_tycoon.engine import GameEngine


class LottoDrawStripPanel(Static):
    """Compact panel showing only today's lotto numbers in a single line.

    No title, just a one-line display like: "1 * 2 * 12 * 3 * 6 * 34".
    """

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine

    def compose(self) -> ComposeResult:
        # Horizontal strip with 6 boxes; texts updated in update_strip()
        with Horizontal(id="lotto-draw-strip"):
            for i in range(6):
                yield Static("-", id=f"lotto-box-{i+1}", classes="lotto-draw-box")

    def update_strip(self) -> None:
        draw = getattr(self.engine.state, "lotto_today_draw", None)
        if not draw or not getattr(draw, "numbers", None):
            nums = ["-"] * 6
        else:
            try:
                nums = [str(n) for n in sorted(list(draw.numbers))]
            except Exception:
                nums = [str(n) for n in list(draw.numbers)]
        # Ensure exactly 6 boxes
        nums = (nums + ["-"] * 6)[:6]
        # Update existing boxes' content
        for i, n in enumerate(nums, start=1):
            try:
                box = self.query_one(f"#lotto-box-{i}", Static)
                box.update(n)
            except Exception:
                pass
