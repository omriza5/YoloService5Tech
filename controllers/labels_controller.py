from fastapi import APIRouter, HTTPException, UploadFile, File, Request,Depends
from sqlalchemy.orm import Session
from services.labels_service import get_unique_labels
from db.utils import get_db

router = APIRouter()



@router.get("/labels")
def get_labels(db: Session = Depends(get_db)):
    """
    Get all distinct labels detected in the last N days (default 7)
    """
    labels = get_unique_labels(db)
    
    if not labels or len(labels) == 0:
        return {"labels": []}
    
    return {"labels": labels}