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
    # If the database has only 1 competition (the default seed), expand it to include all open StatsBomb competitions
    if len(competitions) <= 1:
        try:
            df = statsbomb_service.get_competitions()
            # Drop duplicates on competition_id to keep competition entries unique
            unique_df = df.drop_duplicates(subset=['competition_id'])
            for _, row in unique_df.iterrows():
                comp_id = int(row['competition_id'])
                existing = db.query(models.Competition).filter(models.Competition.competition_id == comp_id).first()
                if not existing:
                    comp = models.Competition(
                        competition_id=comp_id,
                        competition_name=str(row['competition_name']),
                        country_name=str(row.get('country_name', 'Europe'))
                    )
                    db.add(comp)
            db.commit()
            competitions = db.query(models.Competition).offset(skip).limit(limit).all()
        except Exception as e:
            # Fallback in case of StatsBomb offline or error
            pass
    return competitions

