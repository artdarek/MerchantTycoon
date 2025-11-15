from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Container


ASCII_HOME = '''
                        .8 
                      .888
                    .8888'
                   .8888'
                   888'
                   8'
      .88888888888. .88888888888.
   .8888888888888888888888888888888.
 .8888888888888888888888888888888888.
.&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&'
&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&'
&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&'
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@:
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@:
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@:
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%. 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%. 
`%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%.
 `00000000000000000000000000000000000'
  `000000000000000000000000000000000'
   `0000000000000000000000000000000'
     `###########################'
       `#######################'
         `#########''########'
           `"""""'  `"""""'
             Hello aiPhone
'''


class HomePanel(Static):
    def __init__(self):
        super().__init__()
        self._glow_timer = None
        # Sequence of class suffixes for smooth pulsing (go up then down)
        self._glow_seq = ["0","1","2","3","4","5","4","3","2","1"]
        self._glow_pos = 0

    def compose(self) -> ComposeResult:
        # Center a content-sized box (with border) inside SCREEN
        with Container(id="home-ascii"):
            yield Static(ASCII_HOME, id="home-box", classes="home-box")

    def on_mount(self) -> None:
        # Start glow animation timer
        try:
            self._apply_glow()
            # Faster interval for smoother animation (~8 FPS)
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
        self._glow_pos = (self._glow_pos + 1) % len(self._glow_seq)
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
        box.add_class(f"glow-{self._glow_seq[self._glow_pos]}")
