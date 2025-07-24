import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app import app

class TestAuthMiddleware(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_route_no_auth(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)

    def test_users_route_no_auth(self):
        # Mock user creation to avoid DB write
        with patch("controllers.user_controller.create_new_user", return_value={"id": 1, "username": "test"}):
            response = self.client.post("/users", json={"username": "test", "password": "test"})
            self.assertIn(response.status_code, [200, 400])

    def test_valid_credentials(self):
        with patch("middlewares.auth.get_credentials_from_headers", return_value=("user", "pass")), \
             patch("middlewares.auth.verify_credentials", return_value=123):
            response = self.client.get("/labels", headers={"Authorization": "Basic dXNlcjpwYXNz"})
            self.assertNotEqual(response.status_code, 401)

    def test_invalid_credentials(self):
        with patch("middlewares.auth.get_credentials_from_headers", return_value=("user", "wrong")), \
             patch("middlewares.auth.verify_credentials", return_value=None):
            response = self.client.get("/labels", headers={"Authorization": "Basic dXNlcjp3cm9uZw=="})
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.json()["detail"], "Unauthorized")

    def test_missing_credentials(self):
        with patch("middlewares.auth.get_credentials_from_headers", return_value=(None, None)), \
             patch("middlewares.auth.verify_credentials", return_value=None):
            response = self.client.get("/labels")
            self.assertEqual(response.status_code, 401)

    def test_predict_creation_sets_user_id(self):
        # Patch verify_credentials and prediction saving to avoid DB write
        with patch("middlewares.auth.get_credentials_from_headers", return_value=("user", "pass")), \
             patch("middlewares.auth.verify_credentials", return_value=42), \
             patch("services.prediction_service.save_prediction_session_dao", return_value={"id": 1, "result": "ok"}), \
             patch("services.prediction_service.save_detection_object_dao", return_value={"id": 1, "result": "ok"}):
            with open("tests/assets/bear.jpg", "rb") as img_file:
                response = self.client.post(
                    "/predict",
                    files={"file": ("bear.jpg", img_file, "image/jpeg")},
                    headers={"Authorization": "Basic dXNlcjpwYXNz"}
                )
            
            self.assertNotEqual(response.status_code, 401)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["user_id"], 42)
            
    def test_no_authorization_header(self):
        # Patch get_credentials_from_headers to return None
        with patch("middlewares.auth.get_credentials_from_headers", return_value=(None, None)), \
             patch("middlewares.auth.verify_credentials", return_value=None):
            response = self.client.get("/labels")
            self.assertEqual(response.status_code, 401)
       