from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Container
from merchant_tycoon.engine.applets.home_applet import HomeApplet


class HomePanel(Static):
    def __init__(self):
        super().__init__()
        self._glow_timer = None
        self.service: HomeApplet | None = None

    def compose(self) -> ComposeResult:
        # Center a content-sized box (with border) inside SCREEN
        with Container(id="home-ascii"):
            ascii_art = ""
            try:
                if self.service is None:
                    self.service = getattr(self.app.engine, 'home_applet', None)
                if self.service:
                    ascii_art = self.service.get_ascii()
            except Exception:
                ascii_art = ""
            yield Static(ascii_art, id="home-box", classes="home-box")

    def on_mount(self) -> None:
        # Bind service and start glow animation timer
        try:
            if self.service is None:
                self.service = getattr(self.app.engine, 'home_applet', None)
        except Exception:
            self.service = None
        try:
            if self.service:
                self.service.reset_glow()
            self._apply_glow()
            self._glow_timer = self.set_interval(0.12, self._tick_glow)
        except Exception:
            pass

    def on_unmount(self) -> None:
        try:
            if self._glow_timer is not None:
                self._glow_timer.stop()
        except Exception:
            pass

    def _tick_glow(self) -> None:
        try:
            if self.service:
                self.service.tick_glow()
        except Exception:
            pass
        self._apply_glow()

    def _apply_glow(self) -> None:
        try:
            box = self.query_one("#home-box", Static)
        except Exception:
            return
        # Clear previous glow-* classes
        for cls in ("glow-0","glow-1","glow-2","glow-3","glow-4","glow-5"):
            try:
                box.remove_class(cls)
            except Exception:
                pass
        # Apply next state
        try:
            glow = self.service.get_glow_class() if self.service else "glow-0"
        except Exception:
            glow = "glow-0"
        box.add_class(glow)
