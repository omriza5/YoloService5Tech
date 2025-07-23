from models.detection_object import DetectionObject

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
           