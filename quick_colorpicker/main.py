#!/usr/bin/env python3
"""
Quick Color Picker - pick the color of the exact pixel under your mouse cursor,
from anywhere on your screen, with a global hotkey.
"""

import argparse
import json
import re
import sys
from pathlib import Path

from rich.console import Console
from rich.markup import escape

from quick_colorpicker import __version__
from quick_colorpicker.colors import FORMATS, hex_to_rgb

APP_DIR = Path.home() / ".quick-colorpicker"
HISTORY_FILE = APP_DIR / "color_history.json"
CONFIG_FILE = APP_DIR / "config.json"

# Every setting can be overridden in CONFIG_FILE. Hotkeys are "+"-joined: modifiers
# (ctrl, shift, alt, cmd) and one key: a pynput Key name (f1, space, ...), a single
# character, or a mouse button as left_click / right_click / middle_click.
# Set a hotkey to "" to disable it.
DEFAULTS = {
    "pick_hotkey": "ctrl+f1",
    "alt_pick_hotkey": "ctrl+shift+f1",
    "live_hotkey": "ctrl+f2",
    "history_hotkey": "ctrl+h",
    "format": "hex",
    "alt_format": "rgb",
    "auto_copy": True,
    "history_size": 10,
    "loupe": True,
}

console = Console()


def load_config(path=CONFIG_FILE):
    """Defaults, overridden by the JSON config file if there is one."""
    config = dict(DEFAULTS)
    if not path.exists():
        return config
    try:
        user = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(user, dict):
            raise ValueError("expected a JSON object")
    except (OSError, ValueError) as e:
        console.print(f"[red]Ignoring {escape(str(path))}: {escape(str(e))}[/red]")
        return config
    for key in sorted(set(user) - set(DEFAULTS)):
        console.print(f"[yellow]Unknown config key {key!r} in {escape(str(path))}[/yellow]")
    config.update({k: v for k, v in user.items() if k in DEFAULTS})
    return config


def check_config(config):
    """Return a list of problems with config values."""
    problems = []
    for key in ("format", "alt_format"):
        if config[key] not in FORMATS:
            problems.append(f"{key} must be one of {', '.join(FORMATS)}")
    size = config["history_size"]
    if not isinstance(size, int) or isinstance(size, bool) or size < 1:
        problems.append("history_size must be a whole number of 1 or more")
    return problems


def load_history(path=HISTORY_FILE):
    """Load the history, skipping entries that are missing fields."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    if not isinstance(data, list):
        return []
    return [
        e for e in data
        if isinstance(e, dict) and isinstance(e.get("hex"), str) and re.fullmatch(r"#[0-9a-fA-F]{6}", e["hex"])
        and "timestamp" in e
    ]


def save_history(history, size, path=HISTORY_FILE):
    try:
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(history[-size:]), encoding="utf-8")
    except OSError as e:
        console.print(f"[red]Could not save history to {escape(str(path))}: {escape(str(e))}[/red]")


def export_history(history, path):
    """Write the history (newest first) as .json, .css custom properties or a .gpl palette."""
    path = Path(path)
    newest_first = list(reversed(history))
    suffix = path.suffix.lower()
    if suffix == ".json":
        text = json.dumps(newest_first, indent=2) + "\n"
    elif suffix == ".css":
        lines = [f"  --color-{i}: {e['hex']};" for i, e in enumerate(newest_first, 1)]
        text = ":root {\n" + "\n".join(lines) + "\n}\n"
    elif suffix == ".gpl":
        lines = ["GIMP Palette", "Name: quick-colorpicker history", "Columns: 0", "#"]
        for e in newest_first:
            r, g, b = hex_to_rgb(e["hex"])
            lines.append(f"{r:3d} {g:3d} {b:3d}\t{e['hex']}")
        text = "\n".join(lines) + "\n"
    else:
        raise ValueError(f"unsupported export type {suffix or '(none)'}: use .json, .css or .gpl")
    path.write_text(text, encoding="utf-8")


def positive_int(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be 1 or more")
    return number


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="quick-colorpicker",
        description="Pick the color of the exact pixel under your mouse cursor with a global hotkey.",
        epilog=f"Settings file: {CONFIG_FILE}",
    )
    parser.add_argument("--format", choices=FORMATS, help="format copied by the pick hotkey (default: hex)")
    parser.add_argument("--alt-format", choices=FORMATS, help="format copied by the alternate pick hotkey (default: rgb)")
    parser.add_argument("--no-copy", action="store_true", help="do not copy picked colors to the clipboard")
    parser.add_argument("--no-loupe", action="store_true", help="show a plain swatch instead of the 5x5 pixel zoom")
    parser.add_argument("--history-size", type=positive_int, metavar="N", help="number of colors to keep (default: 10)")
    parser.add_argument("--export", metavar="FILE", help="export the color history to FILE (.json, .css or .gpl) and exit")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser.parse_args(argv)


def main(argv=None):
    """Main application entry point."""
    args = parse_args(argv)
    config = load_config()
    for key, value in (("format", args.format), ("alt_format", args.alt_format), ("history_size", args.history_size)):
        if value is not None:
            config[key] = value
    if args.no_copy:
        config["auto_copy"] = False
    if args.no_loupe:
        config["loupe"] = False
    problems = check_config(config)
    if problems:
        for problem in problems:
            console.print(f"[red]Config error: {escape(problem)}[/red]")
        sys.exit(2)

    history = load_history()

    if args.export:
        try:
            export_history(history, args.export)
        except (OSError, ValueError) as e:
            console.print(f"[red]Export failed: {escape(str(e))}[/red]")
            sys.exit(1)
        console.print(f"[green]Exported {len(history)} colors to {escape(args.export)}[/green]")
        return

    try:
        from quick_colorpicker.picker import Picker
    except ImportError as e:
        # pynput raises ImportError when there is no usable display (e.g. Wayland without X, SSH)
        console.print(f"[red]Could not start: {escape(str(e))}[/red]")
        console.print("Reinstall with: pip install --upgrade quick-colorpicker")
        sys.exit(1)

    try:
        picker = Picker(config, history, lambda: save_history(history, config["history_size"]))
    except ValueError as e:
        console.print(f"[red]Config error: {escape(str(e))}[/red]")
        sys.exit(2)
    picker.run()


if __name__ == "__main__":
    main()
