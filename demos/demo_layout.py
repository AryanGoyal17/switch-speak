"""Empty SwitchSpeak window: coloured placeholder frames only, so the team can agree on the geometry."""

import tkinter as tk

from switchspeak.ui import theme

# Root window rows, top to bottom: (region, weight). Every row first gets the height its
# content needs; weights then share out any extra height. Weight 0 = never grows.
ROOT_ROWS: tuple[tuple[str, int], ...] = (
    ("top bar", 0),
    ("message bar", 2),
    ("suggestions", 1),
    ("middle", 6),
    ("actions", 1),
    ("status line", 0),
)
MIDDLE_COLUMNS = (3, 2)  # letters : phrases = 60% : 40%
PHRASE_COLUMNS = 2       # 8 phrases drawn as 4 rows x 2, row-major, so 20 pt text fits
PHRASES_ROWS: tuple[tuple[str, int], ...] = (
    ("yes / no", 2),
    ("tabs", 1),
    ("phrase row 0", 1),
    ("phrase row 1", 1),
    ("phrase row 2", 1),
    ("phrase row 3", 1),
    ("emergency", 1),
)


# OOP: inheritance - a Placeholder is a tk.Frame, so it can be gridded anywhere a frame can
class Placeholder(tk.Frame):
    """A coloured frame with its region name in a label, reserving the highlight ring like a real item."""

    def __init__(
        self,
        parent: tk.Misc,
        name: str,
        bg: str = theme.CELL,
        fg: str = theme.CELL_TEXT,
        role: str = "tile",
        ring: str = theme.PANEL,
        sticky: str = "",
        scale: float = 1.0,
        ring_width: int = theme.BORDER_WIDTH,
    ) -> None:
        super().__init__(
            parent,
            bg=bg,
            highlightthickness=ring_width,
            highlightbackground=ring,
            highlightcolor=ring,
        )
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        # bd=0 and pady=0: the reserved ring already gives the text its breathing room
        tk.Label(self, text=name, bg=bg, fg=fg, font=theme.font(role, scale), bd=0, pady=0).grid(
            row=0, column=0, sticky=sticky, padx=theme.PAD_MEDIUM
        )


