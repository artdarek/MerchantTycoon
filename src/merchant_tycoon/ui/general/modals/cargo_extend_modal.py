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

    def _current_cost(self) -> int:
        """Mirror GoodsService pricing with selected strategy."""
        try:
            cap = int(getattr(self.engine.state, "max_inventory", SETTINGS.cargo.base_capacity))
        except Exception:
            cap = SETTINGS.cargo.base_capacity
        step = max(1, int(SETTINGS.cargo.extend_step))
        over_base = max(0, cap - SETTINGS.cargo.base_capacity)
        bundles = over_base // step
        mode = str(getattr(SETTINGS.cargo, "extend_pricing_mode", "linear")).lower()
        if mode == "exponential":
            factor = float(getattr(SETTINGS.cargo, "extend_cost_factor", 2.0))
            return int(int(SETTINGS.cargo.extend_base_cost) * (factor ** bundles))
        else:
            base = int(SETTINGS.cargo.extend_base_cost)
            factor = float(getattr(SETTINGS.cargo, "extend_cost_factor", 1.0))
            increment = base * factor
            return int(base + increment * bundles)

    def compose(self) -> ComposeResult:
        used = self.engine.state.get_inventory_count()
        cap = self.engine.state.max_inventory
        cash = self.engine.state.cash
        cost = self._current_cost()
        step = max(1, int(SETTINGS.cargo.extend_step))
        mode = str(getattr(SETTINGS.cargo, "extend_pricing_mode", "linear")).lower()
        if mode == "exponential":
            note = f"Each additional bundle of {step} slot(s) multiplies cost (factor {getattr(SETTINGS.cargo, 'extend_cost_factor', 2.0):g})."
        else:
            base = int(SETTINGS.cargo.extend_base_cost)
            factor = float(getattr(SETTINGS.cargo, "extend_cost_factor", 1.0))
            inc = int(base * factor)
            note = f"Each additional bundle of {step} slot(s) increases cost by +${inc:,}."
        prompt = (
            f"Extend cargo capacity by +{step} slot(s)?\n"
            f"(Capacity: {used}/{cap} | Cash: ${cash:,} | Current cost: ${cost:,})\n"
            f"Note: {note}"
        )
        with Container(id="input-modal"):
            yield Label("📦 Extend Cargo", id="modal-title")
            yield Label(prompt, id="modal-prompt")
            with Horizontal(id="modal-buttons"):
                yield Button("Extend", id="extend-btn", variant="primary")
                yield Button("Cancel", id="cancel-btn", variant="default")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "extend-btn":
            try:
                ok = bool(self._on_extend()) if callable(self._on_extend) else False
            except Exception:
                ok = False
            if ok:
                self.dismiss()
            else:
                # Keep modal open; refresh displayed values (cash/cost/capacity)
                try:
                    self.refresh_content()
                except Exception:
                    pass
        elif event.button.id == "cancel-btn":
            self.dismiss()

    def refresh_content(self) -> None:
        """Re-render the modal prompt to reflect latest state."""
        try:
            used = self.engine.state.get_inventory_count()
            cap = self.engine.state.max_inventory
            cash = self.engine.state.cash
            cost = self._current_cost()
            step = max(1, int(SETTINGS.cargo.extend_step))
            mode = str(getattr(SETTINGS.cargo, "extend_pricing_mode", "linear")).lower()
            if mode == "exponential":
                note = f"Each additional bundle of {step} slot(s) multiplies cost (factor {getattr(SETTINGS.cargo, 'extend_cost_factor', 2.0):g})."
            else:
                base = int(SETTINGS.cargo.extend_base_cost)
                factor = float(getattr(SETTINGS.cargo, "extend_cost_factor", 1.0))
                inc = int(base * factor)
                note = f"Each additional bundle of {step} slot(s) increases cost by +${inc:,}."
            prompt = (
                f"Extend cargo capacity by +{step} slot(s)?\n"
                f"(Capacity: {used}/{cap} | Cash: ${cash:,} | Current cost: ${cost:,})\n"
                f"Note: {note}"
            )
            self.query_one("#modal-prompt", Label).update(prompt)
        except Exception:
            pass

    def action_dismiss_modal(self) -> None:
        self.dismiss()
