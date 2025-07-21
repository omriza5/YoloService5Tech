import unittest
from fastapi.testclient import TestClient
from .services.auth import get_basic_auth_header
from app import app
from db.utils import init_db

client = TestClient(app)

class TestGetPredictionByUidEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        init_db()
        
        self.username = "testuser"
        self.password = "testpass"
        self.client.post("/users", json={"username": self.username, "password": self.password})


        
    def test_get_prediction_by_uid(self):
        # Arrange
        headers = get_basic_auth_header(self.username, self.password)
        response = self.client.post(
            "/predict",
            files={"file": ("test.jpg", open("tests/assets/bear.jpg", "rb"), "image/jpeg")},
        )
        prediction = response.json()
        uid = prediction['prediction_uid']
        
        # Act
        prediction_response = self.client.get(f"/prediction/{uid}", headers=headers)

        # Assert
        self.assertEqual(prediction_response.status_code, 200)
        self.assertIn('uid', prediction_response.json())
        self.assertEqual(prediction_response.json()['uid'], uid)
    
    
    def test_get_prediction_by_uid_unauthorized(self):
        # Arrange
        response = self.client.post(
            "/predict",
            files={"file": ("test.jpg", open("tests/assets/bear.jpg", "rb"), "image/jpeg")},
        )
        prediction = response.json()
        uid = prediction['prediction_uid']
        
        # Act
        prediction_response = self.client.get(f"/prediction/{uid}")

        # Assert
        self.assertEqual(prediction_response.status_code, 401)
        self.assertIn("detail", prediction_response.json())
    
    def test_get_prediction_by_non_existent_uid(self):
        # Arrange
        uid = "non-existent-uid"
        headers = get_basic_auth_header(self.username, self.password)
        
        # Act
        prediction_response = self.client.get(f"/prediction/{uid}", headers=headers)

        # Assert
        self.assertEqual(prediction_response.status_code, 404)
        self.assertIn("detail", prediction_response.json())
        self.assertEqual(prediction_response.json()["detail"], "Prediction not found")