import pytest
import pandas as pd
from analytics.event_processor import clean_events, filter_by_team, extract_passes, extract_shots
from analytics.feature_engineering import extract_features, get_feature_matrix

def test_clean_events():
    data = pd.DataFrame({
        'type': ['Pass', 'Pressure'],
        'team': ['Team A', 'Team B'],
        'location': [[10.0, 20.0], [30.0, 40.0]],
        'under_pressure': [None, True]
    })
    cleaned = clean_events(data)
    assert 'location_x' in cleaned.columns
    assert 'location_y' in cleaned.columns
    assert cleaned.iloc[0]['location_x'] == 10.0
    assert cleaned.iloc[1]['under_pressure'] == True
    assert cleaned.iloc[0]['under_pressure'] == False

def test_filter_by_team():
    data = pd.DataFrame({
        'type': ['Pass', 'Pressure'],
        'team': ['Team A', 'Team B'],
    })
    filtered = filter_by_team(data, 'Team A')
    assert len(filtered) == 1
    assert filtered.iloc[0]['team'] == 'Team A'

def test_feature_engineering_extraction():
    data = pd.DataFrame({
        'possession': [1, 1],
        'index': [1, 2],
        'type': ['Pressure', 'Ball Recovery'],
        'team': ['Team A', 'Team A'],
        'location': [[85.0, 40.0], [86.0, 40.0]],
        'minute': [10, 10],
        'period': [1, 1],
        'counterpress': [True, None],
        'under_pressure': [None, None],
        'play_pattern': ['Regular Play', 'Regular Play']
    })

    features = extract_features(data)
    assert len(features) == 1
    assert 'dist_from_goal' in features.columns
    assert features.iloc[0]['pitch_zone'] == 'attacking'
    assert features.iloc[0]['press_success'] == 1

def test_get_feature_matrix():
    data = pd.DataFrame({
        'location_x': [85.0],
        'location_y': [40.0],
        'dist_from_goal': [35.0],
        'pitch_zone': ['attacking'],
        'minute': [10],
        'match_period': [1],
        'counterpress': [True],
        'under_pressure': [False],
        'play_pattern': ['Regular Play'],
        'press_success': [1]
    })
    X, y = get_feature_matrix(data)
    assert 'pitch_zone_attacking' in X.columns
    assert y.iloc[0] == 1
