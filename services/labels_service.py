

from datetime import datetime, timedelta
from models.detection_object import DetectionObject  

def get_unique_labels(db):
    "Get all distinct labels detected in the last N days (default 7)"
    days = 7
    since = datetime.now() - timedelta(days=days)
    print(f"Fetching labels since: {since}")
    labels = db.query(DetectionObject.label).distinct().filter(DetectionObject.timestamp >= since).all()
    return [label[0] for label in labels]