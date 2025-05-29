# Python Quick Colorpicker

A cross-platform Python script that lets users pick a color anywhere on the screen by pressing a hotkey. The picked color is displayed in HEX format along with a color preview block in the terminal.

<img src="https://tov.monster/host/pythoncolorpicker.png" alt="colorpickimg">

## Features

- Pick colors anywhere on screen, by default, with Ctrl + F1 
- Outputs color in HEX format
- Shows a colored block in terminal as preview (_Warning: This may not be accurate, as color rendering depends on the terminal used_)
- Cross-platform (Windows, macOS, Linux)
- Clean exit with Ctrl+C
- In-Script configurable hotkeys for Color Picking

## Requirements

- Python 3.x
- Packages: `pynput`, `Pillow`, `pyautogui`

Install dependencies:

```bash
pip install pynput pillow pyautogui
```

## Usage

Run the script:

```bash
python quick_colorpicker.py
```

Then hold **Ctrl** and **F1** anywhere on the screen to get the color under the cursor.

Press **Ctrl+C** to exit.

---

Created by [Monstertov](https://github.com/Monstertov)
