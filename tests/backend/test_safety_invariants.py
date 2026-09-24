import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "backend" / "factor-api"))
sys.path.insert(0, str(ROOT / "backend" / "calculator-api"))

from factor_lookup import lookup_factor
from calculator import calculate_emissions


class SafetyInvariantTests(unittest.TestCase):
    def test_ambiguous_factor_cannot_be_calculated(self):
        lookup = lookup_factor(
            scope="Scope 1",
            activity="Diesel",
            unit="litres",
            year=2026,
            category="Liquid fuels",
        )
        self.assertEqual(lookup["status"], "REVIEW_REQUIRED")
        result = calculate_emissions(
            quantity=2500,
            factor_value=2.66155,
            factor_unit="kg CO2e per litres",
            factor_status=lookup["status"],
        )
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIsNone(result["kg_co2e"])
        self.assertIsNone(result["tco2e"])

    def test_unknown_factor_cannot_be_calculated(self):
        lookup = lookup_factor(
            scope="Scope 1",
            activity="Quantum diesel fuel",
            unit="litres",
            year=2026,
            category="Liquid fuels",
            fuel_subtype="quantum-diesel",
        )
        self.assertEqual(lookup["status"], "FACTOR_NOT_FOUND")
        result = calculate_emissions(
            quantity=2500,
            factor_value=999999,
            factor_unit="kg CO2e per litres",
            factor_status=lookup["status"],
        )
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIsNone(result["kg_co2e"])
        self.assertIsNone(result["tco2e"])

    def test_every_unverified_status_blocks_calculation(self):
        for status in ("REVIEW_REQUIRED", "FACTOR_NOT_FOUND", "BLOCKED"):
            with self.subTest(status=status):
                result = calculate_emissions(
                    quantity=2500,
                    factor_value=2.66155,
                    factor_unit="kg CO2e per litres",
                    factor_status=status,
                )
                self.assertEqual(result["status"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
