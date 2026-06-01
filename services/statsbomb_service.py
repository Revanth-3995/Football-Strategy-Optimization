import pandas as pd
from statsbombpy import sb
import os
import pickle
import json
from services.cache import redis_client

CACHE_DIR = os.environ.get("CACHE_DIR", "data/cache")

class DataLoadError(Exception):
    pass

def get_competitions() -> pd.DataFrame:
    cache_key = "statsbomb:competitions"
    cached = redis_client.get(cache_key)
    if cached:
        return pd.DataFrame(json.loads(cached))

    try:
        comps = sb.competitions()
        required_cols = ['competition_id', 'competition_name', 'season_id', 'season_name', 'country_name']
        # Add country_name missing from old implementation to fulfill the schema
        available_cols = [c for c in required_cols if c in comps.columns]
        comps = comps[available_cols]
        redis_client.set(cache_key, json.dumps(comps.to_dict(orient="records")), ex=86400) # cache for 1 day
        return comps
    except Exception as e:
        raise DataLoadError(f"Failed to load competitions: {e}")

def get_matches(competition_id: int, season_id: int) -> pd.DataFrame:
    cache_key = f"statsbomb:matches:{competition_id}:{season_id}"
    cached = redis_client.get(cache_key)
    if cached:
        return pd.DataFrame(json.loads(cached))

    try:
        matches = sb.matches(competition_id=competition_id, season_id=season_id)
        required_cols = ['match_id', 'home_team', 'away_team', 'home_score', 'away_score', 'match_date']

        if 'match_date' not in matches.columns:
            matches['match_date'] = None

        available_cols = [c for c in required_cols if c in matches.columns]
        res = matches[available_cols]

        redis_client.set(cache_key, json.dumps(res.to_dict(orient="records")), ex=86400)
        return res
    except Exception as e:
        raise DataLoadError(f"Failed to load matches for competition {competition_id}, season {season_id}: {e}")

def get_events(match_id: int) -> pd.DataFrame:
    """
    Events are too large for Redis usually without serialization/deserialization overhead.
    Following strict rules, use pickle cache for StatsBomb events.
    """
    cache_file = os.path.join(CACHE_DIR, f"{match_id}.pkl")

    if os.path.exists(cache_file):
        try:
            with open(cache_file, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Warning: Failed to load cache from {cache_file}: {e}")

    try:
        events = sb.events(match_id=match_id)

        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(cache_file, "wb") as f:
            pickle.dump(events, f)

        return events
    except Exception as e:
        raise DataLoadError(f"Failed to load events for match {match_id}: {e}")
