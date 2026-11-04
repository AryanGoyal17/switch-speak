"""EmergencyOverlay on its own: it covers a message-bar stand-in, counts 5, 4, 3, 2, 1, then hides."""

import tkinter as tk

from switchspeak.ui import theme
from switchspeak.ui.emergency_overlay import EmergencyOverlay

TICK_MS = 1000
HIDDEN_MS = 2500


# OOP: inheritance - it extends tk.Tk, so the demo object is the root window itself.
# OOP: composition - it owns an EmergencyOverlay over a message-bar stand-in and drives it only through show and hide.
class EmergencyDemo(tk.Tk):
    """A window with a stand-in message bar and a caption; the overlay counts down over the bar, then hides."""

    # OOP: dunder methods - Python calls __init__ for EmergencyDemo(); it builds the window and starts the countdown.
    # OOP: encapsulation (private attributes) - the seconds left and the timer id live in `_seconds` and `_step_id`.
    def __init__(self) -> None:
        super().__init__()
        self.title("SwitchSpeak - EmergencyOverlay demo")
        self.configure(bg=theme.BACKGROUND)
        width, _height = theme.MIN_WINDOW
        self.geometry(f"{width}x{width // 5}")
        self.update_idletasks()
        scale = theme.compute_scale(self)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        host = tk.Frame(self, bg=theme.PANEL)
        host.grid(row=0, column=0, sticky="nsew", padx=theme.PAD_MEDIUM, pady=theme.PAD_MEDIUM)
        tk.Label(host, text="message bar (the overlay covers this area)", bg=theme.PANEL, fg=theme.CELL_TEXT,
                 font=theme.font("message", scale)).pack(expand=True)
        self._overlay = EmergencyOverlay(host, scale)
        self._caption = tk.Label(self, text="", bg=theme.BACKGROUND, fg=theme.DIM_TEXT,
                                 font=theme.font("status", scale), anchor="w")
        self._caption.grid(row=1, column=0, sticky="ew", padx=theme.PAD_MEDIUM, pady=(0, theme.PAD_MEDIUM))

        self._seconds = theme.EMERGENCY_SECONDS
        self._step_id: str | None = None
        self._tick()

    # OOP: polymorphism - it replaces tk.Tk.destroy, cancels the timer, then calls the original.
    def destroy(self) -> None:
        """Cancel the countdown timer, then close the window."""
        if self._step_id is not None:
            self.after_cancel(self._step_id)
            self._step_id = None
        super().destroy()

    def _tick(self) -> None:
        """Show the next number, or hide the overlay after 1 and start over once it has been seen empty."""
        if self._seconds > 0:
            self._overlay.show(self._seconds)
            self._caption.configure(text=f"show({self._seconds}) - is_visible = {self._overlay.is_visible}")
            self._seconds -= 1
            delay = TICK_MS
        else:
            self._overlay.hide()
            self._caption.configure(text=f"hide() - is_visible = {self._overlay.is_visible}")
            self._seconds = theme.EMERGENCY_SECONDS
            delay = HIDDEN_MS
        self._step_id = self.after(delay, self._tick)


def main() -> None:
    """Open the demo window; the countdown repeats until it is closed."""
    EmergencyDemo().mainloop()


if __name__ == "__main__":
    main()
