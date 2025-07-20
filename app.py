from fastapi import FastAPI, HTTPException, Request, Body
import bcrypt
from fastapi.responses import FileResponse
import sqlite3
import os
from controllers.health_controller import router as health_router
from controllers.prediction_controller import router as prediction_router
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


@app.get("/prediction/{uid}")
def get_prediction_by_uid(uid: str):
    """
    Get prediction session by uid with all detected objects
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        # Get prediction session
        session = conn.execute(
            "SELECT * FROM prediction_sessions WHERE uid = ?", (uid,)
        ).fetchone()
        if not session:
            raise HTTPException(status_code=404, detail="Prediction not found")

        # Get all detection objects for this prediction
        objects = conn.execute(
            "SELECT * FROM detection_objects WHERE prediction_uid = ?", (uid,)
        ).fetchall()

        return {
            "uid": session["uid"],
            "timestamp": session["timestamp"],
            "original_image": session["original_image"],
            "predicted_image": session["predicted_image"],
            "detection_objects": [
                {
                    "id": obj["id"],
                    "label": obj["label"],
                    "score": obj["score"],
                    "box": obj["box"],
                }
                for obj in objects
            ],
        }


@app.delete("/prediction/{uid}")
def delete_prediction(uid: str):
    """
    Delete prediction session by uid
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            # Get image paths before deleting from DB
            row = conn.execute(
                "SELECT original_image, predicted_image FROM prediction_sessions WHERE uid = ?",
                (uid,),
            ).fetchone()
            if not row:
                raise HTTPException(status_code=400, detail="Prediction not found")
            original_image, predicted_image = row

            # Delete from DB
            conn.execute("DELETE FROM prediction_sessions WHERE uid = ?", (uid,))
            conn.execute(
                "DELETE FROM detection_objects WHERE prediction_uid = ?", (uid,)
            )

        # Delete image files if they exist
        for path in [original_image, predicted_image]:
            if path and os.path.exists(path):
                os.remove(path)

        return {"detail": "Prediction and images deleted"}
    except Exception as e:
        status_code = getattr(e, "status_code", 500)
        detail = getattr(e, "detail", "Failed to delete prediction.")
        raise HTTPException(status_code=status_code, detail=detail)


@app.get("/labels")
def get_labels():
    """
    Get all distinct labels detected in the last N days (default 7)
    """
    days = 7
    with sqlite3.connect(DB_PATH) as conn:
        query = f"""
            SELECT DISTINCT do.label
            FROM detection_objects do
            JOIN prediction_sessions ps ON do.prediction_uid = ps.uid
            WHERE ps.timestamp >= datetime('now', '-{days} days')
        """
        rows = conn.execute(query).fetchall()
        return {"labels": [row[0] for row in rows]}


@app.get("/labels")
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


@app.get("/predictions/label/{label}")
def get_predictions_by_label(label: str):
    """
    Get prediction sessions containing objects with specified label
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT DISTINCT ps.uid, ps.timestamp
            FROM prediction_sessions ps
            JOIN detection_objects do ON ps.uid = do.prediction_uid
            WHERE do.label = ?
        """,
            (label,),
        ).fetchall()

        return [{"uid": row["uid"], "timestamp": row["timestamp"]} for row in rows]


@app.get("/predictions/score/{min_score}")
def get_predictions_by_score(min_score: float):
    """
    Get prediction sessions containing objects with score >= min_score
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT DISTINCT ps.uid, ps.timestamp
            FROM prediction_sessions ps
            JOIN detection_objects do ON ps.uid = do.prediction_uid
            WHERE do.score >= ?
        """,
            (min_score,),
        ).fetchall()

        return [{"uid": row["uid"], "timestamp": row["timestamp"]} for row in rows]


@app.get("/image/{type}/{filename}")
def get_image(type: str, filename: str):
    """
    Get image by type and filename
    """
    if type not in ["original", "predicted"]:
        raise HTTPException(status_code=400, detail="Invalid image type")
    path = os.path.join("uploads", type, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(path)


@app.get("/prediction/{uid}/image")
def get_prediction_image(uid: str, request: Request):
    """
    Get prediction image by uid
    """
    accept = request.headers.get("accept", "")
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT predicted_image FROM prediction_sessions WHERE uid = ?", (uid,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Prediction not found")
        image_path = row[0]

    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Predicted image file not found")

    if "image/png" in accept:
        return FileResponse(image_path, media_type="image/png")
    elif "image/jpeg" in accept or "image/jpg" in accept:
        return FileResponse(image_path, media_type="image/jpeg")
    else:
        # If the client doesn't accept image, respond with 406 Not Acceptable
        raise HTTPException(
            status_code=406, detail="Client does not accept an image format"
        )


@app.post("/users")
def create_user(
    username: str = Body(...),
    password: str = Body(...),
):
    """
    Create a new user with hashed password
    """
    if not username or not password or username.strip() == "" or password.strip() == "":
        raise HTTPException(status_code=400, detail="Invalid Credentials")
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode(
        "utf-8"
    )
    username = username.lower().strip()
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                """
                INSERT INTO users (username, password)
                VALUES (?, ?)
            """,
                (username, hashed_pw),
            )
        return {"detail": "User created successfully"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists")




if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
