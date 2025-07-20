from fastapi import APIRouter, HTTPException, UploadFile, File, Request,Depends
from sqlalchemy.orm import Session
from db.utils import get_db
from services.image_service import get_image_by_type_and_filename


router = APIRouter()

# [ ] - add tests for get_image
@router.get("/image/{type}/{filename}")
def get_image(type: str, filename: str, db: Session = Depends(get_db)):
    """
    Get image by type and filename
    """
    try:
        return get_image_by_type_and_filename(type, filename,db)
    except Exception as e:
        status_code = getattr(e, "status_code", 500)
        detail = getattr(e, "detail", "Server Error.")
        raise HTTPException(status_code=status_code, detail=detail)

    
