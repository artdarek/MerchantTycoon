from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static

from merchant_tycoon.engine import GameEngine
from merchant_tycoon.ui.phone.panels.left_menu_panel import LeftMenuPanel
from merchant_tycoon.ui.phone.panels.screen_panel import ScreenPanel


class PhonePanel(Static):
    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine
        self.menu: LeftMenuPanel | None = None
        self.phone_screen: ScreenPanel | None = None

    def compose(self) -> ComposeResult:
        with Horizontal(id="phone-root"):
            with Static(id="phone-left-col"):
                self.menu = LeftMenuPanel(self.engine)
                yield self.menu
            with Static(id="phone-right-col"):
                self.phone_screen = ScreenPanel(self.engine)
                yield self.phone_screen

    def on_mount(self) -> None:
        # Ensure default app selected
        if not self.engine.phone_service.get_active_app():
            self.engine.phone_service.set_active_app("home")
        self.refresh_phone()

    def refresh_phone(self) -> None:
        try:
            if self.menu:
                self.menu.update_menu()
        except Exception:
            pass
        try:
            if self.phone_screen:
                self.phone_screen.update_screen()
        except Exception:
            pass
