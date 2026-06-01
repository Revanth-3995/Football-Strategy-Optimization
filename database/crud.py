from sqlalchemy.orm import Session
from database import models
from typing import Dict, Any

def save_match_analytics(db: Session, analytics_data: Dict[str, Any]) -> models.MatchAnalytics:
    """
    Upserts match analytics data.
    If a record for the match_id and team_name already exists, updates it.
    Otherwise creates a new record.
    """
    db_analytics = db.query(models.MatchAnalytics).filter(
        models.MatchAnalytics.match_id == analytics_data["match_id"],
        models.MatchAnalytics.team_name == analytics_data["team_name"]
    ).first()

    if db_analytics:
        for key, value in analytics_data.items():
            setattr(db_analytics, key, value)
    else:
        db_analytics = models.MatchAnalytics(**analytics_data)
        db.add(db_analytics)

    db.commit()
    db.refresh(db_analytics)
    return db_analytics

def get_match_analytics(db: Session, match_id: int, team_name: str = None):
    query = db.query(models.MatchAnalytics).filter(models.MatchAnalytics.match_id == match_id)
    if team_name:
        query = query.filter(models.MatchAnalytics.team_name == team_name)
    return query.all()
