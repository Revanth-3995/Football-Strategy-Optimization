import pandas as pd
from typing import Dict, Any

from services import statsbomb_service
from analytics import event_processor
from analytics import feature_engineering

def process_match_analytics(match_id: int, team_name: str) -> Dict[str, Any]:
    """
    Orchestrates the data pipeline for a specific match and team.
    Returns a dictionary of aggregated analytics ready for DB storage.
    """
    # 1. Ingestion
    raw_events = statsbomb_service.get_events(match_id)

    # 2. Cleaning / Pre-processing
    cleaned_events = event_processor.clean_events(raw_events)

    # 3. Filtering
    team_events = event_processor.filter_by_team(cleaned_events, team_name)

    if team_events.empty:
        raise ValueError(f"No events found for team {team_name} in match {match_id}")

    # 4. Feature Extraction (Pressing)
    pressing_features = feature_engineering.extract_features(raw_events)
    team_pressures = pressing_features[raw_events.loc[pressing_features.index, 'team'] == team_name]

    # 5. Basic Aggregations
    passes = event_processor.extract_passes(team_events)
    shots = event_processor.extract_shots(team_events)

    total_passes = len(passes)
    completed_passes = len(passes[passes['pass_outcome'].isna()]) if 'pass_outcome' in passes.columns else 0
    pass_completion_rate = (completed_passes / total_passes) * 100 if total_passes > 0 else 0

    total_shots = len(shots)
    total_goals = len(shots[shots['shot_outcome'] == 'Goal']) if 'shot_outcome' in shots.columns else 0

    press_success_rate = 0.0
    if not team_pressures.empty:
        press_success_rate = team_pressures['press_success'].mean() * 100

    # Assemble analytics payload
    analytics_payload = {
        "match_id": match_id,
        "team_name": team_name,
        "total_passes": total_passes,
        "completed_passes": completed_passes,
        "pass_completion_rate": pass_completion_rate,
        "total_shots": total_shots,
        "goals": total_goals,
        "press_success_rate": press_success_rate,
        "total_pressures": len(team_pressures)
    }

    return analytics_payload
