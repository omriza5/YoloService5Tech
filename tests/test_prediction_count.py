import unittest
from fastapi.testclient import TestClient

from app import app


class TestPredictionCount(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_prediction_count(self):
        """Test the prediction_count endpoint"""
        response = self.client.get("/prediction/count")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Verify the response contains the prediction_count field
        self.assertIn("prediction_count", data)
        self.assertIsInstance(data["prediction_count"], int)
