from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import session
from services import statsbomb_service, coach_service, scouting_service, recruitment_service
from pydantic import BaseModel
from typing import List, Dict, Any

router = APIRouter()
coach_ai = coach_service.FootballCoachAI()
scouter = scouting_service.OpponentScoutingPlatform()
recruitment = recruitment_service.RecruitmentEngine()

class ChatRequest(BaseModel):
    match_id: int
    team_name: str
    message: str

class SimulateRequest(BaseModel):
    formation: str
    press_intensity: str # "high", "medium", "low"
    defensive_line: str # "high", "medium", "low"
    build_up_style: str # "short", "direct", "long"

@router.post("/chat")
def chat_with_match(req: ChatRequest):
    try:
        events = statsbomb_service.get_events(req.match_id)
        if events.empty:
            raise HTTPException(status_code=404, detail="No events found for this match.")
            
        answer = coach_ai.answer_coaching_query(events, req.team_name, req.message)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scouting")
def scout_opponent(match_id: int, opponent_team: str):
    try:
        events = statsbomb_service.get_events(match_id)
        if events.empty:
            raise HTTPException(status_code=404, detail="No events found.")
            
        report = scouter.generate_scouting_report(events, opponent_team)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/simulate")
def simulate_tactics(req: SimulateRequest):
    try:
        # Grounded rule-based tactical sandbox simulation
        press_factor = 1.2 if req.press_intensity == "high" else (0.8 if req.press_intensity == "low" else 1.0)
        line_factor = 1.3 if req.defensive_line == "high" else (0.7 if req.defensive_line == "low" else 1.0)
        
        # Calculate simulated metrics
        simulated_recoveries = int(52 * press_factor)
        simulated_xg = round(1.4 * press_factor * (1.1 if req.build_up_style == "short" else 0.9), 2)
        simulated_possession = round(50.0 * (1.1 if req.build_up_style == "short" else 0.9), 1)
        simulated_conceded = round(1.2 / press_factor * line_factor, 2)
        
        efficiency = round(float((simulated_xg / (simulated_xg + simulated_conceded)) * 100), 1)
        
        return {
            "expected_recoveries": simulated_recoveries,
            "expected_xg": simulated_xg,
            "expected_possession": simulated_possession,
            "expected_chances_conceded": simulated_conceded,
            "tactical_efficiency": efficiency,
            "recommendation": "Maintain a High press with Short build-up for maximum dominance." if efficiency > 55 else "Conserve energy in a Mid block to avoid conceding transitions."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recruitment")
def recruit_players(position: str = "All", age_max: int = 35, budget_max: int = 200000000, 
                    att: float = 0.5, pas: float = 0.5, dfn: float = 0.5, prs: float = 0.5, 
                    drb: float = 0.5, phy: float = 0.5):
    try:
        style_weights = [att, pas, dfn, prs, drb, phy]
        results = recruitment.search_similar_players(position, age_max, budget_max, style_weights)
        return {"recommendations": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
