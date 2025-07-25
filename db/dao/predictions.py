from models.prediction_session import PredictionSession
from models.detection_object import DetectionObject

def save_prediction_session_dao(db,uid, original_image, predicted_image, user_id):
    """
    Save prediction session to database
    """
    row = PredictionSession(uid=uid, predicted_image=predicted_image, original_image=original_image, user_id=user_id)
    
    db.add(row)
    db.commit()
    
def get_predictions_count_dao(db, timestamp=None):
    """
    Get count of predictions from the given timestamp until now.
    If timestamp is None, return total count.
    """
    query = db.query(PredictionSession)
    if timestamp:
        query = query.filter(PredictionSession.timestamp >= timestamp)
    return query.count()

def get_prediction_by_uid_dao(db, uid):
    return db.query(PredictionSession).filter(PredictionSession.uid == uid).first()

def delete_prediction_by_uid_dao(db, uid):
    """
    Delete prediction session by uid
    """
    db.query(PredictionSession).filter(PredictionSession.uid == uid).delete()
    db.query(DetectionObject).filter(DetectionObject.prediction_uid == uid).delete()
    db.commit()
    
def get_all_predictions_by_label_dao(db, label):
    """
    Get prediction sessions containing objects with specified label
    """
    return db.query(PredictionSession).join(DetectionObject).filter(DetectionObject.label == label).all()

def get_all_predictions_by_score_dao(db, min_score):
    """
    Get prediction sessions containing objects with score >= min_score
    """
    return db.query(PredictionSession).join(DetectionObject).filter(DetectionObject.score >= min_score).all()    
    
    
