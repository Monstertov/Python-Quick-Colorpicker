"""Color conversions, formatting and nearest-name lookups.

Pure Python with no screen or keyboard dependencies, so it can be tested headless.
"""

import colorsys
import math
from functools import lru_cache

from quick_colorpicker.palettes import CSS_COLORS, TAILWIND_COLORS

FORMATS = ("hex", "rgb", "hsl", "hsv", "cmyk", "css", "tailwind")


def rgb_to_hex(r, g, b):
    return f"#{r:02x}{g:02x}{b:02x}"


def hex_to_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hsl(r, g, b):
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    return round(h * 360) % 360, round(s * 100), round(l * 100)


def rgb_to_hsv(r, g, b):
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    return round(h * 360) % 360, round(s * 100), round(v * 100)


def rgb_to_cmyk(r, g, b):
    k = 1 - max(r, g, b) / 255
    if k == 1:
        return 0, 0, 0, 100
    c, m, y = ((1 - v / 255 - k) / (1 - k) for v in (r, g, b))
    return round(c * 100), round(m * 100), round(y * 100), round(k * 100)


@lru_cache(maxsize=None)
def _lab(rgb):
    """sRGB to CIE L*a*b* (D65), used to find the perceptually closest named color."""
    def linear(c):
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = map(linear, rgb)
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883

    def f(t):
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116

    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def nearest_name(r, g, b, palette):
    """Return (name, exact) for the palette color closest to r, g, b."""
    target = _lab((r, g, b))
    name = min(palette, key=lambda n: math.dist(target, _lab(hex_to_rgb(palette[n]))))
    return name, palette[name] == rgb_to_hex(r, g, b)


def format_color(r, g, b, fmt="hex"):
    """Format a color as one of FORMATS."""
    if fmt == "rgb":
        return f"rgb({r}, {g}, {b})"
    if fmt == "hsl":
        return "hsl({}, {}%, {}%)".format(*rgb_to_hsl(r, g, b))
    if fmt == "hsv":
        return "hsv({}, {}%, {}%)".format(*rgb_to_hsv(r, g, b))
    if fmt == "cmyk":
        return "cmyk({}%, {}%, {}%, {}%)".format(*rgb_to_cmyk(r, g, b))
    if fmt == "css":
        return nearest_name(r, g, b, CSS_COLORS)[0]
    if fmt == "tailwind":
        return nearest_name(r, g, b, TAILWIND_COLORS)[0]
    return rgb_to_hex(r, g, b)


def contrast_color(r, g, b):
    """Black or white, whichever reads better on top of r, g, b."""
    return "#000000" if 0.299 * r + 0.587 * g + 0.114 * b > 150 else "#ffffff"
