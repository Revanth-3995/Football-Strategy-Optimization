from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import session, models
from backend import schemas
from services import statsbomb_service

router = APIRouter()

@router.get("/", response_model=List[schemas.Match])
def read_matches(competition_id: Optional[int] = None, season_id: Optional[int] = None, 
                 skip: int = 0, limit: int = 100, db: Session = Depends(session.get_db)):
    # Standardize filtering
    query = db.query(models.Match)
    if competition_id:
        # Resolve DB model relationship if competition exists
        db_comp = db.query(models.Competition).filter(models.Competition.competition_id == competition_id).first()
        if db_comp:
            query = query.filter(models.Match.competition_id == db_comp.id)
            
    matches = query.offset(skip).limit(limit).all()
    
    if not matches and competition_id and season_id:
        try:
            # Self-healing match ingestion
            df = statsbomb_service.get_matches(competition_id, season_id)
            db_comp = db.query(models.Competition).filter(models.Competition.competition_id == competition_id).first()
            if not db_comp:
                db_comp = models.Competition(competition_id=competition_id, competition_name="UEFA Euro 2020", country_name="Europe")
                db.add(db_comp)
                db.commit()
                db.refresh(db_comp)
                
            # Create a season if not exists
            db_season = db.query(models.Season).filter(models.Season.season_id == season_id).first()
            if not db_season:
                db_season = models.Season(season_id=season_id, season_name="2020")
                db.add(db_season)
                db.commit()
                db.refresh(db_season)
                
            for _, row in df.iterrows():
                # Check if teams exist
                home_team_name = str(row['home_team'])
                away_team_name = str(row['away_team'])
                
                db_home = db.query(models.Team).filter(models.Team.team_name == home_team_name).first()
                if not db_home:
                    db_home = models.Team(team_id=int(np.random.randint(1000, 9999)) if 'home_team_id' not in row else int(row['home_team_id']), team_name=home_team_name)
                    db.add(db_home)
                db_away = db.query(models.Team).filter(models.Team.team_name == away_team_name).first()
                if not db_away:
                    db_away = models.Team(team_id=int(np.random.randint(1000, 9999)) if 'away_team_id' not in row else int(row['away_team_id']), team_name=away_team_name)
                    db.add(db_away)
                db.commit()
                
                db_home = db.query(models.Team).filter(models.Team.team_name == home_team_name).first()
                db_away = db.query(models.Team).filter(models.Team.team_name == away_team_name).first()
                
                date_str = str(row.get('match_date', '2021-06-11'))
                try:
                    match_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                except Exception:
                    match_date = datetime.now().date()
                    
                match = models.Match(
                    match_id=int(row['match_id']),
                    match_date=match_date,
                    home_team_id=db_home.id,
                    away_team_id=db_away.id,
                    home_score=int(row['home_score']),
                    away_score=int(row['away_score']),
                    competition_id=db_comp.id,
                    season_id=db_season.id
                )
                db.add(match)
            db.commit()
            
            # Re-query
            query = db.query(models.Match)
            if db_comp:
                query = query.filter(models.Match.competition_id == db_comp.id)
            matches = query.offset(skip).limit(limit).all()
        except Exception as e:
            pass
            
    return matches

import numpy as np

