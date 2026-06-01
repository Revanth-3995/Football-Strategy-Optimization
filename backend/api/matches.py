from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import session, models
from backend import schemas

router = APIRouter()

@router.get("/", response_model=List[schemas.Match])
def read_matches(skip: int = 0, limit: int = 100, db: Session = Depends(session.get_db)):
    matches = db.query(models.Match).offset(skip).limit(limit).all()
    return matches
