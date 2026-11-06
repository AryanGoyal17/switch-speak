"""PhrasesPanel: YES/NO, category tabs, phrase rows and EMERGENCY. Owner: Member 3."""

import tkinter as tk
import tkinter.font as tkfont
from collections.abc import Sequence

from switchspeak.ui import theme
from switchspeak.ui.contract import EMERGENCY_LABEL, PHRASES_HEAD
from switchspeak.ui.yes_no import YesNoTiles

EMERGENCY_TEXT = "EMERGENCY - CALL HELP"
PHRASE_COLUMNS = 2
PHRASE_LINES = 1
ELLIPSIS = "…"
HEAD = len(PHRASES_HEAD)
ROW_WEIGHTS = (2, 1, 4, 1)


class PhrasesPanel(tk.Frame):
    """Display-only phrases zone: YES/NO, up to 4 category tabs, up to 8 phrase rows, then EMERGENCY."""

    def __init__(self, parent: tk.Misc, scale: float = 1.0) -> None:
        super().__init__(parent, bg=theme.BACKGROUND)
        self._categories: list[str] = []
        self._active = 0
        self._phrases: list[str] = []
        self._highlighted: int | None = None
        self._highlighted_label: str | None = None

        self.columnconfigure(0, weight=1)
        for row, weight in enumerate(ROW_WEIGHTS):
            self.rowconfigure(row, weight=weight)

        self._yes_no = YesNoTiles(self, scale)
        self._yes_no.grid(row=0, column=0, sticky="nsew")
        self._build_tabs(scale)
        self._build_phrase_rows(scale)
        self._build_emergency(scale)

        self.set_categories([], 0)
        self.set_phrases([])

    def set_categories(self, names: Sequence[str], active: int) -> None:
        """Show up to 4 category tabs left to right and colour the tab at index active teal."""
        kept = list(names)[:theme.MAX_CATEGORIES]
        if kept and not 0 <= active < len(kept):
            raise ValueError(f"active category {active!r} out of range for {len(kept)} tab(s)")
        self._categories = kept
        self._active = active if kept else 0
        for t, tab in enumerate(self._tabs):
            if t < len(kept):
                tab.configure(text=kept[t])
                tab.grid()
            else:
                tab.grid_remove()
        self._fit_tab_font()
        self._refresh()

    def set_phrases(self, texts: Sequence[str]) -> None:
        """Fill up to 8 phrase rows in order; the rows beyond the given texts are hidden, not blank."""
        self._phrases = list(texts)[:theme.MAX_PHRASES]
        for i, row in enumerate(self._rows):
            if i < len(self._phrases):
                self._show_phrase(i)
                row.grid()
            else:
                row.grid_remove()
        self._refresh()

    def item_count(self) -> int:
        """Return 2 + tabs + phrases + 1: YES, NO, every tab, every phrase row, EMERGENCY."""
        return HEAD + len(self._categories) + len(self._phrases) + 1

    def item_labels(self) -> list[str]:
        """Return 'YES', 'NO', the tab names, the phrase texts and 'EMERGENCY' in scan order."""
        return [*PHRASES_HEAD, *self._categories, *self._phrases, EMERGENCY_LABEL]

    def highlight_item(self, i: int) -> None:
        """Clear the old highlight, then give item i of the scan order the strong highlight."""
        self._check_index(i)
        self.clear()
        self._highlighted = i
        self._highlighted_label = self.item_labels()[i]
        if i < HEAD:
            self._yes_no.highlight_item(i)
        else:
            self._paint(i)

    def clear(self) -> None:
        """Remove the highlight, if any, from whichever item has it."""
        if self._highlighted is None:
            return
        old, self._highlighted, self._highlighted_label = self._highlighted, None, None
        if old < HEAD:
            self._yes_no.clear()
        else:
            self._paint(old)

    def _build_tabs(self, scale: float) -> None:
        """Build the 4 tab Labels once, equal in width, sharing one font so they always look alike."""
        self._tab_font = tkfont.Font(root=self, font=theme.font("heading", scale))
        self._tab_top = theme.font("heading", scale)[1]
        self._tab_floor = min(self._tab_top, theme.font("chip", scale)[1])
        self._tab_inner = 0
        strip = tk.Frame(self, bg=theme.BACKGROUND)
        strip.grid(row=1, column=0, sticky="nsew")
        height = self._tab_font.metrics("linespace") + 2 * (theme.BORDER_WIDTH + 2 * theme.PAD_SMALL)
        strip.rowconfigure(0, weight=1, minsize=height)
        self._tabs: list[tk.Label] = []
        for t in range(theme.MAX_CATEGORIES):
            strip.columnconfigure(t, weight=1, uniform="phrase_tabs")
            tab = tk.Label(strip, font=self._tab_font, width=1, height=1, anchor="center", bd=0,
                           padx=0, pady=theme.PAD_SMALL, highlightthickness=theme.BORDER_WIDTH)
            tab.grid(row=0, column=t, sticky="nsew", padx=theme.PAD_SMALL, pady=theme.PAD_SMALL)
            tab.bind("<Configure>", self._on_tab_resize)
            self._tabs.append(tab)
        tk.Frame(strip, width=0, height=0, bg=theme.BACKGROUND).grid(row=0, column=theme.MAX_CATEGORIES - 1)

    def _build_phrase_rows(self, scale: float) -> None:
        """Build the 8 phrase Labels once, row-major in PHRASE_COLUMNS columns, each with room for 2 lines."""
        self._phrase_font = tkfont.Font(root=self, font=theme.font("phrase", scale))
        self._phrase_inner = [0] * theme.MAX_PHRASES
        grid = tk.Frame(self, bg=theme.BACKGROUND)
        grid.grid(row=2, column=0, sticky="nsew")
        for column in range(PHRASE_COLUMNS):
            grid.columnconfigure(column, weight=1, uniform="phrase_cols")
        height = (PHRASE_LINES * self._phrase_font.metrics("linespace")
                  + 2 * (theme.BORDER_WIDTH + 2 * theme.PAD_SMALL))
        grid_rows = -(-theme.MAX_PHRASES // PHRASE_COLUMNS)
        for r in range(grid_rows):
            grid.rowconfigure(r, weight=1, uniform="phrase_rows", minsize=height)
        tk.Frame(grid, width=0, height=0, bg=theme.BACKGROUND).grid(row=grid_rows - 1, column=PHRASE_COLUMNS - 1)
        self._rows: list[tk.Label] = []
        for i in range(theme.MAX_PHRASES):
            row = tk.Label(grid, font=self._phrase_font, width=1, height=PHRASE_LINES, anchor="w",
                           justify="left", bd=0, padx=theme.PAD_MEDIUM, pady=theme.PAD_SMALL,
                           highlightthickness=theme.BORDER_WIDTH)
            row.grid(row=i // PHRASE_COLUMNS, column=i % PHRASE_COLUMNS, sticky="nsew",
                     padx=theme.PAD_SMALL, pady=theme.PAD_SMALL)
            row.bind("<Configure>", lambda event, i=i: self._on_row_resize(i, event.width))
            self._rows.append(row)

    def _build_emergency(self, scale: float) -> None:
        """Build the red EMERGENCY tile: one bold line inside one ring."""
        self._emergency = tk.Frame(self, highlightthickness=theme.BORDER_WIDTH)
        self._emergency.grid(row=3, column=0, sticky="nsew", padx=theme.PAD_SMALL, pady=theme.PAD_SMALL)
        self._emergency.columnconfigure(0, weight=1)
        self._emergency.rowconfigure(0, weight=1)
        self._emergency_texts = [
            tk.Label(self._emergency, text=EMERGENCY_TEXT, font=theme.font("heading", scale), width=1,
                     anchor="center", bd=0, pady=theme.PAD_SMALL, padx=theme.PAD_MEDIUM),
        ]
        self._emergency_texts[0].grid(row=0, column=0, sticky="nsew")

    def _show_phrase(self, i: int) -> None:
        """Put phrase i into its row, wrapped to 2 lines for the width the row has now."""
        inner = self._phrase_inner[i]
        text = self._phrases[i]
        if inner > 0:
            text = self._wrap_two_lines(text, self._phrase_font, inner)
        self._rows[i].configure(text=text)

    def _fit_tab_font(self) -> None:
        """Use the heading size if the longest tab name fits, else the largest smaller size that does."""
        if not self._categories or self._tab_inner <= 0:
            return
        for size in range(self._tab_top, self._tab_floor - 1, -1):
            self._tab_font.configure(size=size)
            if max(self._tab_font.measure(name) for name in self._categories) <= self._tab_inner:
                return

    def _on_tab_resize(self, event: "tk.Event[tk.Label]") -> None:
        """Remember how much width a tab has for text and refit the shared tab font when it changes."""
        inner = event.width - 2 * theme.BORDER_WIDTH
        if inner != self._tab_inner:
            self._tab_inner = inner
            self._fit_tab_font()

    def _on_row_resize(self, i: int, width: int) -> None:
        """Re-wrap phrase row i when the width it has for text changes."""
        inner = width - 2 * (theme.BORDER_WIDTH + theme.PAD_MEDIUM)
        if inner != self._phrase_inner[i]:
            self._phrase_inner[i] = inner
            if i < len(self._phrases):
                self._show_phrase(i)

    def _refresh(self) -> None:
        """After new content: drop a highlight whose item is gone or changed, then repaint what changed."""
        labels = self.item_labels()
        if self._highlighted is not None and (
            self._highlighted >= len(labels) or labels[self._highlighted] != self._highlighted_label
        ):
            self._highlighted = self._highlighted_label = None
        for i in range(HEAD, len(labels)):
            self._paint(i)

    def _paint(self, i: int) -> None:
        """Colour item i (a tab, a phrase row or EMERGENCY) for its state: strong if highlighted, else its own."""
        phrase_start = HEAD + len(self._categories)
        emergency = phrase_start + len(self._phrases)
        if i < phrase_start:
            base_bg = theme.TEAL if i - HEAD == self._active else theme.CELL
        elif i < emergency:
            base_bg = theme.CELL
        else:
            base_bg = theme.RED
        if i == self._highlighted:
            style = theme.highlight_style(theme.LEVEL_STRONG)
        else:
            style = theme.highlight_style(theme.LEVEL_NORMAL, base_bg=base_bg, ring=theme.BACKGROUND)
        if i < phrase_start:
            widgets: list[tk.Misc] = [self._tabs[i - HEAD]]
        elif i < emergency:
            widgets = [self._rows[i - phrase_start]]
        else:
            widgets = [self._emergency, *self._emergency_texts]
        for widget in widgets:
            widget.configure(bg=style["bg"])
            if widget not in self._emergency_texts:
                widget.configure(highlightbackground=style["ring"], highlightcolor=style["ring"])
            if widget is not self._emergency:
                widget.configure(fg=style["fg"])

    @staticmethod
    def _wrap_two_lines(text: str, font: tkfont.Font, width: int) -> str:
        """Break text into at most 2 lines no wider than width; what does not fit ends in an ellipsis."""
        lines = [""]
        for word in text.split():
            trial = f"{lines[-1]} {word}".strip()
            if not lines[-1] or font.measure(trial) <= width:
                lines[-1] = trial
            else:
                lines.append(word)
        if len(lines) > PHRASE_LINES:
            lines[PHRASE_LINES - 1:] = [" ".join(lines[PHRASE_LINES - 1:]) + ELLIPSIS]
        for n, line in enumerate(lines):
            while font.measure(line) > width and len(line) > 1:
                line = line[:-2] + ELLIPSIS if line.endswith(ELLIPSIS) else line[:-1] + ELLIPSIS
            lines[n] = line
        return "\n".join(lines)

    def _check_index(self, i: int) -> None:
        """Raise ValueError unless 0 <= i < item_count()."""
        if not isinstance(i, int) or not 0 <= i < self.item_count():
            raise ValueError(f"phrases index {i!r} out of range 0..{self.item_count() - 1}")
