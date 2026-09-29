import json
import tempfile
import unittest
from pathlib import Path

from quick_colorpicker.colors import format_color, nearest_name, rgb_to_cmyk, rgb_to_hsl
from quick_colorpicker.main import check_config, export_history, load_history, DEFAULTS
from quick_colorpicker.palettes import CSS_COLORS, TAILWIND_COLORS


class ColorTests(unittest.TestCase):
    def test_formats(self):
        self.assertEqual(format_color(255, 0, 0, "hex"), "#ff0000")
        self.assertEqual(format_color(255, 0, 0, "rgb"), "rgb(255, 0, 0)")
        self.assertEqual(format_color(255, 0, 0, "hsl"), "hsl(0, 100%, 50%)")
        self.assertEqual(format_color(0, 128, 0, "hsv"), "hsv(120, 100%, 50%)")
        self.assertEqual(format_color(255, 0, 0, "cmyk"), "cmyk(0%, 100%, 100%, 0%)")

    def test_hsl_edge_cases(self):
        self.assertEqual(rgb_to_hsl(0, 0, 0), (0, 0, 0))
        self.assertEqual(rgb_to_hsl(255, 255, 255), (0, 0, 100))
        self.assertEqual(rgb_to_hsl(255, 0, 1)[0], 0)  # 359.8 rounds to 360, wraps to 0

    def test_cmyk_black(self):
        self.assertEqual(rgb_to_cmyk(0, 0, 0), (0, 0, 0, 100))

    def test_nearest_names(self):
        self.assertEqual(nearest_name(255, 0, 0, CSS_COLORS), ("red", True))
        self.assertEqual(nearest_name(250, 2, 3, CSS_COLORS), ("red", False))
        self.assertEqual(nearest_name(0xfb, 0x2c, 0x36, TAILWIND_COLORS), ("red-500", True))
        self.assertEqual(format_color(0x2b, 0x7f, 0xff, "tailwind"), "blue-500")


class HistoryTests(unittest.TestCase):
    history = [
        {"hex": "#ff0000", "rgb": [255, 0, 0], "timestamp": "2026-01-01T10:00:00"},
        {"hex": "#00ff00", "rgb": [0, 255, 0], "timestamp": "2026-01-01T10:01:00"},
    ]

    def test_export_formats(self):
        with tempfile.TemporaryDirectory() as tmp:
            export_history(self.history, Path(tmp, "h.css"))
            self.assertIn("--color-1: #00ff00;", Path(tmp, "h.css").read_text())
            export_history(self.history, Path(tmp, "h.gpl"))
            self.assertIn("255   0   0\t#ff0000", Path(tmp, "h.gpl").read_text())
            export_history(self.history, Path(tmp, "h.json"))
            self.assertEqual(json.loads(Path(tmp, "h.json").read_text())[0]["hex"], "#00ff00")
            with self.assertRaises(ValueError):
                export_history(self.history, Path(tmp, "h.txt"))

    def test_load_skips_bad_entries(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp, "history.json")
            path.write_text(json.dumps(self.history + [{"hex": "red"}, "junk", {"rgb": [1, 2, 3]}]))
            self.assertEqual(load_history(path), self.history)
            path.write_text("{not json")
            self.assertEqual(load_history(path), [])

    def test_check_config(self):
        self.assertEqual(check_config(dict(DEFAULTS)), [])
        self.assertEqual(len(check_config(dict(DEFAULTS, format="png", history_size=0))), 2)


if __name__ == "__main__":
    unittest.main()
