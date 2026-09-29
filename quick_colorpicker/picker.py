"""The running picker: global hotkeys, screen sampling and terminal output."""

import queue
import struct
import sys
import threading
import time
from datetime import datetime

if sys.platform == "win32":
    import ctypes

    # Per-monitor DPI awareness puts the cursor position and the screen grab in the same
    # physical pixels, so the pick is the exact pixel under the cursor on scaled displays.
    try:
        ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
    except AttributeError:  # Windows older than 10 1703
        ctypes.windll.user32.SetProcessDPIAware()

import pyperclip
from PIL import Image, ImageGrab
from pynput import keyboard, mouse
from rich.console import Console, Group
from rich.live import Live
from rich.markup import escape
from rich.table import Table
from rich.text import Text

from quick_colorpicker import __version__
from quick_colorpicker.colors import contrast_color, format_color, hex_to_rgb, nearest_name, rgb_to_hex
from quick_colorpicker.main import CONFIG_FILE
from quick_colorpicker.palettes import CSS_COLORS, TAILWIND_COLORS

console = Console()

LOUPE_RADIUS = 2  # 5x5 pixels around the cursor
ACTIONS = ("pick", "alt_pick", "live", "history")

MODIFIER_KEYS = {}
for _name, _variants in (
    ("ctrl", ("ctrl", "ctrl_l", "ctrl_r")),
    ("shift", ("shift", "shift_l", "shift_r")),
    ("alt", ("alt", "alt_l", "alt_r", "alt_gr")),
    ("cmd", ("cmd", "cmd_l", "cmd_r")),
):
    for _variant in _variants:
        if hasattr(keyboard.Key, _variant):
            MODIFIER_KEYS[getattr(keyboard.Key, _variant)] = _name


def parse_hotkey(text):
    """'ctrl+shift+f1' -> (frozenset({'ctrl', 'shift'}), Key.f1). Returns None for ''."""
    if not text:
        return None
    if not isinstance(text, str):
        raise ValueError(f"hotkey must be a string like \"ctrl+f1\", got {text!r}")
    *mods, name = [part.strip().lower() for part in text.split("+")]
    if not name or set(mods) - set(MODIFIER_KEYS.values()):
        raise ValueError(f"invalid hotkey {text!r}")
    if name.endswith("_click") and name[:-6] in mouse.Button.__members__:
        trigger = mouse.Button[name[:-6]]
    elif name in keyboard.Key.__members__:
        trigger = keyboard.Key[name]
    elif len(name) == 1:
        trigger = name
    else:
        raise ValueError(f"unknown key {name!r} in hotkey {text!r}")
    return frozenset(mods), trigger


def pretty_hotkey(text):
    parts = [part.strip() for part in text.split("+")]
    return " + ".join(p.upper() if len(p) == 1 else p.replace("_", " ").capitalize() for p in parts)


def key_matches(key, trigger):
    if isinstance(trigger, str):
        if sys.platform == "win32" and trigger.isascii() and trigger.isalnum():
            if getattr(key, "vk", None) == ord(trigger.upper()):
                return True
        char = getattr(key, "char", None)
        # With Ctrl held, letters can arrive as control characters (Ctrl+H is '\x08')
        return char is not None and (char.lower() == trigger or (trigger.isalpha() and char == chr(ord(trigger) & 0x1F)))
    return key == trigger


def key_id(key):
    """Identity for pairing press and release. The char can change with modifiers, the vk does not."""
    return getattr(key, "vk", None) or key


def grab(x, y):
    """The (2 * LOUPE_RADIUS + 1) square of screen pixels centered on x, y."""
    r = LOUPE_RADIUS
    if sys.platform == "win32":
        return _grab_win32(x - r, y - r, 2 * r + 1)
    return ImageGrab.grab(bbox=(x - r, y - r, x + r + 1, y + r + 1), all_screens=True).convert("RGB")


