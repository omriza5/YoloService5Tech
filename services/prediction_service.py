import os
import uuid
import time
import shutil
from PIL import Image
from services.yolo_service import model
from datetime import datetime, timedelta
from fastapi import HTTPException
from fastapi.responses import FileResponse
from db.dao.predictions import (save_prediction_session_dao, 
                                get_predictions_count_dao,
                                get_prediction_by_uid_dao,
                                delete_prediction_by_uid_dao,
                                get_all_predictions_by_label_dao,
                                get_all_predictions_by_score_dao)
from db.dao.detections import save_detection_object_dao, get_detection_objects_by_prediction_uid_dao
import boto3

UPLOAD_DIR = "uploads/original"
PREDICTED_DIR = "uploads/predicted"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PREDICTED_DIR, exist_ok=True)

def create_prediction(chat_id,image_name, request, db):
    start_time = time.time()
    s3 = boto3.client("s3")
    
    original_s3_key = f"{chat_id}/original/{image_name}"
    original_path = os.path.join(UPLOAD_DIR, chat_id + '-' + image_name ) # keeping original image for caching purpose
    predicted_path = os.path.join(PREDICTED_DIR, chat_id + '-' + image_name) # keeping predicted image for caching purpose
    uid = str(uuid.uuid4())
    
    download_from_s3(s3, original_s3_key, original_path)
    
    # Run YOLO prediction
    results = model(original_path, device="cpu")
    annotated_frame = results[0].plot()  # NumPy image with boxes
    annotated_image = Image.fromarray(annotated_frame)
    annotated_image.save(predicted_path)

    # Upload the predicted image to S3
    predicted_s3_key = f"{chat_id}/predicted/{image_name}"
    upload_to_s3(s3, predicted_s3_key, predicted_path)

    # Save prediction session in DB
    user_id = getattr(request.state, "user_id", None)
    save_prediction_session_dao(db, uid, original_path, predicted_path, user_id)

    detected_labels = []
    for box in results[0].boxes:
        label_idx = int(box.cls[0].item())
        label = model.names[label_idx]
        score = float(box.conf[0])
        bbox = box.xyxy[0].tolist()
        save_detection_object_dao(db, uid, label, score, bbox)
        detected_labels.append(label)

    processing_time = round(time.time() - start_time, 2)

    return {
        "prediction_uid": uid,
        "detection_count": len(results[0].boxes),
        "labels": detected_labels,
        "time_took": processing_time,
        "user_id": user_id,
        "predicted_s3_key": predicted_s3_key,
    }



def get_predictions_count(db):
    """
    Get the total count of prediction sessions
    """
    seven_days_ago = datetime.now() - timedelta(days=7)
    count = get_predictions_count_dao(db,timestamp=seven_days_ago)
    return {"prediction_count": count}

def prediction_by_uid(uid, db):
    """
    Get prediction session by uid with all detected objects
    """
    prediction = get_prediction_by_uid_dao(db, uid)
    if not prediction:
        return None
        
    objects = get_detection_objects_by_prediction_uid_dao(db, uid)

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
    prediction = get_prediction_by_uid_dao(db, uid)
    if not prediction:
        raise HTTPException(status_code=400, detail="Prediction not found")
    
    delete_prediction_by_uid_dao(db, uid)

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
    predictions = get_all_predictions_by_label_dao(db, label)
    
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
    predictions = get_all_predictions_by_score_dao(db, min_score)
    
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
    prediction = get_prediction_by_uid_dao(db, uid)
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

def download_from_s3(s3_client, s3_key, path):
    """
    Download a file from S3
    """
    bucket = "omri-zaher-yolo"
    try:
        s3_client.download_file(bucket, s3_key, path)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Resource not found in S3: {e}")

def upload_to_s3(s3_client, s3_key, path):
    """
    Upload a file to S3
    """
    bucket = "omri-zaher-yolo"
    try:
        s3_client.upload_file(path, bucket, s3_key)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Error while uploading to S3: {e}")