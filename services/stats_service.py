from sqlalchemy import func
from datetime import datetime, timedelta
from models.predection_session import PredictionSession
from models.detection_object import DetectionObject

def get_stats_data(db, days=7):
    since = datetime.now() - timedelta(days=days)
    # 1. Total number of predictions made in the last N days
    total_predictions = db.query(func.count(PredictionSession.uid)).filter(PredictionSession.timestamp >= since).scalar()

    # 2. Average confidence scores in the last N days
    avg_score = (
        db.query(func.avg(DetectionObject.score))
        .filter(DetectionObject.timestamp >= since)
        .scalar()
    )
    avg_score = round(avg_score, 4) if avg_score is not None else 0.0

    # 3. Most frequently detected object labels in the last N days
    rows = (
        db.query(DetectionObject.label, func.count(DetectionObject.label).label("count"))
        .filter(DetectionObject.timestamp >= since)
        .group_by(DetectionObject.label)
        .order_by(func.count(DetectionObject.label).desc())
        .limit(5)
        .all()
    )
    most_common_labels = {row[0]: row[1] for row in rows}

    return {
        "total_predictions": total_predictions,
        "average_confidence_score": avg_score,
        "most_common_labels": most_common_labels,
    }
