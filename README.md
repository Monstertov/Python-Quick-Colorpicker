# Python Quick Colorpicker

[![PyPI version](https://img.shields.io/pypi/v/quick-colorpicker)](https://pypi.org/project/quick-colorpicker/)
[![Python versions](https://img.shields.io/pypi/pyversions/quick-colorpicker)](https://pypi.org/project/quick-colorpicker/)
[![Downloads](https://img.shields.io/pypi/dm/quick-colorpicker)](https://pypi.org/project/quick-colorpicker/)
[![CI](https://github.com/Monstertov/Python-Quick-Colorpicker/actions/workflows/ci.yml/badge.svg)](https://github.com/Monstertov/Python-Quick-Colorpicker/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/pypi/l/quick-colorpicker)](https://github.com/Monstertov/Python-Quick-Colorpicker/blob/main/LICENSE)

A cross-platform color picker that lives in your terminal. Point your mouse at anything on any screen,
press **Ctrl + F1**, and the color of the exact pixel under the cursor is copied to your clipboard.

<img src="https://raw.githubusercontent.com/Monstertov/Python-Quick-Colorpicker/main/docs/screenshot.svg" alt="quick-colorpicker in a terminal: hotkey list, a pick with a 5x5 pixel zoom and all color formats, and the color history">

## Features

- **Ctrl + F1** reads the exact pixel under your mouse cursor and copies it (HEX by default)
- **Ctrl + Shift + F1** copies the same pick in a second format (RGB by default)
- **Ctrl + F2** (hold) shows a live preview of the pixels under the cursor while you aim
- 5x5 pixel zoom with every pick, so you see exactly which pixel was read
- HEX, RGB, HSL, HSV, CMYK, nearest CSS color name and nearest Tailwind CSS color
- Color history (**Ctrl + H**), kept between sessions, exportable to JSON, CSS or a GIMP palette
- Works on multiple monitors and on scaled (high-DPI) displays
- Windows, macOS and Linux (X11)

## Installation

```bash
pip install quick-colorpicker
```

Or from source:

```bash
git clone https://github.com/Monstertov/Python-Quick-Colorpicker.git
cd Python-Quick-Colorpicker
pip install .
```

Needs Python 3.9 or newer. pip installs everything else for you:

- [pynput](https://pypi.org/project/pynput/): global hotkeys and the mouse position
- [Pillow](https://pypi.org/project/pillow/): reads the pixels from the screen
- [pyperclip](https://pypi.org/project/pyperclip/): copies the color to the clipboard
- [rich](https://pypi.org/project/rich/): the colored terminal output

## Usage

```bash
quick-colorpicker
```

Leave it running in a terminal and use the hotkeys from any application:

| Hotkey | Action |
| --- | --- |
| Ctrl + F1 | Copy the color of the exact pixel under your mouse cursor |
| Ctrl + Shift + F1 | Same, copied in the alternate format |
| Ctrl + F2 (hold) | Live preview of the pixels under the cursor; release to stop |
| Ctrl + H | Show color history |
| Ctrl + C | Exit (in the picker's own terminal window) |

### Command-line options

| Option | Effect |
| --- | --- |
| `--format FORMAT` | Format copied by Ctrl + F1: `hex`, `rgb`, `hsl`, `hsv`, `cmyk`, `css`, `tailwind` |
| `--alt-format FORMAT` | Format copied by Ctrl + Shift + F1 |
| `--no-copy` | Show picks without copying them to the clipboard |
| `--no-loupe` | Show a plain swatch instead of the 5x5 pixel zoom |
| `--history-size N` | Number of colors to keep in history (default 10) |
| `--export FILE` | Write the history to `FILE` (`.json`, `.css` or `.gpl`) and exit |
| `--version` | Show the version |

Example: copy Tailwind class colors and keep the last 50 picks:

```bash
quick-colorpicker --format tailwind --history-size 50
```

### Settings file

Create `~/.quick-colorpicker/config.json` (on Windows `C:\Users\<you>\.quick-colorpicker\config.json`)
to change the defaults. Every key is optional, command-line options win over the file:

```json
{
  "pick_hotkey": "ctrl+f1",
  "alt_pick_hotkey": "ctrl+shift+f1",
  "live_hotkey": "ctrl+f2",
  "history_hotkey": "ctrl+h",
  "format": "hex",
  "alt_format": "rgb",
  "auto_copy": true,
  "history_size": 10,
  "loupe": true
}
```

Hotkeys are modifiers (`ctrl`, `shift`, `alt`, `cmd`) plus one key joined with `+`. The key can be a
[pynput key name](https://pynput.readthedocs.io/en/latest/keyboard.html#pynput.keyboard.Key)
(`f1`, `insert`, `space`, ...), a single character, or a mouse button: `left_click`, `right_click`,
`middle_click`. Use `""` to turn a hotkey off.

### Export

```bash
quick-colorpicker --export colors.gpl   # GIMP, Inkscape, Krita palette
quick-colorpicker --export colors.css   # :root { --color-1: #2b7fff; ... }
quick-colorpicker --export colors.json
```

The newest pick comes first. History is stored in `~/.quick-colorpicker/color_history.json`.

## Platform notes

- **macOS**: allow your terminal app in System Settings > Privacy & Security > **Accessibility** (for the
  hotkeys) and **Screen Recording** (to read pixels), then restart the terminal.
- **Linux**: needs an X11 session (Xorg or XWayland apps). Global hotkeys do not work on pure Wayland.
  Clipboard copy needs `xclip` or `xsel` installed.
- **Windows**: works out of the box, including multi-monitor and mixed display scaling.

## Development

```bash
pip install -e .
python -m unittest discover -s tests
```

Releases: bump `__version__` in `quick_colorpicker/__init__.py`, add a section to `CHANGELOG.md`, push
the commit and a `vX.Y.Z` tag. CI tests, publishes to PyPI and creates the GitHub release.

## Contributing

Bug reports, ideas and pull requests are welcome on
[GitHub](https://github.com/Monstertov/Python-Quick-Colorpicker/issues).

## License

[MIT](https://github.com/Monstertov/Python-Quick-Colorpicker/blob/main/LICENSE). See the [changelog](https://github.com/Monstertov/Python-Quick-Colorpicker/blob/main/CHANGELOG.md) for release history.

---

Created by [Monstertov](https://github.com/Monstertov)
