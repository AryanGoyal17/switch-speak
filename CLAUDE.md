# SwitchSpeak — Project Handbook

Read this whole file at the start of every session. It replaces the context block
the team used to paste. If something here conflicts with a direct instruction from
the person you are working with, the direct instruction wins.

---

## 1. Project summary

**SwitchSpeak** is a one-switch communication board for people who cannot speak
and cannot use their hands. It is an Object-Oriented Programming lab project
(Python 3.10+), built with **plain Tkinter only**.

**The one-switch idea.** The user never points, clicks or types. A highlight moves
across the screen by itself (scanning). When the highlight is on what the user
wants, they press their **single switch**. Scanning is two-step: first a zone or
row is softly highlighted, a press enters it, then single items are highlighted
strongly, a press chooses one. Everything the user can do must be reachable this
way.

**Press vocabulary** (the only three things a switch can say):

| Press | Duration | Meaning |
|---|---|---|
| Short press | under 0.5 s | **Select** whatever is highlighted |
| Medium hold | 0.5 s to 2 s | **Go back** one level (leave the row or zone) |
| Long hold | 3 s or more | **Emergency** (shows the emergency countdown) |

Holds between 2 s and 3 s mean nothing. During development the switch is the
**spacebar**.

**Who it is for:** people with severe motor and speech impairments, their
carers, and anyone sitting about 2 metres from the screen.

---

## 2. Architecture in plain words

### The four zones

The screen has four scannable zones, plus non-scannable display areas.

- **letters**: a 5 x 6 grid of letters and symbols for spelling.
- **suggestions**: up to 4 predicted words.
- **phrases**: YES / NO, category tabs, ready-made phrases and EMERGENCY.
- **actions**: SPEAK, BACKSPACE, CLEAR, PAUSE.

Display-only areas (never highlighted): the **message bar** (the text typed so
far), the **chips** (switch connected/ok, current mode, scan speed), the
**status line**, and the **emergency overlay**.

### The path of a press

```
switch (spacebar in dev)
   │  raw down/up events, read by the app or a demo script, NEVER by Board
   ▼
Scanner ── decides short / medium / long, owns the scan timer, knows where the
   │       highlight is, and calls Board.highlight_* to move it
   ▼
Key ────── the chosen item as an object (a letter, a word, a phrase, an action);
   │       it knows what choosing it means
   ▼
Composer ─ holds the typed text, applies letters/words/backspace/clear
Speaker ── says the text out loud
Board ──── is TOLD what to show: set_message, set_suggestions, highlight_*, ...
```

The GUI is a **display only**. It draws what it is told and never decides what a
press means.

### Who owns which job

| Class | Job | Lives in |
|---|---|---|
| `BoardAPI` | Abstract base class: the GUI contract (section 3) as abstract methods. Every board implements it. | `switchspeak/ui/board_api.py` |
| `Board` | The real Tkinter window. Builds and composes the panels, validates zones and indexes, forwards calls to panels and the `HighlightManager`. | `switchspeak/ui/board.py` |
| `ConsoleBoard` | Text-only `BoardAPI` for tests and machines without a display. Same contract, same `ValueError`s, prints instead of drawing. | `switchspeak/ui/console_board.py` |
| Panels | One `tk.Frame` subclass per area. Each draws its own items and can colour one item or row as soft/strong/normal. No panel knows about scanning. | `switchspeak/ui/*_panel.py`, `chips_bar.py`, `status_bar.py`, `emergency_overlay.py` |
| `HighlightManager` | Remembers the one thing currently highlighted, un-highlights it, then highlights the new thing. Guarantees "exactly one highlight". | `switchspeak/ui/highlight.py` |
| `Scanner` | Press timing and scan order; drives `highlight_*`. | teammates' code, outside `ui/` |
| `Keys` | Item objects that know what selecting them does. | teammates' code, outside `ui/` |
| `Composer` | Holds and edits the typed message. | teammates' code, outside `ui/` |
| `Speaker` | Text-to-speech. | teammates' code, outside `ui/` |

UI work never edits `Scanner`, `Keys`, `Composer` or `Speaker`. Those are only
called through, or call into, `BoardAPI`.

---

## 3. GUI contract (do not rename)

> Copied word for word. Never rename a public method listed here.

