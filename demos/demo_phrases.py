"""PhrasesPanel on its own: the highlight walks through every item, then the category switches and it walks again."""

import tkinter as tk
from collections.abc import Callable

from switchspeak.ui import theme
from switchspeak.ui.contract import PHRASES_HEAD
from switchspeak.ui.phrases_panel import PhrasesPanel

CATEGORIES: tuple[str, ...] = ("Needs", "People", "Feelings", "Alerts")
PHRASES: tuple[tuple[str, ...], ...] = (
    ("I need water", "I am hungry", "I need the washroom", "I am in pain", "I am feeling cold",
     "Please call the nurse", "Please call my family", "Thank you"),
    ("Please come here", "Please stay with me", "Where is my family?", "I love you", "Thank you"),
)
STEP_MS = 1000


class PhrasesDemo(tk.Tk):
    """A window that shows one PhrasesPanel, walks the highlight through every item, switches category and repeats."""

    def __init__(self) -> None:
        super().__init__()
        self.title("SwitchSpeak - PhrasesPanel demo")
        self.configure(bg=theme.BACKGROUND)
        width, height = theme.MIN_WINDOW
        self.geometry(f"{width * 2 // 5}x{height}")
        self.update_idletasks()
        scale = theme.compute_scale(self)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self._panel = PhrasesPanel(self, scale)
        self._panel.grid(row=0, column=0, sticky="nsew", padx=theme.PAD_MEDIUM, pady=theme.PAD_MEDIUM)
        self._caption = tk.Label(self, bg=theme.BACKGROUND, fg=theme.DIM_TEXT,
                                 font=theme.font("status", scale), anchor="w")
        self._caption.grid(row=1, column=0, sticky="ew", padx=theme.PAD_LARGE, pady=(0, theme.PAD_MEDIUM))
        self.update_idletasks()
        self.geometry(f"{width * 2 // 5}x{max(height, self.winfo_reqheight())}")

        self._steps: list[Callable[[], str]] = []
        for active, phrases in enumerate(PHRASES):
            self._steps.append(lambda active=active: self._switch(active))
            for i in range(len(PHRASES_HEAD) + len(CATEGORIES) + len(phrases) + 1):
                self._steps.append(lambda i=i: self._highlight(i))
            self._steps.append(self._clear)
        self._step = -1
        self._step_id: str | None = None
        self._next()

    def destroy(self) -> None:
        """Cancel the step timer, then close the window."""
        if self._step_id is not None:
            self.after_cancel(self._step_id)
            self._step_id = None
        super().destroy()

    def _switch(self, active: int) -> str:
        """Make category active the teal tab and fill the rows with its phrases."""
        self._panel.set_categories(CATEGORIES, active)
        self._panel.set_phrases(PHRASES[active])
        return f"set_categories(active={active}) + set_phrases({len(PHRASES[active])} phrases)"

    def _highlight(self, i: int) -> str:
        """Highlight item i and return the call and the item's label for the caption."""
        self._panel.highlight_item(i)
        return f"highlight_item({i}) of {self._panel.item_count()}  {self._panel.item_labels()[i]}"

    def _clear(self) -> str:
        """Remove the highlight and return the call for the caption."""
        self._panel.clear()
        return "clear()"

    def _next(self) -> None:
        """Run the next step, show its name and schedule the one after it."""
        self._step = (self._step + 1) % len(self._steps)
        name = self._steps[self._step]()
        self._caption.configure(text=name)
        self._step_id = self.after(STEP_MS, self._next)


def main() -> None:
    """Open the demo window; the steps repeat until it is closed."""
    PhrasesDemo().mainloop()


if __name__ == "__main__":
    main()
