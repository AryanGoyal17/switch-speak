"""LetterGrid on its own: walks rows 0 to 4, then the cells across row 2, then clears; one step every 500 ms."""

import tkinter as tk
from collections.abc import Callable

from switchspeak.ui import theme
from switchspeak.ui.contract import LETTER_LABELS
from switchspeak.ui.letter_grid import LetterGrid

GRID: list[list[str]] = [
    list(LETTER_LABELS[r * theme.GRID_COLS:(r + 1) * theme.GRID_COLS]) for r in range(theme.GRID_ROWS)
]
DEMO_ROW = 2
STEP_MS = 500


class LetterGridDemo(tk.Tk):
    """A window that shows one LetterGrid and plays the row, cell and clear steps in a loop."""

    def __init__(self) -> None:
        super().__init__()
        self.title("SwitchSpeak - LetterGrid demo")
        self.configure(bg=theme.BACKGROUND)
        width, height = theme.MIN_WINDOW
        self.geometry(f"{width}x{height}")
        self.update_idletasks()
        scale = theme.compute_scale(self)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self._grid = LetterGrid(self, GRID, scale)
        self._grid.grid(row=0, column=0, sticky="nsew", padx=theme.PAD_MEDIUM, pady=theme.PAD_MEDIUM)
        self._caption = tk.Label(self, bg=theme.BACKGROUND, fg=theme.DIM_TEXT,
                                 font=theme.font("status", scale), anchor="w")
        self._caption.grid(row=1, column=0, sticky="ew", padx=theme.PAD_LARGE, pady=(0, theme.PAD_MEDIUM))

        self._steps: list[tuple[str, Callable[[], None]]] = []
        for r in range(theme.GRID_ROWS):
            self._steps.append((f"highlight_row({r})", lambda r=r: self._grid.highlight_row(r)))
        for c in range(theme.GRID_COLS):
            self._steps.append((f"highlight_cell({DEMO_ROW}, {c})",
                                lambda c=c: self._grid.highlight_cell(DEMO_ROW, c)))
        self._steps.append(("clear()", self._grid.clear))
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
    LetterGridDemo().mainloop()


if __name__ == "__main__":
    main()
