from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Label, Button
from textual.screen import ModalScreen

if TYPE_CHECKING:
    from ...engine import GameEngine


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
        # Mirror pricing formula: 100 * (2 ** slots_purchased)
        try:
            cap = int(getattr(self.engine.state, "max_inventory", 50))
        except Exception:
            cap = 50
        slots_purchased = max(0, cap - 50)
        return 100 * (2 ** slots_purchased)

    def compose(self) -> ComposeResult:
        used = self.engine.state.get_inventory_count()
        cap = self.engine.state.max_inventory
        cash = self.engine.state.cash
        cost = self._current_cost()
        prompt = (
            "Extend cargo capacity by +1 slot?\n"
            f"(Capacity: {used}/{cap} | Cash: ${cash:,} | Current cost: ${cost:,})\n"
            "Note: Each additional slot doubles in price."
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
            prompt = (
                "Extend cargo capacity by +1 slot?\n"
                f"(Capacity: {used}/{cap} | Cash: ${cash:,} | Current cost: ${cost:,})\n"
                "Note: Each additional slot doubles in price."
            )
            self.query_one("#modal-prompt", Label).update(prompt)
        except Exception:
            pass

    def action_dismiss_modal(self) -> None:
        self.dismiss()
