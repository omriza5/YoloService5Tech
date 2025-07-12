import unittest
import os
from fastapi.testclient import TestClient
from app import app, DB_PATH, init_db
from tests.services.image_utils import create_dummy_image

class TestStatsEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
    
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        init_db()

    def test_stats_empty(self):
        # Act
        response = self.client.get("/stats")
        
        # Assert
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["total_predictions"], 0)
        self.assertEqual(data["average_confidence_score"], 0.0)
        self.assertEqual(data["most_common_labels"], {})

    def test_stats_single_prediction(self):
        # Arrange
        image = create_dummy_image('red', 'umbrella')
        self.client.post(
            "/predict",
            files={"file": ("test_image.jpg", image, "image/jpeg")}
        )

        # Act
        response = self.client.get("/stats")
        data = response.json()
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["total_predictions"], 1)
        self.assertIsInstance(data["average_confidence_score"], float)
        self.assertIsInstance(data["most_common_labels"], dict)
        self.assertGreaterEqual(len(data["most_common_labels"]), 1)

    def test_stats_multiple_predictions(self):
        # Arrange
        for color, shape in [("red", "umbrella"), ("blue", "umbrella"), ("red", "donut")]:
            image = create_dummy_image(color, shape)
            self.client.post(
                "/predict",
                files={"file": ("test_image.jpg", image, "image/jpeg")}
            )
        
        # Act
        response = self.client.get("/stats")
        data = response.json()
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["total_predictions"], 3)
        self.assertIsInstance(data["average_confidence_score"], float)
        self.assertIsInstance(data["most_common_labels"], dict)
        self.assertGreaterEqual(len(data["most_common_labels"]), 1)

    # Add two predictions with the same shape, one with a different
    def test_stats_label_counts(self):
        # Arrange
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
        response = self.client.get("/stats")
        data = response.json()
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn(2, data["most_common_labels"].values())

