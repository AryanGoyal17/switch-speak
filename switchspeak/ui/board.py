"""Board: the Tk window that composes all panels and implements the contract. Owner: Member 1."""

import tkinter as tk
from collections.abc import Sequence
from typing import Any

from switchspeak.ui import theme
from switchspeak.ui.action_bar import ActionBar
from switchspeak.ui.contract import BoardAPI, check_zone
from switchspeak.ui.emergency_overlay import EmergencyOverlay
from switchspeak.ui.highlight import HighlightManager
from switchspeak.ui.letter_grid import LetterGrid
from switchspeak.ui.message_bar import MessageBar
from switchspeak.ui.phrases_panel import PhrasesPanel
from switchspeak.ui.status_bar import StatusLine, TopBar
from switchspeak.ui.suggestions import SuggestionRow

APP_TITLE = "SwitchSpeak"
ROOT_ROW_WEIGHTS = (0, 0, 1, 0)
BODY_COLUMN_WEIGHTS = (1, 1)
LEFT_ROW_WEIGHTS = (0, 1)
RESCALE_MS = 150


# OOP: inheritance - Board extends BoardAPI, so it is a board and must fill in every contract method
# OOP: polymorphism - it answers the same 16 calls as ConsoleBoard, so the app works with either board
# OOP: composition - it owns the top bar, message bar, four zone panels, status line, overlay and HighlightManager
class Board(BoardAPI):
    """The real Tk board: lays out every panel in the root window and forwards each contract call to one of them."""

    # OOP: dunder methods - Python calls __init__ for Board(root, grid); it builds every panel once
    # OOP: encapsulation - the panels, the scale and the last value of every set_* call live in _ attributes
    def __init__(self, root: tk.Misc, grid: list[list[str]]) -> None:
        """Build the window over root with grid as the 5 x 6 letters, and rescale it when root is resized."""
        self._root = root
        self._grid = [list(row) for row in grid]
        self._message = ""
        self._words: list[str] = []
        self._categories: list[str] = []
        self._active = 0
        self._phrases: list[str] = []
        self._chips: tuple[str, bool, str, float] | None = None
        self._status = ""
        self._paused = False
        self._emergency: int | None = None
        self._rescale_id: str | None = None
        self._frame: tk.Frame | None = None

        if isinstance(root, (tk.Tk, tk.Toplevel)):
            root.title(APP_TITLE)
            root.minsize(*theme.MIN_WINDOW)
        root.configure(bg=theme.BACKGROUND)
        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)
        root.update_idletasks()
        self._scale = theme.compute_scale(root)
        self._build(None)
        root.bind("<Configure>", self._on_configure, add="+")
        root.bind("<Destroy>", self._on_destroy, add="+")

    # ---- content -------------------------------------------------------------------------------

    def set_message(self, text: str) -> None:
        """Show the typed message in the message bar."""
        self._message_bar.set_text(text)
        self._message = text

    def set_suggestions(self, words: Sequence[str]) -> None:
        """Show up to 4 words; drop the highlight if its word is gone or changed."""
        before = self._suggestions.item_labels()
        self._suggestions.set_words(words)
        self._words = list(words)
        self._drop_stale_highlight("suggestions", before)

    def set_phrase_categories(self, names: Sequence[str], active: int) -> None:
        """Show up to 4 category tabs with tab active marked; drop the highlight if its item moved."""
        before = self._phrases_panel.item_labels()
        self._phrases_panel.set_categories(names, active)
        self._categories, self._active = list(names), active
        self._drop_stale_highlight("phrases", before)

    def set_phrases(self, texts: Sequence[str]) -> None:
        """Show up to 8 phrase rows; drop the highlight if its item is gone or changed."""
        before = self._phrases_panel.item_labels()
        self._phrases_panel.set_phrases(texts)
        self._phrases = list(texts)
        self._drop_stale_highlight("phrases", before)

    def set_chips(self, switch_text: str, switch_ok: bool, mode_text: str, speed_seconds: float) -> None:
        """Show the switch, mode and speed chips in the top bar."""
        self._top_bar.set_chips(switch_text, switch_ok, mode_text, speed_seconds)
        self._chips = (switch_text, switch_ok, mode_text, speed_seconds)

    def set_status(self, text: str) -> None:
        """Show one line of status text in the status line."""
        self._status_line.set_text(text)
        self._status = text

    def set_paused(self, flag: bool) -> None:
        """Show or hide the paused state on the PAUSE tile."""
        self._action_bar.set_paused(flag)
        self._paused = bool(flag)

    # ---- zones ---------------------------------------------------------------------------------

    def item_count(self, zone: str) -> int:
        """Return how many scannable items the zone's panel has."""
        check_zone(zone)
        return self._panels[zone].item_count()

    def item_labels(self, zone: str) -> list[str]:
        """Return the zone's item labels in scan order, from its panel."""
        check_zone(zone)
        return self._panels[zone].item_labels()

    # ---- highlight -----------------------------------------------------------------------------

    def highlight_zone(self, zone: str) -> None:
        """Replace the highlight with a thick outline round a zone."""
        self._manager.zone(zone)

    def highlight_row(self, r: int) -> None:
        """Replace the highlight with a soft highlight on letters row r."""
        self._manager.row(r)

    def highlight_cell(self, r: int, c: int) -> None:
        """Replace the highlight with a strong highlight on letters cell (r, c)."""
        self._manager.cell(r, c)

    def highlight_item(self, zone: str, i: int) -> None:
        """Replace the highlight with a strong highlight on item i of a zone."""
        self._manager.item(zone, i)

    def clear_highlight(self) -> None:
        """Leave nothing highlighted."""
        self._manager.clear()

    # ---- emergency -----------------------------------------------------------------------------

    def show_emergency(self, seconds_left: int) -> None:
        """Clear the highlight, then cover the message area with the countdown at seconds_left."""
        self.clear_highlight()
        self._overlay.show(seconds_left)
        self._emergency = seconds_left

    def hide_emergency(self) -> None:
        """Remove the emergency overlay."""
        self._overlay.hide()
        self._emergency = None

    # ---- building and rescaling ----------------------------------------------------------------

    def _build(self, lit: tuple[str | int, ...] | None) -> None:
        """Build every panel at the current scale, replacing any older set, then replay the last state and lit."""
        if self._frame is not None:
            self._frame.destroy()
        self._frame = tk.Frame(self._root, bg=theme.BACKGROUND)
        self._frame.grid(row=0, column=0, sticky="nsew")
        self._frame.columnconfigure(0, weight=1)
        for row, weight in enumerate(ROOT_ROW_WEIGHTS):
            self._frame.rowconfigure(row, weight=weight)

        scale = self._scale
        self._top_bar = TopBar(self._frame, scale)
        message_area = tk.Frame(self._frame, bg=theme.PANEL)
        message_area.rowconfigure(0, weight=1)
        message_area.columnconfigure(0, weight=1)
        self._message_bar = MessageBar(message_area, scale)
        self._message_bar.grid(row=0, column=0, sticky="nsew")
        self._overlay = EmergencyOverlay(message_area, scale)
        body = tk.Frame(self._frame, bg=theme.BACKGROUND)
        self._status_line = StatusLine(self._frame, scale)

        body.rowconfigure(0, weight=1)
        body.rowconfigure(1, weight=0)
        for column, weight in enumerate(BODY_COLUMN_WEIGHTS):
            body.columnconfigure(column, weight=weight, uniform="body")
        left = tk.Frame(body, bg=theme.BACKGROUND)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, theme.PAD_MEDIUM))
        left.columnconfigure(0, weight=1)
        for row, weight in enumerate(LEFT_ROW_WEIGHTS):
            left.rowconfigure(row, weight=weight)
        suggestions_border = self._border(left)
        self._suggestions = SuggestionRow(suggestions_border, scale)
        letters_border = self._border(left)
        self._letters = LetterGrid(letters_border, self._grid, scale)
        for row, border in enumerate((suggestions_border, letters_border)):
            border.grid(row=row, column=0, sticky="nsew", pady=(0 if row == 0 else theme.PAD_MEDIUM, 0))
        phrases_border = self._border(body)
        self._phrases_panel = PhrasesPanel(phrases_border, scale)
        phrases_border.grid(row=0, column=1, sticky="nsew")
        actions_border = self._border(body)
        self._action_bar = ActionBar(actions_border, scale)
        actions_border.grid(row=1, column=0, columnspan=len(BODY_COLUMN_WEIGHTS), sticky="nsew",
                            pady=(theme.PAD_MEDIUM, 0))
        for panel in (self._suggestions, self._letters, self._action_bar, self._phrases_panel):
            panel.grid(row=0, column=0, sticky="nsew")

        regions = (self._top_bar, message_area, body, self._status_line)
        last = len(regions) - 1
        for row, region in enumerate(regions):
            bottom = theme.PAD_MEDIUM if row == last else 0
            region.grid(row=row, column=0, sticky="nsew", padx=theme.PAD_MEDIUM, pady=(theme.PAD_MEDIUM, bottom))

        self._panels: dict[str, Any] = {
            "letters": self._letters,
            "suggestions": self._suggestions,
            "phrases": self._phrases_panel,
            "actions": self._action_bar,
        }
        borders = {"letters": letters_border, "suggestions": suggestions_border,
                   "phrases": phrases_border, "actions": actions_border}
        self._manager = HighlightManager(self._panels, borders)
        self._replay(lit)

    # OOP: staticmethod - making a border Frame needs only the parent widget, not the board
    @staticmethod
    def _border(parent: tk.Misc) -> tk.Frame:
        """Return a new Frame that holds one zone panel and is the outline HighlightManager draws on."""
        border = tk.Frame(parent, bg=theme.BACKGROUND)
        border.rowconfigure(0, weight=1)
        border.columnconfigure(0, weight=1)
        return border

    def _replay(self, lit: tuple[str | int, ...] | None) -> None:
        """Show the last state again on freshly built panels, including the highlight lit before."""
        self._message_bar.set_text(self._message)
        self._suggestions.set_words(self._words)
        self._phrases_panel.set_categories(self._categories, self._active)
        self._phrases_panel.set_phrases(self._phrases)
        if self._chips is not None:
            self._top_bar.set_chips(*self._chips)
        self._status_line.set_text(self._status)
        self._action_bar.set_paused(self._paused)
        if self._emergency is not None:
            self._overlay.show(self._emergency)
        if lit is None:
            return
        kind = lit[0]
        if kind == "zone":
            self._manager.zone(str(lit[1]))
        elif kind == "row":
            self._manager.row(int(lit[1]))
        elif kind == "cell":
            self._manager.cell(int(lit[1]), int(lit[2]))
        else:
            self._manager.item(str(lit[1]), int(lit[2]))

    def _drop_stale_highlight(self, zone: str, before: list[str]) -> None:
        """Clear the highlight if it was on an item of zone that new content removed or changed."""
        lit = self._manager.current
        if lit is None or lit[0] != "item" or lit[1] != zone:
            return
        i = int(lit[2])
        after = self._panels[zone].item_labels()
        if i >= len(after) or after[i] != before[i]:
            self._manager.clear()

    def _on_configure(self, event: "tk.Event[tk.Misc]") -> None:
        """When root itself is resized, schedule one rescale check unless one is already waiting."""
        if event.widget is self._root and self._rescale_id is None:
            self._rescale_id = self._root.after(RESCALE_MS, self._rescale)

    def _rescale(self) -> None:
        """Recompute the font scale and rebuild the panels only if it changed."""
        self._rescale_id = None
        scale = theme.compute_scale(self._root)
        if scale != self._scale:
            self._scale = scale
            self._build(self._manager.current)

    def _on_destroy(self, event: "tk.Event[tk.Misc]") -> None:
        """Cancel a waiting rescale when root is destroyed, so no timer fires after the window is gone."""
        if event.widget is self._root and self._rescale_id is not None:
            self._root.after_cancel(self._rescale_id)
            self._rescale_id = None