Zones: 'letters', 'suggestions', 'phrases', 'actions'.
- letters: 5 rows x 6 columns, row-major, index = r*6 + c. Labels come from the caller, e.g. 'A'..'Z','SPACE','.','?','BACKSPACE' (BACKSPACE is drawn as ⌫).
- suggestions: up to 4 words, left to right. Empty slots are dim and are not counted as items.
- phrases: scan order = YES, NO, category tabs (up to 4), phrase rows (up to 8), EMERGENCY last.
- actions: SPEAK, BACKSPACE, CLEAR, PAUSE, in that order.
Board methods:
  set_message(text) | set_suggestions(words) | set_phrase_categories(names, active) | set_phrases(texts)
  set_chips(switch_text, switch_ok, mode_text, speed_seconds) | set_status(text) | set_paused(flag)
  item_count(zone) -> int | item_labels(zone) -> list[str]
  highlight_zone(zone) | highlight_row(r) | highlight_cell(r, c) | highlight_item(zone, i) | clear_highlight()
  show_emergency(seconds_left) | hide_emergency()
Behaviour: exactly ONE thing is highlighted at a time. An unknown zone or an out-of-range index raises ValueError. Soft highlight = tinted background (a zone or a row). Strong highlight = yellow background, dark text and a thick border (the chosen item).

### Item order per zone, at a glance

| Zone | Items, in scan order | `item_count` |
|---|---|---|
| letters | 30 cells, row 0 col 0 … row 4 col 5; `index = r*6 + c` | 30 |
| suggestions | word 0 … word 3, left to right; empty slots skipped | number of non-empty words (0–4) |
| phrases | YES, NO, tabs (0–4), phrase rows (0–8), EMERGENCY | 3 + tabs + phrases |
| actions | SPEAK, BACKSPACE, CLEAR, PAUSE | 4 |

`highlight_row(r)` and `highlight_cell(r, c)` refer to the letters grid
(`0 <= r < 5`, `0 <= c < 6`). `item_labels(zone)` returns labels in the same
order as `highlight_item(zone, i)` indexes.

---

## 4. Folder structure

```
Switch-Speak/
├── CLAUDE.md                     this handbook
├── Synopsis.doc                  lab synopsis form
├── switchspeak/
│   ├── __init__.py               package marker
│   └── ui/
│       ├── __init__.py           exports Board, ConsoleBoard, BoardAPI
│       ├── theme.py              every colour, font, size, padding and border width
│       ├── board_api.py          BoardAPI abstract base class = the GUI contract
│       ├── board.py              Board: Tk window that composes all panels
│       ├── console_board.py      ConsoleBoard: text-only BoardAPI for tests/headless
│       ├── highlight.py          HighlightManager: keeps exactly one highlight
│       ├── message_panel.py      MessagePanel: shows the typed message
│       ├── letters_panel.py      LettersPanel: 5 x 6 letter grid, ⌫ for BACKSPACE
│       ├── suggestions_panel.py  SuggestionsPanel: up to 4 words, dim empty slots
│       ├── phrases_panel.py      PhrasesPanel: YES/NO, tabs, phrase rows, EMERGENCY
│       ├── actions_panel.py      ActionsPanel: SPEAK, BACKSPACE, CLEAR, PAUSE
│       ├── chips_bar.py          ChipsBar: switch state, mode, scan speed
│       ├── status_bar.py         StatusBar: one line of status text, paused state
│       └── emergency_overlay.py  EmergencyOverlay: full-screen emergency countdown
├── demos/
│   ├── __init__.py               package marker so demos run with python -m
│   ├── demo_board.py             whole story on the full Board, spacebar only
│   ├── demo_message.py           MessagePanel on its own
│   ├── demo_letters.py           LettersPanel on its own
│   ├── demo_suggestions.py       SuggestionsPanel on its own
│   ├── demo_phrases.py           PhrasesPanel on its own
│   ├── demo_actions.py           ActionsPanel on its own
│   ├── demo_chips_status.py      ChipsBar and StatusBar on their own
│   ├── demo_emergency.py         EmergencyOverlay show/countdown/hide
│   ├── benchmark_highlight.py    times highlight calls, prints the average in ms
│   └── check_contrast.py         prints PASS/FAIL contrast ratio for theme colour pairs
└── tests/
    ├── __init__.py               package marker for unittest discovery
    ├── test_board_contract.py    Board and ConsoleBoard both satisfy the contract
    ├── test_highlight.py         exactly one highlight; soft vs strong styling
    ├── test_letters_panel.py     grid order, index = r*6 + c, ⌫ drawing
    ├── test_suggestions_panel.py empty slots dim and not counted
    ├── test_phrases_panel.py     YES, NO, tabs, phrases, EMERGENCY order and limits
    ├── test_actions_panel.py     fixed action order
    ├── test_errors.py            unknown zone / out-of-range index raise ValueError
    └── test_theme.py             theme has every token; no literals outside theme.py
```

