import pytest
import pandas as pd
import numpy as np
import backend.visualizations as viz

def test_generate_charts():
    # Create mock event data
    events = pd.DataFrame({
        'type': ['Pass', 'Pass', 'Shot', 'Ball Recovery', 'Carry'],
        'team': ['TeamA', 'TeamA', 'TeamA', 'TeamA', 'TeamA'],
        'player': ['P1', 'P2', 'P1', 'P2', 'P1'],
        'location': [[20, 40], [80, 40], [100, 40], [50, 50], [60, 60]],
        'pass_end_location': [[40, 40], [100, 40], np.nan, np.nan, np.nan],
        'pass_outcome': [np.nan, np.nan, np.nan, np.nan, np.nan],
        'shot_statsbomb_xg': [np.nan, np.nan, 0.5, np.nan, np.nan],
        'shot_outcome': [np.nan, np.nan, 'Goal', np.nan, np.nan],
        'position': ['Midfielder', 'Forward', 'Midfielder', 'Forward', 'Midfielder']
    })

    match_id = 999
    team = 'TeamA'

    res = viz.generate_recovery_heatmap(events, match_id, team)
    assert 'recovery_heatmap' in res

    res = viz.generate_zone_control_map(events, match_id, team)
    assert 'zone_control_map' in res

    res = viz.generate_progressive_pass_map(events, match_id, team)
    assert 'progressive_pass_map' in res

    res = viz.generate_tactical_occupancy_map(events, match_id, team)
    assert 'tactical_occupancy_map' in res

    res = viz.generate_expected_threat_map(events, match_id, team)
    assert 'expected_threat_map' in res

    res = viz.generate_possession_flow_map(events, match_id, team)
    assert 'possession_flow_map' in res

    res = viz.generate_team_shape_map(events, match_id, team)
    assert 'team_shape_map' in res

    res = viz.generate_defensive_block_map(events, match_id, team)
    assert 'defensive_block_map' in res
