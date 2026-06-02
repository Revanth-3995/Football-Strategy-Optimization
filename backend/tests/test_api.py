from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_get_competitions():
    response = client.get("/api/competitions")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_matches():
    # Euro 2020: 55, season 43
    response = client.get("/api/matches?competition_id=55&season_id=43")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

from unittest.mock import patch
import pandas as pd
import numpy as np

@patch("backend.data_loader.get_events")
def test_get_advanced_visualizations(mock_get_events):
    mock_get_events.return_value = pd.DataFrame({
        'type': ['Pass', 'Pass', 'Ball Recovery', 'Carry'],
        'team': ['TeamA', 'TeamA', 'TeamA', 'TeamA'],
        'player': ['P1', 'P2', 'P2', 'P1'],
        'location': [[20, 40], [80, 40], [50, 50], [60, 60]],
        'pass_end_location': [[40, 40], [100, 40], np.nan, np.nan],
        'pass_outcome': [np.nan, np.nan, np.nan, np.nan],
        'pass_recipient': ['P2', 'P1', np.nan, np.nan],
        'position': ['Midfielder', 'Forward', 'Forward', 'Midfielder'],
        'shot_outcome': [np.nan, np.nan, np.nan, np.nan],
        'shot_statsbomb_xg': [np.nan, np.nan, np.nan, np.nan]
    })

    response = client.get("/api/visualizations/advanced/999/TeamA")
    assert response.status_code == 200

    data = response.json()
    assert "recovery_heatmap" in data
    assert "zone_control_map" in data
    assert "expected_threat_map" in data
    assert "team_shape_map" in data
    assert "formation_overlay_map" in data

def test_predict_without_model():
    # Ensure this works assuming model isn't trained yet.
    # It might fail if a model was trained during other tests, so let's handle that.
    import os
    if os.path.exists("outputs/model.pkl"):
        os.remove("outputs/model.pkl")
    if os.path.exists("outputs/model_columns.pkl"):
        os.remove("outputs/model_columns.pkl")

    data = {
        "location_x": 60,
        "location_y": 40,
        "minute": 10,
        "match_period": 1,
        "counterpress": False,
        "under_pressure": False,
        "play_pattern": "Regular Play"
    }

    response = client.post("/api/predict", json=data)
    assert response.status_code == 404
