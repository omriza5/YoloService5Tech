import io
from PIL import Image
import unittest
from fastapi.testclient import TestClient
from .services.auth import get_basic_auth_header
from app import app
from db.utils import init_db


class TestPredictionCount(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        init_db()    
        
        # Create a simple test image
        self.test_image = Image.new('RGB', (100, 100), color='red')
        self.image_bytes = io.BytesIO()
        self.test_image.save(self.image_bytes, format='JPEG')
        self.image_bytes.seek(0)
        
        self.username = "testuser"
        self.password = "testpass"
        self.client.post("/users", json={"username": self.username, "password": self.password})
    

    def test_prediction_count(self):
        """Test the prediction_count endpoint"""
        headers = get_basic_auth_header(self.username, self.password)
        response = self.client.get("/prediction/count", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Verify the response contains the prediction_count field
        self.assertIn("prediction_count", data)
        self.assertIsInstance(data["prediction_count"], int)
    
    def test_empty_predictions(self):
        headers = get_basic_auth_header(self.username, self.password)
        response = self.client.get(f"/prediction/count", headers=headers)

        data = response.json()
        self.assertEqual(data['prediction_count'], 0)
    
    def test_single_prediction(self):
        headers = get_basic_auth_header(self.username, self.password)
        self.client.post(
               "/predict",
               files={"file": ("test.jpg", self.image_bytes, "image/jpeg")}
           )
        response = self.client.get(f"/prediction/count", headers=headers)
        data = response.json()
        self.assertEqual(data['prediction_count'], 1)
    
    def test_n_prediction(self):
        headers = get_basic_auth_header(self.username, self.password)
        n=3
           
        for _ in range(n):
            self.client.post(
                "/predict",
                files={"file": ("test.jpg", self.image_bytes, "image/jpeg")}
            )
        response = self.client.get(f"/prediction/count", headers=headers)
        data = response.json()
        self.assertEqual(data['prediction_count'], n)
    
    def test_prediction_count_unauthenticated(self):
        """Test that accessing prediction_count without authentication returns 401"""
        response = self.client.get("/prediction/count")
        self.assertEqual(response.status_code, 401)