Create files as they are needed; keep these names so demos, tests and this
handbook stay in sync. If a file is added or renamed, update this section in the
same pull request.

---

## 5. Coding rules

1. **Tkinter only.** Standard library `tkinter` (and `tkinter.font`). No other GUI
   library, nothing to `pip install`.
2. **No mouse, no buttons.** Items are `tk.Label`s / `tk.Frame`s coloured by the
   theme. No `tk.Button`, no `<Button-1>` bindings, no hover effects, no
   scrollbars that need dragging.
3. **`theme.py` for everything visual.** No colour strings, hex codes, font
   tuples, font sizes or border widths anywhere else. Import names from
   `switchspeak.ui.theme`.
4. **One class, one job.** One panel class per area, each a `tk.Frame` subclass,
   composed by `Board`. Panels do not import each other.
5. **Type hints on every function and method, and a one-line docstring** on every
   class and public method.
6. **Only the main thread touches widgets.** Code on another thread must hand work
   to the main thread (for example through `root.after(0, ...)` or a queue polled
   with `after`). Never call a widget method from a worker thread.
7. **Board never reads key presses.** No `bind` on keys inside `switchspeak/ui/`.
   Demo scripts may bind the spacebar.
8. **Never rename a contract method.** Adding private helpers is fine.
9. **Edit only the files you are asked to edit.**
10. **Always give complete files**, ready to paste, followed by 3 lines on how to
    run or test them.

---

## 6. Design and accessibility rules

- **Large, high-contrast targets.** Every item is big enough to read and tell
  apart at a glance. Text/background pairs must pass `check_contrast.py` (WCAG
  contrast ratio of at least 4.5:1; aim for 7:1 on letters and the message bar).
- **A highlight never relies on colour alone.** The strong highlight is yellow
  background **plus** dark text **plus** a thick border. The soft tint must also
  differ in brightness, not just hue, so it shows on a greyscale screen and to
  colour-blind users.
- **Nothing flashes faster than once per second.** That includes the emergency
  overlay and any paused indicator. The highlight moves only when the Scanner
  says so.
- **Readable from 2 metres.** Font sizes in `theme.py` are chosen for that
  distance; do not shrink them to fit more items. Fix layout instead.
- **Calm and predictable.** Item positions never move while scanning. Empty
  slots keep their place (dimmed) so the layout does not jump.
- **Emergency is unmistakable.** The overlay covers the board, uses the theme's
  emergency colours, and shows the seconds left in very large text.

---

## 7. Commands

Run everything from the repo root (`D:\Projects\Switch-Speak`).

```bash
# Full story, spacebar only
python -m demos.demo_board

# One demo per panel
python -m demos.demo_message
python -m demos.demo_letters
python -m demos.demo_suggestions
python -m demos.demo_phrases
python -m demos.demo_actions
python -m demos.demo_chips_status
python -m demos.demo_emergency

# All tests
python -m unittest discover -s tests -v

# One test file / one test case
python -m unittest tests.test_highlight -v
python -m unittest tests.test_errors.TestErrors -v

# Highlight benchmark (average must be under 10 ms)
python -m demos.benchmark_highlight

# Contrast check (must print no FAIL)
python -m demos.check_contrast
```

Tests that create a `Board` need a display. On a machine without one, tests that
use `ConsoleBoard` still run; Tk-based tests should skip cleanly when `tk.Tk()`
raises `tk.TclError`.

---

## 8. Team and workflow

**Branches**

| Branch | UI member | Owns |
|---|---|---|
| `feat/ui-member1` | Member 1 | `theme.py`, `board_api.py`, `board.py`, `highlight.py`, `console_board.py`, `ui/__init__.py`, `demos/demo_board.py`, `demos/benchmark_highlight.py`, `tests/test_board_contract.py`, `tests/test_highlight.py`, `tests/test_errors.py`, `tests/test_theme.py` |
| `feat/ui-member2` | Member 2 | `message_panel.py`, `letters_panel.py`, `suggestions_panel.py`, their demos (`demo_message`, `demo_letters`, `demo_suggestions`) and tests |
| `feat/ui-member3` | Member 3 | `phrases_panel.py`, `actions_panel.py`, `chips_bar.py`, `status_bar.py`, `emergency_overlay.py`, their demos (`demo_phrases`, `demo_actions`, `demo_chips_status`, `demo_emergency`), their tests, `demos/check_contrast.py` |

