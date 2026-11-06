"""LetterGrid panel: the 5 x 6 letters grid, BACKSPACE drawn as ⌫, word labels shrunk to fit. Owner: Member 2."""

import tkinter as tk
import tkinter.font as tkfont

from switchspeak.ui import theme

SYMBOLS: dict[str, str] = {"BACKSPACE": "⌫"}


class LetterGrid(tk.Frame):
    """Display-only 5 x 6 grid of letter cells that can show a soft row or a strong cell."""

    def __init__(self, parent: tk.Misc, grid: list[list[str]], scale: float = 1.0) -> None:
        if len(grid) != theme.GRID_ROWS or any(len(row) != theme.GRID_COLS for row in grid):
            raise ValueError(f"grid must be {theme.GRID_ROWS} lists of {theme.GRID_COLS} strings")
        super().__init__(parent, bg=theme.PANEL)
        self._texts = [list(row) for row in grid]
        self._highlighted: list[tuple[int, int]] = []
        self._word_font = tkfont.Font(root=self, font=theme.font("cell", scale))
        self._word_top = theme.font("cell", scale)[1]
        self._word_floor = min(self._word_top, theme.font("chip", scale)[1])
        self._word_inner = 0
        self._words = [SYMBOLS.get(t, t) for row in self._texts for t in row if len(SYMBOLS.get(t, t)) > 1]

        for r in range(theme.GRID_ROWS):
            self.rowconfigure(r, weight=1, uniform="letter_rows")
        for c in range(theme.GRID_COLS):
            self.columnconfigure(c, weight=1, uniform="letter_cols")

        normal = theme.highlight_style(theme.LEVEL_NORMAL)
        self._labels: list[list[tk.Label]] = []
        for r, row in enumerate(self._texts):
            labels: list[tk.Label] = []
            for c, text in enumerate(row):
                shown = SYMBOLS.get(text, text)
                is_word = len(shown) > 1
                label = tk.Label(
                    self, text=shown, width=1,
                    font=self._word_font if is_word else theme.font("cell", scale), anchor="center", bd=0,
                    padx=theme.PAD_SMALL, pady=theme.PAD_SMALL,
                    bg=normal["bg"], fg=normal["fg"], highlightthickness=theme.BORDER_WIDTH,
                    highlightbackground=normal["ring"], highlightcolor=normal["ring"],
                )
                label.grid(row=r, column=c, sticky="nsew", padx=theme.PAD_SMALL, pady=theme.PAD_SMALL)
                if is_word:
                    label.bind("<Configure>", self._on_word_resize)
                labels.append(label)
            self._labels.append(labels)

    def item_count(self) -> int:
        """Return the number of cells: always 30."""
        return theme.GRID_ROWS * theme.GRID_COLS

    def item_labels(self) -> list[str]:
        """Return the 30 cell labels as given (BACKSPACE and SPACE, not their symbols), row-major: index = r*6 + c."""
        return [text for row in self._texts for text in row]

    def highlight_row(self, r: int) -> None:
        """Clear the old highlight, then softly highlight all 6 cells of row r."""
        self._check_row(r)
        self.clear()
        for c in range(theme.GRID_COLS):
            self._style(r, c, theme.LEVEL_SOFT)

    def highlight_cell(self, r: int, c: int) -> None:
        """Clear the old highlight, then softly highlight row r and strongly highlight cell (r, c)."""
        self._check_row(r)
        self._check_col(c)
        self.clear()
        for col in range(theme.GRID_COLS):
            self._style(r, col, theme.LEVEL_STRONG if col == c else theme.LEVEL_SOFT)

    def clear(self) -> None:
        """Reset only the cells that were highlighted, leaving nothing highlighted."""
        for r, c in self._highlighted:
            self._paint(r, c, theme.LEVEL_NORMAL)
        self._highlighted.clear()

    def _on_word_resize(self, event: "tk.Event[tk.Label]") -> None:
        """Shrink the shared word font (e.g. for SPACE) until the longest word fits a cell, never below chip size."""
        inner = event.width - 2 * (theme.BORDER_WIDTH + theme.PAD_SMALL)
        if inner == self._word_inner or inner <= 0:
            return
        self._word_inner = inner
        for size in range(self._word_top, self._word_floor - 1, -1):
            self._word_font.configure(size=size)
            if max(self._word_font.measure(word) for word in self._words) <= inner:
                return

    def _style(self, r: int, c: int, level: str) -> None:
        """Paint cell (r, c) at a highlight level and remember it for clear()."""
        self._paint(r, c, level)
        self._highlighted.append((r, c))

    def _paint(self, r: int, c: int, level: str) -> None:
        """Set the colours and ring of cell (r, c) for a highlight level."""
        style = theme.highlight_style(level)
        self._labels[r][c].configure(bg=style["bg"], fg=style["fg"], highlightbackground=style["ring"],
                                     highlightcolor=style["ring"])

    def _check_row(self, r: int) -> None:
        """Raise ValueError unless 0 <= r < 5."""
        if not 0 <= r < theme.GRID_ROWS:
            raise ValueError(f"row {r} out of range 0..{theme.GRID_ROWS - 1}")

    def _check_col(self, c: int) -> None:
        """Raise ValueError unless 0 <= c < 6."""
        if not 0 <= c < theme.GRID_COLS:
            raise ValueError(f"column {c} out of range 0..{theme.GRID_COLS - 1}")
