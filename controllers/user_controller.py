from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.orm import Session
from db.utils import get_db
from services.user_service import create_new_user

router = APIRouter()

@router.post("/users")
def create_user(username: str = Body(...),
                password: str = Body(...), 
                db: Session = Depends(get_db)):
    """
    Create a new user
    """
    try:
        return create_new_user(username, password, db)
    except Exception as e:
        status_code = getattr(e, "status_code", 500)
        detail = getattr(e, "detail", "Server Error.")
        raise HTTPException(status_code=status_code, detail=detail)

    
