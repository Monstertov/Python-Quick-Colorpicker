#!/usr/bin/env python3
# @author: Monstertov
# @github: https://github.com/Monstertov
# Requirements
# pip install pynput pillow pyautogui

from pynput import mouse, keyboard
import pyautogui
import time

shift_pressed = False

def print_color_block(r, g, b):
    print(f"\033[48;2;{r};{g};{b}m  \033[0m", end='')

def get_color_at(x, y):
    try:
        r, g, b = pyautogui.pixel(x, y)
        return r, g, b, '#{:02x}{:02x}{:02x}'.format(r, g, b)
    except Exception:
        return None, None, None, None

def on_click(x, y, button, pressed):
    global shift_pressed
    if pressed and button == mouse.Button.left and shift_pressed:
        r, g, b, hex_color = get_color_at(x, y)
        if hex_color:
            print(f"Color at ({x},{y}): {hex_color} ", end='')
            print_color_block(r, g, b)
            print()
        else:
            print(f"Could not get color at ({x},{y})")

def on_press(key):
    global shift_pressed
    if key == keyboard.Key.shift:
        shift_pressed = True

def on_release(key):
    global shift_pressed
    if key == keyboard.Key.shift:
        shift_pressed = False

print("Shift + Left Click to pick color. Press Ctrl+C to exit.")

mouse_listener = mouse.Listener(on_click=on_click)
keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)

mouse_listener.start()
keyboard_listener.start()

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nExited by user.")
    mouse_listener.stop()
    keyboard_listener.stop()