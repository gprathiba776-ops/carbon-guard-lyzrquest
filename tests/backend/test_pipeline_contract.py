import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "backend" / "factor-api"))
sys.path.insert(0, str(ROOT / "backend" / "calculator-api"))

from factor_lookup import lookup_factor
from calculator import calculate_emissions


class PipelineContractTests(unittest.TestCase):
    def test_verified_factor_flows_to_exact_calculation(self):
        factor = lookup_factor(
            scope="Scope 1",
            activity="Diesel (100% mineral diesel)",
            unit="litres",
            year=2026,
            category="Liquid fuels",
            fuel_subtype="diesel",
        )
        self.assertEqual(factor["status"], "VERIFIED")
        self.assertEqual(factor["match"]["factor_id"], "1_101_1012_8_1")

        result = calculate_emissions(
            quantity=2500,
            factor_value=factor["match"]["factor"],
            factor_unit=factor["match"]["factor_unit"],
            factor_status=factor["status"],
        )
        self.assertEqual(result["status"], "CALCULATED")
        self.assertAlmostEqual(result["kg_co2e"], 6653.875, places=9)
        self.assertAlmostEqual(result["tco2e"], 6.653875, places=9)
        self.assertEqual(result["formula"], "2500 × 2.66155")

    def test_factor_provenance_survives_before_calculation(self):
        factor = lookup_factor(
            scope="Scope 2",
            activity="Electricity",
            unit="kWh",
            year=2026,
        )
        self.assertEqual(factor["status"], "VERIFIED")
        match = factor["match"]
        self.assertIn("factor_id", match)
        self.assertIn("source", match)
        self.assertEqual(match["year"], 2026)

    def test_review_required_never_enters_calculator_as_verified(self):
        factor = lookup_factor(
            scope="Scope 1",
            activity="Diesel",
            unit="litres",
            year=2026,
            category="Liquid fuels",
        )
        self.assertEqual(factor["status"], "REVIEW_REQUIRED")
        result = calculate_emissions(
            quantity=2500,
            factor_value=2.66155,
            factor_unit="kg CO2e per litres",
            factor_status=factor["status"],
        )
        self.assertEqual(result["status"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
