import unittest
from fastapi.testclient import TestClient
from app import app
from db.utils import init_db

class TestUsersEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        init_db()

    def test_create_user(self):
        # Arrange
        username = "testuser"
        password = "testpassword"
        
        # Act
        response = self.client.post("/users", json={"username": username, "password": password})
        
        # Assert
        self.assertEqual(response.status_code, 201)
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


