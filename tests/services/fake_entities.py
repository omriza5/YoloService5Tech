# Fake class to simulate a SQLAlchemy DB model object
from datetime import datetime

class FakePrediction:
    def __init__(self, uid, timestamp, original_image, predicted_image):
        self.uid = uid
        self.timestamp = timestamp
        self.original_image = original_image
        self.predicted_image = predicted_image
        
class FakeUser:
    def __init__(self, username, password):
        self.username = username
        self.password = password 
        self.created_at = datetime.now()