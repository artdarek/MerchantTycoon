from typing import List

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Label, Button, OptionList
from textual.widgets.option_list import Option
from textual.screen import ModalScreen

from ...models import City


class CitySelectModal(ModalScreen):
    """City selection modal"""

    def __init__(self, cities: List[City], current_city: int, callback):
        super().__init__()
        self.cities = cities
        self.current_city = current_city
        self.callback = callback

    def compose(self) -> ComposeResult:
        with Container(id="city-modal"):
            yield Label("🗺️  Select Destination", id="modal-title")
            options = []
            for i, city in enumerate(self.cities):
                if i == self.current_city:
                    options.append(Option(f"{city.name}, {city.country} (current)", id=str(i), disabled=True))
                else:
                    options.append(Option(f"{city.name}, {city.country}", id=str(i)))
            yield OptionList(*options, id="city-list")
            yield Button("Cancel", variant="default", id="cancel-btn")

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        city_index = int(event.option.id)
        self.dismiss()
        self.callback(city_index)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()
