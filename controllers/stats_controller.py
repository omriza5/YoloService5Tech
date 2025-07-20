from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from db.utils import get_db
from services.stats_service import get_stats_data

router = APIRouter()

# [ ] - undestand the queries in stats_service.py
@router.get("/stats")
def stats_endpoint(db: Session = Depends(get_db)):
    """
    Get statistics about predictions in the last N days (default 7)
    """
    try:
        return get_stats_data(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
