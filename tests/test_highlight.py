"""Tests for HighlightManager using fake panels and borders (no Tk window). Owner: Member 1."""

import unittest
from typing import Any

from switchspeak.ui import theme
from switchspeak.ui.contract import ZONES
from switchspeak.ui.highlight import HighlightManager

SOFT_RING = theme.highlight_style(theme.LEVEL_SOFT)["ring"]
NORMAL_RING = theme.highlight_style(theme.LEVEL_NORMAL)["ring"]


# OOP: polymorphism - answers the same method names as the real panels, so HighlightManager cannot tell the difference
class FakePanel:
    """Stands in for a panel: counts items, remembers if it is lit and logs every call."""

    def __init__(self, zone: str, count: int, log: list[tuple[Any, ...]]) -> None:
        """Start unlit with count items, writing every call to the shared log."""
        self.zone = zone
        self.count = count
        self.lit = False
        self.log = log

    def item_count(self) -> int:
        """Return the fixed number of items."""
        return self.count

    def highlight_item(self, i: int) -> None:
        """Record that item i was lit."""
        self.lit = True
        self.log.append((self.zone, "item", i))

    def highlight_row(self, r: int) -> None:
        """Record that row r was lit."""
        self.lit = True
        self.log.append((self.zone, "row", r))

    def highlight_cell(self, r: int, c: int) -> None:
        """Record that cell (r, c) was lit."""
        self.lit = True
        self.log.append((self.zone, "cell", r, c))

    def clear(self) -> None:
        """Record that the panel was cleared."""
        self.lit = False
        self.log.append((self.zone, "clear"))


# OOP: polymorphism - offers configure() like a tk.Frame, so HighlightManager draws on it exactly as on a real border
class FakeBorder:
    """Stands in for a tk.Frame: keeps the options it was configured with."""

    def __init__(self, zone: str, log: list[tuple[Any, ...]]) -> None:
        """Start with no options, writing every configure call to the shared log."""
        self.zone = zone
        self.options: dict[str, Any] = {}
        self.log = log

    # OOP: encapsulation - read-only property that works out from the stored options whether the border is outlined
    @property
    def lit(self) -> bool:
        """Return True while the outline has the soft highlight colour."""
        return self.options.get("highlightbackground") == SOFT_RING

    def configure(self, **options: Any) -> None:
        """Store the options and log the outline colour."""
        self.options.update(options)
        self.log.append((self.zone, "border", options["highlightbackground"]))


# OOP: inheritance - extends unittest.TestCase so every test class below gets the fake panels and a ready manager
class HighlightTestCase(unittest.TestCase):
    """Builds a manager over four fake panels and four fake borders."""

    COUNTS = {"letters": 30, "suggestions": 2, "phrases": 9, "actions": 4}

    def setUp(self) -> None:
        """Build fresh fakes and a manager, then empty the log."""
        self.log: list[tuple[Any, ...]] = []
        self.panels = {z: FakePanel(z, n, self.log) for z, n in self.COUNTS.items()}
        self.borders = {z: FakeBorder(z, self.log) for z in ZONES}
        self.manager = HighlightManager(self.panels, self.borders)
        self.log.clear()

    def lit_count(self) -> int:
        """Return how many fake panels and borders are lit right now."""
        return sum(p.lit for p in self.panels.values()) + sum(b.lit for b in self.borders.values())


class TestConstruction(HighlightTestCase):
    """A new manager starts with nothing lit and needs every zone."""

    def test_nothing_highlighted_at_start(self) -> None:
        self.assertIsNone(self.manager.current)
        self.assertEqual(self.lit_count(), 0)

    def test_borders_reserve_thickness_in_normal_colour(self) -> None:
        for border in self.borders.values():
            self.assertEqual(border.options["highlightthickness"], theme.BORDER_WIDTH)
            self.assertEqual(border.options["highlightbackground"], NORMAL_RING)

    def test_missing_zone_raises(self) -> None:
        partial = {z: p for z, p in self.panels.items() if z != "actions"}
        with self.assertRaises(ValueError):
            HighlightManager(partial, self.borders)
        with self.assertRaises(ValueError):
            HighlightManager(self.panels, {z: b for z, b in self.borders.items() if z != "phrases"})


class TestDrawing(HighlightTestCase):
    """Each highlight method calls the right panel or border."""

    def test_zone_outlines_border_and_leaves_items_plain(self) -> None:
        self.manager.zone("phrases")
        self.assertEqual(self.borders["phrases"].options["highlightbackground"], SOFT_RING)
        self.assertEqual(self.borders["phrases"].options["highlightthickness"], theme.BORDER_WIDTH)
        self.assertEqual(self.log, [("phrases", "border", SOFT_RING)])
        self.assertFalse(any(p.lit for p in self.panels.values()))
        self.assertEqual(self.manager.current, ("zone", "phrases"))

    def test_row_cell_and_item_call_the_right_panel(self) -> None:
        self.manager.row(2)
        self.assertEqual(self.log, [("letters", "row", 2)])
        self.assertEqual(self.manager.current, ("row", 2))
        self.log.clear()
        self.manager.cell(4, 5)
        self.assertEqual(self.log, [("letters", "clear"), ("letters", "cell", 4, 5)])
        self.assertEqual(self.manager.current, ("cell", 4, 5))
        self.log.clear()
        self.manager.item("phrases", 3)
        self.assertEqual(self.log, [("letters", "clear"), ("phrases", "item", 3)])
        self.assertEqual(self.manager.current, ("item", "phrases", 3))

    def test_letters_item_maps_index_to_row_and_column(self) -> None:
        self.manager.item("letters", 13)
        self.assertEqual(self.log, [("letters", "cell", 2, 1)])
        self.assertEqual(self.manager.current, ("item", "letters", 13))


