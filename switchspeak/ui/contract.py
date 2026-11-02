"""The GUI contract: BoardAPI, ZONES, check_zone and the text-only ConsoleBoard. Owner: Member 1."""

import string
from abc import ABC, abstractmethod
from collections.abc import Sequence

ZONES: tuple[str, ...] = ("letters", "suggestions", "phrases", "actions")

LETTER_ROWS = 5
LETTER_COLS = 6
MAX_SUGGESTIONS = 4
MAX_CATEGORIES = 4
MAX_PHRASES = 8

LETTER_LABELS: tuple[str, ...] = (*string.ascii_uppercase, "SPACE", ".", "?", "BACKSPACE")
ACTION_LABELS: tuple[str, ...] = ("SPEAK", "BACKSPACE", "CLEAR", "PAUSE")
PHRASES_HEAD: tuple[str, ...] = ("YES", "NO")
EMERGENCY_LABEL = "EMERGENCY"


def check_zone(zone: str) -> None:
    """Raise ValueError if zone is not one of ZONES."""
    if zone not in ZONES:
        raise ValueError(f"unknown zone {zone!r}; expected one of {ZONES}")


def _show(value: object) -> str:
    """Format one call argument for the console log (strings without quotes)."""
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(_show(v) for v in value) + "]"
    return str(value)


# OOP: abstraction (ABC, abstractmethod) - defines the 16 board methods with no code, so every board must supply them
class BoardAPI(ABC):
    """The GUI contract: everything the rest of the app may ask a board to do."""

    @abstractmethod
    def set_message(self, text: str) -> None:
        """Show the typed message so far."""

    @abstractmethod
    def set_suggestions(self, words: Sequence[str]) -> None:
        """Show up to 4 predicted words, left to right; empty slots stay dim."""

    @abstractmethod
    def set_phrase_categories(self, names: Sequence[str], active: int) -> None:
        """Show up to 4 category tabs and mark the tab at index active."""

    @abstractmethod
    def set_phrases(self, texts: Sequence[str]) -> None:
        """Show up to 8 ready-made phrase rows."""

    @abstractmethod
    def set_chips(self, switch_text: str, switch_ok: bool, mode_text: str, speed_seconds: float) -> None:
        """Show the switch state, current mode and scan speed chips."""

    @abstractmethod
    def set_status(self, text: str) -> None:
        """Show one line of status text."""

    @abstractmethod
    def set_paused(self, flag: bool) -> None:
        """Show or hide the paused state."""

    @abstractmethod
    def item_count(self, zone: str) -> int:
        """Return how many scannable items the zone has; ValueError for an unknown zone."""

    @abstractmethod
    def item_labels(self, zone: str) -> list[str]:
        """Return the zone's item labels in scan order; ValueError for an unknown zone."""

    @abstractmethod
    def highlight_zone(self, zone: str) -> None:
        """Softly highlight a whole zone; ValueError for an unknown zone."""

    @abstractmethod
    def highlight_row(self, r: int) -> None:
        """Softly highlight letters row r (0-4); ValueError if out of range."""

    @abstractmethod
    def highlight_cell(self, r: int, c: int) -> None:
        """Strongly highlight the letters cell at row r, column c; ValueError if out of range."""

    @abstractmethod
    def highlight_item(self, zone: str, i: int) -> None:
        """Strongly highlight item i of a zone; ValueError for a bad zone or index."""

    @abstractmethod
    def clear_highlight(self) -> None:
        """Remove the current highlight so nothing is highlighted."""

    @abstractmethod
    def show_emergency(self, seconds_left: int) -> None:
        """Cover the board with the emergency countdown showing seconds_left."""

    @abstractmethod
    def hide_emergency(self) -> None:
        """Remove the emergency overlay."""


