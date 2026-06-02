from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import session
from services import statsbomb_service, visualization_service

router = APIRouter()

@router.post("/generate")
def generate_all_visualizations(match_id: int, team_name: str, db: Session = Depends(session.get_db)):
    try:
        events = statsbomb_service.get_events(match_id)
        if events.empty:
            raise HTTPException(status_code=404, detail="No events found for this match ID.")
            
        # Get opponent
        teams = events['team'].dropna().unique()
        opponent = teams[1] if len(teams) > 1 and teams[0] == team_name else (teams[0] if len(teams) > 0 else "Opponent")
        
        # Generate the 15 charts
        charts = {
            "pressing_heatmap": visualization_service.generate_pressing_heatmap(events, match_id, team_name),
            "defensive_heatmap": visualization_service.generate_defensive_heatmap(events, match_id, team_name),
            "recovery_heatmap": visualization_service.generate_recovery_heatmap(events, match_id, team_name),
            "shot_map": visualization_service.generate_shot_map(events, match_id, team_name),
            "pass_network": visualization_service.generate_pass_network(events, match_id, team_name),
            "ball_recovery_map": visualization_service.generate_ball_recovery_map(events, match_id, team_name),
            "progressive_passes": visualization_service.generate_progressive_pass_map(events, match_id, team_name),
            "expected_threat": visualization_service.generate_expected_threat_map(events, match_id, team_name),
            "team_shape": visualization_service.generate_team_shape_map(events, match_id, team_name),
            "formation_overlay": visualization_service.generate_formation_overlay(events, match_id, team_name),
            "defensive_block": visualization_service.generate_defensive_block_map(events, match_id, team_name),
            "tactical_occupancy": visualization_service.generate_tactical_zone_occupancy_map(events, match_id, team_name),
        }
        
        if len(teams) > 1:
            charts["zone_control"] = visualization_service.generate_zone_control_map(events, match_id, teams[0], teams[1])
            charts["possession_flow"] = visualization_service.generate_possession_flow_map(events, match_id, teams[0], teams[1])
            
        # Top touch player
        touches = events[events['team'] == team_name]
        if not touches.empty and 'player' in touches.columns:
            top_player = touches['player'].value_counts().idxmax()
            charts["player_touchmap"] = visualization_service.generate_player_touchmap(events, match_id, top_player)
            
        # Format paths for frontend relative access
        for k, v in charts.items():
            if v:
                charts[k] = f"/charts/{os.path.basename(v)}"
                
        return {"status": "success", "charts": charts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
import os
