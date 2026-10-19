import unittest

from app import app


class TestVoyageAnalyticsAPI(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_home_endpoint(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(data["app"], "Voyage Analytics API")
        self.assertEqual(data["status"], "running")
        self.assertIn("/health", data["endpoints"])
        self.assertIn("/predict", data["endpoints"])

    def test_health_endpoint(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("model_loaded", data)

    def test_predict_missing_fields(self):
        response = self.client.post("/predict", json={})

        self.assertEqual(response.status_code, 400)

        data = response.get_json()
        self.assertEqual(data["error"], "Missing fields")

        expected_fields = [
            "from_location",
            "to_location",
            "flight_type",
            "agency",
            "travel_time",
            "distance",
        ]

        self.assertEqual(data["fields"], expected_fields)


if __name__ == "__main__":
    unittest.main()
