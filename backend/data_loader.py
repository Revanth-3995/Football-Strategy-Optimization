import pandas as pd
from statsbombpy import sb
import os
import pickle
from dotenv import load_dotenv

load_dotenv()

CACHE_DIR = os.environ.get("CACHE_DIR", "data/cache")

class DataLoadError(Exception):
    """Custom exception for data loading errors."""
    pass

# Memory caches
_competitions_cache = None
_matches_cache = {}

def get_competitions() -> pd.DataFrame:
    """
    Return all StatsBomb free competitions as a DataFrame.
    Columns needed: competition_id, competition_name, season_id, season_name.
    Cache result in memory (module-level dict) so second call is instant.
    """
    global _competitions_cache
    if _competitions_cache is not None:
        return _competitions_cache

    try:
        comps = sb.competitions()
        required_cols = ['competition_id', 'competition_name', 'season_id', 'season_name']
        _competitions_cache = comps[required_cols]
        return _competitions_cache
    except Exception as e:
        raise DataLoadError(f"Failed to load competitions: {e}")

def get_matches(competition_id: int, season_id: int) -> pd.DataFrame:
    """
    Return all matches for given competition+season.
    Columns needed: match_id, home_team, away_team, home_score, away_score, match_date.
    Cache per (competition_id, season_id) key.
    """
    cache_key = (competition_id, season_id)
    if cache_key in _matches_cache:
        return _matches_cache[cache_key]

    try:
        matches = sb.matches(competition_id=competition_id, season_id=season_id)
        required_cols = ['match_id', 'home_team', 'away_team', 'home_score', 'away_score', 'match_date']

        # handle missing match_date column if necessary
        if 'match_date' not in matches.columns:
            matches['match_date'] = None

        _matches_cache[cache_key] = matches[required_cols]
        return _matches_cache[cache_key]
    except Exception as e:
        raise DataLoadError(f"Failed to load matches for competition {competition_id}, season {season_id}: {e}")

def get_events(match_id: int) -> pd.DataFrame:
    """
    Load all events for a single match.
    If events are already cached on disk at data/cache/{match_id}.pkl,
    load from pickle (fast). Otherwise fetch via statsbombpy and save to pickle.
    Return raw events DataFrame — no filtering here.
    """
    cache_file = os.path.join(CACHE_DIR, f"{match_id}.pkl")

    if os.path.exists(cache_file):
        try:
            with open(cache_file, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            # If load fails, we should fall back to fetching
            print(f"Warning: Failed to load cache from {cache_file}: {e}")

    try:
        events = sb.events(match_id=match_id)

        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(cache_file, "wb") as f:
            pickle.dump(events, f)

        return events
    except Exception as e:
        raise DataLoadError(f"Failed to load events for match {match_id}: {e}")