`Scanner`, `Keys`, `Composer` and `Speaker` belong to the teammates who wrote
them and are outside these UI branches.

**Rules**

- **Edit only your own files.** If you need a change in someone else's file (for
  example a new token in `theme.py`), ask its owner or open a small PR they review.
- Branch from `main`, keep one feature per branch, open a **pull request** into
  `main`. Never push straight to `main`.
- Before opening a PR: all tests pass, your demo runs, contrast check prints no
  FAIL, benchmark is under 10 ms.
- At least one other team member reviews and approves each PR.
- A PR that adds, removes or renames a file also updates section 4 of this file.

---

## 9. Definition of done for the GUI

The GUI is done when **all** of these are true:

- [ ] `demos/demo_board.py` plays the whole story using **only the spacebar**.
- [ ] Every panel has its own demo, and each one runs.
- [ ] `python -m unittest discover -s tests -v` passes with no failures.
- [ ] `python -m demos.check_contrast` prints no FAIL.
- [ ] `python -m demos.benchmark_highlight` reports an average highlight call
      under **10 ms**.

**What the GUI does NOT do** (do not add these to `switchspeak/ui/`):

- read key presses
- speak
- hold the typed text (it only shows what `set_message` gives it)
- predict words
- talk to hardware
- send alerts

---

## 10. Known pitfalls

- **Cancel Tkinter timers in `destroy`.** Any `after(...)` id a widget starts must
  be stored and cancelled with `after_cancel` in that widget's `destroy`, or Tk
  raises errors after the window closes.
- **Never recreate widgets on every highlight.** Build each label once (when the
  panel is built or when its content changes via a `set_*` call) and only
  reconfigure colours/borders when highlighting.
- **A highlight change touches only the widgets that change.** Un-style the
  previous highlight, style the new one, nothing else. Repainting whole panels
  breaks the 10 ms budget and causes flicker.
- **Bad zone or index raises `ValueError`.** Check before touching any widget,
  in both `Board` and `ConsoleBoard`, so a bad call leaves the old highlight in
  place. Empty suggestion slots are not valid indexes.
- **Exactly one highlight.** `highlight_zone`, `highlight_row`, `highlight_cell`
  and `highlight_item` all clear the previous highlight first, through
  `HighlightManager`. `clear_highlight()` leaves nothing highlighted.
- **`set_*` while something is highlighted.** If new content removes the
  highlighted item (for example fewer suggestions), clear the highlight rather
  than leaving a stale one.
- **Colour literals sneak in.** `"#fff"`, `"white"` or `("Arial", 20)` outside
  `theme.py` is a bug; `test_theme.py` looks for them.

---

## 11. OOP LOG RULE

This is an Object-Oriented Programming lab project, so every use of an OOP
concept must be traceable and explainable in a viva.

Whenever you write or change code that uses an OOP concept:

1. **(a)** Add one row to `docs/OOP_LOG.md` (columns: File | Class or method |
   Concept | What it does here | Viva line). If the row for that class or method
   already exists, update it instead of adding a duplicate.
2. **(b)** Put a one-line comment directly above the class or method (above its
   decorator, if it has one), in exactly this form:

   ```python
   # OOP: <concept> - <why>
   ```

**Concepts to log:**

- class and object
- encapsulation (private attributes, properties, validation)
- inheritance
- abstraction (`ABC`, `abstractmethod`)
- polymorphism
- composition
- dataclass
- enum
- dunder methods
- classmethod or staticmethod

**Do not log** plain functions or constants.

Use the concept names above in the comment and in the log so the two always
match. To list every tagged place in the project, see the commands at the top of
`docs/OOP_LOG.md`.

---

## 12. DESIGN FREEDOM

The Stitch mockups are **inspiration only**, not a specification.

You may improve or change anything about the look when it makes the screen
clearer or nicer for a tired user: layout, colours, fonts, shapes, spacing,
icons and label wording.

Always keep:

- the **GUI contract** (section 3: method names, zone names, item order),
- the **accessibility rules** (section 6),
- **Tkinter only**, and
- **no mouse** (no buttons, no click bindings, no hover effects).

If you think the contract itself should change, tell the team **what** should
change and **why** instead of changing it silently.
