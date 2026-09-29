# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [1.1.0] - 2026-09-30

### Added
- 5x5 pixel zoom (loupe) around the cursor with every pick, so you can see exactly which pixel was read.
- Live preview: hold Ctrl + F2 to see the pixels and values under the cursor update as you move.
- Ctrl + Shift + F1 copies the pick in an alternate format (RGB by default).
- New formats: HSV, CMYK, nearest CSS named color and nearest Tailwind CSS v4 color.
- Command-line options: `--format`, `--alt-format`, `--no-copy`, `--no-loupe`, `--history-size`, `--export`, `--version`.
- Settings file at `~/.quick-colorpicker/config.json` for hotkeys and defaults.
- History export to JSON, CSS custom properties or a GIMP/Inkscape/Krita palette (`.gpl`).
- History shows the date for picks that were not made today.
- `python -m quick_colorpicker` works.
- Unit tests and CI on Windows, macOS and Linux; releases publish to PyPI and GitHub from CI.
- MIT `LICENSE` file.

### Fixed
- Picking right after start, before the mouse moved, failed with "Could not get color at (None,None)".
  The cursor position is now read at the moment of the pick.
- Ctrl + H did nothing on Windows (the key arrives as a control character while Ctrl is held).
- On scaled or mixed-DPI Windows displays the picked pixel could be offset from the cursor.
  The picker is now per-monitor DPI aware.
- Ctrl + Shift + F1 (or any extra modifier) also triggered the Ctrl + F1 pick; hotkeys now need an exact modifier match.
- Holding the hotkey no longer spams picks through key auto-repeat.
- A history file that could not be written stopped the hotkeys; a damaged history file crashed the history view.
- Screen reads and clipboard writes no longer run inside the OS keyboard hook, which could lag input.
- Installation on Python 3.13 and newer failed because Pillow was pinned to 10.2.0 (which also had known security issues).

### Changed
- Requires Python 3.9 or newer (older versions could not install the dependencies anyway).
- Dropped the `pyautogui` dependency; screen reads use Pillow (and a direct region copy on Windows, about 10x faster).
- Packaging moved from `setup.py` to `pyproject.toml`.

## [1.0.3] - 2025-05-31

### Changed
- Documentation and packaging metadata updates.

## [1.0.2] - 2025-05-30

### Changed
- Packaging fixes for PyPI.

## [1.0.1] - 2025-05-30

### Added
- First release on PyPI: Ctrl + F1 to pick, Ctrl + H for history, HEX/RGB/HSL output, clipboard copy.

[1.1.0]: https://github.com/Monstertov/Python-Quick-Colorpicker/compare/v1.0.3...v1.1.0
[1.0.3]: https://github.com/Monstertov/Python-Quick-Colorpicker/compare/v1.0.2...v1.0.3
[1.0.2]: https://github.com/Monstertov/Python-Quick-Colorpicker/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/Monstertov/Python-Quick-Colorpicker/releases/tag/v1.0.1
