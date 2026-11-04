"""TopBar and StatusLine on their own: the switch chip toggles between connected and keyboard mode."""

import tkinter as tk

from switchspeak.ui import theme
from switchspeak.ui.status_bar import StatusLine, TopBar

STATES: tuple[tuple[str, bool, str, float, str], ...] = (
    ("Switch: Button - Connected", True, "Scan: Zone > Item", 1.2, "Ready - scanning the letters"),
    ("Keyboard mode", False, "Scan: Zone > Item", 1.5, "No switch found - press the spacebar instead"),
)
STEP_MS = 3000


class StatusDemo(tk.Tk):
    """A window with a TopBar above and a StatusLine below that flips between connected and keyboard mode."""

    def __init__(self) -> None:
        super().__init__()
        self.title("SwitchSpeak - TopBar and StatusLine demo")
        self.configure(bg=theme.BACKGROUND)
        width, _height = theme.MIN_WINDOW
        self.geometry(f"{width}x{width // 5}")
        self.update_idletasks()
        scale = theme.compute_scale(self)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self._top = TopBar(self, scale)
        self._top.grid(row=0, column=0, sticky="ew", padx=theme.PAD_MEDIUM, pady=theme.PAD_MEDIUM)
        self._status = StatusLine(self, scale)
        self._status.grid(row=2, column=0, sticky="ew", pady=(0, theme.PAD_MEDIUM))

        self._state = -1
        self._step_id: str | None = None
        self._next()

    def destroy(self) -> None:
        """Cancel the step timer, then close the window."""
        if self._step_id is not None:
            self.after_cancel(self._step_id)
            self._step_id = None
        super().destroy()

    def _next(self) -> None:
        """Show the other state in both widgets and schedule the next switch."""
        self._state = (self._state + 1) % len(STATES)
        switch_text, switch_ok, mode_text, speed, status = STATES[self._state]
        self._top.set_chips(switch_text, switch_ok, mode_text, speed)
        self._status.set_text(status)
        self._step_id = self.after(STEP_MS, self._next)


def main() -> None:
    """Open the demo window; the two states alternate until it is closed."""
    StatusDemo().mainloop()


if __name__ == "__main__":
    main()
