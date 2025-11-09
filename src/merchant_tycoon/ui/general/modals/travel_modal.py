from typing import List

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Label, Button, OptionList, Input
from textual.widgets.option_list import Option
from textual.screen import ModalScreen

from merchant_tycoon.domain.model.city import City


class TravelModal(ModalScreen):
    """City selection modal with current/destination read-only fields and Travel/Cancel buttons."""

    def __init__(self, cities: List[City], current_city: int, callback):
        super().__init__()
        self.cities = cities
        self.current_city = current_city
        self.callback = callback
        from typing import Optional
        self._selected_id: Optional[str] = None

    BINDINGS = [
        ("escape", "dismiss_modal", "Close"),
    ]

    def compose(self) -> ComposeResult:
        with Container(id="city-modal"):
            # Title (emoji + uppercase)
            title = "✈️ Travel"
            parts = title.split(None, 1)
            if len(parts) == 2:
                title = f"{parts[0]} {parts[1].upper()}"
            else:
                title = title.upper()
            yield Label(title, id="modal-title")

            # Current location (read-only)
            yield Label("Currently in")
            cur_city = self.cities[self.current_city]
            yield Input(f"{cur_city.name}, {cur_city.country}", id="current-input", disabled=True)

            # Destination select (exclude current city)
            yield Label("Buy ticket to")
            options: list[Option] = []
            for i, city in enumerate(self.cities):
                if i == self.current_city:
                    continue  # exclude current city
                options.append(Option(f"{city.name}, {city.country}", id=str(i)))
            yield OptionList(*options, id="city-list")

            # Destination (read-only mirror of selection)
            yield Label("Destination")
            yield Input("", id="destination-input", disabled=True)

            # Action buttons
            with Horizontal(id="modal-buttons"):
                yield Button("Travel", id="travel-btn", variant="success", disabled=True)
                yield Button("Cancel", id="cancel-btn", variant="error")

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        # Mirror selected city in destination input and enable Travel
        try:
            self._selected_id = event.option.id
            idx = int(self._selected_id)
            city = self.cities[idx]
            dest = f"{city.name}, {city.country}"
            self.query_one("#destination-input", Input).value = dest
            self.query_one("#travel-btn", Button).disabled = False
        except Exception:
            pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "travel-btn" and self._selected_id is not None:
            try:
                city_index = int(self._selected_id)
            except Exception:
                city_index = None
            self.dismiss()
            if city_index is not None:
                self.callback(city_index)
        elif event.button.id == "cancel-btn":
            self.dismiss()

    def action_dismiss_modal(self) -> None:
        self.dismiss()
