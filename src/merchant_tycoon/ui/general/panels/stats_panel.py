from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static, Label
from rich.text import Text

from merchant_tycoon.engine import GameEngine


def render_cargo_bar(used: int, total: int, segments: int = 10) -> Text:
    """Return ASCII-style progress bar for cargo usage.

    Args:
        used: Current cargo slots used
        total: Maximum cargo capacity
        segments: Number of bar segments to display (default: 10)

    Returns:
        Rich Text object with styled cargo bar

    Example:
        >>> render_cargo_bar(30, 100, 10)
        Text with: [bold white]███[/bold white][dim]███████[/dim]
    """
    if total <= 0:
        # No capacity, show empty bar
        return Text("│" * segments, style="dim")

    # Calculate fill ratio and number of filled segments
    ratio = min(1.0, used / total)
    filled = int(ratio * segments)
    empty = segments - filled

    # Create the bar with styled segments
    bar = Text()

    # Determine color based on usage level
    if ratio >= 0.9:
        # 90%+ full: red (critical)
        fill_style = "bold red"
    elif ratio >= 0.7:
        # 70-90% full: orange (warning)
        fill_style = "bold #ff8800"
    elif ratio >= 0.5:
        # 50-70% full: yellow (caution)
        fill_style = "bold yellow"
    else:
        # <50% full: white (normal)
        fill_style = "bold white"

    # Add filled segments (full blocks)
    if filled > 0:
        bar.append("▓" * filled, style=fill_style)

    # Add empty segments (light shade blocks)
    if empty > 0:
        bar.append("░" * empty, style="dim")

    return bar


class StatsPanel(Static):
    """Display player stats"""

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine

    def compose(self) -> ComposeResult:
        with Horizontal(id="stats-row"):
            yield Label("", id="stats-left")
            yield Label("", id="stats-spacer")
            yield Label("", id="stats-cargo")

    def update_stats(self):
        state = self.engine.state

        # Get cargo space used (accounting for product sizes)
        if hasattr(self.engine, 'cargo_service') and self.engine.cargo_service:
            cargo_used = self.engine.cargo_service.get_used_slots()
            cargo_max = self.engine.cargo_service.get_max_slots()
        else:
            # Fallback to old method if cargo service not available
            cargo_used = state.get_inventory_count()
            cargo_max = state.max_inventory

        # Calculate total portfolio value
        portfolio_value = 0
        for symbol, quantity in state.portfolio.items():
            if symbol in self.engine.asset_prices:
                portfolio_value += quantity * self.engine.asset_prices[symbol]

        # Bank balance (added to header after Cash)
        bank_balance = state.bank.balance if hasattr(state, "bank") and state.bank is not None else 0

        left_text = (
            f"💰 Cash → ${state.cash:,}  •  "
            f"🏦 Bank → ${bank_balance:,}  •  "
            f"📈 Assets → ${portfolio_value:,}  •  "
            f"💳 Debt → ${state.debt:,}"
        )

        # Create cargo text with visual progress bar
        right_render = Text(f"📦 Cargo → {cargo_used}/{cargo_max} ", no_wrap=True, overflow="crop")
        cargo_bar = render_cargo_bar(cargo_used, cargo_max, segments=10)
        right_render.append_text(cargo_bar)

        left_render = Text(left_text, no_wrap=True, overflow="ellipsis")
        self.query_one("#stats-left", Label).update(left_render)
        self.query_one("#stats-cargo", Label).update(right_render)
