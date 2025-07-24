import unittest
from unittest.mock import patch, Mock, ANY
from fastapi.testclient import TestClient
from app import app
from db.utils import get_db

class TestPredictionCount(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        app.dependency_overrides[get_db] = lambda: Mock()    
        
    def tearDown(self):
        # Clean up dependency overrides after each test
        app.dependency_overrides = {}
        
    @patch("middlewares.auth.verify_credentials")
    @patch("controllers.prediction_controller.get_predictions_count")
    def test_prediction_count(self, mock_get_predictions_count, mock_verify_credentials):
        """Test the prediction_count endpoint"""
        # Arrange
        mock_verify_credentials.return_value = 1  # Mocking auth
        mock_get_predictions_count.return_value = {
            "prediction_count": 5,
            "average_confidence_score": 0.75,
            "most_common_labels": {"bear": 2, "cat": 1}
        }
        
        # Act
        response = self.client.get("/prediction/count")
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("prediction_count", data)
        self.assertIsInstance(data["prediction_count"], int)
        mock_get_predictions_count.assert_called_once_with(ANY)
    
    @patch("middlewares.auth.verify_credentials")
    @patch("controllers.prediction_controller.get_predictions_count")
    def test_empty_predictions(self, mock_get_predictions_count, mock_verify_credentials):
        """Test the prediction_count endpoint when there are no predictions"""
        # Arrange
        mock_verify_credentials.return_value = 1  # Mocking auth
        mock_get_predictions_count.return_value = {
            "prediction_count": 0,
            "average_confidence_score": 0.0,
            "most_common_labels": {}
        }

        # Act
        response = self.client.get(f"/prediction/count")
        data = response.json()
        
        # Assert
        self.assertEqual(data['prediction_count'], 0)
        mock_get_predictions_count.assert_called_once_with(ANY)
    
    @patch("middlewares.auth.verify_credentials")
    @patch("controllers.prediction_controller.get_predictions_count")
    def test_single_prediction(self, mock_get_predictions_count, mock_verify_credentials):
        """Test the prediction_count endpoint with a single prediction"""
        # Arrange
        mock_verify_credentials.return_value = 1  # Mocking auth
        mock_get_predictions_count.return_value = {
            "prediction_count": 1,
            "average_confidence_score": 0.85,
            "most_common_labels": {"bear": 1}
        }
        
        # Act
        response = self.client.get(f"/prediction/count")
        data = response.json()
        
        # Assert
        self.assertEqual(data['prediction_count'], 1)
        mock_get_predictions_count.assert_called_once_with(ANY)
    
    @patch("middlewares.auth.verify_credentials")
    @patch("controllers.prediction_controller.get_predictions_count")
    def test_n_prediction(self, mock_get_predictions_count, mock_verify_credentials):
        """Test the prediction_count endpoint with multiple predictions"""
        # Arrange
        mock_verify_credentials.return_value = 1  # Mocking auth
        mock_get_predictions_count.return_value = {
            "prediction_count": 3,
            "average_confidence_score": 0.9,
            "most_common_labels": {"bear": 2, "cat": 1}
        }
        
        # Act
        response = self.client.get(f"/prediction/count")
        data = response.json()
        
        # Assert
        self.assertEqual(data['prediction_count'], 3)
        mock_get_predictions_count.assert_called_once_with(ANY)
    
    @patch("middlewares.auth.verify_credentials")
    @patch("controllers.prediction_controller.get_predictions_count")
    def test_prediction_count_unauthenticated(self, mock_get_predictions_count, mock_verify_credentials):
        """Test that accessing prediction_count without authentication returns 401"""
        # Arrange
        mock_verify_credentials.return_value = None

        # Act
        response = self.client.get("/prediction/count")
        
        # Assert
        self.assertEqual(response.status_code, 401)
        mock_get_predictions_count.assert_not_called()
