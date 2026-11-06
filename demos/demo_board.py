"""The whole SwitchSpeak story on the full Board, driven by the spacebar only, with a fake scanner."""

import time
import tkinter as tk

from switchspeak.ui.board import Board

LETTERS: tuple[str, ...] = (*"ABCDEFGHIJKLMNOPQRSTUVWXYZ", "SPACE", ".", "?", "BACKSPACE")
GRID: list[list[str]] = [list(LETTERS[r * 6:(r + 1) * 6]) for r in range(5)]
ZONE_ORDER: tuple[str, ...] = ("letters", "suggestions", "phrases", "actions")
CATEGORIES: tuple[str, ...] = ("Needs", "People", "Feelings", "Alerts")
PHRASES: tuple[str, ...] = ("I need water", "I am hungry", "I need the washroom", "I am in pain",
                            "I am feeling cold", "Please call the nurse", "Please call my family", "Thank you")
LONG_MESSAGE = ("I NEED WATER PLEASE AND THEN I WOULD LIKE TO SIT BY THE WINDOW FOR A WHILE "
                "BEFORE MY FAMILY ARRIVES THIS EVENING. THANKS")
DATA_STATES: dict[str, tuple[str, str, list[str]]] = {
    "1": ("Empty state", "", []),
    "2": ("Typing 'I NEED WA'", "I NEED WA", ["WATER", "WAIT", "WALK", "WASH"]),
    "3": ("120-character message", LONG_MESSAGE, ["WINDOW", "WATER"]),
}

SCAN_SECONDS = 1.2
SCAN_MS = int(SCAN_SECONDS * 1000)
SHORT_LIMIT = 0.5
MEDIUM_LIMIT = 2.0
LONG_HOLD_MS = 3000
EMERGENCY_SECONDS = 5
TICK_MS = 1000
RELEASE_SETTLE_MS = 40


