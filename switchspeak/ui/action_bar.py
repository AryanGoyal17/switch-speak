"""ActionBar panel: SPEAK, BACKSPACE, CLEAR, PAUSE in that order. Owner: Member 2."""

import tkinter as tk

from switchspeak.ui import theme
from switchspeak.ui.contract import ACTION_LABELS

DISPLAY_TEXT: dict[str, str] = {
    "SPEAK": "SPEAK",
    "BACKSPACE": "⌫ BACKSPACE",
    "CLEAR": "CLEAR ALL",
    "PAUSE": "PAUSE SCANNING",
}
RESUME_TEXT = "RESUME SCANNING"
COLUMN_WEIGHTS = (3, 2, 2, 2)
TILE_LINES = 2
PAUSE_INDEX = ACTION_LABELS.index("PAUSE")


class ActionBar(tk.Frame):
    """Display-only row of four action tiles: SPEAK, BACKSPACE, CLEAR, PAUSE."""

    def __init__(self, parent: tk.Misc, scale: float = 1.0) -> None:
        super().__init__(parent, bg=theme.BACKGROUND)
        self._highlighted: int | None = None
        self._paused = False
        self._tiles: list[tk.Label] = []

        self.rowconfigure(0, weight=1)
        for i, name in enumerate(ACTION_LABELS):
            self.columnconfigure(i, weight=COLUMN_WEIGHTS[i], uniform="actions")
            tile = tk.Label(
                self, text=DISPLAY_TEXT[name], font=theme.font("tile", scale), width=1,
                height=TILE_LINES, anchor="center", justify="center", bd=0,
                padx=theme.PAD_MEDIUM, pady=theme.PAD_MEDIUM, highlightthickness=theme.BORDER_WIDTH,
            )
            tile.grid(row=0, column=i, sticky="nsew", padx=theme.PAD_SMALL, pady=theme.PAD_SMALL)
            tile.bind("<Configure>", self._on_resize)
            self._tiles.append(tile)
            self._paint(i)

    def item_count(self) -> int:
        """Return the number of action tiles: always 4."""
        return len(ACTION_LABELS)

    def item_labels(self) -> list[str]:
        """Return the internal action names in scan order (not the display text)."""
        return list(ACTION_LABELS)

    def highlight_item(self, i: int) -> None:
        """Clear the old highlight, then give tile i (0 to 3) the strong highlight."""
        self._check_index(i)
        self.clear()
        self._highlighted = i
        self._paint(i)

    def clear(self) -> None:
        """Remove the highlight, if any, leaving the paused border in place."""
        if self._highlighted is None:
            return
        old, self._highlighted = self._highlighted, None
        self._paint(old)

    def set_paused(self, flag: bool) -> None:
        """Show the last tile as RESUME SCANNING with an amber border when paused, or as PAUSE SCANNING when not."""
        self._paused = bool(flag)
        self._tiles[PAUSE_INDEX].configure(text=RESUME_TEXT if self._paused else DISPLAY_TEXT["PAUSE"])
        self._paint(PAUSE_INDEX)

    def _paint(self, i: int) -> None:
        """Colour tile i for its current state: strong if highlighted, else its own colours and ring."""
        if i == self._highlighted:
            style = theme.highlight_style(theme.LEVEL_STRONG)
        else:
            base_bg = theme.GREEN if ACTION_LABELS[i] == "SPEAK" else theme.CELL
            ring = theme.AMBER if i == PAUSE_INDEX and self._paused else theme.BACKGROUND
            style = theme.highlight_style(theme.LEVEL_NORMAL, base_bg=base_bg, ring=ring)
        self._tiles[i].configure(bg=style["bg"], fg=style["fg"], highlightbackground=style["ring"],
                                 highlightcolor=style["ring"])

    def _on_resize(self, event: "tk.Event[tk.Label]") -> None:
        """Wrap a tile's text to the width it actually has inside its ring and padding."""
        inner = event.width - 2 * (theme.BORDER_WIDTH + theme.PAD_MEDIUM)
        event.widget.configure(wraplength=max(1, inner))

    def _check_index(self, i: int) -> None:
        """Raise ValueError unless 0 <= i < 4."""
        if not 0 <= i < len(ACTION_LABELS):
            raise ValueError(f"action index {i} out of range 0..{len(ACTION_LABELS) - 1}")
