import importlib
import sys
import unittest
from pathlib import Path

try:
    import flask  # noqa: F401
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

ROOT = Path(__file__).parents[2]


def load_service(service_dir: Path, module_name: str):
    service_path = str(service_dir)
    sys.path.insert(0, service_path)
    try:
        return importlib.import_module(module_name)
    finally:
        sys.path.remove(service_path)


@unittest.skipUnless(FLASK_AVAILABLE, "Flask is installed in CI; install service requirements to run API contract tests locally")
class FactorApiContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for name in ("app", "config", "observability", "factor_lookup", "calculator"):
            sys.modules.pop(name, None)
        cls.app_module = load_service(ROOT / "backend" / "factor-api", "app")
        cls.client = cls.app_module.app.test_client()

    def test_health_and_readiness(self):
        health = self.client.get("/health")
        ready = self.client.get("/ready")
        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.get_json()["status"], "ok")
        self.assertEqual(ready.status_code, 200)
        self.assertEqual(ready.get_json()["status"], "ready")

    def test_lookup_verified_factor(self):
        response = self.client.post(
            "/lookup-factor",
            json={
                "scope": "Scope 1",
                "activity": "Diesel (100% mineral diesel)",
                "unit": "litres",
                "year": 2026,
                "category": "Liquid fuels",
                "fuel_subtype": "diesel",
            },
        )
        body = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body["status"], "VERIFIED")
        self.assertEqual(body["match"]["factor_id"], "1_101_1012_8_1")

    def test_lookup_missing_fields_is_400(self):
        response = self.client.post("/lookup-factor", json={"scope": "Scope 1"})
        body = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(body["error_code"], "MISSING_FIELDS")
        self.assertIn("activity", body["missing_fields"])

    def test_lookup_malformed_json_is_400(self):
        response = self.client.post(
            "/lookup-factor", data="not-json", content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error_code"], "INVALID_JSON")

    def test_unknown_route_is_404(self):
        response = self.client.get("/does-not-exist")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()["error_code"], "NOT_FOUND")


@unittest.skipUnless(FLASK_AVAILABLE, "Flask is installed in CI; install service requirements to run API contract tests locally")
class CalculatorApiContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # The calculator service uses module names shared by the factor service.
        # Remove the previously imported service modules before loading it.
        for name in ("app", "config", "observability", "factor_lookup", "calculator"):
            sys.modules.pop(name, None)
        cls.app_module = load_service(ROOT / "backend" / "calculator-api", "app")
        cls.client = cls.app_module.app.test_client()

    def test_health_and_readiness(self):
        health = self.client.get("/health")
        ready = self.client.get("/ready")
        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.get_json()["status"], "ok")
        self.assertEqual(ready.status_code, 200)
        self.assertEqual(ready.get_json()["status"], "ready")

    def test_verified_calculation(self):
        response = self.client.post(
            "/calculate",
            json={
                "quantity": 2500,
                "factor_value": 2.66155,
                "factor_unit": "kg CO2e per litres",
                "factor_status": "VERIFIED",
            },
        )
        body = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body["status"], "CALCULATED")
        self.assertAlmostEqual(body["tco2e"], 6.653875, places=9)

    def test_unverified_factor_is_blocked(self):
        response = self.client.post(
            "/calculate",
            json={
                "quantity": 2500,
                "factor_value": 2.66155,
                "factor_unit": "kg CO2e per litres",
                "factor_status": "REVIEW_REQUIRED",
            },
        )
        body = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body["status"], "BLOCKED")
        self.assertIsNone(body["tco2e"])

    def test_missing_calculation_fields_is_400(self):
        response = self.client.post("/calculate", json={"quantity": 2500})
        body = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(body["error_code"], "MISSING_FIELDS")

    def test_malformed_json_is_400(self):
        response = self.client.post(
            "/calculate", data="not-json", content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error_code"], "INVALID_JSON")

    def test_unknown_route_is_404(self):
        response = self.client.get("/does-not-exist")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()["error_code"], "NOT_FOUND")


if __name__ == "__main__":
    unittest.main()
