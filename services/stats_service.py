from datetime import datetime, timedelta
from db.dao.predictions import get_predictions_count_dao
from db.dao.detections import get_average_detection_score_since, get_most_common_labels_since

def get_stats_data(db, days=7):
    since = datetime.now() - timedelta(days=days)
    # 1. Total number of predictions made in the last N days
    total_predictions = get_predictions_count_dao(db, since)

    # 2. Average confidence scores in the last N days
    avg_score = get_average_detection_score_since(db, since)
    avg_score = round(avg_score, 4) if avg_score is not None else 0.0

    # 3. Most frequently detected object labels in the last N days
    rows = get_most_common_labels_since(db, since, limit=5)
  # Debugging line to check the output of the query
    most_common_labels = {row[0]: row[1] for row in rows}

    return {
        "total_predictions": total_predictions,
        "average_confidence_score": avg_score,
        "most_common_labels": most_common_labels,
    }
