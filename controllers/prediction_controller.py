from fastapi import APIRouter, HTTPException, UploadFile, File, Request,Depends
from sqlalchemy.orm import Session
from services.prediction_service import create_prediction
from db.utils import get_db
router = APIRouter()

@router.post("/predict")
def predict(file: UploadFile = File(...), request: Request = None, db: Session = Depends(get_db)):
    """
    Predict objects in an image
    """
    try:
       create_prediction(file, request, db)
       
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