# OOP: class and object - a real board object that stands in for the Tk window in tests and demos
# OOP: inheritance - extends BoardAPI, so it is accepted anywhere a board is expected
# OOP: polymorphism - overrides all 16 contract methods, so callers cannot tell it from the Tk Board
class ConsoleBoard(BoardAPI):
    """A board with no window: prints every call and enforces the same rules as the real one."""

    # OOP: dunder methods - __init__ runs when a ConsoleBoard is created and sets its starting state
    # OOP: encapsulation (private attributes) - the _ names mark state that only board methods may change
    def __init__(self) -> None:
        """Start with no suggestions, categories or phrases, and nothing highlighted."""
        self._suggestions: list[str] = []
        self._categories: list[str] = []
        self._phrases: list[str] = []
        self._highlight: tuple[str | int, ...] | None = None
        self._highlight_label: str | None = None

    # OOP: encapsulation (property) - read-only view of the private highlight so tests can check there is only one
    @property
    def current_highlight(self) -> tuple[str | int, ...] | None:
        """Return ('zone', z), ('row', r), ('cell', r, c), ('item', z, i) or None."""
        return self._highlight

    # OOP: staticmethod - the range check needs no board state, so it is a helper that just lives in the class
    # OOP: encapsulation (validation) - rejects a bad row, column or index before any state changes
    @staticmethod
    def _check_range(value: int, limit: int, what: str) -> None:
        """Raise ValueError unless value is an int with 0 <= value < limit."""
        if not isinstance(value, int) or not 0 <= value < limit:
            raise ValueError(f"{what} {value!r} out of range for {limit} item(s)")

    def _log(self, name: str, *args: object) -> None:
        """Print one call in the form '[board] name(arg, arg)'."""
        print(f"[board] {name}({', '.join(_show(a) for a in args)})")

    def _labels(self, zone: str) -> list[str]:
        """Return the scan-order labels of a zone without printing."""
        check_zone(zone)
        if zone == "letters":
            return list(LETTER_LABELS)
        if zone == "suggestions":
            return list(self._suggestions)
        if zone == "phrases":
            return [*PHRASES_HEAD, *self._categories, *self._phrases, EMERGENCY_LABEL]
        return list(ACTION_LABELS)

    def _drop_stale_highlight(self, zone: str) -> None:
        """Clear the highlight if it was on an item of zone that is gone or has changed."""
        h = self._highlight
        if h is None or h[0] != "item" or h[1] != zone:
            return
        labels = self._labels(zone)
        if h[2] >= len(labels) or labels[h[2]] != self._highlight_label:
            self._highlight = None
            self._highlight_label = None
            print("[board] (stale highlight cleared)")

    def set_message(self, text: str) -> None:
        """Print the message that would be shown."""
        self._log("set_message", text)

    def set_suggestions(self, words: Sequence[str]) -> None:
        """Keep the first 4 slots and drop empty ones, so empty slots are not counted."""
        self._log("set_suggestions", list(words))
        self._suggestions = [w for w in list(words)[:MAX_SUGGESTIONS] if w.strip()]
        self._drop_stale_highlight("suggestions")

    def set_phrase_categories(self, names: Sequence[str], active: int) -> None:
        """Keep up to 4 tab names; ValueError if active is not one of them."""
        self._log("set_phrase_categories", list(names), active)
        kept = list(names)[:MAX_CATEGORIES]
        if kept:
            self._check_range(active, len(kept), "active category")
        self._categories = kept
        self._drop_stale_highlight("phrases")

    def set_phrases(self, texts: Sequence[str]) -> None:
        """Keep up to 8 phrase rows."""
        self._log("set_phrases", list(texts))
        self._phrases = list(texts)[:MAX_PHRASES]
        self._drop_stale_highlight("phrases")

    def set_chips(self, switch_text: str, switch_ok: bool, mode_text: str, speed_seconds: float) -> None:
        """Print the chips that would be shown."""
        self._log("set_chips", switch_text, switch_ok, mode_text, speed_seconds)

    def set_status(self, text: str) -> None:
        """Print the status line that would be shown."""
        self._log("set_status", text)

    def set_paused(self, flag: bool) -> None:
        """Print the paused state that would be shown."""
        self._log("set_paused", flag)

    def item_count(self, zone: str) -> int:
        """Return the number of scannable items in the zone."""
        self._log("item_count", zone)
        return len(self._labels(zone))

    def item_labels(self, zone: str) -> list[str]:
        """Return the zone's labels in scan order."""
        self._log("item_labels", zone)
        return self._labels(zone)

    def highlight_zone(self, zone: str) -> None:
        """Replace any highlight with a soft highlight on the zone."""
        self._log("highlight_zone", zone)
        check_zone(zone)
        self._highlight = ("zone", zone)
        self._highlight_label = None

    def highlight_row(self, r: int) -> None:
        """Replace any highlight with a soft highlight on a letters row."""
        self._log("highlight_row", r)
        self._check_range(r, LETTER_ROWS, "row")
        self._highlight = ("row", r)
        self._highlight_label = None

    def highlight_cell(self, r: int, c: int) -> None:
        """Replace any highlight with a strong highlight on one letters cell."""
        self._log("highlight_cell", r, c)
        self._check_range(r, LETTER_ROWS, "row")
        self._check_range(c, LETTER_COLS, "column")
        self._highlight = ("cell", r, c)
        self._highlight_label = None

    def highlight_item(self, zone: str, i: int) -> None:
        """Replace any highlight with a strong highlight on item i of the zone."""
        self._log("highlight_item", zone, i)
        labels = self._labels(zone)
        self._check_range(i, len(labels), "index")
        self._highlight = ("item", zone, i)
        self._highlight_label = labels[i]

    def clear_highlight(self) -> None:
        """Leave nothing highlighted."""
        self._log("clear_highlight")
        self._highlight = None
        self._highlight_label = None

    def show_emergency(self, seconds_left: int) -> None:
        """Print the emergency countdown that would be shown."""
        self._log("show_emergency", seconds_left)

    def hide_emergency(self) -> None:
        """Print that the emergency overlay would be removed."""
        self._log("hide_emergency")


if __name__ == "__main__":
    board = ConsoleBoard()
    board.set_message("I am thirsty")
    board.set_suggestions(["water", "want", "", "what"])
    board.set_phrase_categories(["Needs", "Feelings"], 0)
    board.set_phrases(["I am thirsty", "I am cold"])
    board.set_chips("Switch OK", True, "Scanning", 1.5)
    board.set_status("Ready")
    board.set_paused(False)
    print("  ->", board.item_count("phrases"))
    print("  ->", board.item_labels("phrases"))
    board.highlight_zone("phrases")
    board.highlight_row(1)
    board.highlight_cell(1, 2)
    board.highlight_item("phrases", 3)
    print("  ->", board.current_highlight)
    board.clear_highlight()
    board.show_emergency(5)
    board.hide_emergency()
    try:
        board.highlight_item("nowhere", 0)
    except ValueError as error:
        print("  -> ValueError:", error)
