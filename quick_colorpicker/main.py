#!/usr/bin/env python3
"""
Quick Color Picker - A cross-platform color picking utility
that allows you to pick colors from anywhere on your screen.
"""

import sys
import time
import os
import json
from datetime import datetime
from pathlib import Path
try:
    import pyperclip  # For clipboard operations
    from pynput import mouse, keyboard
    import pyautogui
    from rich.console import Console
    from rich.table import Table
except ImportError as e:
    print(f"Failed to import required modules: {e}")
    print("Installing required packages...")
    print("Run: pip install quick-colorpicker")
    sys.exit(1)

# --- CONFIGURABLE HOTKEYS ---
# I have not tested this extensively but you can customize this for your specific environment.
# For more options, see pynput's documentation: https://pynput.readthedocs.io/en/latest/keyboard.html
config = {
    "hotkey_modifiers": {keyboard.Key.ctrl},
    "hotkey_trigger": keyboard.Key.f1,
    "trigger_type": "keypress",
    "max_history": 10,  # Maximum number of colors to keep in history
    "default_color_format": "hex",  # Options: hex, rgb, hsl
    "auto_copy": True,  # Automatically copy color to clipboard
}

# Initialize Rich console for better formatting
console = Console()

# Create application data directory
app_data_dir = Path.home() / ".quick-colorpicker"
app_data_dir.mkdir(exist_ok=True)
history_file = app_data_dir / "color_history.json"

modifiers_pressed = set()
current_x, current_y = None, None
color_history = []

def load_history():
    """Load color history from file."""
    if history_file.exists():
        try:
            with open(history_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_history():
    """Save color history to file."""
    with open(history_file, 'w') as f:
        json.dump(color_history[-config["max_history"]:], f)

def rgb_to_hsl(r, g, b):
    """Convert RGB to HSL color format."""
    r, g, b = r/255, g/255, b/255
    cmax, cmin = max(r, g, b), min(r, g, b)
    delta = cmax - cmin

    # Calculate hue
    if delta == 0:
        h = 0
    elif cmax == r:
        h = 60 * ((g-b)/delta % 6)
    elif cmax == g:
        h = 60 * ((b-r)/delta + 2)
    else:
        h = 60 * ((r-g)/delta + 4)

    # Calculate lightness
    l = (cmax + cmin) / 2

    # Calculate saturation
    s = 0 if delta == 0 else delta / (1 - abs(2*l - 1))

    return round(h), round(s*100), round(l*100)

def format_color(r, g, b, format_type="hex"):
    """Format color in specified format."""
    if format_type == "hex":
        return '#{:02x}{:02x}{:02x}'.format(r, g, b)
    elif format_type == "rgb":
        return f"rgb({r}, {g}, {b})"
    elif format_type == "hsl":
        h, s, l = rgb_to_hsl(r, g, b)
        return f"hsl({h}, {s}%, {l}%)"
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)

def print_color_block(r, g, b, hex_color):
    """Print a color block with information."""
    table = Table(show_header=False, box=None)
    table.add_row(
        f"[white]Color at ({current_x},{current_y}):[/white]",
        f"[{hex_color}]██████[/]",
        f"[white]HEX: {format_color(r, g, b, 'hex')}[/white]",
        f"[white]RGB: {format_color(r, g, b, 'rgb')}[/white]",
        f"[white]HSL: {format_color(r, g, b, 'hsl')}[/white]"
    )
    console.print(table)

def get_color_at(x, y):
    """Get color at specified coordinates."""
    try:
        r, g, b = pyautogui.pixel(x, y)
        return r, g, b, '#{:02x}{:02x}{:02x}'.format(r, g, b)
    except Exception:
        return None, None, None, None

def pick_color_and_print(x, y):
    """Pick color and display information."""
    r, g, b, hex_color = get_color_at(x, y)
    if hex_color:
        # Add to history
        color_data = {
            "hex": hex_color,
            "rgb": (r, g, b),
            "timestamp": datetime.now().isoformat(),
            "coordinates": (x, y)
        }
        color_history.append(color_data)
        if len(color_history) > config["max_history"]:
            color_history.pop(0)
        save_history()

        # Display color information
        print_color_block(r, g, b, hex_color)
        
        # Copy to clipboard if enabled
        if config["auto_copy"]:
            color_str = format_color(r, g, b, config["default_color_format"])
            try:
                pyperclip.copy(color_str)
                console.print(f"[green]✓[/green] Copied to clipboard: {color_str}")
            except Exception as e:
                console.print(f"[red]Failed to copy to clipboard: {e}[/red]")
    else:
        console.print(f"[red]Could not get color at ({x},{y})[/red]")

