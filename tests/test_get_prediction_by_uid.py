import unittest
from unittest.mock import patch, Mock, ANY
from fastapi.testclient import TestClient
from app import app
from db.utils import init_db
from .services.fake_entities import FakePrediction

client = TestClient(app)

class TestGetPredictionByUidEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        def override_init_db():
            return Mock()
        
        app.dependency_overrides[init_db] = override_init_db


    def tearDown(self):
        # Clean up dependency overrides after each test
        app.dependency_overrides = {}   
     
    @patch("middlewares.auth.verify_credentials")
    @patch("controllers.prediction_controller.prediction_by_uid")   
    def test_get_prediction_by_uid(self,mock_query,mock_verify_credentials):
        # Arrange
        mock_query.return_value = FakePrediction(
            uid="123",
            timestamp="2023-01-01T12:00:00",
            original_image="input.png",
            predicted_image="output.png"
        )
        mock_verify_credentials.return_value = 1
        
        # Act
        prediction_response = self.client.get(f"/prediction/123")

        # Assert
        self.assertEqual(prediction_response.status_code, 200)
        self.assertEqual(prediction_response.json(), {
            "uid": "123",
            "timestamp": "2023-01-01T12:00:00",
            "original_image": "input.png",
            "predicted_image": "output.png"
        })
        
        mock_query.assert_called()
        mock_query.assert_called_with("123", ANY)
    
    @patch("middlewares.auth.verify_credentials")
    def test_get_prediction_by_uid_unauthorized(self, mock_verify_credentials):
        # Arrange
        mock_verify_credentials.return_value = None  # Simulate unauthorized access
        
        # Act
        prediction_response = self.client.get(f"/prediction/123")

        # Assert
        self.assertEqual(prediction_response.status_code, 401)
        self.assertIn("detail", prediction_response.json())
    
    @patch("middlewares.auth.verify_credentials")
    @patch("controllers.prediction_controller.prediction_by_uid")
    def test_get_prediction_by_non_existent_uid(self, mock_query, mock_verify_credentials):
        # Arrange
        mock_query.return_value = None  # Simulate non-existent prediction
        mock_verify_credentials.return_value = 1

        # Act
        prediction_response = self.client.get(f"/prediction/123")

        # Assert
        self.assertEqual(prediction_response.status_code, 404)
        self.assertIn("detail", prediction_response.json())
        self.assertEqual(prediction_response.json()["detail"], "Prediction not found")