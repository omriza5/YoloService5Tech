import unittest
from db.utils import init_db, get_db
from models.detection_object import DetectionObject
from db.dao.predictions import (save_prediction_session_dao, 
                                get_predictions_count_dao, 
                                get_prediction_by_uid_dao, 
                                delete_prediction_by_uid_dao,
                                get_all_predictions_by_label_dao,
                                get_all_predictions_by_score_dao)
from db.dao.detections import save_detection_object_dao
from models.prediction_session import PredictionSession  # Import PredictionSession

class TestPredictionDAO(unittest.TestCase):
    def setUp(self):
        # Use in-memory SQLite for isolation
        init_db()
        self.db = get_db().__next__()
        self.p = PredictionSession(
            uid='test-uid',
            original_image='original_image.jpg',
            predicted_image='predicted_image.jpg',
            user_id=1
        )

    def tearDown(self): 
        self.db.close()

    def test_save_detection_object_dao(self):
        save_prediction_session_dao(self.db, self.p.uid, self.p.original_image, self.p.predicted_image, self.p.user_id)
        obj = self.db.query(PredictionSession).filter_by(uid=self.p.uid).first()
        self.assertIsNotNone(obj)
        self.assertEqual(obj.uid, self.p.uid)
        self.assertEqual(obj.original_image, self.p.original_image)
        self.assertEqual(obj.predicted_image, self.p.predicted_image)
        self.assertEqual(obj.user_id, self.p.user_id)
    
    def test_get_predictions_count_dao(self):
        # Add a prediction session to the database
        save_prediction_session_dao(self.db, self.p.uid, self.p.original_image, self.p.predicted_image, self.p.user_id)
        
        # Test count without timestamp
        count = get_predictions_count_dao(self.db)
        self.assertEqual(count, 1)
        
        # Test count with timestamp
        count_since = get_predictions_count_dao(self.db, timestamp='2023-01-01')
        self.assertEqual(count_since, 1)
    
    def test_get_prediction_by_uid_dao(self):
        # Add a prediction session to the database
        save_prediction_session_dao(self.db, self.p.uid, self.p.original_image, self.p.predicted_image, self.p.user_id)
        
        # Retrieve by UID
        retrieved = get_prediction_by_uid_dao(self.db, self.p.uid)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.uid, self.p.uid)
    
    def test_delete_prediction_by_uid_dao(self):
        # Add a prediction session to the database
        save_prediction_session_dao(self.db, self.p.uid, self.p.original_image, self.p.predicted_image, self.p.user_id)
        
        # Delete by UID
        delete_prediction_by_uid_dao(self.db, self.p.uid)
        
        # Verify deletion
        deleted = get_prediction_by_uid_dao(self.db, self.p.uid)
        self.assertIsNone(deleted)
        
    def test_get_all_predictions_by_label_dao(self):
        # Add a prediction session with a detection object
        save_prediction_session_dao(self.db, self.p.uid, self.p.original_image, self.p.predicted_image, self.p.user_id)
        detection_obj = DetectionObject(
            prediction_uid=self.p.uid,
            label='cat',
            score=0.95,
            box=[1, 2, 3, 4]
        )
        save_detection_object_dao(self.db,
                                  detection_obj.prediction_uid,
                                  detection_obj.label,
                                  detection_obj.score,
                                  detection_obj.box)
        
        # Retrieve predictions by label
        predictions = get_all_predictions_by_label_dao(self.db, 'cat')
        self.assertGreater(len(predictions), 0)
        self.assertEqual(predictions[0].uid, self.p.uid)
        
    
    def test_get_all_predictions_by_score_dao(self):
        # Add a prediction session with a detection object
        save_prediction_session_dao(self.db, self.p.uid, self.p.original_image, self.p.predicted_image, self.p.user_id)
        detection_obj = DetectionObject(
            prediction_uid=self.p.uid,
            label='dog',
            score=0.85,
            box=[5, 6, 7, 8]
        )
        save_detection_object_dao(self.db,
                                  detection_obj.prediction_uid,
                                  detection_obj.label,
                                  detection_obj.score,
                                  detection_obj.box)
        
        # Retrieve predictions by score
        predictions = get_all_predictions_by_score_dao(self.db, 0.8)
        self.assertGreater(len(predictions), 0)
        self.assertEqual(predictions[0].uid, self.p.uid)