def show_history():
    """Display color picking history."""
    if not color_history:
        console.print("[yellow]No colors in history yet[/yellow]")
        return

    table = Table(title="Color History")
    table.add_column("Time", style="cyan")
    table.add_column("Color", style="white")
    table.add_column("HEX", style="white")
    table.add_column("RGB", style="white")
    table.add_column("HSL", style="white")

    for color in reversed(color_history):
        r, g, b = color["rgb"]
        time_str = datetime.fromisoformat(color["timestamp"]).strftime("%H:%M:%S")
        table.add_row(
            time_str,
            f"[{color['hex']}]██████[/]",
            color["hex"],
            format_color(r, g, b, "rgb"),
            format_color(r, g, b, "hsl")
        )
    
    console.print(table)

def on_click(x, y, button, pressed):
    """Handle mouse click events."""
    global current_x, current_y
    current_x, current_y = x, y
    if config["trigger_type"] == "click" and pressed and config["hotkey_modifiers"].issubset(modifiers_pressed) and button == config["hotkey_trigger"]:
        pick_color_and_print(x, y)

def normalize_modifier(key):
    """Normalize modifier keys."""
    if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
        return keyboard.Key.ctrl
    if key in (keyboard.Key.shift_l, keyboard.Key.shift_r):
        return keyboard.Key.shift
    if key in (keyboard.Key.alt_l, keyboard.Key.alt_r):
        return keyboard.Key.alt
    return key

def on_press(key):
    """Handle keyboard press events."""
    global current_x, current_y
    normalized = normalize_modifier(key)

    # Show history when pressing H while holding the modifiers
    if isinstance(key, keyboard.KeyCode) and hasattr(key, 'char') and key.char == 'h':
        if config["hotkey_modifiers"].issubset(modifiers_pressed):
            show_history()
            return

    if normalized in config["hotkey_modifiers"]:
        modifiers_pressed.add(normalized)

    if config["trigger_type"] == "keypress" and key == config["hotkey_trigger"]:
        if config["hotkey_modifiers"].issubset(modifiers_pressed):
            pick_color_and_print(current_x, current_y)

def on_release(key):
    """Handle keyboard release events."""
    normalized = normalize_modifier(key)
    if normalized in modifiers_pressed:
        modifiers_pressed.discard(normalized)

def on_move(x, y):
    """Handle mouse movement events."""
    global current_x, current_y
    current_x, current_y = x, y

def main():
    """Main application entry point."""
    # Load color history
    global color_history
    color_history = load_history()

    # Print welcome message and instructions
    console.print("[bold blue]Quick Color Picker[/bold blue]")
    console.print("=" * 50)
    
    # Format hotkey information
    if config["trigger_type"] == "click":
        trigger_info = " + ".join([str(k).replace('Key.', '').capitalize() for k in config["hotkey_modifiers"]])
        trigger_info += f" + {str(config['hotkey_trigger']).replace('Button.', '').capitalize()} Click"
    else:
        trigger_info = " + ".join([str(k).replace('Key.', '').capitalize() for k in config["hotkey_modifiers"]])
        if isinstance(config["hotkey_trigger"], keyboard.Key):
            trigger_info += f" + {str(config['hotkey_trigger']).replace('Key.', '').capitalize()}"
        elif isinstance(config["hotkey_trigger"], keyboard.KeyCode):
            trigger_info += f" + {config['hotkey_trigger'].char}"

    console.print(f"[green]•[/green] Press [bold]{trigger_info}[/bold] to pick a color")
    console.print(f"[green]•[/green] Press [bold]Ctrl + H[/bold] to show color history")
    console.print(f"[green]•[/green] Press [bold]Ctrl + C[/bold] to exit")
    console.print(f"[green]•[/green] Colors are automatically copied to clipboard")
    console.print("=" * 50)

    # Start listeners
    mouse_listener = mouse.Listener(on_click=on_click, on_move=on_move)
    keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)

    mouse_listener.start()
    keyboard_listener.start()

    try:
        while True:
            time.sleep(0.01)
    except KeyboardInterrupt:
        console.print("\n[yellow]Exiting...[/yellow]")
        mouse_listener.stop()
        keyboard_listener.stop()

if __name__ == "__main__":
    main() 