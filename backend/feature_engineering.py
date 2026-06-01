import pandas as pd
import numpy as np

def extract_features(events: pd.DataFrame) -> pd.DataFrame:
    """
    Input: raw events DataFrame for one match.
    Output: DataFrame with one row per pressing event, containing ALL columns below.

    Columns to produce:
    - location_x         : float, x coordinate of press (0–120)
    - location_y         : float, y coordinate of press (0–80)
    - dist_from_goal     : float, Euclidean distance from (120, 40)
    - pitch_zone         : str, one of ['defensive', 'mid', 'attacking']
                           defensive = x < 40, mid = 40–80, attacking = x > 80
    - minute             : int, match minute
    - match_period       : int, 1 or 2
    - counterpress       : bool, True if counterpress flag is set
    - under_pressure     : bool, True if under_pressure flag is set
    - play_pattern       : str, e.g. 'Regular Play', 'From Goal Kick', etc.
    - press_success      : int, TARGET VARIABLE
                           1 if the NEXT event in same possession is 'Ball Recovery'
                           0 otherwise
                           Logic: sort by (possession, index), shift type by -1,
                           check if shifted type == 'Ball Recovery'

    Handle nulls:
    - counterpress and under_pressure: fillna(False)
    - location: drop rows where location is null
    - play_pattern: fillna('Regular Play')
    - Drop all rows still containing any NaN after above fills.

    Do not modify the input DataFrame — work on a copy.
    """
    df = events.copy()

    # Target variable
    df.sort_values(by=['possession', 'index'], inplace=True)
    df['next_event_type'] = df.groupby('possession')['type'].shift(-1)
    df['press_success'] = (df['next_event_type'] == 'Ball Recovery').astype(int)

    # Filter to pressing events
    df = df[df['type'] == 'Pressure'].copy()

    # Handle nulls
    if 'counterpress' in df.columns:
        df['counterpress'] = df['counterpress'].fillna(False).astype(bool)
    else:
        df['counterpress'] = False

    if 'under_pressure' in df.columns:
        df['under_pressure'] = df['under_pressure'].fillna(False).astype(bool)
    else:
        df['under_pressure'] = False

    if 'play_pattern' in df.columns:
        df['play_pattern'] = df['play_pattern'].fillna('Regular Play')
    else:
        df['play_pattern'] = 'Regular Play'

    df = df.dropna(subset=['location'])

    # Extract location features
    df['location_x'] = df['location'].apply(lambda x: x[0] if isinstance(x, list) and len(x) >= 2 else np.nan)
    df['location_y'] = df['location'].apply(lambda x: x[1] if isinstance(x, list) and len(x) >= 2 else np.nan)

    df = df.dropna(subset=['location_x', 'location_y'])
    df['location_x'] = df['location_x'].astype(float)
    df['location_y'] = df['location_y'].astype(float)

    # Calculate distance
    df['dist_from_goal'] = np.sqrt((df['location_x'] - 120)**2 + (df['location_y'] - 40)**2)

    # Pitch zone
    def get_pitch_zone(x):
        if x < 40:
            return 'defensive'
        elif x <= 80:
            return 'mid'
        else:
            return 'attacking'

    df['pitch_zone'] = df['location_x'].apply(get_pitch_zone)

    # Select needed columns
    cols = [
        'location_x', 'location_y', 'dist_from_goal', 'pitch_zone',
        'minute', 'period', 'counterpress', 'under_pressure', 'play_pattern',
        'press_success'
    ]

    # Rename period to match_period
    df = df.rename(columns={'period': 'match_period'})
    cols[cols.index('period')] = 'match_period'

    df = df[cols]

    # Drop any remaining NaNs
    df = df.dropna()

    return df

def get_feature_matrix(df: pd.DataFrame):
    """
    Input: DataFrame from extract_features().
    Output: (X, y) where:
    - X is pd.get_dummies applied to all feature columns (exclude press_success)
    - y is df['press_success'] as a Series
    Feature columns to use (in this order):
    ['location_x', 'location_y', 'dist_from_goal', 'pitch_zone',
     'minute', 'match_period', 'counterpress', 'under_pressure', 'play_pattern']
    """
    feature_cols = [
        'location_x', 'location_y', 'dist_from_goal', 'pitch_zone',
        'minute', 'match_period', 'counterpress', 'under_pressure', 'play_pattern'
    ]

    X = pd.get_dummies(df[feature_cols])
    y = df['press_success']

    return X, y
