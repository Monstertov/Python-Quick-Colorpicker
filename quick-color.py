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
config = {
    # The key you hold down (e.g., keyboard.Key.shift, keyboard.Key.ctrl, keyboard.Key.alt)
    "hotkey_modifier": keyboard.Key.shift, 

    # The key or mouse button that activates the color picker when pressed with the modifier.
    # If "trigger_type" is "click": Use mouse.Button.left or mouse.Button.right.
    # If "trigger_type" is "keypress": Use a keyboard.Key (like keyboard.Key.f1)
    # or keyboard.KeyCode.from_char('your_key') for regular letters/numbers.
    # For more options, see pynput's documentation: https://pynput.readthedocs.io/en/latest/keyboard.html
    "hotkey_trigger": mouse.Button.left,    

    # Determines how the hotkey is activated:
    # "click": The color is picked when you click "hotkey_trigger" while holding "hotkey_modifier".
    # "keypress": The color is picked at the current mouse position when you press
    #             "hotkey_trigger" while holding "hotkey_modifier".
    "trigger_type": "click"                 
}


modifier_pressed = False
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
    except Exception as e:
        # print(f"Error getting pixel color: {e}") # Uncomment for debugging
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
    global modifier_pressed, current_x, current_y
    current_x, current_y = x, y # Update current mouse position
    
    if config["trigger_type"] == "click" and pressed and modifier_pressed and button == config["hotkey_trigger"]:
        pick_color_and_print(x, y)

def on_press(key):
    global modifier_pressed, current_x, current_y
    
    # Handle modifier key press
    if key == config["hotkey_modifier"]:
        modifier_pressed = True
    
    # Handle non-click hotkey trigger
    if config["trigger_type"] == "keypress" and modifier_pressed and key == config["hotkey_trigger"]:
        # Get current mouse position for keypress trigger
        # pynput mouse listener gives x, y for clicks, but not for key presses directly.
        # pyautogui.position() can be used to get current mouse cursor position.
        if current_x is None or current_y is None: # Fallback if mouse hasn't moved yet
            current_x, current_y = pyautogui.position()
        pick_color_and_print(current_x, current_y)

def on_release(key):
    global modifier_pressed
    if key == config["hotkey_modifier"]:
        modifier_pressed = False

# Print instructions based on configuration
if config["trigger_type"] == "click":
    trigger_info = f"{str(config['hotkey_modifier']).replace('Key.', '').capitalize()} + {str(config['hotkey_trigger']).replace('Button.', '').capitalize()} Click"
else: # keypress
    modifier_name = str(config["hotkey_modifier"]).replace('Key.', '').capitalize()
    trigger_key_name = ""
    if isinstance(config["hotkey_trigger"], keyboard.Key):
        trigger_key_name = str(config["hotkey_trigger"]).replace('Key.', '').capitalize()
    elif isinstance(config["hotkey_trigger"], keyboard.KeyCode):
        trigger_key_name = config["hotkey_trigger"].char
    trigger_info = f"{modifier_name} + {trigger_key_name}"

print(f"{trigger_info} to pick color. Press Ctrl+C to exit.")

mouse_listener = mouse.Listener(on_click=on_click)
keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)

mouse_listener.start()
keyboard_listener.start()

try:
    while True:
        # Update current mouse position continuously if a keypress trigger is configured,
        # so we always have the latest cursor position.
        if config["trigger_type"] == "keypress":
            current_x, current_y = pyautogui.position()
        time.sleep(0.01) # Small delay to reduce CPU usage
except KeyboardInterrupt:
    print("\nExited by user.")
    mouse_listener.stop()
    keyboard_listener.stop()