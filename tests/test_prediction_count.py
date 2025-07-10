import io
import os
from PIL import Image
import unittest
from fastapi.testclient import TestClient

from app import DB_PATH, app,init_db


class TestPredictionCount(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        
        init_db()    
        # Create a simple test image
        self.test_image = Image.new('RGB', (100, 100), color='red')
        self.image_bytes = io.BytesIO()
        self.test_image.save(self.image_bytes, format='JPEG')
        self.image_bytes.seek(0)
    

    def test_prediction_count(self):
        """Test the prediction_count endpoint"""
        response = self.client.get("/prediction/count")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Verify the response contains the prediction_count field
        self.assertIn("prediction_count", data)
        self.assertIsInstance(data["prediction_count"], int)
    
    def test_empty_predictions(self):
        response = self.client.get(f"/prediction/count")
    
        data = response.json()
        self.assertEqual(data['prediction_count'], 0)
    
    def test_single_prediction(self):
        self.client.post(
               "/predict",
               files={"file": ("test.jpg", self.image_bytes, "image/jpeg")}
           )
        response = self.client.get(f"/prediction/count")
        data = response.json()
        self.assertEqual(data['prediction_count'], 1)
    
    def test_n_prediction(self):
        n=3
           
        for _ in range(n):
            self.client.post(
                "/predict",
                files={"file": ("test.jpg", self.image_bytes, "image/jpeg")}
            )
        response = self.client.get(f"/prediction/count")
        data = response.json()
        self.assertEqual(data['prediction_count'], n)
        
