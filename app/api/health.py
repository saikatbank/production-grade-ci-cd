from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db

router = APIRouter()

@router.get("/live", tags=["health"], summary="Liveness probe")
def liveness_check():
    """
    Indicates whether the application is running and able to handle requests.
    """
    return {"status": "UP"}

@router.get("/ready", tags=["health"], summary="Readiness probe")
def readiness_check(db: Session = Depends(get_db)):
    """
    Indicates whether the application is ready to serve requests.
    This also verifies the database connection is alive.
    """
    try:
        db.execute(text("SELECT 1"))
        return {"status": "UP"}
    except Exception as e:
        raise HTTPException(status_code=503, detail="Database connection failed")
