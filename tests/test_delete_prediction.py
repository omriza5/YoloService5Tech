import unittest
from unittest.mock import patch, Mock, ANY
from fastapi.testclient import TestClient
from fastapi import HTTPException
from db.utils import get_db

class TestDeletePredictionEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        app.dependency_overrides[get_db] = lambda: Mock()    
        
    def tearDown(self):
        # Clean up dependency overrides after each test
        app.dependency_overrides = {}
        

    @patch("middlewares.auth.verify_credentials")
    @patch("controllers.prediction_controller.delete_prediction_by_uid")
    def test_delete_existing_prediction(self, mock_delete_prediction, mock_verify_credentials):
        # Arrange
        mock_verify_credentials.return_value = 1  # Mocking auth
        mock_delete_prediction.return_value = {"detail": "Prediction and images deleted"}

        # Act
        prediction_delete_response = self.client.delete(f"/prediction/123")

        # Assert
        self.assertEqual(prediction_delete_response.status_code, 200)
        self.assertEqual(prediction_delete_response.json(), {"detail": "Prediction and images deleted"})
        mock_delete_prediction.assert_called_once_with("123", ANY)

    @patch("middlewares.auth.verify_credentials")
    @patch("controllers.prediction_controller.delete_prediction_by_uid")
    def test_delete_prediction_unauthorized_returns_401(self, mock_delete_prediction, mock_verify_credentials):
        # Arrange
        mock_verify_credentials.return_value = None

        # Act - try to delete without auth header
        prediction_delete_response = self.client.delete(f"/prediction/123")

        # Assert
        self.assertEqual(prediction_delete_response.status_code, 401)
        self.assertIn("detail", prediction_delete_response.json())
        mock_delete_prediction.assert_not_called()
        
    @patch("middlewares.auth.verify_credentials")
    @patch("controllers.prediction_controller.delete_prediction_by_uid")    
    def test_delete_none_existent_prediction(self, mock_delete_prediction, mock_verify_credentials):
        # Arrange
        mock_verify_credentials.return_value = 1  # Mocking auth
        mock_delete_prediction.side_effect = HTTPException(status_code=400, detail="Prediction not found")

        # Act
        resp = self.client.delete(f"/prediction/123")
        
        # Assert
        expected_response = {"detail": "Prediction not found"}
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), expected_response)
        mock_delete_prediction.assert_called_once_with("123", ANY)

    @patch("middlewares.auth.verify_credentials")
    @patch("controllers.prediction_controller.delete_prediction_by_uid")
    def test_delete_twice_returns_400(self, mock_delete_prediction, mock_verify_credentials):
        # Arrange
        mock_verify_credentials.return_value = 1  # Mocking auth
        mock_delete_prediction.side_effect = HTTPException(status_code=400, detail="Prediction not found")
              
        # Act 
        response = self.client.delete(f"/prediction/123")

        # Assert second delete
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "Prediction not found"})
        mock_delete_prediction.assert_called_once_with("123", ANY)


