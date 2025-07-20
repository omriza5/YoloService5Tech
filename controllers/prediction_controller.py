from fastapi import APIRouter, HTTPException, UploadFile, File, Request,Depends
from sqlalchemy.orm import Session
from services.prediction_service import create_prediction, get_predictions_count
from db.utils import get_db
from datetime import datetime, timedelta
from models.predection_session import PredictionSession

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

