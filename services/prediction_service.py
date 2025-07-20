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
from fastapi import HTTPException
from fastapi.responses import FileResponse

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

def prediction_by_uid(uid, db):
    """
    Get prediction session by uid with all detected objects
    """
    prediction = db.query(PredictionSession).filter(PredictionSession.uid == uid).first()
    if not prediction:
        return None
        
    objects = db.query(DetectionObject).filter(DetectionObject.prediction_uid == uid).all()

    return {
        "uid": prediction.uid,
        "timestamp": prediction.timestamp,
        "original_image": prediction.original_image,
        "predicted_image": prediction.predicted_image,
        "detection_objects": [
            {
                "id": obj.id,
                "label": obj.label,
                "score": obj.score,
                "box": obj.box,
            }
            for obj in objects
        ],
    }


def delete_prediction_by_uid(uid, db):
    """
    Delete prediction session by uid
    """
    prediction = db.query(PredictionSession).filter(PredictionSession.uid == uid).first()
    if not prediction:
        raise HTTPException(status_code=400, detail="Prediction not found")
    
    db.query(PredictionSession).filter(PredictionSession.uid == uid).delete()
    db.query(DetectionObject).filter(DetectionObject.prediction_uid == uid).delete()
    db.commit()

    # Clean up image files
    original_image_path = os.path.join(UPLOAD_DIR, uid + ".jpg")
    predicted_image_path = os.path.join(PREDICTED_DIR, uid + ".jpg")

    if os.path.exists(original_image_path):
        os.remove(original_image_path)
    if os.path.exists(predicted_image_path):
        os.remove(predicted_image_path)

    return {"detail": "Prediction and images deleted"}
    

def get_all_predictions_by_label(label, db):
    """
    Get prediction sessions containing objects with specified label
    """
    predictions = db.query(PredictionSession).join(DetectionObject).filter(DetectionObject.label == label).all()
    
    if not predictions:
        raise HTTPException(status_code=404, detail="No predictions found for this label")
    
    return [
        {
            "uid": pred.uid,
            "timestamp": pred.timestamp,
            "original_image": pred.original_image,
            "predicted_image": pred.predicted_image,
        }
        for pred in predictions
    ]

def get_all_predictions_by_score(min_score, db):
    """
    Get prediction sessions containing objects with score >= min_score
    """
    predictions = db.query(PredictionSession).join(DetectionObject).filter(DetectionObject.score >= min_score).all()
    
    if not predictions:
        return None
    
    return [
        {
            "uid": pred.uid,
            "timestamp": pred.timestamp,
            "original_image": pred.original_image,
            "predicted_image": pred.predicted_image,
        }
        for pred in predictions
    ]
    

def get_prediction_image_by_uid(uid, request, db):
    accept = request.headers.get("accept", "")
    prediction = db.query(PredictionSession).filter(PredictionSession.uid == uid).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    image_path = prediction.predicted_image

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
        