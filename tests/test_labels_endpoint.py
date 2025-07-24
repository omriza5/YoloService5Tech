import unittest
from unittest.mock import patch, Mock, ANY
from fastapi.testclient import TestClient
from app import app
from db.utils import get_db

class TestLabelsEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        app.dependency_overrides[get_db] = lambda: Mock()    
        
    def tearDown(self):
        # Clean up dependency overrides after each test
        app.dependency_overrides = {}
        
    @patch("middlewares.auth.verify_credentials")
    @patch("controllers.labels_controller.get_unique_labels")
    def test_labels_endpoint_no_predictions(self, mock_get_unique_labels, mock_verify_credentials):
        # Arrange
        mock_verify_credentials.return_value = 1  # Mocking auth
        mock_get_unique_labels.return_value = []

        # Act
        response = self.client.get("/labels")
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["labels"], [])
        mock_get_unique_labels.assert_called_once_with(ANY)
    
    @patch("middlewares.auth.verify_credentials")
    @patch("controllers.labels_controller.get_unique_labels")
    def test_labels_endpoint_returns_multiple_unique_labels(self, mock_get_unique_labels, mock_verify_credentials):
        """
        Test that the /labels endpoint returns multiple unique labels after uploading images with different objects.
        """
        # Arrange
        mock_verify_credentials.return_value = 1  # Mocking auth
        mock_get_unique_labels.return_value = ["bear", "cat", "dog"]    
        
        # Act
        response = self.client.get("/labels")
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.json()
        labels = data.get("labels", [])
        self.assertGreaterEqual(len(set(labels)), 2)
        mock_get_unique_labels.assert_called_once_with(ANY)
        
    @patch("middlewares.auth.verify_credentials")
    @patch("controllers.labels_controller.get_unique_labels")
    def test_labels_endpoint_unauthorized_no_credentials(self, mock_get_unique_labels, mock_verify_credentials):
        """
        Test that accessing /labels without credentials returns 401 Unauthorized.
        """
        # Arrange
        mock_verify_credentials.return_value = None
        
        # Act
        response = self.client.get("/labels")
        
        # Assert
        self.assertEqual(response.status_code, 401)
        mock_get_unique_labels.assert_not_called()

