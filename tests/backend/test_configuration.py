import importlib
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).parents[2]


class ConfigurationTests(unittest.TestCase):
    def test_factor_defaults_are_validated(self):
        service = ROOT / "backend" / "factor-api"
        sys.path.insert(0, str(service))
        try:
            module = importlib.import_module("config")
            self.assertEqual(module.settings.year, 2026)
            self.assertEqual(module.settings.port, 8000)
            self.assertEqual(module.settings.log_level, "INFO")
        finally:
            sys.path.remove(str(service))
            sys.modules.pop("config", None)

    def test_calculator_defaults_are_validated(self):
        service = ROOT / "backend" / "calculator-api"
        sys.path.insert(0, str(service))
        try:
            module = importlib.import_module("config")
            self.assertEqual(module.settings.port, 8000)
            self.assertEqual(module.settings.log_level, "INFO")
        finally:
            sys.path.remove(str(service))
            sys.modules.pop("config", None)


if __name__ == "__main__":
    unittest.main()
