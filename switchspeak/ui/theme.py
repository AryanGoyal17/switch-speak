"""Every colour, font, size, padding and border width used by the GUI. Owner: Member 1."""

import tkinter as tk
import tkinter.font as tkfont

# ---------------------------------------------------------------------------
# Colours: a calm dark theme with a cool blue-grey base and warm accents.
# ---------------------------------------------------------------------------

BACKGROUND = "#0E1318"        # window background
PANEL = "#171E26"             # panels and the message bar
CELL = "#232D3A"              # a normal item (letter, word, phrase, action)
EMPTY_CELL = "#141A21"        # an empty suggestion slot (kept in place, dimmed)
CELL_TEXT = "#F4F6F8"         # text on cells, panels and coloured fills
DIM_TEXT = "#98A5B3"          # empty slots, hints, secondary text

SOFT_HIGHLIGHT = "#34546F"    # tinted background: brighter than CELL, text stays readable
SOFT_BORDER = "#7BB0DA"       # ring colour of a softly highlighted item
STRONG_HIGHLIGHT = "#FFD60A"  # bright accent background of the chosen item
STRONG_TEXT = "#0E1318"       # dark text on STRONG_HIGHLIGHT and AMBER
STRONG_BORDER = "#FFFFFF"     # ring colour of the chosen item

GREEN = "#1F7A45"             # SPEAK and YES
RED_BROWN = "#8E3A2B"         # NO
RED = "#C62828"               # EMERGENCY
TEAL = "#0E7C73"              # active category tab
AMBER = "#F2A93B"             # paused

# ---------------------------------------------------------------------------
# Fonts: sizes are points at scale 1.0 (a 768 px high window).
# ---------------------------------------------------------------------------

FONT_FAMILY = "Segoe UI"
FONT_FALLBACK = "Helvetica"

# role -> (size at scale 1.0, weight). For the huge emergency countdown use
# font("heading", scale * 5) so the size still follows the screen.
FONT_ROLES: dict[str, tuple[int, str]] = {
    "message": (36, "bold"),    # the typed message
    "cell": (24, "bold"),       # letters grid cells
    "tile": (22, "bold"),       # suggestions, YES/NO, actions
    "phrase": (20, "normal"),   # phrase rows
    "chip": (16, "normal"),     # switch / mode / speed chips
    "status": (18, "normal"),   # status line
    "heading": (20, "bold"),    # category tabs, EMERGENCY, overlay text
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
        return FONT_FAMILY  # no Tk root yet: do not remember this answer
    _resolved_family = FONT_FAMILY if FONT_FAMILY in installed else FONT_FALLBACK
    return _resolved_family


def font(role: str, scale: float = 1.0) -> tuple[str, int, str]:
    """Return a (family, size, weight) tuple for a font role, with the size multiplied by scale."""
    if role not in FONT_ROLES:
        raise ValueError(f"unknown font role {role!r}; expected one of {tuple(FONT_ROLES)}")
    size, weight = FONT_ROLES[role]
    return (_family(), max(1, round(size * scale)), weight)


# ---------------------------------------------------------------------------
# Scale: fonts grow on big screens.
# ---------------------------------------------------------------------------

REFERENCE_HEIGHT = 768
SCALE_MIN = 0.8
SCALE_MAX = 1.6


def compute_scale(root: tk.Misc) -> float:
    """Return a font scale from SCALE_MIN to SCALE_MAX: 1.0 at a 768 px high window, bigger above.

    Call it once the window has its final size; before it is drawn the screen height is used.
    """
    height = root.winfo_height()
    if height <= 1:
        height = root.winfo_screenheight()
    return round(min(SCALE_MAX, max(SCALE_MIN, height / REFERENCE_HEIGHT)), 2)


# ---------------------------------------------------------------------------
# Layout, spacing and borders
# ---------------------------------------------------------------------------

GRID_ROWS = 5
GRID_COLS = 6
MAX_SUGGESTIONS = 4
MAX_PHRASES = 8
MAX_CATEGORIES = 4
EMERGENCY_SECONDS = 5
MIN_WINDOW = (1100, 700)

PAD_SMALL = 4
PAD_MEDIUM = 8
PAD_LARGE = 16

# Every item reserves this ring all the time (invisible when normal) so
# highlighting never changes an item's size and nothing moves while scanning.
BORDER_WIDTH = 6

# ---------------------------------------------------------------------------
# Highlight rules: the ONE place that decides how an item looks.
#   normal = the item's own colours, ring hidden
#   soft   = tinted, brighter background + mid-tone ring (a zone or a row)
#   strong = bright accent background + dark text + thick bright ring (chosen item)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Contrast pairs for demos/check_contrast.py: (name, text, background, minimum ratio)
# ---------------------------------------------------------------------------

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
