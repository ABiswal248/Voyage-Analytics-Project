
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

    def test_predict_invalid_travel_date(self):
        response = self.client.post(
            "/predict",
            json={
                "from_location": "Delhi",
                "to_location": "Mumbai",
                "flight_type": "Economy",
                "agency": "Test Agency",
                "travel_time": 2.5,
                "distance": 1150,
                "travel_date": "not-a-valid-date",
            },
        )

        self.assertEqual(response.status_code, 400)

        data = response.get_json()
        self.assertIn("Invalid input", data["error"])

    def test_predict_invalid_travel_time(self):
        response = self.client.post(
            "/predict",
            json={
                "from_location": "Delhi",
                "to_location": "Mumbai",
                "flight_type": "Economy",
                "agency": "Test Agency",
                "travel_time": "invalid",
                "distance": 1150,
                "travel_date": "2026-10-25",
            },
        )

        self.assertEqual(response.status_code, 400)

        data = response.get_json()
        self.assertIn("Invalid input", data["error"])

    def test_predict_invalid_distance(self):
        response = self.client.post(
            "/predict",
            json={
                "from_location": "Delhi",
                "to_location": "Mumbai",
                "flight_type": "Economy",
                "agency": "Test Agency",
                "travel_time": 2.5,
                "distance": "invalid",
                "travel_date": "2026-10-25",
            },
        )

        self.assertEqual(response.status_code, 400)

        data = response.get_json()
        self.assertIn("Invalid input", data["error"])


if __name__ == "__main__":
    unittest.main()
