import unittest
import os
import sqlite3
from fastapi.testclient import TestClient
from app import app, DB_PATH, init_db, PREDICTED_DIR, UPLOAD_DIR
from tests.services.image_utils import create_dummy_image
from .services.auth import get_basic_auth_header

class TestDeletePredictionEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        # Clean DB and folders for isolation
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        init_db()
        # remove any existing files in upload and predicted directories
        for dir in [UPLOAD_DIR, PREDICTED_DIR]:
            if os.path.exists(dir):
                for file in os.listdir(dir):
                    os.remove(os.path.join(dir, file))
        
        self.username = "testuser"
        self.password = "testpass"
        self.client.post("/users", json={"username": self.username, "password": self.password})

    def test_delete_existing_prediction(self):
        # Arrange
        image = create_dummy_image('red','donut')
        headers = get_basic_auth_header(self.username, self.password)
        response = self.client.post(
            "/predict",
            files={"file": ("test_image.jpg", image, "image/jpeg")},
            headers=headers
        )
        prediction = response.json()
        uid = prediction['prediction_uid']
        
        # Act
        prediction_delete_response = self.client.delete(f"/prediction/{uid}",headers =headers)

        # Assert
        expected_response = {"detail": "Prediction and images deleted"}
        self.assertEqual(prediction_delete_response.status_code, 200)
        self.assertEqual(prediction_delete_response.json(), expected_response)

    def test_delete_prediction_unauthorized_returns_401(self):
        # Arrange
        image = create_dummy_image('red', 'donut')
        headers = get_basic_auth_header(self.username, self.password)
        response = self.client.post(
            "/predict",
            files={"file": ("test_image.jpg", image, "image/jpeg")},
            headers=headers
        )
        prediction = response.json()
        uid = prediction['prediction_uid']

        # Act - try to delete without auth header
        prediction_delete_response = self.client.delete(f"/prediction/{uid}")

        # Assert
        self.assertEqual(prediction_delete_response.status_code, 401)
        self.assertIn("detail", prediction_delete_response.json())
        
    def test_delete_none_existent_prediction(self):
        # Arrange
        uid = "does-not-exist-uid"
        headers = get_basic_auth_header(self.username, self.password)
        # Act
        resp = self.client.delete(f"/prediction/{uid}", headers=headers)
        
        # Assert
        expected_response = {"detail": "Prediction not found"}
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), expected_response)

    def test_delete_twice_returns_400(self):
        # Arrange
        image = create_dummy_image('red','donut')
        response = self.client.post(
            "/predict",
            files={"file": ("test_image.jpg", image, "image/jpeg")}
        )
        prediction = response.json()
        uid = prediction['prediction_uid']
        headers = get_basic_auth_header(self.username, self.password)
        
        # Act - first delete
        first_delete_response = self.client.delete(f"/prediction/{uid}", headers=headers)

        # Assert first delete
        expected_first_response = {"detail": "Prediction and images deleted"}
        self.assertEqual(first_delete_response.status_code, 200)
        self.assertEqual(first_delete_response.json(), expected_first_response)
        
        # Act - second delete
        second_delete_response = self.client.delete(f"/prediction/{uid}",headers=headers)
        
        # Assert second delete
        expected_second_response = {"detail": "Prediction not found"}
        self.assertEqual(second_delete_response.status_code, 400)
        self.assertEqual(second_delete_response.json(), expected_second_response)
        


