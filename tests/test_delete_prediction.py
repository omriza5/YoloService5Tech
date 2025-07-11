import unittest
import os
import sqlite3
from fastapi.testclient import TestClient
from app import app, DB_PATH, init_db, PREDICTED_DIR, UPLOAD_DIR
from tests.services.image_utils import create_dummy_image

class TestDeletePredictionEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        # Clean DB and folders for isolation
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        init_db()
        # remove any existing files in upload and predicted directories
        for dir in [UPLOAD_DIR, PREDICTED_DIR]:
            if os.path.exists(dir):
                for file in os.listdir(dir):
                    os.remove(os.path.join(dir, file))

    def test_delete_existing_prediction(self):
        # Arrange
        image = create_dummy_image('red','donut')
        response = self.client.post(
            "/predict",
            files={"file": ("test_image.jpg", image, "image/jpeg")}
        )
        prediction = response.json()
        uid = prediction['prediction_uid']
        
        # Act
        prediction_delete_response = self.client.delete(f"/prediction/{uid}")

        # Assert
        expected_response = {"detail": "Prediction and images deleted"}
        self.assertEqual(prediction_delete_response.status_code, 200)
        self.assertEqual(prediction_delete_response.json(), expected_response)

    # def test_delete_nonexistent_prediction(self):
    #     uid = "does-not-exist-uid"
    #     resp = self.client.delete(f"/prediction/{uid}")
    #     self.assertIn(resp.status_code, (400, 404))
    #     self.assertIn("not found", resp.json()["detail"].lower())

    # def test_delete_twice_returns_404(self):
    #     uid, orig_path, pred_path = self.create_dummy_prediction()
    #     resp1 = self.client.delete(f"/prediction/{uid}")
    #     self.assertEqual(resp1.status_code, 200)
    #     resp2 = self.client.delete(f"/prediction/{uid}")
    #     self.assertIn(resp2.status_code, (400, 404))

    # def test_delete_prediction_file_removal_failure(self):
    #     uid, orig_path, pred_path = self.create_dummy_prediction()
    #     # Patch os.remove to raise OSError
    #     original_remove = os.remove
    #     def fail_remove(path):
    #         raise OSError("Simulated file removal error")
    #     os.remove = fail_remove
    #     try:
    #         resp = self.client.delete(f"/prediction/{uid}")
    #         self.assertEqual(resp.status_code, 500)
    #         self.assertIn("failed to delete", resp.json()["detail"].lower())
    #     finally:
    #         os.remove = original_remove
    #         # Clean up files if still exist
    #         for p in [orig_path, pred_path]:
    #             if os.path.exists(p):
    #                 os.remove(p)

    # def test_delete_prediction_missing_files(self):
    #     # Only create DB entry, no files
    #     uid, orig_path, pred_path = self.create_dummy_prediction(missing_files=['original', 'predicted'])
    #     self.assertFalse(os.path.exists(orig_path))
    #     self.assertFalse(os.path.exists(pred_path))
    #     resp = self.client.delete(f"/prediction/{uid}")
    #     self.assertEqual(resp.status_code, 200)
    #     self.assertIn("deleted", resp.json()["detail"].lower())
    #     # DB should be gone
    #     with sqlite3.connect(DB_PATH) as conn:
    #         row = conn.execute("SELECT * FROM prediction_sessions WHERE uid = ?", (uid,)).fetchone()
    #         self.assertIsNone(row)




