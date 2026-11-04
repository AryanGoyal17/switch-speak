"""LetterGrid panel: the 5 x 6 letters grid, BACKSPACE drawn as ⌫. Owner: Member 2."""

import tkinter as tk

from switchspeak.ui import theme

BACKSPACE = "BACKSPACE"
BACKSPACE_SYMBOL = "⌫"


class LetterGrid(tk.Frame):
    """Display-only 5 x 6 grid of letter cells that can show a soft row or a strong cell."""

    def __init__(self, parent: tk.Misc, grid: list[list[str]], scale: float = 1.0) -> None:
        if len(grid) != theme.GRID_ROWS or any(len(row) != theme.GRID_COLS for row in grid):
            raise ValueError(f"grid must be {theme.GRID_ROWS} lists of {theme.GRID_COLS} strings")
        super().__init__(parent, bg=theme.PANEL)
        self._texts = [list(row) for row in grid]
        self._highlighted: list[tuple[int, int]] = []

        for r in range(theme.GRID_ROWS):
            self.rowconfigure(r, weight=1, uniform="letter_rows")
        for c in range(theme.GRID_COLS):
            self.columnconfigure(c, weight=1, uniform="letter_cols")

        normal = theme.highlight_style(theme.LEVEL_NORMAL)
        self._labels: list[list[tk.Label]] = []
        for r, row in enumerate(self._texts):
            labels: list[tk.Label] = []
            for c, text in enumerate(row):
                label = tk.Label(
                    self, text=BACKSPACE_SYMBOL if text == BACKSPACE else text,
                    font=theme.font("cell", scale), anchor="center", bd=0,
                    padx=theme.PAD_MEDIUM, pady=theme.PAD_MEDIUM,
                    bg=normal["bg"], fg=normal["fg"], highlightthickness=theme.BORDER_WIDTH,
                    highlightbackground=normal["ring"], highlightcolor=normal["ring"],
                )
                label.grid(row=r, column=c, sticky="nsew", padx=theme.PAD_SMALL, pady=theme.PAD_SMALL)
                labels.append(label)
            self._labels.append(labels)

    def item_count(self) -> int:
        """Return the number of cells: always 30."""
        return theme.GRID_ROWS * theme.GRID_COLS

    def item_labels(self) -> list[str]:
        """Return the 30 cell labels as given (BACKSPACE, not ⌫), row-major: index = r*6 + c."""
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
