from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Label, Button
from textual.screen import ModalScreen

from merchant_tycoon.engine import GameEngine
from merchant_tycoon.config import SETTINGS


class InvestmentsLockedModal(ModalScreen):
    """Modal shown when investments are locked due to insufficient wealth.

    This dedicated modal computes its own title and message from the engine state,
    avoiding duplication at call sites.
    """

    BINDINGS = [
        ("escape", "dismiss_modal", "Close"),
        ("enter", "dismiss_modal", "Close"),
    ]

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine

    def _build_title(self) -> str:
        return "🔒 Investments Locked"

    def _build_message(self) -> str:
        try:
            threshold = int(getattr(SETTINGS.investments, "min_wealth_to_unlock_trading", 0))
        except Exception:
            threshold = 0
        # Compute current wealth using engine state and current prices
        try:
            asset_prices = getattr(self.engine, "asset_prices", {})
            goods_prices = getattr(self.engine, "prices", {})
            current_wealth = int(self.engine.state.calculate_total_wealth(asset_prices, goods_prices))
        except Exception:
            current_wealth = 0
        try:
            peak_wealth = int(getattr(self.engine.state, "peak_wealth", 0))
        except Exception:
            peak_wealth = 0
        progress_pct = (peak_wealth / threshold * 100) if threshold > 0 else 0

        message = (
            f"Investment trading is currently locked.\n\n"
            f"Required wealth: ${threshold:,}\n"
            f"Current wealth: ${current_wealth:,}\n"
            f"Peak wealth: ${peak_wealth:,}\n"
            f"Progress: {progress_pct:.1f}%\n\n"
            f"💡 Trade goods to build your wealth!\n"
            f"(cash + bank + goods + portfolio − debt)"
        )
        return message

    def compose(self) -> ComposeResult:
        # Use the negative alert style for locked state
        with Container(id="alert-modal-negative"):
            # Uppercase the title while preserving leading emoji + single space
            t = self._build_title() or ""
            parts = t.split(None, 1)
            if len(parts) == 2:
                t = f"{parts[0]} {parts[1].upper()}"
            else:
                t = t.upper()
            yield Label(t, id="modal-title")
            yield Label(self._build_message(), id="alert-message")
            yield Button("OK (ENTER)", variant="error", id="ok-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ok-btn":
            self.dismiss()

    def action_dismiss_modal(self) -> None:
        """Close the modal when ESC or ENTER is pressed"""
        self.dismiss()
