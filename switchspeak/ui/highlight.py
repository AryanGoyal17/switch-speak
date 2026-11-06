"""HighlightManager: keeps exactly one soft or strong highlight on screen. Owner: Member 1."""

from collections.abc import Mapping
from typing import Any

from switchspeak.ui import theme
from switchspeak.ui.contract import ZONES, check_zone


# OOP: class and object - one HighlightManager object per board remembers the single thing that is lit
# OOP: composition - it holds the four panels and four border frames it is given and hands the drawing to them
class HighlightManager:
    """Guarantees exactly one highlight: clears the previous one, checks the new one, then draws it."""

    # OOP: dunder methods - Python calls __init__ when HighlightManager(panels, borders) is written
    # OOP: encapsulation - the panels, borders and current highlight live in _ attributes only this class changes
    def __init__(self, panels: Mapping[str, Any], borders: Mapping[str, Any]) -> None:
        """Take the panel and border frame of every zone and start with nothing highlighted."""
        for name, group in (("panels", panels), ("borders", borders)):
            missing = [zone for zone in ZONES if zone not in group]
            if missing:
                raise ValueError(f"{name} is missing zone(s) {missing}; expected all of {ZONES}")
        self._panels: dict[str, Any] = {zone: panels[zone] for zone in ZONES}
        self._borders: dict[str, Any] = {zone: borders[zone] for zone in ZONES}
        self._current: tuple[str | int, ...] | None = None
        for zone in ZONES:
            self._paint_border(zone, theme.LEVEL_NORMAL)

    # OOP: encapsulation - read-only property: callers can see what is lit but only the highlight methods change it
    @property
    def current(self) -> tuple[str | int, ...] | None:
        """Return ('zone', z), ('row', r), ('cell', r, c), ('item', z, i) or None."""
        return self._current

    def zone(self, zone: str) -> None:
        """Replace the highlight with a thick outline round a zone; its items stay plain."""
        check_zone(zone)
        self.clear()
        self._paint_border(zone, theme.LEVEL_SOFT)
        self._current = ("zone", zone)

    def row(self, r: int) -> None:
        """Replace the highlight with a soft highlight on letters row r (0-4)."""
        self._check_range(r, theme.GRID_ROWS, "row")
        self.clear()
        self._panels["letters"].highlight_row(r)
        self._current = ("row", r)

    def cell(self, r: int, c: int) -> None:
        """Replace the highlight with a strong highlight on the letters cell at row r, column c."""
        self._check_range(r, theme.GRID_ROWS, "row")
        self._check_range(c, theme.GRID_COLS, "column")
        self.clear()
        self._panels["letters"].highlight_cell(r, c)
        self._current = ("cell", r, c)

    def item(self, zone: str, i: int) -> None:
        """Replace the highlight with a strong highlight on item i of a zone."""
        check_zone(zone)
        self._check_range(i, self._panels[zone].item_count(), "index")
        self.clear()
        if zone == "letters":
            self._panels[zone].highlight_cell(*divmod(i, theme.GRID_COLS))
        else:
            self._panels[zone].highlight_item(i)
        self._current = ("item", zone, i)

    # OOP: polymorphism - clear() is called on whichever panel or border is lit without asking its class
    def clear(self) -> None:
        """Undo only the highlight drawn last, leaving nothing highlighted."""
        current, self._current = self._current, None
        if current is None:
            return
        kind, target = current[0], str(current[1])
        if kind == "zone":
            self._paint_border(target, theme.LEVEL_NORMAL)
        elif kind in ("row", "cell"):
            self._panels["letters"].clear()
        else:
            self._panels[target].clear()

    def _paint_border(self, zone: str, level: str) -> None:
        """Set the outline colour of a zone's border frame, keeping its thickness fixed so nothing moves."""
        ring = theme.highlight_style(level)["ring"]
        self._borders[zone].configure(
            highlightthickness=theme.BORDER_WIDTH, highlightbackground=ring, highlightcolor=ring
        )

    # OOP: staticmethod - the range check needs only the numbers it is given, not the manager or the class
    # OOP: encapsulation - validation runs before anything is cleared, so a bad call leaves the old highlight in place
    @staticmethod
    def _check_range(value: int, limit: int, what: str) -> None:
        """Raise ValueError unless value is an int with 0 <= value < limit."""
        if not isinstance(value, int) or not 0 <= value < limit:
            raise ValueError(f"{what} {value!r} out of range for {limit} item(s)")
