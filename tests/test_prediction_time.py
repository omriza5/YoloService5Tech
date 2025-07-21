import unittest
from fastapi.testclient import TestClient
import io
from app import app
from db.utils import init_db

class TestProcessingTime(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        init_db()


    def test_predict_includes_processing_time(self):
        """Test that the predict endpoint returns processing time"""
        
        response = self.client.post(
            "/predict",
            files={"file": ("test.jpg", open("tests/assets/bear.jpg", "rb"), "image/jpeg")}
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify new field exists
        self.assertIn("time_took", data)
        self.assertIsInstance(data["time_took"], (int, float))
        self.assertGreater(data["time_took"], 0)


    def test_predict_exception_returns_500(self):
        """Test that predict endpoint returns 500 on exception"""
        # Send invalid file (not an image)
        response = self.client.post(
            "/predict",
            files={"file": ("test.txt", io.BytesIO(b"not an image"), "text/plain")}
        )
        self.assertEqual(response.status_code, 500)
        self.assertIn("Prediction failed", response.json()["detail"])