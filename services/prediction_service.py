import os
import uuid
from models.predection_session import PredictionSession
from models.detection_object import DetectionObject
import time
import shutil
from PIL import Image
from services.yolo_model import model
from sqlalchemy import func
from datetime import datetime, timedelta

UPLOAD_DIR = "uploads/original"
PREDICTED_DIR = "uploads/predicted"


def save_prediction_session(db,uid, original_image, predicted_image, user_id):
    """
    Save prediction session to database
    """
    row = PredictionSession(uid=uid, predicted_image=predicted_image, original_image=original_image, user_id=user_id)
    
    db.add(row)
    db.commit()

def save_detection_object(db,prediction_uid, label, score, box):
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

def create_prediction(file, request, db):
    start_time = time.time()
    ext = os.path.splitext(file.filename)[1]
    uid = str(uuid.uuid4())
    original_path = os.path.join(UPLOAD_DIR, uid + ext)
    predicted_path = os.path.join(PREDICTED_DIR, uid + ext)

    with open(original_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

        results = model(original_path, device="cpu")
        annotated_frame = results[0].plot()  # NumPy image with boxes
        annotated_image = Image.fromarray(annotated_frame)
        annotated_image.save(predicted_path)

        # It could be NULL if no user is logged in
        user_id = request.state.user_id 
        save_prediction_session(db,uid, original_path, predicted_path, user_id)

        detected_labels = []
        for box in results[0].boxes:
            label_idx = int(box.cls[0].item())
            label = model.names[label_idx]
            score = float(box.conf[0])
            bbox = box.xyxy[0].tolist()
            save_detection_object(db,uid, label, score, bbox)
            detected_labels.append(label)

        processing_time = round(time.time() - start_time, 2)

        return {
            "prediction_uid": uid,
            "detection_count": len(results[0].boxes),
            "labels": detected_labels,
            "time_took": processing_time,
            "user_id": user_id,
        }



def get_predictions_count(db):
    """
    Get the total count of prediction sessions
    """
    seven_days_ago = datetime.now() - timedelta(days=7)
    count = db.query(func.count(PredictionSession.uid)).filter(PredictionSession.timestamp >= seven_days_ago).scalar()
    return {"prediction_count": count}