class TestOnlyOneHighlight(HighlightTestCase):
    """Exactly one thing is lit after every call."""

    def test_exactly_one_thing_lit_after_every_call(self) -> None:
        steps = [
            lambda: self.manager.zone("letters"),
            lambda: self.manager.row(1),
            lambda: self.manager.cell(1, 3),
            lambda: self.manager.item("suggestions", 1),
            lambda: self.manager.zone("actions"),
            lambda: self.manager.item("actions", 0),
            lambda: self.manager.item("letters", 29),
            lambda: self.manager.zone("phrases"),
            lambda: self.manager.zone("phrases"),
        ]
        for n, step in enumerate(steps):
            with self.subTest(step=n):
                step()
                self.assertEqual(self.lit_count(), 1)

    def test_only_the_previous_highlight_is_cleared(self) -> None:
        self.manager.item("phrases", 3)
        self.log.clear()
        self.manager.row(0)
        self.assertEqual(self.log, [("phrases", "clear"), ("letters", "row", 0)])

    def test_zone_after_zone_restores_old_border(self) -> None:
        self.manager.zone("letters")
        self.manager.zone("actions")
        self.assertFalse(self.borders["letters"].lit)
        self.assertTrue(self.borders["actions"].lit)

    def test_zone_after_item_clears_the_item(self) -> None:
        self.manager.item("actions", 2)
        self.manager.zone("actions")
        self.assertFalse(self.panels["actions"].lit)
        self.assertTrue(self.borders["actions"].lit)


class TestErrors(HighlightTestCase):
    """Bad zones and indexes raise ValueError and change nothing."""

    def test_bad_calls_raise_value_error(self) -> None:
        bad_calls = {
            "zone unknown": lambda: self.manager.zone("menu"),
            "item unknown zone": lambda: self.manager.item("menu", 0),
            "row negative": lambda: self.manager.row(-1),
            "row too big": lambda: self.manager.row(5),
            "row not int": lambda: self.manager.row("1"),  # type: ignore[arg-type]
            "cell row too big": lambda: self.manager.cell(5, 0),
            "cell column too big": lambda: self.manager.cell(0, 6),
            "cell column negative": lambda: self.manager.cell(0, -1),
            "item negative": lambda: self.manager.item("actions", -1),
            "item too big": lambda: self.manager.item("actions", 4),
            "letters item too big": lambda: self.manager.item("letters", 30),
            "empty suggestion slot": lambda: self.manager.item("suggestions", 2),
            "phrases item too big": lambda: self.manager.item("phrases", 9),
            "item not int": lambda: self.manager.item("actions", 1.5),  # type: ignore[arg-type]
        }
        for name, call in bad_calls.items():
            with self.subTest(name):
                with self.assertRaises(ValueError):
                    call()

    def test_bad_call_leaves_old_highlight_in_place(self) -> None:
        self.manager.item("phrases", 3)
        self.log.clear()
        for call in (lambda: self.manager.row(9), lambda: self.manager.item("phrases", 99),
                     lambda: self.manager.zone("menu")):
            with self.assertRaises(ValueError):
                call()
        self.assertEqual(self.manager.current, ("item", "phrases", 3))
        self.assertTrue(self.panels["phrases"].lit)
        self.assertEqual(self.log, [])


class TestClearAndCurrent(HighlightTestCase):
    """clear() undoes only what was lit; current is read-only."""

    def test_clear_with_nothing_lit_does_nothing(self) -> None:
        self.manager.clear()
        self.assertEqual(self.log, [])
        self.assertIsNone(self.manager.current)

    def test_clear_removes_each_kind_of_highlight(self) -> None:
        for draw in (lambda: self.manager.zone("suggestions"), lambda: self.manager.row(3),
                     lambda: self.manager.cell(0, 0), lambda: self.manager.item("actions", 1)):
            draw()
            self.manager.clear()
            self.assertEqual(self.lit_count(), 0)
            self.assertIsNone(self.manager.current)

    def test_clear_touches_only_what_was_lit(self) -> None:
        self.manager.item("actions", 1)
        self.log.clear()
        self.manager.clear()
        self.assertEqual(self.log, [("actions", "clear")])

    def test_second_clear_is_a_no_op(self) -> None:
        self.manager.item("actions", 1)
        self.manager.clear()
        self.log.clear()
        self.manager.clear()
        self.assertEqual(self.log, [])

    def test_current_is_read_only(self) -> None:
        with self.assertRaises(AttributeError):
            self.manager.current = ("zone", "letters")  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
