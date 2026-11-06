"""Every colour, font, size, padding and border width used by the GUI. Owner: Member 1."""

import tkinter as tk
import tkinter.font as tkfont


BACKGROUND = "#0E1318"
PANEL = "#171E26"
CELL = "#232D3A"
EMPTY_CELL = "#141A21"
CELL_TEXT = "#F4F6F8"
DIM_TEXT = "#98A5B3"

SOFT_HIGHLIGHT = "#34546F"
SOFT_BORDER = "#7BB0DA"
STRONG_HIGHLIGHT = "#FFD60A"
STRONG_TEXT = "#0E1318"
STRONG_BORDER = "#FFFFFF"

GREEN = "#1F7A45"
RED_BROWN = "#8E3A2B"
RED = "#C62828"
TEAL = "#0E7C73"
AMBER = "#F2A93B"


FONT_FAMILY = "Segoe UI"
FONT_FALLBACK = "Helvetica"

FONT_ROLES: dict[str, tuple[int, str]] = {
    "message": (36, "bold"),
    "cell": (24, "bold"),
    "tile": (22, "bold"),
    "phrase": (20, "normal"),
    "chip": (16, "normal"),
    "status": (18, "normal"),
    "heading": (20, "bold"),
}

_resolved_family: str | None = None


def _family() -> str:
    """Return FONT_FAMILY if Tk has it, otherwise FONT_FALLBACK (looked up once a Tk root exists)."""
    global _resolved_family
    if _resolved_family is not None:
        return _resolved_family
    try:
        installed = set(tkfont.families())
    except (RuntimeError, tk.TclError):
        return FONT_FAMILY
    _resolved_family = FONT_FAMILY if FONT_FAMILY in installed else FONT_FALLBACK
    return _resolved_family


def font(role: str, scale: float = 1.0) -> tuple[str, int, str]:
    """Return a (family, size, weight) tuple for a font role, with the size multiplied by scale."""
    if role not in FONT_ROLES:
        raise ValueError(f"unknown font role {role!r}; expected one of {tuple(FONT_ROLES)}")
    size, weight = FONT_ROLES[role]
    return (_family(), max(1, round(size * scale)), weight)



REFERENCE_HEIGHT = 880
REFERENCE_PIXELS_PER_POINT = 96 / 72
SCALE_MIN = 0.8
SCALE_MAX = 1.6


def compute_scale(root: tk.Misc) -> float:
    """Return a font scale from SCALE_MIN to SCALE_MAX: 1.0 at an 880 px high window at 96 DPI, bigger above.

    Fonts are in points, so the height is first converted to 96-DPI pixels; the layout then fits the
    same way whether or not Windows display scaling makes the process DPI-aware.
    Call it once the window has its final size; before it is drawn the screen height is used.
    """
    height = root.winfo_height()
    if height <= 1:
        height = root.winfo_screenheight()
    pixels_per_point = float(root.tk.call("tk", "scaling"))
    height_96dpi = height * REFERENCE_PIXELS_PER_POINT / pixels_per_point
    return round(min(SCALE_MAX, max(SCALE_MIN, height_96dpi / REFERENCE_HEIGHT)), 2)



GRID_ROWS = 5
GRID_COLS = 6
MAX_SUGGESTIONS = 4
MAX_PHRASES = 8
MAX_CATEGORIES = 4
EMERGENCY_SECONDS = 5
MIN_WINDOW = (1100, 740)

PAD_SMALL = 4
PAD_MEDIUM = 8
PAD_LARGE = 16

BORDER_WIDTH = 6


LEVEL_NORMAL = "normal"
LEVEL_SOFT = "soft"
LEVEL_STRONG = "strong"


def highlight_style(
    level: str, base_bg: str = CELL, base_fg: str = CELL_TEXT, ring: str = PANEL
) -> dict[str, str]:
    """Return {'bg', 'fg', 'ring'} colours for a highlight level; ring is the hidden-ring colour."""
    if level == LEVEL_NORMAL:
        return {"bg": base_bg, "fg": base_fg, "ring": ring}
    if level == LEVEL_SOFT:
        return {"bg": SOFT_HIGHLIGHT, "fg": CELL_TEXT, "ring": SOFT_BORDER}
    if level == LEVEL_STRONG:
        return {"bg": STRONG_HIGHLIGHT, "fg": STRONG_TEXT, "ring": STRONG_BORDER}
    raise ValueError(f"unknown highlight level {level!r}; expected normal, soft or strong")



CONTRAST_PAIRS: tuple[tuple[str, str, str, float], ...] = (
    ("letters: cell text on cell", CELL_TEXT, CELL, 7.0),
    ("message: text on panel", CELL_TEXT, PANEL, 7.0),
    ("status: text on background", CELL_TEXT, BACKGROUND, 7.0),
    ("soft highlight: text on tint", CELL_TEXT, SOFT_HIGHLIGHT, 7.0),
    ("strong highlight: dark text on yellow", STRONG_TEXT, STRONG_HIGHLIGHT, 7.0),
    ("SPEAK / YES: text on green", CELL_TEXT, GREEN, 4.5),
    ("NO: text on red-brown", CELL_TEXT, RED_BROWN, 4.5),
    ("EMERGENCY: text on red", CELL_TEXT, RED, 4.5),
    ("active tab: text on teal", CELL_TEXT, TEAL, 4.5),
    ("paused: dark text on amber", STRONG_TEXT, AMBER, 7.0),
    ("dim text on panel", DIM_TEXT, PANEL, 4.5),
    ("dim text on background", DIM_TEXT, BACKGROUND, 4.5),
    ("dim text on empty slot", DIM_TEXT, EMPTY_CELL, 4.5),
)
