import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).parents[2] / "backend" / "factor-api"))
from factor_lookup import lookup_factor


class FactorLookupTests(unittest.TestCase):
    def test_exact_diesel_is_verified(self):
        result = lookup_factor(
            scope="Scope 1", activity="Diesel (100% mineral diesel)",
            unit="litres", year=2026, category="Liquid fuels", fuel_subtype="diesel"
        )
        self.assertEqual(result["status"], "VERIFIED")
        self.assertEqual(result["match"]["factor_id"], "1_101_1012_8_1")
        self.assertEqual(result["match"]["factor"], 2.66155)

    def test_ambiguous_diesel_is_not_selected(self):
        result = lookup_factor(
            scope="Scope 1", activity="Diesel", unit="litres", year=2026,
            category="Liquid fuels"
        )
        self.assertEqual(result["status"], "REVIEW_REQUIRED")
        self.assertGreater(len(result["matches"]), 1)

    def test_unknown_activity_is_not_guessed(self):
        result = lookup_factor(
            scope="Scope 1", activity="Quantum diesel fuel", unit="litres", year=2026,
            category="Liquid fuels", fuel_subtype="quantum-diesel"
        )
        self.assertEqual(result["status"], "FACTOR_NOT_FOUND")

    def test_scope_2_uk_electricity(self):
        result = lookup_factor(
            scope="Scope 2", activity="Electricity", unit="kWh", year=2026
        )
        self.assertEqual(result["status"], "VERIFIED")
        self.assertEqual(result["match"]["factor_id"], "7_400_4000_5_1")
        self.assertEqual(result["match"]["factor"], 0.13096)


if __name__ == "__main__":
    unittest.main()

# Additional regression tests for deterministic constraint behavior.
class FactorConstraintRegressionTests(unittest.TestCase):
    def test_year_mismatch_never_falls_back_to_current_year(self):
        result = lookup_factor(
            scope="Scope 1", activity="Diesel (100% mineral diesel)",
            unit="litres", year=2025, category="Liquid fuels", fuel_subtype="diesel"
        )
        self.assertEqual(result["status"], "FACTOR_NOT_FOUND")
        self.assertEqual(result["matches"], [])

    def test_category_constraint_is_not_a_fuzzy_path_match(self):
        result = lookup_factor(
            scope="Scope 1", activity="Diesel (100% mineral diesel)",
            unit="litres", year=2026, category="Not a real category", fuel_subtype="diesel"
        )
        self.assertEqual(result["status"], "FACTOR_NOT_FOUND")

    def test_subtype_is_required_to_disambiguate_known_alias(self):
        exact = lookup_factor(
            scope="Scope 1", activity="Diesel (100% mineral diesel)",
            unit="litres", year=2026, category="Liquid fuels", fuel_subtype="diesel"
        )
        self.assertEqual(exact["status"], "VERIFIED")

class FactorBoundaryTests(unittest.TestCase):
    def test_scope_mismatch_returns_not_found(self):
        result = lookup_factor(
            scope="Scope 2", activity="Diesel (100% mineral diesel)",
            unit="litres", year=2026, category="Liquid fuels", fuel_subtype="diesel"
        )
        self.assertEqual(result["status"], "FACTOR_NOT_FOUND")

    def test_unit_mismatch_returns_not_found(self):
        result = lookup_factor(
            scope="Scope 1", activity="Diesel (100% mineral diesel)",
            unit="kWh", year=2026, category="Liquid fuels", fuel_subtype="diesel"
        )
        self.assertEqual(result["status"], "FACTOR_NOT_FOUND")

    def test_whitespace_and_case_are_normalized(self):
        result = lookup_factor(
            scope=" scope 1 ", activity=" DIESEL (100% MINERAL DIESEL) ",
            unit=" LITRES ", year=2026, category=" LIQUID FUELS ", fuel_subtype="DIESEL"
        )
        self.assertEqual(result["status"], "VERIFIED")
        self.assertEqual(result["match"]["factor_id"], "1_101_1012_8_1")

    def test_mineral_diesel_alias_is_verified(self):
        result = lookup_factor(
            scope="Scope 1", activity="Diesel (100% mineral diesel)",
            unit="litres", year=2026, category="Liquid fuels", fuel_subtype="mineral diesel"
        )
        self.assertEqual(result["status"], "VERIFIED")

    def test_unknown_subtype_cannot_select_a_factor(self):
        result = lookup_factor(
            scope="Scope 1", activity="Diesel (100% mineral diesel)",
            unit="litres", year=2026, category="Liquid fuels", fuel_subtype="fictional fuel"
        )
        self.assertEqual(result["status"], "FACTOR_NOT_FOUND")

    def test_blank_optional_constraints_preserve_deterministic_behavior(self):
        result = lookup_factor(
            scope="Scope 2", activity="Electricity", unit="kWh", year=2026,
            category="", fuel_subtype=""
        )
        self.assertEqual(result["status"], "VERIFIED")
        self.assertEqual(result["match"]["factor"], 0.13096)
