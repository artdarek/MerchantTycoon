from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Container

from merchant_tycoon.engine import GameEngine
from merchant_tycoon.ui.phone.apps.whatsup_panel import WhatsUpPanel
from merchant_tycoon.ui.phone.apps.wordle_game_panel import WordleGamePanel
from merchant_tycoon.ui.phone.apps.camera_panel import CameraPanel
from merchant_tycoon.ui.phone.apps.home_panel import HomePanel


class ScreenPanel(Static):
    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine

    def compose(self) -> ComposeResult:
        from textual.widgets import Label
        yield Label("🖥 SCREEN", classes="panel-title")
        yield Container(id="phone-screen")

    def update_screen(self) -> None:
        active = self.engine.phone_service.get_active_app()
        try:
            container = self.query_one("#phone-screen", Container)
        except Exception:
            return

        # Clear and mount the selected app panel
        try:
            container.remove_children()
        except Exception:
            pass

        panel: Static
        if active == "home":
            panel = HomePanel()
            container.mount(panel)
        elif active == "whatsup":
            panel = WhatsUpPanel()
            container.mount(panel)
            try:
                panel.refresh_messages()
            except Exception:
                pass
        elif active == "camera":
            panel = CameraPanel()
            container.mount(panel)
        elif active == "wordle":
            panel = WordleGamePanel()
            container.mount(panel)
        else:
            panel = Static(f"Unknown app: {active}")
            container.mount(panel)