if sys.platform == "win32":
    from ctypes import wintypes

    _user32 = ctypes.WinDLL("user32")  # own instances: argtypes set here must not leak into pynput
    _gdi32 = ctypes.WinDLL("gdi32")
    for _func, _res, _args in (
        (_user32.GetDC, wintypes.HDC, (wintypes.HWND,)),
        (_user32.ReleaseDC, ctypes.c_int, (wintypes.HWND, wintypes.HDC)),
        (_gdi32.CreateCompatibleDC, wintypes.HDC, (wintypes.HDC,)),
        (_gdi32.CreateCompatibleBitmap, wintypes.HBITMAP, (wintypes.HDC, ctypes.c_int, ctypes.c_int)),
        (_gdi32.SelectObject, wintypes.HGDIOBJ, (wintypes.HDC, wintypes.HGDIOBJ)),
        (_gdi32.BitBlt, wintypes.BOOL, (wintypes.HDC,) + (ctypes.c_int,) * 4 + (wintypes.HDC, ctypes.c_int, ctypes.c_int, wintypes.DWORD)),
        (_gdi32.GetDIBits, ctypes.c_int, (wintypes.HDC, wintypes.HBITMAP, wintypes.UINT, wintypes.UINT, ctypes.c_void_p, ctypes.c_void_p, wintypes.UINT)),
        (_gdi32.DeleteObject, wintypes.BOOL, (wintypes.HGDIOBJ,)),
        (_gdi32.DeleteDC, wintypes.BOOL, (wintypes.HDC,)),
    ):
        _func.restype, _func.argtypes = _res, _args

    def _grab_win32(left, top, size):
        """Copy only a size x size screen region. Pillow's ImageGrab copies the whole desktop."""
        screen = _user32.GetDC(None)
        memory = _gdi32.CreateCompatibleDC(screen)
        bitmap = _gdi32.CreateCompatibleBitmap(screen, size, size)
        try:
            _gdi32.SelectObject(memory, bitmap)
            # SRCCOPY | CAPTUREBLT: include layered windows (tooltips, translucent windows)
            if not _gdi32.BitBlt(memory, 0, 0, size, size, screen, left, top, 0x00CC0020 | 0x40000000):
                raise OSError("BitBlt failed")
            # BITMAPINFOHEADER for a top-down 32-bit BGRX image
            header = ctypes.create_string_buffer(struct.pack("<IiiHHIIiiII", 40, size, -size, 1, 32, 0, 0, 0, 0, 0, 0), 44)
            pixels = ctypes.create_string_buffer(size * size * 4)
            if _gdi32.GetDIBits(memory, bitmap, 0, size, pixels, header, 0) != size:
                raise OSError("GetDIBits failed")
        finally:
            _gdi32.DeleteObject(bitmap)
            _gdi32.DeleteDC(memory)
            _user32.ReleaseDC(None, screen)
        return Image.frombuffer("RGB", (size, size), pixels.raw, "raw", "BGRX", 0, 1)


def render_loupe(image):
    text = Text()
    for y in range(image.height):
        for x in range(image.width):
            r, g, b = image.getpixel((x, y))
            if (x, y) == (LOUPE_RADIUS, LOUPE_RADIUS):
                text.append("[]", style=f"{contrast_color(r, g, b)} on {rgb_to_hex(r, g, b)}")
            else:
                text.append("  ", style=f"on {rgb_to_hex(r, g, b)}")
        if y < image.height - 1:
            text.append("\n")
    return text


def render_pick(x, y, image, loupe=True):
    r, g, b = image.getpixel((LOUPE_RADIUS, LOUPE_RADIUS))
    values = Table.grid(padding=(0, 2))
    values.add_column(style="bold")
    values.add_column()
    for label in ("hex", "rgb", "hsl", "hsv", "cmyk"):
        values.add_row(label.upper(), format_color(r, g, b, label))
    for label, palette in (("CSS", CSS_COLORS), ("Tailwind", TAILWIND_COLORS)):
        name, exact = nearest_name(r, g, b, palette)
        values.add_row(label, name if exact else f"{name} [dim](nearest, {palette[name]})[/dim]")

    side = 2 * LOUPE_RADIUS + 1
    swatch = render_loupe(image) if loupe else Text("\n".join([" " * 2 * side] * side), style=f"on {rgb_to_hex(r, g, b)}")
    layout = Table.grid(padding=(0, 3))
    layout.add_row(swatch, values)
    return Group(Text(f"Pixel at ({x}, {y})", style="bold"), layout)


