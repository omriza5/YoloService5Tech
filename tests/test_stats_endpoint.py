import unittest
from unittest.mock import patch, Mock, ANY
from fastapi.testclient import TestClient
from app import app
from db.utils import get_db


class TestStatsEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        # Mock the database dependency
        app.dependency_overrides[get_db] = lambda: Mock()
        
        

    def tearDown(self):
        # Clean up dependency overrides after each test
        app.dependency_overrides = {}

    @patch("middlewares.auth.verify_credentials")
    @patch("controllers.stats_controller.get_stats_data")
    def test_stats_empty(self, mock_get_stats, mock_verify_credentials):
        # Arrange
        mock_verify_credentials.return_value = 1 # Mocking auth
        mock_get_stats.return_value = {
            "total_predictions": 0,
            "average_confidence_score": 0.0,
            "most_common_labels": {}
        }
        
        response = self.client.get("/stats")

        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_predictions"], 0)
        self.assertEqual(data["average_confidence_score"], 0.0)
        self.assertEqual(data["most_common_labels"], {})
        mock_get_stats.assert_called_once_with(ANY)

    @patch("middlewares.auth.verify_credentials")
    @patch("controllers.stats_controller.get_stats_data")
    def test_stats_single_prediction(self, mock_get_stats, mock_verify_credentials):
        # Arrange
        mock_verify_credentials.return_value = 1  # Mocking auth
        mock_get_stats.return_value = {
            "total_predictions": 1,
            "average_confidence_score": 0.8,
            "most_common_labels": {"bear": 1}
        }
        # Act
        response = self.client.get("/stats")

        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_predictions"], 1)
        self.assertIsInstance(data["average_confidence_score"], float)
        self.assertIsInstance(data["most_common_labels"], dict)
        self.assertGreaterEqual(len(data["most_common_labels"]), 1)
        mock_get_stats.assert_called_once_with(ANY)

    @patch("middlewares.auth.verify_credentials")
    @patch("controllers.stats_controller.get_stats_data")
    def test_stats_multiple_predictions(self, mock_get_stats, mock_verify_credentials):
        # Arrange
        mock_verify_credentials.return_value = 1  # Mocking auth
        mock_get_stats.return_value = {
            "total_predictions": 2,
            "average_confidence_score": 0.75,
            "most_common_labels": {"bear": 1, "cat": 1}
        }
        
        # Act
        response = self.client.get("/stats")
        self.assertEqual(response.status_code, 200)
        
        # Assert
        data = response.json()
        self.assertEqual(data["total_predictions"], 2)
        self.assertIsInstance(data["average_confidence_score"], float)
        self.assertIsInstance(data["most_common_labels"], dict)
        self.assertGreaterEqual(len(data["most_common_labels"]), 1)
        mock_get_stats.assert_called_once_with(ANY)

    # Add two predictions with the same shape, one with a different
    @patch("middlewares.auth.verify_credentials")
    @patch("controllers.stats_controller.get_stats_data")
    def test_stats_label_counts(self, mock_get_stats, mock_verify_credentials):
        # Arrange
        mock_verify_credentials.return_value = 1  # Mocking auth
        mock_get_stats.return_value = {
            "total_predictions": 3,
            "average_confidence_score": 0.76,
            "most_common_labels": {"bear": 2, "cat": 1}
        }      
        # Act
        response = self.client.get("/stats")

        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn(2, data["most_common_labels"].values())
    
    @patch("middlewares.auth.verify_credentials")
    @patch("controllers.stats_controller.get_stats_data")
    def test_stats_unauthorized(self, mock_get_stats, mock_verify_credentials):
        # Arrange
        mock_verify_credentials.return_value = None  # Simulate unauthorized access
        # Act
        response = self.client.get("/stats")  # No auth header

        # Assert
        self.assertEqual(response.status_code, 401)
        mock_get_stats.assert_not_called()  # Ensure middleware prevents access



