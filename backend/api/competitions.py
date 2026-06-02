from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import session, models
from backend import schemas
from services import statsbomb_service

router = APIRouter()

@router.get("/", response_model=List[schemas.Competition])
def read_competitions(skip: int = 0, limit: int = 100, db: Session = Depends(session.get_db)):
    competitions = db.query(models.Competition).offset(skip).limit(limit).all()
    if not competitions:
        try:
            # Self-healing ingestion
            df = statsbomb_service.get_competitions()
            for _, row in df.iterrows():
                comp = models.Competition(
                    competition_id=int(row['competition_id']),
                    competition_name=str(row['competition_name']),
                    country_name=str(row.get('country_name', 'Europe'))
                )
                db.add(comp)
            db.commit()
            competitions = db.query(models.Competition).offset(skip).limit(limit).all()
        except Exception as e:
            # Fallback in case of StatsBomb offline
            pass
    return competitions

