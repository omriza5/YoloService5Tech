import unittest
from fastapi.testclient import TestClient
from app import app
from db.utils import init_db
from tests.services.image_utils import create_dummy_image
from .services.auth import get_basic_auth_header

class TestStatsEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        init_db()

        self.username = "testuser"
        self.password = "testpass"
        self.client.post("/users", json={"username": self.username, "password": self.password})

    def test_stats_empty(self):
        # Act
        headers = get_basic_auth_header(self.username, self.password)
        response = self.client.get("/stats", headers=headers)

        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_predictions"], 0)
        self.assertEqual(data["average_confidence_score"], 0.0)
        self.assertEqual(data["most_common_labels"], {})

    def test_stats_single_prediction(self):
        # Arrange
        image = create_dummy_image('red', 'umbrella')
        headers = get_basic_auth_header(self.username, self.password)
        self.client.post(
            "/predict",
            files={"file": ("test_image.jpg", image, "image/jpeg")}
        )

        # Act
        response = self.client.get("/stats", headers=headers)

        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_predictions"], 1)
        self.assertIsInstance(data["average_confidence_score"], float)
        self.assertIsInstance(data["most_common_labels"], dict)
        self.assertGreaterEqual(len(data["most_common_labels"]), 1)

    def test_stats_multiple_predictions(self):
        # Arrange
        headers = get_basic_auth_header(self.username, self.password)
        for color, shape in [("red", "umbrella"), ("blue", "umbrella"), ("red", "donut")]:
            image = create_dummy_image(color, shape)
            self.client.post(
                "/predict",
                files={"file": ("test_image.jpg", image, "image/jpeg")}
            )
        
        # Act
        response = self.client.get("/stats", headers=headers)
        self.assertEqual(response.status_code, 200)
        
        # Assert
        data = response.json()
        self.assertEqual(data["total_predictions"], 3)
        self.assertIsInstance(data["average_confidence_score"], float)
        self.assertIsInstance(data["most_common_labels"], dict)
        self.assertGreaterEqual(len(data["most_common_labels"]), 1)

    # Add two predictions with the same shape, one with a different
    def test_stats_label_counts(self):
        # Arrange
        headers = get_basic_auth_header(self.username, self.password)
        for _ in range(2):
            image = create_dummy_image('red', 'umbrella')
            self.client.post(
                "/predict",
                files={"file": ("test_image.jpg", image, "image/jpeg")}
            )
        image = create_dummy_image('blue', 'donut')
        self.client.post(
            "/predict",
            files={"file": ("test_image.jpg", image, "image/jpeg")}
        )
        
        # Act
        response = self.client.get("/stats", headers=headers)

        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn(2, data["most_common_labels"].values())
    
    def test_stats_unauthorized(self):
        # Act
        response = self.client.get("/stats")  # No auth header

        # Assert
        self.assertEqual(response.status_code, 401)



