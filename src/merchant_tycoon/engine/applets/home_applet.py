from __future__ import annotations


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


class HomeApplet:
    """Lightweight state for the Home applet (glow animation).

    Keeps the glow cycle state. UI calls `tick_glow()` on timer and reads
    `get_glow_class()` to update CSS class.
    """

    def __init__(self) -> None:
        # Sequence for smooth pulse (up and down)
        self._glow_seq = ["0", "1", "2", "3", "4", "5", "4", "3", "2", "1"]
        self._pos = 0

    def get_ascii(self) -> str:
        return ASCII_HOME

    def reset_glow(self) -> None:
        self._pos = 0

    def tick_glow(self) -> None:
        self._pos = (self._pos + 1) % len(self._glow_seq)

    def get_glow_class(self) -> str:
        return f"glow-{self._glow_seq[self._pos]}"
