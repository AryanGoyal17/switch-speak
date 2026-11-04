"""ActionBar on its own: moves the highlight through all four tiles, clears it, then toggles pause twice."""

import tkinter as tk
from collections.abc import Callable

from switchspeak.ui import theme
from switchspeak.ui.action_bar import ActionBar

STEP_MS = 1000


class ActionBarDemo(tk.Tk):
    """A window that shows one ActionBar and plays the highlight and pause steps in a loop."""

    def __init__(self) -> None:
        super().__init__()
        self.title("SwitchSpeak - ActionBar demo")
        self.configure(bg=theme.BACKGROUND)
        width, _height = theme.MIN_WINDOW
        self.geometry(f"{width}x{width // 4}")
        self.update_idletasks()
        scale = theme.compute_scale(self)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self._bar = ActionBar(self, scale)
        self._bar.grid(row=0, column=0, sticky="nsew", padx=theme.PAD_MEDIUM, pady=theme.PAD_MEDIUM)
        self._caption = tk.Label(self, bg=theme.BACKGROUND, fg=theme.DIM_TEXT,
                                 font=theme.font("status", scale), anchor="w")
        self._caption.grid(row=1, column=0, sticky="ew", padx=theme.PAD_LARGE, pady=(0, theme.PAD_MEDIUM))

        self._steps: list[tuple[str, Callable[[], None]]] = [
            (f"highlight_item({i})  {name}", lambda i=i: self._bar.highlight_item(i))
            for i, name in enumerate(self._bar.item_labels())
        ]
        self._steps += [
            ("clear()", self._bar.clear),
            ("set_paused(True)", lambda: self._bar.set_paused(True)),
            ("set_paused(False)", lambda: self._bar.set_paused(False)),
        ]
        self._step = -1
        self._step_id: str | None = None
        self._next()

    def destroy(self) -> None:
        """Cancel the step timer, then close the window."""
        if self._step_id is not None:
            self.after_cancel(self._step_id)
            self._step_id = None
        super().destroy()

    def _next(self) -> None:
        """Run the next step, show its name and schedule the one after it."""
        self._step = (self._step + 1) % len(self._steps)
        name, action = self._steps[self._step]
        action()
        self._caption.configure(text=f"Step {self._step + 1} of {len(self._steps)}: {name}")
        self._step_id = self.after(STEP_MS, self._next)


def main() -> None:
    """Open the demo window; the steps repeat until it is closed."""
    ActionBarDemo().mainloop()


if __name__ == "__main__":
    main()
