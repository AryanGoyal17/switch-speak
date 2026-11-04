"""EmergencyOverlay: full-screen emergency countdown. Owner: Member 1."""

import tkinter as tk
import tkinter.font as tkfont

from switchspeak.ui import theme

TITLE_TEMPLATE = "SENDING ALERT IN {}"
TITLE_SAMPLE = TITLE_TEMPLATE.format(88)
CANCEL_TEXT = "Press the switch to CANCEL"
FIT_MIN_SCALE = 0.5
FIT_MAX_SCALE = 4.0


# OOP: inheritance - it is a tk.Frame, so Board can place() it over the message area like any widget.
# OOP: composition - it owns two Labels and two Fonts and only changes their text and size.
class EmergencyOverlay(tk.Frame):
    """Display-only solid red cover with 'SENDING ALERT IN n' in huge white text and a cancel hint."""

    # OOP: dunder methods - Python calls __init__ for EmergencyOverlay(parent); it builds both labels once.
    # OOP: encapsulation (private attributes) - the visible flag, seconds and fonts live in `_` attributes.
    def __init__(self, parent: tk.Misc, scale: float = 1.0) -> None:
        super().__init__(
            parent, bg=theme.RED, highlightthickness=theme.BORDER_WIDTH,
            highlightbackground=theme.STRONG_BORDER, highlightcolor=theme.STRONG_BORDER,
        )
        self._visible = False
        self._seconds: int | None = None
        self._title_font = tkfont.Font(font=theme.font("message", scale))
        self._title_size = int(self._title_font.actual("size"))
        self._sub_font = tkfont.Font(font=theme.font("heading", scale))
        self._min_size = theme.font("message", FIT_MIN_SCALE * scale)[1]
        self._max_size = theme.font("message", FIT_MAX_SCALE * scale)[1]

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)
        self._title = tk.Label(
            self, text=TITLE_TEMPLATE.format(theme.EMERGENCY_SECONDS), font=self._title_font, width=1,
            bg=theme.RED, fg=theme.CELL_TEXT, bd=0, padx=theme.PAD_LARGE, pady=0, anchor="center",
        )
        self._title.grid(row=1, column=0, sticky="ew")
        self._hint = tk.Label(
            self, text=CANCEL_TEXT, font=self._sub_font, width=1, bg=theme.RED, fg=theme.CELL_TEXT,
            bd=0, padx=theme.PAD_LARGE, pady=0, anchor="center",
        )
        self._hint.grid(row=2, column=0, sticky="ew", pady=(theme.PAD_SMALL, 0))
        self.bind("<Configure>", self._on_configure)

    # OOP: encapsulation (property) - read-only flag, so only show() and hide() can change visibility.
    @property
    def is_visible(self) -> bool:
        """Return True while the overlay covers its parent."""
        return self._visible

    # OOP: encapsulation (validation) - a bad seconds_left raises ValueError before any widget changes.
    def show(self, seconds_left: int) -> None:
        """Cover the parent and show 'SENDING ALERT IN seconds_left'; call again with a smaller number to count down."""
        if isinstance(seconds_left, bool) or not isinstance(seconds_left, int) or seconds_left < 0:
            raise ValueError(f"seconds_left must be an integer of 0 or more, got {seconds_left!r}")
        if seconds_left != self._seconds:
            self._seconds = seconds_left
            self._title.configure(text=TITLE_TEMPLATE.format(seconds_left))
        if not self._visible:
            self._visible = True
            self.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.lift()

    def hide(self) -> None:
        """Remove the overlay so the area under it shows again; does nothing if it is already hidden."""
        if not self._visible:
            return
        self._visible = False
        self._seconds = None
        self.place_forget()

    def _on_configure(self, _event: "tk.Event[tk.Misc]") -> None:
        """Refit the title when the overlay is resized."""
        self._fit_title()

    def _fit_title(self) -> None:
        """Make the title as large as fits the width and the height left over by the hint, within the size limits."""
        width, height = self.winfo_width(), self.winfo_height()
        if width <= 1 or height <= 1:
            return
        ring = 2 * theme.BORDER_WIDTH
        avail_w = width - ring - 2 * theme.PAD_LARGE
        avail_h = (height - ring - 2 * theme.PAD_MEDIUM - theme.PAD_SMALL
                   - self._sub_font.metrics("linespace"))
        font = self._title_font
        ratio = min(avail_w / font.measure(TITLE_SAMPLE), avail_h / font.metrics("linespace"))
        size = max(self._min_size, min(self._max_size, int(self._title_size * ratio)))
        while size > self._min_size:
            font.configure(size=size)
            if font.measure(TITLE_SAMPLE) <= avail_w and font.metrics("linespace") <= avail_h:
                break
            size -= 1
        font.configure(size=size)
        self._title_size = size