# OOP: inheritance - LayoutWindow is a tk.Tk, so it is the root window itself
# OOP: composition - the window is built from region frames and Placeholder objects it owns
class LayoutWindow(tk.Tk):
    """The SwitchSpeak root window filled with placeholders, laid out with grid weights only."""

    # OOP: dunder methods - __init__ runs when the window is created and builds every region once
    # OOP: encapsulation (private attributes) - _fullscreen and _scale are kept inside the window
    def __init__(self) -> None:
        super().__init__()
        self.title("SwitchSpeak")
        self.configure(bg=theme.BACKGROUND)
        width, height = theme.MIN_WINDOW
        self.minsize(width, height)
        self.geometry(f"{width}x{height}")
        self.update_idletasks()
        self._scale = theme.compute_scale(self)  # fonts follow the starting window height
        self._fullscreen = False
        self.bind("<F11>", self._toggle_fullscreen)  # carer key in this demo; ui/ never binds keys

        self.columnconfigure(0, weight=1)
        for row, (_name, weight) in enumerate(ROOT_ROWS):
            self.rowconfigure(row, weight=weight)

        builders = (
            self._build_top_bar,
            self._build_message_bar,
            self._build_suggestions,
            self._build_middle,
            self._build_actions,
            self._build_status_line,
        )
        last = len(builders) - 1
        for row, build in enumerate(builders):
            region = build()
            bottom = theme.PAD_MEDIUM if row == last else 0
            region.grid(row=row, column=0, sticky="nsew",
                        padx=theme.PAD_MEDIUM, pady=(theme.PAD_MEDIUM, bottom))

    # OOP: encapsulation (private attributes) - flips the private _fullscreen flag and applies it
    def _toggle_fullscreen(self, _event: "tk.Event[tk.Misc] | None" = None) -> None:
        """Switch between fullscreen and a normal window."""
        self._fullscreen = not self._fullscreen
        self.attributes("-fullscreen", self._fullscreen)

    def _row_of_tiles(self, parent: tk.Misc, tiles: list[Placeholder], group: str) -> None:
        """Grid tiles left to right in row 0 of parent, in equal-width columns."""
        for column, tile in enumerate(tiles):
            parent.columnconfigure(column, weight=1, uniform=group)
            tile.grid(row=0, column=column, sticky="nsew",
                      padx=theme.PAD_SMALL, pady=theme.PAD_SMALL)

    def _build_top_bar(self) -> tk.Frame:
        """Thin bar: app name on the left, three chips on the right."""
        bar = tk.Frame(self, bg=theme.PANEL)
        bar.rowconfigure(0, weight=1)
        bar.columnconfigure(0, weight=1)
        tk.Label(bar, text="SwitchSpeak", bg=theme.PANEL, fg=theme.CELL_TEXT,
                 font=theme.font("heading", self._scale), bd=0, pady=0).grid(
            row=0, column=0, sticky="w", padx=theme.PAD_LARGE)
        chips = ("chip: switch ok", "chip: mode", "chip: speed")
        for column, name in enumerate(chips, start=1):
            bar.columnconfigure(column, weight=0)
            Placeholder(bar, name, role="chip", scale=self._scale, ring_width=0).grid(
                row=0, column=column, sticky="nsew", padx=(0, theme.PAD_SMALL), pady=theme.PAD_SMALL)
        return bar

    def _build_message_bar(self) -> tk.Frame:
        """Tall, full-width bar for the typed message, text starting on the left."""
        return Placeholder(self, "message bar", bg=theme.PANEL, role="message",
                           ring=theme.BACKGROUND, sticky="w", scale=self._scale)

    def _build_suggestions(self) -> tk.Frame:
        """Four equal word slots; the last is shown dimmed as an empty slot."""
        row = tk.Frame(self, bg=theme.BACKGROUND)
        row.rowconfigure(0, weight=1)
        tiles = [Placeholder(row, f"word {i}", ring=theme.BACKGROUND, scale=self._scale)
                 for i in range(theme.MAX_SUGGESTIONS - 1)]
        tiles.append(Placeholder(row, "empty slot", bg=theme.EMPTY_CELL, fg=theme.DIM_TEXT,
                                 ring=theme.BACKGROUND, scale=self._scale))
        self._row_of_tiles(row, tiles, "suggestions")
        return row

    def _build_middle(self) -> tk.Frame:
        """Two columns, 60% / 40%: letters grid on the left, YES/NO and phrases on the right."""
        middle = tk.Frame(self, bg=theme.BACKGROUND)
        middle.rowconfigure(0, weight=1)
        for column, weight in enumerate(MIDDLE_COLUMNS):
            middle.columnconfigure(column, weight=weight, uniform="middle")
        self._build_letters(middle).grid(row=0, column=0, sticky="nsew", padx=(0, theme.PAD_MEDIUM))
        self._build_phrases(middle).grid(row=0, column=1, sticky="nsew")
        return middle

    def _build_letters(self, parent: tk.Misc) -> tk.Frame:
        """5 x 6 grid of equal cells, each labelled 'row,column'."""
        grid = tk.Frame(parent, bg=theme.PANEL)
        for r in range(theme.GRID_ROWS):
            grid.rowconfigure(r, weight=1, uniform="letter_rows")
        for c in range(theme.GRID_COLS):
            grid.columnconfigure(c, weight=1, uniform="letter_cols")
        for r in range(theme.GRID_ROWS):
            for c in range(theme.GRID_COLS):
                Placeholder(grid, f"{r},{c}", role="cell", scale=self._scale).grid(
                    row=r, column=c, sticky="nsew", padx=theme.PAD_SMALL, pady=theme.PAD_SMALL)
        return grid

    def _build_phrases(self, parent: tk.Misc) -> tk.Frame:
        """YES/NO on top, then category tabs, 8 phrases (4 rows x 2) and EMERGENCY across the bottom."""
        panel = tk.Frame(parent, bg=theme.PANEL)
        for row, (_name, weight) in enumerate(PHRASES_ROWS):
            panel.rowconfigure(row, weight=weight)
        for column in range(PHRASE_COLUMNS):
            panel.columnconfigure(column, weight=1, uniform="phrase_cols")
        cell = {"sticky": "nsew", "padx": theme.PAD_SMALL, "pady": theme.PAD_SMALL}

        Placeholder(panel, "YES", bg=theme.GREEN, scale=self._scale).grid(row=0, column=0, **cell)
        Placeholder(panel, "NO", bg=theme.RED_BROWN, scale=self._scale).grid(row=0, column=1, **cell)

        tabs = tk.Frame(panel, bg=theme.PANEL)
        tabs.grid(row=1, column=0, columnspan=PHRASE_COLUMNS, sticky="nsew")
        tabs.rowconfigure(0, weight=1)
        tab_tiles = [Placeholder(tabs, "tab 0", bg=theme.TEAL, role="heading", scale=self._scale)]
        tab_tiles += [Placeholder(tabs, f"tab {i}", role="heading", scale=self._scale)
                     for i in range(1, theme.MAX_CATEGORIES)]
        self._row_of_tiles(tabs, tab_tiles, "tabs")

        first_phrase_row = 2
        for i in range(theme.MAX_PHRASES):
            Placeholder(panel, f"phrase {i}", role="phrase", scale=self._scale).grid(
                row=first_phrase_row + i // PHRASE_COLUMNS, column=i % PHRASE_COLUMNS, **cell)

        Placeholder(panel, "EMERGENCY", bg=theme.RED, role="heading", scale=self._scale).grid(
            row=len(PHRASES_ROWS) - 1, column=0, columnspan=PHRASE_COLUMNS, **cell)
        return panel

    def _build_actions(self) -> tk.Frame:
        """Four equal action tiles: SPEAK, BACKSPACE, CLEAR, PAUSE."""
        row = tk.Frame(self, bg=theme.BACKGROUND)
        row.rowconfigure(0, weight=1)
        tiles = [Placeholder(row, "SPEAK", bg=theme.GREEN, ring=theme.BACKGROUND, scale=self._scale)]
        tiles += [Placeholder(row, name, ring=theme.BACKGROUND, scale=self._scale)
                  for name in ("BACKSPACE", "CLEAR", "PAUSE")]
        self._row_of_tiles(row, tiles, "actions")
        return row

    def _build_status_line(self) -> tk.Frame:
        """Thin line of status text along the bottom."""
        line = tk.Frame(self, bg=theme.BACKGROUND)
        line.columnconfigure(0, weight=1)
        tk.Label(line, text="status line", bg=theme.BACKGROUND, fg=theme.CELL_TEXT,
                 font=theme.font("status", self._scale), bd=0, pady=0).grid(
            row=0, column=0, sticky="w", padx=theme.PAD_MEDIUM)
        return line


def main() -> None:
    """Open the layout window; F11 toggles fullscreen."""
    LayoutWindow().mainloop()


if __name__ == "__main__":
    main()
