import pandas as pd
import numpy as np
from backend.feature_engineering import extract_features, get_feature_matrix

def test_extract_features():
    # Mock some basic events to satisfy the conditions
    events = pd.DataFrame({
        'possession': [1, 1],
        'index': [1, 2],
        'type': ['Pressure', 'Ball Recovery'],
        'location': [[60.0, 40.0], [61.0, 41.0]],
        'counterpress': [True, False],
        'under_pressure': [False, False],
        'play_pattern': ['Regular Play', 'Regular Play'],
        'minute': [10, 10],
        'period': [1, 1],
    })

    df = extract_features(events)

    # Check returned columns
    expected_cols = [
        'location_x', 'location_y', 'dist_from_goal', 'pitch_zone',
        'minute', 'match_period', 'counterpress', 'under_pressure', 'play_pattern',
        'press_success'
    ]
    for col in expected_cols:
        assert col in df.columns

    # Check location_x range (60.0)
    assert df['location_x'].iloc[0] == 60.0

    # Check binary target
    assert df['press_success'].iloc[0] in [0, 1]

    # Check no nulls
    assert df.isnull().sum().sum() == 0
