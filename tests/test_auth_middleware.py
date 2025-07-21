import unittest
from fastapi.testclient import TestClient
from app import app
from db.setup_db import DB_PATH
from db.utils import init_db
from .services.auth import get_basic_auth_header
import os

class TestAuthMiddleware(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        init_db()
        # Create a test user
        self.username = "testuser"
        self.password = "testpass"
        self.client.post("/users", json={"username": self.username, "password": self.password})

    def test_predict_without_auth(self):
        response = self.client.post(
            "/predict",
            files={"file": ("test.jpg", open("tests/assets/bear.jpg", "rb"), "image/jpeg")}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json().get("user_id"))

    def test_predict_with_invalid_auth(self):
        headers = get_basic_auth_header("wrong", "wrong")
        response = self.client.post(
            "/predict",
            files={"file": ("test.jpg", open("tests/assets/bear.jpg", "rb"), "image/jpeg")},
            headers=headers
        )
          
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json().get("user_id"))

    def test_predict_with_valid_auth(self):
        headers = get_basic_auth_header(self.username, self.password)
        response = self.client.post(
            "/predict",
            files={"file": ("test.jpg", open("tests/assets/bear.jpg", "rb"), "image/jpeg")},
            headers=headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json().get("user_id"))
    
    def test_stats_without_auth(self):
        response = self.client.get("/stats")
        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.json())
        self.assertEqual(response.json()["detail"], "Unauthorized")
    
    def test_stats_with_valid_auth(self):
        headers = get_basic_auth_header(self.username, self.password)
        response = self.client.get("/stats", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("total_predictions", response.json())
