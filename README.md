# Python Quick Colorpicker

[![PyPI version](https://badge.fury.io/py/quick-colorpicker.svg)](https://badge.fury.io/py/quick-colorpicker)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/quick-colorpicker)](https://pypi.org/project/quick-colorpicker/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/quick-colorpicker)](https://pypi.org/project/quick-colorpicker/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A professional cross-platform color picking utility that lets you instantly grab colors from anywhere on your screen. Perfect for developers, designers, and digital artists who need quick access to color values.

<img src="https://tov.monster/host/pythoncolorpicker.png" alt="colorpickimg">

## Features

- Pick colors anywhere on screen with Ctrl + F1
- Automatic clipboard copying of color values
- Multiple color formats supported (HEX, RGB, HSL)
- Color history with visual previews
- Cross-platform compatibility (Windows, macOS, Linux)
- Configurable hotkeys
- Beautiful terminal UI with color previews
- Lightweight and fast

## Installation

### Via pip (Recommended)
```bash
pip install quick-colorpicker
```

### From source
```bash
git clone https://github.com/Monstertov/quick-colorpicker.git
cd quick-colorpicker
pip install -r requirements.txt
python setup.py install
```

## Requirements

- Python 3.6 or higher
- Dependencies are automatically installed with pip:
  - pynput
  - pyautogui
  - Pillow
  - pyperclip
  - rich

## Usage

### Quick Start
After installation, simply run:
```bash
quick-colorpicker
```

### Keyboard Shortcuts
- **Ctrl + F1**: Pick color under cursor
- **Ctrl + H**: Show color history
- **Ctrl + C**: Exit application

### Features in Detail

#### Color Formats
Colors are displayed in multiple formats:
- HEX: `#RRGGBB`
- RGB: `rgb(R, G, B)`
- HSL: `hsl(H, S%, L%)`

#### Color History
- Automatically saves your last 10 picked colors
- Displays time of pick and all color formats
- Persists between sessions

#### Clipboard Integration
Colors are automatically copied to your clipboard in your preferred format (configurable in the script)

## Configuration

You can customize the following settings in the script:
```python
config = {
    "hotkey_modifiers": {keyboard.Key.ctrl},
    "hotkey_trigger": keyboard.Key.f1,
    "trigger_type": "keypress",
    "max_history": 10,
    "default_color_format": "hex",  # Options: hex, rgb, hsl
    "auto_copy": True
}
```

## Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

## License

This project is open source and available under the MIT License.

---

Created by [Monstertov](https://github.com/Monstertov)
