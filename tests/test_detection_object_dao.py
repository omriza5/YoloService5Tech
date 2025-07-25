import unittest
from db.utils import init_db, get_db
from models.detection_object import DetectionObject
from db.dao.detections import save_detection_object_dao

class TestDetectionObjectDAO(unittest.TestCase):
    def setUp(self):
        # Use in-memory SQLite for isolation
        init_db()
        self.db = get_db().__next__()

    def tearDown(self): 
        self.db.close()

    def test_save_detection_object_dao(self):
        prediction_uid = 'test-uid'
        label = 'cat'
        score = 0.95
        box = [1, 2, 3, 4]
        save_detection_object_dao(self.db, prediction_uid, label, score, box)
        obj = self.db.query(DetectionObject).filter_by(prediction_uid=prediction_uid).first()
        self.assertIsNotNone(obj)
        self.assertEqual(obj.label, label)
        self.assertEqual(obj.score, score)
        self.assertEqual(obj.box, str(box))

    