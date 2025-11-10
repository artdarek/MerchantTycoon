from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Label, Button
from textual.screen import ModalScreen
from merchant_tycoon.config import SETTINGS

if TYPE_CHECKING:
    from merchant_tycoon.engine import GameEngine


class CargoExtendModal(ModalScreen):
    """Modal to extend cargo capacity by purchasing an extra slot.

    Shows current usage, capacity, cash, current cost, and a note about doubling price.
    The provided `on_extend` callback should perform the purchase using the engine
    and return True on success, False on failure. On success this modal will close;
    on failure it stays open so the user can try again later.
    """

    BINDINGS = [
        ("escape", "dismiss_modal", "Close"),
    ]

    def __init__(self, engine: "GameEngine", on_extend):
        super().__init__()
        self.engine = engine
        self._on_extend = on_extend

    def compose(self) -> ComposeResult:
        cash = self.engine.state.cash
        cost = self.engine.goods_service.extend_cargo_current_cost()
        prompt = self._prepare_content(cash, cost)
        with Container(id="input-modal"):
            t = "📦 Extend Cargo"
            parts = t.split(None, 1)
            if len(parts) == 2:
                t = f"{parts[0]} {parts[1].upper()}"
            else:
                t = t.upper()
            yield Label(t, id="modal-title")
            yield Label(prompt, id="modal-prompt")
            with Horizontal(id="modal-buttons"):
                yield Button("Extend", id="extend-btn", variant="success", disabled=cost > cash)
                yield Button("Cancel", id="cancel-btn", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "extend-btn":
            try:
                ok = bool(self._on_extend()) if callable(self._on_extend) else False
            except Exception:
                ok = False
            if ok:
                self.dismiss()
            else:
                # Keep modal open; refresh displayed valques (cash/cost/capacity)
                try:
                    self.refresh_content()
                except Exception:
                    pass
        elif event.button.id == "cancel-btn":
            self.dismiss()

    def refresh_content(self) -> None:
        """Re-render the modal prompt to reflect latest state."""
        try:
            cash = self.engine.state.cash
            cost = self.engine.goods_service.extend_cargo_current_cost()
            self._prepare_content(cash, cost)

            # disable button until we have enough cash
            self.query_one("#modal-prompt", Label).update(prompt)
            extend_btn = self.query_one("#extend-btn", Button)
            extend_btn.disabled = cost > cash
        except Exception:
            pass

    def _prepare_content(self, cash: int, cost: int) -> str:
        step = max(1, int(SETTINGS.cargo.extend_step))
        mode = str(getattr(SETTINGS.cargo, "extend_pricing_mode", "linear")).lower()
        if mode == "exponential":
            note = f"Each additional bundle of {step} slot(s) multiplies cost (factor {getattr(SETTINGS.cargo, 'extend_cost_factor', 2.0):g})."
        else:
            base = int(SETTINGS.cargo.extend_base_cost)
            factor = float(getattr(SETTINGS.cargo, "extend_cost_factor", 1.0))
            inc = int(base * factor)
            note = (
                f"Each additional bundle of {step} slot(s) increases cost by +${inc:,}."
            )
        prompt = (
            f"Extend cargo capacity by +{step} slot(s)?\n"
            f"Current cost: ${cost:,}\n"
            f"Note: {note}"
        )
        return prompt

    def action_dismiss_modal(self) -> None:
        self.dismiss()
