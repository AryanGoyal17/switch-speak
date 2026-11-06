"""YesNoTiles panel: the YES and NO tiles at the start of the phrases zone. Owner: Member 3."""

import tkinter as tk

from switchspeak.ui import theme
from switchspeak.ui.contract import PHRASES_HEAD

DISPLAY_TEXT: dict[str, str] = {
    "YES": "✔  YES",
    "NO": "✖  NO",
}
BASE_COLOURS: dict[str, str] = {"YES": theme.GREEN, "NO": theme.RED_BROWN}
TILE_LINES = 1


class YesNoTiles(tk.Frame):
    """Display-only pair of big equal tiles: YES (green, ✔) and NO (red-brown, ✖)."""

    def __init__(self, parent: tk.Misc, scale: float = 1.0) -> None:
        super().__init__(parent, bg=theme.BACKGROUND)
        self._highlighted: int | None = None
        self._tiles: list[tk.Label] = []

        self.rowconfigure(0, weight=1)
        for i, name in enumerate(PHRASES_HEAD):
            self.columnconfigure(i, weight=1, uniform="yes_no")
            tile = tk.Label(
                self, text=DISPLAY_TEXT[name], font=theme.font("tile", scale), width=1,
                height=TILE_LINES, anchor="center", justify="center", bd=0,
                padx=theme.PAD_MEDIUM, pady=theme.PAD_MEDIUM, highlightthickness=theme.BORDER_WIDTH,
            )
            tile.grid(row=0, column=i, sticky="nsew", padx=theme.PAD_SMALL, pady=theme.PAD_SMALL)
            self._tiles.append(tile)
            self._paint(i)

    def item_count(self) -> int:
        """Return the number of tiles: always 2."""
        return len(PHRASES_HEAD)

    def item_labels(self) -> list[str]:
        """Return the item names in scan order: ['YES', 'NO']."""
        return list(PHRASES_HEAD)

    def highlight_item(self, i: int) -> None:
        """Clear the old highlight, then give tile i (0 = YES, 1 = NO) the strong highlight."""
        self._check_index(i)
        self.clear()
        self._highlighted = i
        self._paint(i)

    def clear(self) -> None:
        """Remove the highlight, if any, so both tiles show their own colours."""
        if self._highlighted is None:
            return
        old, self._highlighted = self._highlighted, None
        self._paint(old)

    def _paint(self, i: int) -> None:
        """Colour tile i for its current state: strong if highlighted, else its own colour with the ring hidden."""
        if i == self._highlighted:
            style = theme.highlight_style(theme.LEVEL_STRONG)
        else:
            style = theme.highlight_style(theme.LEVEL_NORMAL, base_bg=BASE_COLOURS[PHRASES_HEAD[i]],
                                          ring=theme.BACKGROUND)
        self._tiles[i].configure(bg=style["bg"], fg=style["fg"], highlightbackground=style["ring"],
                                 highlightcolor=style["ring"])

    def _check_index(self, i: int) -> None:
        """Raise ValueError unless 0 <= i < 2."""
        if not 0 <= i < len(PHRASES_HEAD):
            raise ValueError(f"yes/no index {i} out of range 0..{len(PHRASES_HEAD) - 1}")
