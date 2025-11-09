from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static, Button, Label
class GlobalActionsBar(Static):
    """Top bar showing global actions available at all times"""

    def compose(self) -> ComposeResult:
        with Horizontal(id="global-actions-bar"):
            yield Button("Ⓝ  New Game ↔ F1", id="action-new", classes="action-item")
            yield Button("Ⓢ  Save ↔ F2", id="action-save", classes="action-item")
            yield Button("Ⓛ  Load ↔ F3", id="action-load", classes="action-item")
            yield Button("ⓗ  Help ↔ F4", id="action-help", classes="action-item")
            # Use circled info glyph for About; keep space after glyph for clarity
            yield Button("ⓘ  About ↔ F5", id="action-about", classes="action-item")
            yield Button("Ⓠ  Quit ↔ ESC", id="action-quit", classes="action-item")
            yield Static("", id="global-spacer")
            yield Label("", id="global-info")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Dispatch top bar button clicks to the same actions as hotkeys."""
        bid = event.button.id or ""
        app = self.app
        if bid == "action-new":
            app.action_new_game()
        elif bid == "action-save":
            app.action_save()
        elif bid == "action-load":
            app.action_load()
        elif bid == "action-help":
            app.action_help()
        elif bid == "action-about":
            app.action_about()
        elif bid == "action-quit":
            try:
                app.action_quit()
            except Exception:
                app.exit()

    def on_mount(self) -> None:
        self.update_info()

    def update_info(self) -> None:
        try:
            engine = getattr(self.app, "engine", None)
            if not engine:
                return
            state = engine.state
            from merchant_tycoon.domain.constants import CITIES
            city = CITIES[state.current_city]
            date_raw = getattr(state, "date", "")
            try:
                day_num = int(getattr(state, "day", 0))
            except Exception:
                day_num = getattr(state, "day", 0)
            date_disp = f"{date_raw} ← {day_num}" if date_raw else f"{day_num}"
            text = f"{date_disp} • {city.name}/{city.country}"
            self.query_one("#global-info", Label).update(text)
        except Exception:
            try:
                self.query_one("#global-info", Label).update("")
            except Exception:
                pass

    
