#!/usr/bin/env python3
# @author: Monstertov
# @github: https://github.com/Monstertov
# Requirements
# pip install pynput pillow pyautogui

import sys, time, os
try:
    from pynput import mouse, keyboard
except ImportError as e:
    print(f"Failed to import pynput modules: {e}")
    print("Ensure you are running this in a supported GUI environment.")
    sys.exit(1)

import pyautogui

# --- CONFIGURABLE HOTKEYS ---
# I have not tested this extensivly but you can customize this for your specific environment.
# For more options, see pynput's documentation: https://pynput.readthedocs.io/en/latest/keyboard.html
config = {
    "hotkey_modifiers": {keyboard.Key.ctrl},
    "hotkey_trigger": keyboard.Key.f1,
    "trigger_type": "keypress"
}

# Example config for Shift + Left Click
#config = {
    # The key you hold down (e.g., keyboard.Key.shift, keyboard.Key.ctrl, keyboard.Key.alt)
#    "hotkey_modifiers": {keyboard.Key.shift}, 
#    "hotkey_trigger": mouse.Button.left,    
#    "trigger_type": "click"                 
#}
# --- END CONFIGURABLE HOTKEYS ---

modifiers_pressed = set()
current_x, current_y = None, None

def check_display():
    if sys.platform.startswith('linux'):
        display = os.environ.get('DISPLAY')
        if not display:
            print("Error: DISPLAY environment variable is not set. Are you running in a GUI session?")
            sys.exit(1)

check_display()

def print_color_block(r, g, b):
    print(f"\033[48;2;{r};{g};{b}m  \033[0m", end='')

def get_color_at(x, y):
    try:
        r, g, b = pyautogui.pixel(x, y)
        return r, g, b, '#{:02x}{:02x}{:02x}'.format(r, g, b)
    except Exception:
        return None, None, None, None

def pick_color_and_print(x, y):
    r, g, b, hex_color = get_color_at(x, y)
    if hex_color:
        print(f"Color at ({x},{y}): {hex_color} ", end='')
        print_color_block(r, g, b)
        print()
    else:
        print(f"Could not get color at ({x},{y})")

def on_click(x, y, button, pressed):
    global current_x, current_y
    current_x, current_y = x, y
    if config["trigger_type"] == "click" and pressed and config["hotkey_modifiers"].issubset(modifiers_pressed) and button == config["hotkey_trigger"]:
        pick_color_and_print(x, y)

def normalize_modifier(key):
    if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
        return keyboard.Key.ctrl
    if key in (keyboard.Key.shift_l, keyboard.Key.shift_r):
        return keyboard.Key.shift
    if key in (keyboard.Key.alt_l, keyboard.Key.alt_r):
        return keyboard.Key.alt
    return key

def on_press(key):
    global current_x, current_y
    normalized = normalize_modifier(key)

    if normalized in config["hotkey_modifiers"]:
        modifiers_pressed.add(normalized)

    if config["trigger_type"] == "keypress" and key == config["hotkey_trigger"]:
        if config["hotkey_modifiers"].issubset(modifiers_pressed):
            pick_color_and_print(current_x, current_y)

def on_release(key):
    normalized = normalize_modifier(key)
    if normalized in modifiers_pressed:
        modifiers_pressed.discard(normalized)

# --- Instruction Output ---
if config["trigger_type"] == "click":
    trigger_info = " + ".join([str(k).replace('Key.', '').capitalize() for k in config["hotkey_modifiers"]])
    trigger_info += f" + {str(config['hotkey_trigger']).replace('Button.', '').capitalize()} Click"
else:
    trigger_info = " + ".join([str(k).replace('Key.', '').capitalize() for k in config["hotkey_modifiers"]])
    if isinstance(config["hotkey_trigger"], keyboard.Key):
        trigger_info += f" + {str(config['hotkey_trigger']).replace('Key.', '').capitalize()}"
    elif isinstance(config["hotkey_trigger"], keyboard.KeyCode):
        trigger_info += f" + {config['hotkey_trigger'].char}"

print(f"{trigger_info} to pick color. Press Ctrl+C to exit.")

def on_move(x, y):
    global current_x, current_y
    current_x, current_y = x, y
    

# --- Start Listeners ---
mouse_listener = mouse.Listener(on_click=on_click, on_move=on_move)
keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)

mouse_listener.start()
keyboard_listener.start()

try:
    while True:
        time.sleep(0.01)
except KeyboardInterrupt:
    print("\nExited by user.")
    mouse_listener.stop()
    keyboard_listener.stop()
