"""Suggestions panel: up to 4 words, empty slots dim and not counted. Owner: Member 3."""

import tkinter as tk
from collections.abc import Sequence

from switchspeak.ui import theme

EMPTY_TEXT = "—"


class SuggestionRow(tk.Frame):
    """Display-only row of 4 word slots; empty slots stay in place, dimmed."""

    def __init__(self, parent: tk.Misc, scale: float = 1.0) -> None:
        super().__init__(parent, bg=theme.BACKGROUND)
        self._words: list[str] = []
        self._highlighted: int | None = None
        self._slots: list[tk.Label] = []

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        slots = tk.Frame(self, bg=theme.BACKGROUND)
        slots.grid(row=0, column=0, sticky="nsew")
        slots.rowconfigure(0, weight=1)
        for i in range(theme.MAX_SUGGESTIONS):
            slots.columnconfigure(i, weight=1, uniform="suggestions")
            slot = tk.Label(slots, font=theme.font("tile", scale), width=1, anchor="center", bd=0,
                            padx=theme.PAD_MEDIUM, pady=theme.PAD_MEDIUM,
                            highlightthickness=theme.BORDER_WIDTH)
            slot.grid(row=0, column=i, sticky="nsew", padx=theme.PAD_SMALL, pady=theme.PAD_SMALL)
            self._slots.append(slot)
        self.set_words([])

    def set_words(self, words: Sequence[str]) -> None:
        """Fill the slots left to right with up to 4 words in upper case; the rest show a dim '—'."""
        self._words = [w for w in list(words)[:theme.MAX_SUGGESTIONS] if w.strip()]
        if self._highlighted is not None and self._highlighted >= len(self._words):
            self._highlighted = None
        for i, slot in enumerate(self._slots):
            slot.configure(text=self._words[i].upper() if i < len(self._words) else EMPTY_TEXT)
            self._paint(i)

    def item_count(self) -> int:
        """Return the number of filled slots (0 to 4); empty slots are not items."""
        return len(self._words)

    def item_labels(self) -> list[str]:
        """Return the words in the filled slots, left to right, as they were given."""
        return list(self._words)

    def highlight_item(self, i: int) -> None:
        """Clear the old highlight, then give filled slot i the strong highlight."""
        self._check_index(i)
        self.clear()
        self._highlighted = i
        self._paint(i)

    def clear(self) -> None:
        """Remove the highlight, if any."""
        if self._highlighted is None:
            return
        old, self._highlighted = self._highlighted, None
        self._paint(old)

    def _paint(self, i: int) -> None:
        """Colour slot i: strong if highlighted, a normal cell if filled, dimmed if empty."""
        if i == self._highlighted:
            style = theme.highlight_style(theme.LEVEL_STRONG)
        elif i < len(self._words):
            style = theme.highlight_style(theme.LEVEL_NORMAL, ring=theme.BACKGROUND)
        else:
            style = theme.highlight_style(theme.LEVEL_NORMAL, base_bg=theme.EMPTY_CELL,
                                          base_fg=theme.DIM_TEXT, ring=theme.BACKGROUND)
        self._slots[i].configure(bg=style["bg"], fg=style["fg"], highlightbackground=style["ring"],
                                 highlightcolor=style["ring"])

    def _check_index(self, i: int) -> None:
        """Raise ValueError unless slot i holds a word."""
        if not 0 <= i < len(self._words):
            raise ValueError(f"suggestion index {i} out of range: {len(self._words)} filled slot(s)")