# OOP: inheritance - BoardDemo extends tk.Tk, so the demo object is the root window itself
# OOP: composition - it owns a Board and drives it only through the contract, as the real Scanner will
class BoardDemo(tk.Tk):
    """A window with the full Board and a fake one-switch scanner: zone, then row or item, then select."""

    # OOP: dunder methods - Python calls __init__ for BoardDemo(); it builds the board, fills it and starts scanning
    # OOP: encapsulation (private attributes) - the scan level, position, press time and every timer id are private
    def __init__(self) -> None:
        """Build the board, fill it with demo data, bind the spacebar and keys 1-3, and start scanning."""
        super().__init__()
        self._board = Board(self, GRID)
        self.geometry("{}x{}".format(*self.minsize()))
        self._level = "zones"
        self._zone = -1
        self._row = 0
        self._pos = 0
        self._pressed_at: float | None = None
        self._press_used = False
        self._countdown: int | None = None
        self._scan_id: str | None = None
        self._long_id: str | None = None
        self._release_id: str | None = None
        self._tick_id: str | None = None

        self._board.set_phrase_categories(CATEGORIES, 0)
        self._board.set_phrases(PHRASES)
        self._board.set_chips("Switch: Keyboard mode", True, "Scan: Zone > Item", SCAN_SECONDS)
        self._load("2")

        self.bind("<KeyPress-space>", self._on_press)
        self.bind("<KeyRelease-space>", self._on_release)
        for key in DATA_STATES:
            self.bind(f"<KeyPress-{key}>", lambda _event, key=key: self._load(key))
        self._next_zone()
        self._restart_scan()

    # OOP: polymorphism - overrides tk.Tk.destroy to cancel every timer before the window closes
    def destroy(self) -> None:
        """Cancel every timer, then close the window."""
        for timer in (self._scan_id, self._long_id, self._release_id, self._tick_id):
            if timer is not None:
                self.after_cancel(timer)
        self._scan_id = self._long_id = self._release_id = self._tick_id = None
        super().destroy()

    # ---- demo data -----------------------------------------------------------------------------

    def _load(self, key: str) -> None:
        """Switch the message and suggestions to data state 1, 2 or 3 and go back to zone scanning."""
        if self._countdown is not None:
            return
        name, message, words = DATA_STATES[key]
        self._board.set_message(message)
        self._board.set_suggestions(words)
        self._board.set_status(f"Data {key}: {name}. Tap SPACE to enter the highlighted zone.")
        if self._level != "zones":
            self._to_zones()

    # ---- switch timing -------------------------------------------------------------------------

    def _on_press(self, _event: "tk.Event[tk.Misc]") -> None:
        """Start timing a press; a press that only repeats a held key is ignored."""
        if self._release_id is not None:
            self.after_cancel(self._release_id)
            self._release_id = None
            return
        if self._pressed_at is not None:
            return
        self._pressed_at = time.monotonic()
        self._press_used = False
        self._long_id = self.after(LONG_HOLD_MS, self._long_hold)

    def _on_release(self, _event: "tk.Event[tk.Misc]") -> None:
        """Wait a moment before ending the press, so key auto-repeat is not taken for a release."""
        if self._pressed_at is not None and self._release_id is None:
            self._release_id = self.after(RELEASE_SETTLE_MS, self._released)

    def _released(self) -> None:
        """End the press and act on how long it was held: short = select, medium = back, 2-3 s = nothing."""
        self._release_id = None
        if self._long_id is not None:
            self.after_cancel(self._long_id)
            self._long_id = None
        held = time.monotonic() - (self._pressed_at or time.monotonic())
        self._pressed_at = None
        if self._press_used:
            return
        if self._countdown is not None:
            self._cancel_emergency()
        elif held < SHORT_LIMIT:
            self._select()
        elif held <= MEDIUM_LIMIT:
            self._back()

    def _long_hold(self) -> None:
        """The switch has been held for 3 s: start the emergency countdown while it is still down."""
        self._long_id = None
        self._press_used = True
        if self._countdown is None:
            self._start_emergency()

    # ---- fake scanner --------------------------------------------------------------------------

    def _restart_scan(self) -> None:
        """Restart the step timer so the highlight moves SCAN_MS after the latest change."""
        if self._scan_id is not None:
            self.after_cancel(self._scan_id)
        self._scan_id = self.after(SCAN_MS, self._step)

    def _step(self) -> None:
        """Move the highlight one place at the current level, then schedule the next step."""
        self._scan_id = None
        if self._level == "zones":
            self._next_zone()
        elif self._level == "rows":
            self._row = (self._row + 1) % len(GRID)
            self._board.highlight_row(self._row)
        elif self._level == "cells":
            self._pos = (self._pos + 1) % len(GRID[0])
            self._board.highlight_cell(self._row, self._pos)
        else:
            self._pos = (self._pos + 1) % self._board.item_count(ZONE_ORDER[self._zone])
            self._board.highlight_item(ZONE_ORDER[self._zone], self._pos)
        self._scan_id = self.after(SCAN_MS, self._step)

    def _next_zone(self) -> None:
        """Highlight the next zone that has items (an empty suggestions row is skipped)."""
        for _ in ZONE_ORDER:
            self._zone = (self._zone + 1) % len(ZONE_ORDER)
            if self._board.item_count(ZONE_ORDER[self._zone]):
                self._board.highlight_zone(ZONE_ORDER[self._zone])
                return

    def _select(self) -> None:
        """Short press: enter the highlighted zone or row, or choose the highlighted item."""
        zone = ZONE_ORDER[self._zone] if self._zone >= 0 else None
        if zone is None:
            return
        if self._level == "zones":
            self._pos = 0
            if zone == "letters":
                self._level, self._row = "rows", 0
                self._board.highlight_row(0)
            else:
                self._level = "items"
                self._board.highlight_item(zone, 0)
        elif self._level == "rows":
            self._level, self._pos = "cells", 0
            self._board.highlight_cell(self._row, 0)
        else:
            index = self._row * len(GRID[0]) + self._pos if self._level == "cells" else self._pos
            label = self._board.item_labels(zone)[index]
            print(f"Selected: {label}  ({zone} #{index})")
            self._board.set_status(f"Selected: {label}")
            self._to_zones(keep_status=True)
            return
        self._restart_scan()

    def _back(self) -> None:
        """Medium hold: leave the row or zone and scan the zones again."""
        if self._level != "zones":
            self._to_zones()

    def _to_zones(self, keep_status: bool = False) -> None:
        """Go back to zone level with the current zone highlighted."""
        self._level = "zones"
        if self._zone >= 0 and self._board.item_count(ZONE_ORDER[self._zone]):
            self._board.highlight_zone(ZONE_ORDER[self._zone])
        else:
            self._board.clear_highlight()
        if not keep_status:
            self._board.set_status("Back to zones.")
        self._restart_scan()

    # ---- emergency -----------------------------------------------------------------------------

    def _start_emergency(self) -> None:
        """Stop scanning and show the emergency overlay counting down from EMERGENCY_SECONDS."""
        if self._scan_id is not None:
            self.after_cancel(self._scan_id)
            self._scan_id = None
        self._countdown = EMERGENCY_SECONDS
        self._board.show_emergency(self._countdown)
        self._board.set_status("EMERGENCY: tap SPACE to cancel.")
        print("Emergency countdown started")
        self._tick_id = self.after(TICK_MS, self._tick)

    def _tick(self) -> None:
        """Count down by one second; at zero the (fake) alert is sent."""
        self._tick_id = None
        if self._countdown is None:
            return
        self._countdown -= 1
        self._board.show_emergency(self._countdown)
        if self._countdown > 0:
            self._tick_id = self.after(TICK_MS, self._tick)
            return
        print("Emergency alert sent (demo: nothing is really sent)")
        self._end_emergency("Emergency alert sent (demo only).")

    def _cancel_emergency(self) -> None:
        """A tap during the countdown cancels it."""
        if self._tick_id is not None:
            self.after_cancel(self._tick_id)
            self._tick_id = None
        print("Emergency cancelled")
        self._end_emergency("Emergency cancelled.")

    def _end_emergency(self, status: str) -> None:
        """Hide the overlay, show status and resume zone scanning."""
        self._countdown = None
        self._board.hide_emergency()
        self._board.set_status(status)
        self._to_zones(keep_status=True)


def main() -> None:
    """Open the demo: SPACE is the switch, keys 1-3 switch the demo data."""
    print("SPACE: tap = select | hold 0.5-2 s = back | hold 3 s = emergency.  Keys 1/2/3 = demo data.")
    BoardDemo().mainloop()


if __name__ == "__main__":
    main()
