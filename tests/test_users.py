import unittest
from unittest.mock import Mock, patch, ANY
from fastapi import HTTPException
from fastapi.testclient import TestClient
from app import app
from db.utils import get_db

class TestUsersEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        app.dependency_overrides[get_db] = lambda: Mock()
    
    def tearDown(self):
        # Clean up dependency overrides after each test
        app.dependency_overrides = {}

    @patch("controllers.user_controller.create_new_user")
    def test_create_user(self, mock_create_user):
        # Arrange
        mock_create_user.return_value = {"detail": "User created successfully"}

        # Act
        response = self.client.post("/users", json={"username": "fake_username", "password": "fake_password"})
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["detail"], "User created successfully")
        mock_create_user.assert_called_once_with("fake_username", "fake_password",ANY)

    @patch("controllers.user_controller.create_new_user")
    def test_create_user_duplicate(self, mock_create_user):
        # Arrange
        username = "testuser"
        password = "testpassword"
        
        # First user creation
        mock_create_user.return_value = {"detail": "User created successfully"}
        response = self.client.post("/users", json={"username": username, "password": password})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["detail"], "User created successfully")
        
        # Act - After creating the first user, try to create it again
        mock_create_user.side_effect = HTTPException(status_code=400, detail="Username already exists")
        response = self.client.post("/users", json={"username": username, "password": password})
        
        # Assert 
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["detail"], "Username already exists")
        mock_create_user.assert_called_with(username, password, ANY)
        self.assertEqual(mock_create_user.call_count, 2)
        
    @patch("controllers.user_controller.create_new_user")
    def test_create_user_invalid_data(self, mock_create_user):
        # Act
        mock_create_user.side_effect = HTTPException(status_code=400, detail="Invalid Credentials")
        response = self.client.post("/users", json={"username": "", "password": ""})
        
        # Assert
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("detail", data)
        self.assertEqual(data["detail"], "Invalid Credentials")
        mock_create_user.assert_called_once_with("", "", ANY)