class Picker:
    def __init__(self, config, history, save):
        """Raises ValueError for an invalid hotkey in config."""
        self.config, self.history, self.save = config, history, save
        self.hotkeys = {}
        for action in ACTIONS:
            parsed = parse_hotkey(config[f"{action}_hotkey"])
            if parsed:
                self.hotkeys[action] = parsed
        self.mouse = mouse.Controller()
        self.modifiers = set()
        self.down = set()
        # Listener callbacks only queue work: slow work inside an OS input hook lags the whole desktop.
        self.actions = queue.Queue()
        self.live = threading.Event()
        self.in_live = False

    # --- listener callbacks (pynput threads) ---

    def on_press(self, key):
        if key in MODIFIER_KEYS:
            self.modifiers.add(MODIFIER_KEYS[key])
            return
        if key_id(key) in self.down:  # auto-repeat while held
            return
        self.down.add(key_id(key))
        for action, (mods, trigger) in self.hotkeys.items():
            if mods == self.modifiers and not isinstance(trigger, mouse.Button) and key_matches(key, trigger):
                self.trigger(action)
                return

    def on_release(self, key):
        live = self.hotkeys.get("live")
        if key in MODIFIER_KEYS:
            self.modifiers.discard(MODIFIER_KEYS[key])
            if live and MODIFIER_KEYS[key] in live[0]:
                self.live.clear()
            return
        self.down.discard(key_id(key))
        if live and not isinstance(live[1], mouse.Button) and key_matches(key, live[1]):
            self.live.clear()

    def on_click(self, x, y, button, pressed):
        if not pressed:
            if self.hotkeys.get("live", (None, None))[1] == button:
                self.live.clear()
            return
        for action, (mods, trigger) in self.hotkeys.items():
            if trigger == button and mods == self.modifiers:
                self.trigger(action)
                return

    def trigger(self, action):
        if action == "live":
            if not self.live.is_set():
                self.live.set()
                self.actions.put(self.run_live)
        elif action == "history":
            self.actions.put(self.show_history)
        else:
            fmt = self.config["alt_format" if action == "alt_pick" else "format"]
            self.actions.put(lambda: self.pick(fmt))

    # --- work (main thread) ---

    def cursor(self):
        x, y = self.mouse.position
        return int(x), int(y)

    def pick(self, fmt):
        x, y = self.cursor()
        try:
            image = grab(x, y)
        except Exception as e:  # each platform's grab backend raises its own errors
            console.print(f"[red]Could not read the screen at ({x}, {y}): {escape(str(e))}[/red]")
            return
        r, g, b = image.getpixel((LOUPE_RADIUS, LOUPE_RADIUS))
        self.history.append({
            "hex": rgb_to_hex(r, g, b),
            "rgb": [r, g, b],
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "coordinates": [x, y],
        })
        del self.history[:-self.config["history_size"]]
        self.save()
        console.print(render_pick(x, y, image, self.config["loupe"]))
        if self.config["auto_copy"]:
            text = format_color(r, g, b, fmt)
            try:
                pyperclip.copy(text)
                console.print(f"[green]Copied to clipboard:[/green] {escape(text)}")
            except pyperclip.PyperclipException as e:
                console.print(f"[red]Could not copy to clipboard: {escape(str(e))}[/red]")

    def run_live(self):
        if self.in_live:
            return
        self.in_live = True
        try:
            with Live(console=console, refresh_per_second=15, transient=True) as live:
                while self.live.is_set():
                    x, y = self.cursor()
                    try:
                        view = render_pick(x, y, grab(x, y), self.config["loupe"])
                    except Exception as e:
                        view = Text(f"Could not read the screen: {e}", style="red")
                    live.update(Group(Text("Live preview, release the hotkey to stop", style="dim"), view))
                    # Picks made while previewing print above the live view
                    while not self.actions.empty():
                        self.actions.get_nowait()()
                    time.sleep(0.05)
        finally:
            self.in_live = False

    def show_history(self):
        if not self.history:
            console.print("[yellow]No colors in history yet[/yellow]")
            return
        table = Table(title="Color History")
        for column in ("Time", "Color", "HEX", "RGB", "HSL"):
            table.add_column(column)
        today = datetime.now().date()
        for entry in reversed(self.history):
            r, g, b = hex_to_rgb(entry["hex"])
            try:
                when = datetime.fromisoformat(entry["timestamp"])
                when = when.strftime("%H:%M:%S" if when.date() == today else "%Y-%m-%d %H:%M")
            except (TypeError, ValueError):
                when = "?"
            table.add_row(when, Text("      ", style=f"on {entry['hex']}"), entry["hex"],
                          format_color(r, g, b, "rgb"), format_color(r, g, b, "hsl"))
        console.print(table)

    def print_banner(self):
        copy, fmt, alt = self.config["auto_copy"], self.config["format"].upper(), self.config["alt_format"].upper()
        descriptions = {
            "pick": (f"Copy the color of the exact pixel under your mouse cursor as {fmt}" if copy
                     else "Show the color of the exact pixel under your mouse cursor"),
            "alt_pick": f"Same, copied as {alt}" if copy else "Same as above",
            "live": "Hold for a live preview of the pixels under the cursor",
            "history": "Show color history",
        }
        rows = Table.grid(padding=(0, 2))
        rows.add_column(style="bold")
        rows.add_column()
        for action in ACTIONS:
            if action in self.hotkeys:
                rows.add_row(pretty_hotkey(self.config[f"{action}_hotkey"]), descriptions[action])
        rows.add_row("Ctrl + C", "Exit (in this window)")
        console.print(f"[bold blue]Quick Color Picker[/bold blue] {__version__}")
        console.rule(style="blue")
        console.print(rows)
        console.print(f"[dim]Settings: {escape(str(CONFIG_FILE))}[/dim]")
        console.rule(style="blue")

    def run(self):
        self.print_banner()
        listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        listeners = [listener]
        if any(isinstance(trigger, mouse.Button) for _, trigger in self.hotkeys.values()):
            listeners.append(mouse.Listener(on_click=self.on_click))
        for each in listeners:
            each.start()
            each.wait()
        if sys.platform == "darwin" and not getattr(listener, "IS_TRUSTED", True):
            console.print("[yellow]macOS blocks global hotkeys for this terminal. Allow it in System Settings > "
                          "Privacy & Security > Accessibility and Screen Recording, then restart.[/yellow]")
        try:
            while listener.is_alive():
                try:
                    self.actions.get(timeout=0.2)()
                except queue.Empty:
                    pass
            console.print("[red]The keyboard listener stopped unexpectedly.[/red]")
        except KeyboardInterrupt:
            console.print("\n[yellow]Exiting...[/yellow]")
        finally:
            for each in listeners:
                each.stop()
