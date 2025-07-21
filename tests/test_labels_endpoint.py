import unittest
from fastapi.testclient import TestClient
import io
from app import app, init_db
import os
from .services.auth import get_basic_auth_header
from db.setup_db import DB_PATH

class TestLabelsEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
            
        init_db()
        
        self.username = "testuser"
        self.password = "testpass"
        self.client.post("/users", json={"username": self.username, "password": self.password})
    
    def test_labels_endpoint_no_predictions(self):
        headers = get_basic_auth_header(self.username, self.password)
        response = self.client.get("/labels", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["labels"], [])
     
    def test_labels_endpoint_invalid_image_upload(self):
        """
        Test that uploading an invalid (non-image) file to /predict returns an error and does not add any labels.
        """
        headers = get_basic_auth_header(self.username, self.password)
        response = self.client.post(
            "/predict",
            files={"file": ("not_an_image.txt", io.BytesIO(b"not an image"), "text/plain")}
        )
        # Should return 500 due to the error handling in the endpoint
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertIn("Prediction failed", data.get("detail", ""))

        # Ensure /labels is still empty
        response = self.client.get("/labels",headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["labels"], [])       

    def test_labels_endpoint_returns_labels_after_image_upload(self):
        """
        Test that the /labels endpoint returns at least one label after uploading an image.
        Steps:
        1. Upload a test image.
        2. Call the /labels endpoint.
        3. Assert that the response contains at least one label.
        """
        # Arrange test
        self.upload_test_image("tests/assets/cat.jpg")
        headers = get_basic_auth_header(self.username, self.password)

        response = self.client.get("/labels", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # The model may return the same label for different images, so check for at least 1 or 2 unique labels
        self.assertTrue(len(data["labels"]) >= 1)
        
    def test_labels_endpoint_returns_multiple_unique_labels(self):
        """
        Test that the /labels endpoint returns multiple unique labels after uploading images with different objects.
        Steps:
        1. Upload a test image of a cat.
        2. Upload a test image of a bear.
        3. Call the /labels endpoint.
        4. Assert that the response contains at least two unique labels.
        """
        self.upload_test_image("tests/assets/cat.jpg")
        self.upload_test_image("tests/assets/bear.jpg")
        headers = get_basic_auth_header(self.username, self.password)

        response = self.client.get("/labels", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        labels = data.get("labels", [])
        self.assertGreaterEqual(len(set(labels)), 2)
        
    def test_labels_endpoint_returns_unique_labels_with_duplicate_images_labels(self):
        """
        Test that the /labels endpoint returns only unique labels even if multiple images of the same object are uploaded.
        Steps:
        1. Upload a test image of a bear.
        2. Upload a test image of a cat.
        3. Upload another test image of a cat.
        4. Call the /labels endpoint.
        5. Assert that the response contains exactly two unique labels.
        """
        self.upload_test_image("tests/assets/bear.jpg")
        self.upload_test_image("tests/assets/cat.jpg")
        self.upload_test_image("tests/assets/cat.jpg")
        
        headers = get_basic_auth_header(self.username, self.password)
        
        response = self.client.get("/labels", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        labels = data.get("labels", [])
        self.assertEqual(len(set(labels)), 2)

    def upload_test_image(self, path):
        with open(path, "rb") as img_file:
            response = self.client.post(
                "/predict",
                files={"file": ("test_object.jpg", img_file, "image/jpeg")}
            )
        return response 

    def test_labels_endpoint_unauthorized_no_credentials(self):
        """
        Test that accessing /labels without credentials returns 401 Unauthorized.
        """
        response = self.client.get("/labels")
        self.assertEqual(response.status_code, 401)

    def test_labels_endpoint_unauthorized_invalid_credentials(self):
        """
        Test that accessing /labels with invalid credentials returns 401 Unauthorized.
        """
        headers = get_basic_auth_header("wronguser", "wrongpass")
        response = self.client.get("/labels", headers=headers)
        self.assertEqual(response.status_code, 401)

