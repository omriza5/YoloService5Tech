from datetime import datetime, timedelta
from db.dao.detections import get_unique_labels_since_dao

def get_unique_labels(db):
    "Get all distinct labels detected in the last N days (default 7)"
    days = 7
    since = datetime.now() - timedelta(days=days)
    labels = get_unique_labels_since_dao(db, since)
    return [label[0] for label in labels]