"""MessageBar on its own: cycles empty -> 'I NEED WA' -> a 120-character sentence, one step every 3 s."""

import tkinter as tk

from switchspeak.ui import theme
from switchspeak.ui.message_bar import MessageBar

LONG_SENTENCE = (
    "PLEASE CALL MY SISTER AND TELL HER THE DOCTOR SAID I CAN GO HOME ON FRIDAY "
    "IF MY TEST RESULTS COME BACK GOOD. THANK YOU."
)
STATES: tuple[tuple[str, str], ...] = (
    ("empty: dim placeholder, no cursor", ""),
    ("short: text plus blinking cursor", "I NEED WA"),
    (f"long: {len(LONG_SENTENCE)} characters, newest end shown behind '...'", LONG_SENTENCE),
)
STEP_MS = 3000


class MessageBarDemo(tk.Tk):
    """A window that shows one MessageBar and feeds it each demo state in turn."""

    def __init__(self) -> None:
        super().__init__()
        self.title("SwitchSpeak - MessageBar demo")
        self.configure(bg=theme.BACKGROUND)
        width, height = theme.MIN_WINDOW
        self.geometry(f"{width}x{height}")
        self.update_idletasks()
        scale = theme.compute_scale(self)

        self.columnconfigure(0, weight=1)
        self._bar = MessageBar(self, scale)
        self._bar.grid(row=0, column=0, sticky="ew", padx=theme.PAD_MEDIUM, pady=theme.PAD_MEDIUM)
        self._caption = tk.Label(self, bg=theme.BACKGROUND, fg=theme.DIM_TEXT,
                                 font=theme.font("status", scale), anchor="w", justify="left")
        self._caption.grid(row=1, column=0, sticky="ew", padx=theme.PAD_LARGE)

        self._state = -1
        self._step_id: str | None = None
        self._next()

    def destroy(self) -> None:
        """Cancel the cycle timer, then close the window."""
        if self._step_id is not None:
            self.after_cancel(self._step_id)
            self._step_id = None
        super().destroy()

    def _next(self) -> None:
        """Show the next demo state and schedule the one after it."""
        self._state = (self._state + 1) % len(STATES)
        name, text = STATES[self._state]
        self._bar.set_text(text)
        self._caption.configure(
            text=f"State {self._state + 1} of {len(STATES)}: {name}.\n"
                 "Resize the window: the newest letters stay visible, never more than 2 lines."
        )
        self._step_id = self.after(STEP_MS, self._next)


def main() -> None:
    """Open the demo window; it cycles through the states until closed."""
    MessageBarDemo().mainloop()


if __name__ == "__main__":
    main()
