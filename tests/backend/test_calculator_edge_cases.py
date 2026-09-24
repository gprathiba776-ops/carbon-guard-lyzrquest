import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).parents[2] / "backend" / "calculator-api"))
from calculator import calculate_emissions


class CalculatorEdgeCaseTests(unittest.TestCase):
    def test_zero_quantity_is_calculated(self):
        result = calculate_emissions(
            quantity=0,
            factor_value=2.66155,
            factor_unit="kg CO2e per litres",
            factor_status="VERIFIED",
        )
        self.assertEqual(result["status"], "CALCULATED")
        self.assertEqual(result["kg_co2e"], 0)
        self.assertEqual(result["tco2e"], 0)

    def test_boolean_quantity_is_blocked(self):
        result = calculate_emissions(
            quantity=True,
            factor_value=2.66155,
            factor_unit="kg CO2e per litres",
            factor_status="VERIFIED",
        )
        self.assertEqual(result["status"], "BLOCKED")

    def test_non_numeric_factor_is_blocked(self):
        result = calculate_emissions(
            quantity=2500,
            factor_value="2.66155",
            factor_unit="kg CO2e per litres",
            factor_status="VERIFIED",
        )
        self.assertEqual(result["status"], "BLOCKED")

    def test_infinite_quantity_is_blocked(self):
        result = calculate_emissions(
            quantity=float("inf"),
            factor_value=2.66155,
            factor_unit="kg CO2e per litres",
            factor_status="VERIFIED",
        )
        self.assertEqual(result["status"], "BLOCKED")

    def test_infinite_factor_is_blocked(self):
        result = calculate_emissions(
            quantity=2500,
            factor_value=float("inf"),
            factor_unit="kg CO2e per litres",
            factor_status="VERIFIED",
        )
        self.assertEqual(result["status"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()

class CalculatorBoundaryTests(unittest.TestCase):
    def test_nan_quantity_is_blocked(self):
        result = calculate_emissions(
            quantity=float("nan"), factor_value=2.66155,
            factor_unit="kg CO2e per litres", factor_status="VERIFIED"
        )
        self.assertEqual(result["status"], "BLOCKED")

    def test_boolean_factor_is_blocked(self):
        result = calculate_emissions(
            quantity=2500, factor_value=True,
            factor_unit="kg CO2e per litres", factor_status="VERIFIED"
        )
        self.assertEqual(result["status"], "BLOCKED")
