from fastapi import FastAPI, HTTPException, Request, Body

from fastapi.responses import FileResponse
import sqlite3
import os
from controllers.health_controller import router as health_router
from controllers.prediction_controller import router as prediction_router
from controllers.labels_controller import router as labels_router
from controllers.image_controller import router as image_router
from controllers.user_controller import router as user_router
from services.yolo_model import model
from db.utils import init_db


# Disable GPU usage
import torch

torch.cuda.is_available = lambda: False

app = FastAPI()

# Initialize database
init_db()

# Import middleware to ensure registration
import middlewares.auth

UPLOAD_DIR = "uploads/original"
PREDICTED_DIR = "uploads/predicted"
DB_PATH = "predictions.db"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PREDICTED_DIR, exist_ok=True)

# app routes
app.include_router(health_router)
app.include_router(prediction_router)
app.include_router(labels_router)
app.include_router(image_router)
app.include_router(user_router)

@app.get("/stats")
def get_stats():
    """
    Get statistics about predictions in the last N days (default 7)
    """
    days = 7
    with sqlite3.connect(DB_PATH) as conn:
        # 1. Total number of predictions made in the last N days
        total_predictions = conn.execute(
            f"""SELECT COUNT(*) 
              FROM prediction_sessions 
              WHERE timestamp >= datetime('now', '-{days} days')"""
        ).fetchone()[0]

        # 2. Average confidence scores in the last N days
        avg_score = conn.execute(
            f"""
            SELECT ROUND(AVG(score), 2)
            FROM detection_objects do JOIN prediction_sessions ps ON do.prediction_uid = ps.uid
            WHERE ps.timestamp >= datetime('now', '-{days} days')
            """
        ).fetchone()[0]
        avg_score = round(avg_score, 4) if avg_score is not None else 0.0

        # 3. Most frequently detected object labels in the last N days
        rows = conn.execute(
            f"""
            SELECT do.label, COUNT(*) as count
            FROM detection_objects do
            JOIN prediction_sessions ps ON do.prediction_uid = ps.uid
            WHERE ps.timestamp >= datetime('now', '-{days} days')
            GROUP BY do.label
            ORDER BY count DESC
            LIMIT 5
            """
        ).fetchall()
        most_common_labels = {row[0]: row[1] for row in rows}

        return {
            "total_predictions": total_predictions,
            "average_confidence_score": avg_score,
            "most_common_labels": most_common_labels,
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
