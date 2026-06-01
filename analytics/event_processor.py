import pandas as pd
import numpy as np

def clean_events(events: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and standardizes raw StatsBomb event data.
    - Standardizes column names if needed.
    - Extracts scalar coordinates from lists.
    - Handles missing critical fields gracefully.
    """
    df = events.copy()

    # Extract locations if they exist as lists
    if 'location' in df.columns:
        df['location_x'] = df['location'].apply(lambda x: x[0] if isinstance(x, list) and len(x) >= 2 else np.nan)
        df['location_y'] = df['location'].apply(lambda x: x[1] if isinstance(x, list) and len(x) >= 2 else np.nan)

    if 'pass_end_location' in df.columns:
        df['pass_end_location_x'] = df['pass_end_location'].apply(lambda x: x[0] if isinstance(x, list) and len(x) >= 2 else np.nan)
        df['pass_end_location_y'] = df['pass_end_location'].apply(lambda x: x[1] if isinstance(x, list) and len(x) >= 2 else np.nan)

    # Standardize boolean flags
    bool_flags = ['under_pressure', 'counterpress', 'shot_first_time']
    for flag in bool_flags:
        if flag in df.columns:
            df[flag] = df[flag].fillna(False).astype(bool)
        else:
            df[flag] = False

    # Standardize categorical fills
    if 'play_pattern' in df.columns:
        df['play_pattern'] = df['play_pattern'].fillna('Regular Play')

    return df

def filter_by_team(events: pd.DataFrame, team_name: str) -> pd.DataFrame:
    return events[events['team'] == team_name].copy()

def extract_passes(events: pd.DataFrame) -> pd.DataFrame:
    df = events[events['type'] == 'Pass'].copy()
    return df

def extract_shots(events: pd.DataFrame) -> pd.DataFrame:
    df = events[events['type'] == 'Shot'].copy()
    return df
