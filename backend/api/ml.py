from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import session
from services import statsbomb_service, ml_service
from analytics import feature_engineering
from pydantic import BaseModel
from typing import List, Dict, Any

router = APIRouter()
ml_platform = ml_service.MLPlatform()

class PredictPressRequest(BaseModel):
    location_x: float
    location_y: float
    dist_from_goal: float
    pitch_zone: str
    minute: int
    match_period: int
    counterpress: bool
    under_pressure: bool
    play_pattern: str
    match_state: str
    score_difference: int

class PredictOutcomeRequest(BaseModel):
    xg_diff: float
    possession_diff: float
    pass_completion_diff: float
    progressive_passes_diff: float
    defensive_actions_diff: float
    recoveries_diff: float
    press_success_diff: float

@router.post("/train-press")
def train_press_model(match_id: int, team_name: str):
    try:
        events = statsbomb_service.get_events(match_id)
        if events.empty:
            raise HTTPException(status_code=404, detail="No events found for this match.")
            
        # Extract features & enrich with state details
        features = feature_engineering.extract_features(events)
        if features.empty:
            raise HTTPException(status_code=400, detail="Insufficient pressure events to train.")
            
        # Enrich
        features['match_state'] = 'drawing'
        features['score_difference'] = 0
        
        # Train
        res = ml_platform.train_press_model(features)
        return {"status": "success", "results": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict-press")
def predict_press_success(req: PredictPressRequest):
    try:
        res = ml_platform.predict_press_success(req.dict())
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/train-outcome")
def train_outcome_predictor():
    try:
        # Trains on default dataset comparing XGBoost and LightGBM
        res = ml_platform.train_outcome_predictor(pd.DataFrame())
        return {"status": "success", "comparison": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict-outcome")
def predict_match_outcome(req: PredictOutcomeRequest):
    try:
        res = ml_platform.predict_match_outcome(req.dict())
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/detect-formation")
def detect_formation(match_id: int, team_name: str):
    try:
        events = statsbomb_service.get_events(match_id)
        res = ml_platform.detect_formation(events, team_name)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/detect-role")
def detect_player_role(match_id: int, player_name: str):
    try:
        events = statsbomb_service.get_events(match_id)
        res = ml_platform.detect_player_role(events, player_name)
        return {"player": player_name, "role_detected": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cluster-players")
def cluster_players(match_id: int, team_name: str):
    try:
        events = statsbomb_service.get_events(match_id)
        res = ml_platform.cluster_players(events, team_name)
        return {"team": team_name, "clusters": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

import pandas as pd
