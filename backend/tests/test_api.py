from fastapi.testclient import TestClient
from main import app

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
