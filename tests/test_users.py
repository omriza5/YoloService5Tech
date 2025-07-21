import unittest
import os
from fastapi.testclient import TestClient
from db.setup_db import DB_PATH
from app import app, init_db


class TestUsersEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
    
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        init_db()

    def test_create_user(self):
        # Arrange
        username = "testuser"
        password = "testpassword"
        
        # Act
        response = self.client.post("/users", json={"username": username, "password": password})
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["detail"], "User created successfully")

    def test_create_user_duplicate(self):
        # Arrange
        username = "testuser"
        password = "testpassword"
        
        # First user creation
        self.client.post("/users", json={"username": username, "password": password})
        
        # Act
        response = self.client.post("/users", json={"username": username, "password": password})
        
        # Assert
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["detail"], "Username already exists")
        
    def test_create_user_invalid_data(self):
        # Act
        response = self.client.post("/users", json={"username": "", "password": ""})
        
        # Assert
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("detail", data)
        self.assertEqual(data["detail"], "Invalid Credentials")


