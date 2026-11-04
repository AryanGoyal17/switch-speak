"""YesNoTiles on its own: the strong highlight alternates between YES and NO every 600 ms."""

import tkinter as tk

from switchspeak.ui import theme
from switchspeak.ui.yes_no import YesNoTiles

STEP_MS = 600


class YesNoDemo(tk.Tk):
    """A window that shows one YesNoTiles and moves the highlight between its two tiles in a loop."""

    def __init__(self) -> None:
        super().__init__()
        self.title("SwitchSpeak - YesNoTiles demo")
        self.configure(bg=theme.BACKGROUND)
        width, _height = theme.MIN_WINDOW
        self.geometry(f"{width // 2}x{width // 3}")
        self.update_idletasks()
        scale = theme.compute_scale(self)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self._tiles = YesNoTiles(self, scale)
        self._tiles.grid(row=0, column=0, sticky="nsew", padx=theme.PAD_MEDIUM, pady=theme.PAD_MEDIUM)
        self._caption = tk.Label(self, bg=theme.BACKGROUND, fg=theme.DIM_TEXT,
                                 font=theme.font("status", scale), anchor="w")
        self._caption.grid(row=1, column=0, sticky="ew", padx=theme.PAD_LARGE, pady=(0, theme.PAD_MEDIUM))

        self._index = -1
        self._step_id: str | None = None
        self._next()

    def destroy(self) -> None:
        """Cancel the step timer, then close the window."""
        if self._step_id is not None:
            self.after_cancel(self._step_id)
            self._step_id = None
        super().destroy()

    def _next(self) -> None:
        """Highlight the other tile, show the call in the caption and schedule the next move."""
        self._index = (self._index + 1) % self._tiles.item_count()
        self._tiles.highlight_item(self._index)
        name = self._tiles.item_labels()[self._index]
        self._caption.configure(text=f"highlight_item({self._index})  {name}")
        self._step_id = self.after(STEP_MS, self._next)


def main() -> None:
    """Open the demo window; the highlight alternates until it is closed."""
    YesNoDemo().mainloop()


if __name__ == "__main__":
    main()
