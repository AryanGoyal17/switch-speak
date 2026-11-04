"""MessageBar: shows the typed message with a blinking cursor, newest letters always visible. Owner: Member 2."""

import tkinter as tk
import tkinter.font as tkfont
from typing import Callable

from switchspeak.ui import theme

PLACEHOLDER = "Select a letter to begin..."
CURSOR = "|"
ELLIPSIS = "..."
MAX_LINES = 2
CURSOR_BLINK_MS = 600


class MessageBar(tk.Frame):
    """Display-only bar for the typed message: at most 2 lines, newest letters always visible."""

    def __init__(self, parent: tk.Misc, scale: float = 1.0) -> None:
        super().__init__(parent, bg=theme.PANEL)
        self._text = ""
        self._fitted = ""
        self._cursor_on = True
        self._blink_id: str | None = None
        self._width = 0
        self._font = tkfont.Font(root=self, font=theme.font("message", scale))
        self._char_widths: dict[str, int] = {}

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self._label = tk.Label(
            self, bg=theme.PANEL, fg=theme.DIM_TEXT, font=self._font, width=1, height=MAX_LINES,
            anchor="nw", justify="left", bd=0, padx=0, pady=0, highlightthickness=0,
        )
        self._label.grid(row=0, column=0, sticky="ew", padx=theme.PAD_LARGE, pady=theme.PAD_MEDIUM)
        self._label.bind("<Configure>", self._on_resize)
        self.set_text("")

    @property
    def text(self) -> str:
        """The full message last given to set_text, never shortened."""
        return self._text

    def set_text(self, text: str) -> None:
        """Show text followed by a blinking cursor, or a dim placeholder when text is empty."""
        self._text = text
        self._stop_blink()
        if not text:
            self._label.configure(text=PLACEHOLDER, fg=theme.DIM_TEXT)
            return
        self._label.configure(fg=theme.CELL_TEXT)
        self._refit()
        self._cursor_on = True
        self._draw()
        self._blink_id = self.after(CURSOR_BLINK_MS, self._blink)

    def destroy(self) -> None:
        """Cancel the blink timer, then destroy the bar."""
        self._stop_blink()
        super().destroy()

    def _blink(self) -> None:
        """Show or hide the cursor, then schedule the next blink."""
        self._cursor_on = not self._cursor_on
        self._draw()
        self._blink_id = self.after(CURSOR_BLINK_MS, self._blink)

    def _stop_blink(self) -> None:
        """Cancel the pending blink, if any."""
        if self._blink_id is not None:
            self.after_cancel(self._blink_id)
            self._blink_id = None

    def _draw(self) -> None:
        """Put the fitted text on the label; the cursor is its last character, so hiding it moves nothing."""
        shown = self._fitted if self._cursor_on else self._fitted[: -len(CURSOR)]
        self._label.configure(text=shown)

    def _on_resize(self, event: "tk.Event[tk.Label]") -> None:
        """Refit the text when the label's width changes."""
        if event.width == self._width:
            return
        self._width = event.width
        if self._text:
            self._refit()
            self._draw()

    def _refit(self) -> None:
        """Wrap text + cursor onto MAX_LINES lines; if too long, keep the end and put '...' in front."""
        if self._width <= 1:
            self._fitted = self._text + CURSOR
            return
        lines = self._wrap(self._text + CURSOR, self._width, self._measure)
        if len(lines) > MAX_LINES:
            low, high = 1, len(self._text)
            while low < high:
                mid = (low + high) // 2
                tail = ELLIPSIS + self._text[mid:] + CURSOR
                if len(self._wrap(tail, self._width, self._measure)) <= MAX_LINES:
                    high = mid
                else:
                    low = mid + 1
            lines = self._wrap(ELLIPSIS + self._text[low:] + CURSOR, self._width, self._measure)
        self._fitted = "\n".join(lines[-MAX_LINES:])

    def _measure(self, chars: str) -> int:
        """Width of chars in pixels, using a per-character cache so refitting stays fast."""
        total = 0
        for ch in chars:
            if ch not in self._char_widths:
                self._char_widths[ch] = self._font.measure(ch)
            total += self._char_widths[ch]
        return total

    @staticmethod
    def _wrap(text: str, width: int, measure: Callable[[str], int]) -> list[str]:
        """Split text into lines no wider than width: break after a space when possible, mid-word if not."""
        lines: list[str] = []
        line = ""
        for ch in text:
            if ch != " " and line and measure(line + ch) > width:
                cut = line.rfind(" ") + 1
                if cut == 0 or measure(line[cut:] + ch) > width:
                    cut = len(line)
                lines.append(line[:cut])
                line = line[cut:]
            line += ch
        lines.append(line)
        return lines
