from pydantic import BaseModel
from typing import Optional, List, Dict

class Competition(BaseModel):
    competition_id: int
    competition_name: str
    season_id: int
    season_name: str

class Match(BaseModel):
    match_id: int
    home_team: str
    away_team: str
    home_score: Optional[int]
    away_score: Optional[int]
    match_date: Optional[str]

class ModelMetrics(BaseModel):
    accuracy: float
    precision: float
    recall: float
    f1: float
    n_samples: int
    report_text: str

class FeatureImportance(BaseModel):
    feature: str
    importance: float

class TacticalInsight(BaseModel):
    insight: str
    finding: str
    action: str

class TrainResponse(BaseModel):
    match_id: int
    metrics: ModelMetrics
    feature_importance: List[FeatureImportance]
    charts: Dict[str, str]   # chart_name -> URL path
    insights: List[TacticalInsight]

class PredictRequest(BaseModel):
    location_x: float
    location_y: float
    minute: int
    match_period: int
    counterpress: bool
    under_pressure: bool
    play_pattern: str = "Regular Play"

class PredictResponse(BaseModel):
    probability: float
    prediction: int
    interpretation: str   # Human-readable string e.g. "68% chance of winning ball"