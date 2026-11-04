"""SuggestionRow on its own: empty, then 4 words, then 2 words, with the highlight moving through each state."""

import tkinter as tk
from collections.abc import Callable

from switchspeak.ui import theme
from switchspeak.ui.suggestions import SuggestionRow

STATES: tuple[list[str], ...] = ([], ["WATER", "WAIT", "WALK", "WASH"], ["WATER", "WAIT"])
STEP_MS = 800


class SuggestionsDemo(tk.Tk):
    """A window that shows one SuggestionRow and plays each word state with a moving highlight, in a loop."""

    def __init__(self) -> None:
        super().__init__()
        self.title("SwitchSpeak - SuggestionRow demo")
        self.configure(bg=theme.BACKGROUND)
        width, _height = theme.MIN_WINDOW
        self.geometry(f"{width}x{width // 4}")
        self.update_idletasks()
        scale = theme.compute_scale(self)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self._row = SuggestionRow(self, scale)
        self._row.grid(row=0, column=0, sticky="nsew", padx=theme.PAD_MEDIUM, pady=theme.PAD_MEDIUM)
        self._caption = tk.Label(self, bg=theme.BACKGROUND, fg=theme.DIM_TEXT,
                                 font=theme.font("status", scale), anchor="w")
        self._caption.grid(row=1, column=0, sticky="ew", padx=theme.PAD_LARGE, pady=(0, theme.PAD_MEDIUM))

        self._steps: list[tuple[str, Callable[[], None]]] = []
        for words in STATES:
            self._steps.append((f"set_words({words})", lambda words=words: self._row.set_words(words)))
            for i in range(len(words)):
                self._steps.append((f"highlight_item({i})  {words[i]}",
                                    lambda i=i: self._row.highlight_item(i)))
            if words:
                self._steps.append(("clear()", self._row.clear))
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
    SuggestionsDemo().mainloop()


if __name__ == "__main__":
    main()
