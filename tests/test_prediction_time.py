import unittest
from unittest.mock import patch, Mock, ANY
from fastapi import HTTPException
from fastapi.testclient import TestClient
import io
from app import app
from db.utils import get_db

class TestProcessingTime(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        app.dependency_overrides[get_db] = lambda: Mock()
    
    def tearDown(self):
        # Clean up dependency overrides after each test
        app.dependency_overrides = {}

    @patch("controllers.prediction_controller.create_prediction")
    def test_predict_includes_processing_time(self, mock_create_prediction):
        """Test that the predict endpoint returns processing time"""
        
        # Arrange
        mock_create_prediction.return_value = {
            "uid": "test-uid",
            "label": "bear",
            "score": 0.95,
            "time_took": 123.456  # Mocked processing time
        }
        response = self.client.post(
            "/predict",
            files={"file": ("test_image.jpg", io.BytesIO(b"fake image data"), "image/jpeg")}
        )
        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify new field exists
        self.assertIn("time_took", data)
        self.assertIsInstance(data["time_took"], (int, float))
        self.assertGreater(data["time_took"], 0)
        mock_create_prediction.assert_called_once_with(
            ANY,  # The file object
            ANY,  # The request object
            ANY   # The database session
        )

    @patch("controllers.prediction_controller.create_prediction")
    def test_predict_exception_returns_500(self,mock_create_prediction):
        """Test that predict endpoint returns 500 on exception"""
        # Arrange
        mock_create_prediction.side_effect = HTTPException(status_code=500, detail=f"Prediction failed")
        
        # Act
        # Send invalid file (not an image)
        response = self.client.post(
            "/predict",
            files={"file": ("test.txt", io.BytesIO(b"not an image"), "text/plain")}
        )
        
        # Assert
        self.assertEqual(response.status_code, 500)
        self.assertIn("Prediction failed", response.json()["detail"])
        mock_create_prediction.assert_called_once()