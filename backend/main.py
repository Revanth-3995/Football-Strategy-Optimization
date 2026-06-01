from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import pandas as pd
from typing import List
from sklearn.model_selection import train_test_split
from pydantic import BaseModel

import database
import data_loader
import feature_engineering
import model as ml_model
import visualizations
from schemas import (
    Competition, Match, PredictRequest, PredictResponse,
    TrainResponse, ModelMetrics, TacticalInsight
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TrainRequest(BaseModel):
    match_id: int
    team: str

@app.on_event("startup")
def startup_event():
    database.init_db()
    os.makedirs("outputs/charts", exist_ok=True)
    os.makedirs("data/cache", exist_ok=True)

app.mount("/charts", StaticFiles(directory="outputs/charts"), name="charts")

@app.get("/api/competitions", response_model=List[Competition])
def get_competitions():
    try:
        df = data_loader.get_competitions()
        return df.to_dict(orient="records")
    except data_loader.DataLoadError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/matches", response_model=List[Match])
def get_matches(competition_id: int, season_id: int):
    try:
        df = data_loader.get_matches(competition_id, season_id)
        matches = df.to_dict(orient="records")
        for match in matches:
            database.upsert_match(match)
        return matches
    except data_loader.DataLoadError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def derive_insights(pressures_df: pd.DataFrame, model, X: pd.DataFrame) -> list[dict]:
    preds = model.predict_proba(X)[:, 1]
    df = pressures_df.copy()
    df['predicted_prob'] = preds

    insights = []

    # 1. Best Pressing Zone
    zone_means = df.groupby('pitch_zone')['predicted_prob'].mean()
    if not zone_means.empty:
        best_zone = zone_means.idxmax()
        rate = zone_means.max()
        insights.append({
            "insight": "Best Pressing Zone",
            "finding": f"{best_zone} third has {rate:.0%} predicted success rate",
            "action": f"Focus pressing in the {best_zone} third"
        })
    else:
        insights.append({"insight": "Best Pressing Zone", "finding": "N/A", "action": "N/A"})

    # 2. Counterpress Effectiveness
    if not df.empty and 'counterpress' in df.columns:
        cp_true = df[df['counterpress'] == True]['predicted_prob'].mean()
        cp_false = df[df['counterpress'] == False]['predicted_prob'].mean()
        if not pd.isna(cp_true) and not pd.isna(cp_false) and cp_false > 0:
            ratio = cp_true / cp_false
            insights.append({
                "insight": "Counterpress Effectiveness",
                "finding": f"Counterpresses are {ratio:.1f}x more effective than planned presses",
                "action": "Train immediate counterpressing within 5 seconds of losing the ball"
            })
        else:
            insights.append({"insight": "Counterpress Effectiveness", "finding": "N/A", "action": "N/A"})
    else:
        insights.append({"insight": "Counterpress Effectiveness", "finding": "N/A", "action": "N/A"})

    # 3. Time Management
    if not df.empty and 'minute' in df.columns:
        early = df[df['minute'] <= 70]['predicted_prob'].mean()
        late = df[df['minute'] > 70]['predicted_prob'].mean()
        if not pd.isna(early) and not pd.isna(late) and early > 0:
            drop_pct = (early - late) / early * 100
            insights.append({
                "insight": "Time Management",
                "finding": f"Press success drops {drop_pct:.0f}% after the 70th minute",
                "action": "Transition to mid-block after 70 minutes to conserve energy"
            })
        else:
            insights.append({"insight": "Time Management", "finding": "N/A", "action": "N/A"})
    else:
        insights.append({"insight": "Time Management", "finding": "N/A", "action": "N/A"})

    # 4. Wide Pressing Inefficiency
    if not df.empty and 'location_y' in df.columns:
        central = df[(df['location_y'] >= 25) & (df['location_y'] <= 55)]['predicted_prob'].mean()
        wide = df[(df['location_y'] < 25) | (df['location_y'] > 55)]['predicted_prob'].mean()
        if not pd.isna(central) and not pd.isna(wide):
            insights.append({
                "insight": "Wide Pressing Inefficiency",
                "finding": f"Wide pressing has {wide:.0%} vs central {central:.0%} success",
                "action": "Funnel opponent inward; avoid chasing wide — press centrally"
            })
        else:
            insights.append({"insight": "Wide Pressing Inefficiency", "finding": "N/A", "action": "N/A"})
    else:
        insights.append({"insight": "Wide Pressing Inefficiency", "finding": "N/A", "action": "N/A"})

    # 5. Set Piece Pressing
    if not df.empty and 'play_pattern' in df.columns:
        gk_rate = df[df['play_pattern'] == 'From Goal Kick']['predicted_prob'].mean()
        if not pd.isna(gk_rate):
            insights.append({
                "insight": "Set Piece Pressing",
                "finding": f"Goal kick restarts yield {gk_rate:.0%} pressing success rate",
                "action": "Trigger high press immediately after opponent goal kicks"
            })
        else:
            insights.append({"insight": "Set Piece Pressing", "finding": "N/A", "action": "N/A"})
    else:
        insights.append({"insight": "Set Piece Pressing", "finding": "N/A", "action": "N/A"})

    return insights

@app.post("/api/train", response_model=TrainResponse)
def train_pipeline(req: TrainRequest):
    try:
        events = data_loader.get_events(req.match_id)

        # 2. Extract features
        pressures_df = feature_engineering.extract_features(events)

        # Team filter for model and charts
        team_pressures_df = pressures_df[events.loc[pressures_df.index, 'team'] == req.team]

        # If not enough events, just use all for model to not break
        if len(team_pressures_df) > 50:
            model_df = team_pressures_df
        else:
            model_df = pressures_df

        X, y = feature_engineering.get_feature_matrix(model_df)

        # 3. Split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # 4. Train
        model = ml_model.train_model(X_train, y_train)

        # 5. Evaluate
        metrics = ml_model.evaluate_model(model, X_test, y_test)
        metrics['n_samples'] = len(model_df)

        # 6. Importances
        importances = ml_model.get_feature_importance(model, X_train.columns.tolist())

        # 7. Generate Charts
        charts = {}
        charts['pressing_heatmap'] = visualizations.generate_pressing_heatmap(model_df, req.match_id, req.team)
        charts['defensive_heatmap'] = visualizations.generate_defensive_heatmap(events, req.match_id, req.team)
        charts['pass_network'] = visualizations.generate_pass_network(events, req.match_id, req.team)
        charts['shot_map'] = visualizations.generate_shot_map(events, req.match_id, req.team)

        # Top touch player
        touches = events[events['team'] == req.team]
        if not touches.empty and 'player' in touches.columns:
            top_player = touches['player'].value_counts().idxmax()
            charts['player_touchmap'] = visualizations.generate_player_touchmap(events, req.match_id, top_player)
        else:
            charts['player_touchmap'] = ""

        charts['feature_importance'] = visualizations.generate_feature_importance_chart(importances, req.match_id)

        # Update chart paths for frontend
        for k, v in charts.items():
            if v:
                charts[k] = f"/{v.replace('outputs/charts/', 'charts/')}"

        # 8. Insights
        insights = derive_insights(model_df, model, X)

        # 9. Save
        database.save_model_run(req.match_id, metrics)

        return {
            "match_id": req.match_id,
            "metrics": metrics,
            "feature_importance": importances,
            "charts": charts,
            "insights": insights
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    try:
        model, columns = ml_model.load_model()
        row_dict = req.dict()
        res = ml_model.predict_press_success(model, row_dict, columns)
        prob = res["probability"]
        interp = f"{int(prob * 100)}% chance of winning ball"
        return {
            "probability": prob,
            "prediction": res["prediction"],
            "interpretation": interp
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/players", response_model=List[str])
def get_players(match_id: int, team: str):
    try:
        events = data_loader.get_events(match_id)
        team_events = events[events['team'] == team]
        if 'player' in team_events.columns:
            players = sorted(team_events['player'].dropna().unique().tolist())
            return players
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/model-history")
def get_model_history(match_id: int):
    try:
        return database.get_model_runs(match_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
