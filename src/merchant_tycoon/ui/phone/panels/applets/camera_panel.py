from textual.app import ComposeResult
from textual.widgets import Static, Label
from textual.containers import ScrollableContainer
from merchant_tycoon.engine.applets.camera_applet import CameraApplet


class CameraPanel(Static):
    def compose(self) -> ComposeResult:
        yield Label("📷 CAMERA", classes="panel-title")
        with ScrollableContainer(id="camera-ascii"):
            try:
                svc = getattr(self.app.engine, 'camera_applet', None)
                ascii_img = svc.get_ascii() if svc else ""
            except Exception:
                ascii_img = ""
            yield Static(ascii_img)

    def on_mount(self) -> None:
        # Center scroll approximately in the middle after layout
        def _center():
            try:
                cont = self.query_one("#camera-ascii", ScrollableContainer)
                vh = getattr(cont.virtual_size, "height", 0) or 0
                ph = getattr(cont.size, "height", 0) or 0
                target_y = 0
                try:
                    svc = getattr(self.app.engine, 'camera_applet', None)
                    target_y = svc.compute_center_y(vh, ph) if svc else max(0, (vh - ph) // 2)
                except Exception:
                    target_y = max(0, (vh - ph) // 2)
                try:
                    cont.scroll_to(y=target_y, animate=False)
                except Exception:
                    # Fallback to scroll_end/home if precise center unavailable
                    if target_y > 0:
                        cont.scroll_end(animate=False)
                    else:
                        cont.scroll_home(animate=False)
            except Exception:
                pass

        # Delay a tick to ensure virtual_size is computed
        try:
            self.set_timer(0.05, _center)
        except Exception:
            _center()
