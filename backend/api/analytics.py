from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import session, crud
from backend import schemas_analytics
from services import analytics_service

router = APIRouter()

@router.post("/process", response_model=schemas_analytics.MatchAnalyticsResponse)
def process_analytics(req: schemas_analytics.ProcessMatchRequest, db: Session = Depends(session.get_db)):
    try:
        analytics_payload = analytics_service.process_match_analytics(req.match_id, req.team_name)
        db_analytics = crud.save_match_analytics(db, analytics_payload)
        return db_analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{match_id}", response_model=List[schemas_analytics.MatchAnalyticsResponse])
def get_analytics(match_id: int, team_name: str = None, db: Session = Depends(session.get_db)):
    try:
        analytics = crud.get_match_analytics(db, match_id, team_name)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
