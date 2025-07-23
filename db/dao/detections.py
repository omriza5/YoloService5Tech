from models.detection_object import DetectionObject
from sqlalchemy import func

def save_detection_object_dao(db,prediction_uid, label, score, box):
    """
    Save detection object to database
    """
    row = DetectionObject(
        prediction_uid=prediction_uid,
        label=label,
        score=score,
        box=str(box)
    )
    db.add(row)
    db.commit()
    
def get_detection_objects_by_prediction_uid_dao(db, prediction_uid):
    """
    Get all detection objects for a given prediction session uid
    """
    return db.query(DetectionObject).filter(DetectionObject.prediction_uid == prediction_uid).all()

def get_average_detection_score_since(db, since):
    return db.query(func.avg(DetectionObject.score)).filter(DetectionObject.timestamp >= since).scalar()

def get_most_common_labels_since(db, since, limit=5):
    return (
        db.query(DetectionObject.label, func.count(DetectionObject.label).label("count"))
        .filter(DetectionObject.timestamp >= since)
        .group_by(DetectionObject.label)
        .order_by(func.count(DetectionObject.label).desc())
        .limit(limit)
        .all()
    )
    

def get_unique_labels_since_dao(db, since=None):
    """
    Get all distinct labels detected in the last N days
    """
    query = db.query(DetectionObject.label).distinct()
    if since is not None:
        query = query.filter(DetectionObject.timestamp >= since)
    return query.all()
    