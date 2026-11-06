"""TopBar (app name and switch/mode/speed chips) and StatusLine (status text and key hint). Owner: Member 1."""

import tkinter as tk

from switchspeak.ui import theme

APP_NAME = "SwitchSpeak"
DOT = "●"
HINT = "Tap: select   ·   Hold: back   ·   Hold 3 s: emergency"


class TopBar(tk.Frame):
    """Display-only top bar: app name on the left, switch, mode and speed chips on the right."""

    def __init__(self, parent: tk.Misc, scale: float = 1.0) -> None:
        super().__init__(parent, bg=theme.BACKGROUND)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        tk.Label(self, text=APP_NAME, font=theme.font("heading", scale), bg=theme.BACKGROUND,
                 fg=theme.CELL_TEXT, bd=0, pady=0, anchor="w").grid(row=0, column=0, sticky="w",
                                                                   padx=theme.PAD_MEDIUM)

        self._dot, self._switch_text = self._make_chip(1, scale, with_dot=True)
        _, self._mode_text = self._make_chip(2, scale)
        _, self._speed_text = self._make_chip(3, scale)
        self.set_chips("Switch: not connected", False, "Scan: -", 0.0)

    def set_chips(self, switch_text: str, switch_ok: bool, mode_text: str, speed_seconds: float) -> None:
        """Show the switch chip (green dot if switch_ok, else amber), the mode chip and 'Speed: N.N s'."""
        self._dot.configure(fg=theme.GREEN if switch_ok else theme.AMBER)
        self._switch_text.configure(text=switch_text)
        self._mode_text.configure(text=mode_text)
        self._speed_text.configure(text=f"Speed: {speed_seconds:.1f} s")

    def _make_chip(self, column: int, scale: float, with_dot: bool = False) -> tuple[tk.Label, tk.Label]:
        """Build one chip (a panel-coloured frame with an optional dot and a text Label); return (dot, text)."""
        chip = tk.Frame(self, bg=theme.PANEL)
        chip.grid(row=0, column=column, sticky="e", padx=theme.PAD_SMALL, pady=theme.PAD_SMALL)
        font = theme.font("chip", scale)
        dot = tk.Label(chip, text=DOT if with_dot else "", font=font, bg=theme.PANEL, bd=0, pady=0)
        if with_dot:
            dot.grid(row=0, column=0, padx=(theme.PAD_MEDIUM, 0), pady=theme.PAD_SMALL)
        text = tk.Label(chip, font=font, bg=theme.PANEL, fg=theme.CELL_TEXT, bd=0, pady=0)
        text.grid(row=0, column=1, padx=theme.PAD_MEDIUM, pady=theme.PAD_SMALL)
        return dot, text


class StatusLine(tk.Frame):
    """Display-only thin bottom line: dim status text on the left, a fixed key hint on the right."""

    def __init__(self, parent: tk.Misc, scale: float = 1.0) -> None:
        super().__init__(parent, bg=theme.BACKGROUND)
        self.columnconfigure(0, weight=1)
        self._text = tk.Label(self, font=theme.font("status", scale), width=1, bg=theme.BACKGROUND,
                              fg=theme.DIM_TEXT, bd=0, pady=0, anchor="w")
        self._text.grid(row=0, column=0, sticky="ew", padx=theme.PAD_MEDIUM)
        tk.Label(self, text=HINT, font=theme.font("chip", scale), bg=theme.BACKGROUND, fg=theme.DIM_TEXT,
                 bd=0, pady=0, anchor="e").grid(row=0, column=1, sticky="e", padx=theme.PAD_MEDIUM)

    def set_text(self, text: str) -> None:
        """Show one line of status text, left-aligned and dim."""
        self._text.configure(text=text)
