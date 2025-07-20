from fastapi import APIRouter, HTTPException, UploadFile, File, Request,Depends
from sqlalchemy.orm import Session
from services.prediction_service import (
    create_prediction,
    get_predictions_count,
    prediction_by_uid,
    delete_prediction_by_uid,
    get_all_predictions_by_label,
)
from db.utils import get_db

router = APIRouter()

@router.post("/predict")
def predict(file: UploadFile = File(...), request: Request = None, db: Session = Depends(get_db)):
    """
    Predict objects in an image
    """
    try:
       prediction = create_prediction(file, request, db)
       return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.get("/prediction/count")
def prediction_count(db: Session = Depends(get_db)):
    """
    Get the total count of prediction sessions from the last 7 days
    """
    return get_predictions_count(db)


@router.get("/prediction/{uid}")
def get_prediction_by_uid(uid: str, db: Session = Depends(get_db)):
    """
    Get prediction session by uid with all detected objects
    """
    prediction = prediction_by_uid(uid, db)
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return prediction

@router.delete("/prediction/{uid}")
def delete_prediction(uid: str,db: Session = Depends(get_db)):
    """
    Delete prediction session by uid
    """
    try:
        return delete_prediction_by_uid(uid,db)
    except Exception as e:
        status_code = getattr(e, "status_code", 500)
        detail = getattr(e, "detail", "Failed to delete prediction.")
        raise HTTPException(status_code=status_code, detail=detail)

@router.get("/predictions/label/{label}")
def get_predictions_by_label(label: str,db: Session = Depends(get_db)):
    """
    Get prediction sessions containing objects with specified label
    """
    predictions = get_all_predictions_by_label(label,db)
    if not predictions:
        raise HTTPException(status_code=404, detail="No predictions found for this label")
    return predictions
