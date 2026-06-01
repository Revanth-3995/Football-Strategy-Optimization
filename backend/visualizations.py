import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from mplsoccer import Pitch

CHARTS_DIR = os.environ.get("CHARTS_DIR", "outputs/charts")

def generate_pressing_heatmap(pressures: pd.DataFrame, match_id: int, team: str) -> str:
    """
    KDE heatmap on a full pitch.
    Colormap: 'RdYlBu_r', alpha=0.75, levels=100.
    Title: f'Pressing Heatmap — {team}'
    File: outputs/charts/{match_id}_pressing_heatmap.png
    DPI: 150. figsize=(12, 8). pitch_color='grass', line_color='white'.
    Return file path string.
    """
    os.makedirs(CHARTS_DIR, exist_ok=True)
    fig, ax = plt.subplots(figsize=(12, 8), dpi=150)
    pitch = Pitch(pitch_type='statsbomb', pitch_color='grass', line_color='white')
    pitch.draw(ax=ax)

    if len(pressures) > 0:
        pitch.kdeplot(
            x=pressures['location_x'], y=pressures['location_y'], ax=ax,
            cmap='RdYlBu_r', alpha=0.75, levels=100, fill=True
        )

    ax.set_title(f'Pressing Heatmap — {team}', color='white', fontsize=16)
    fig.patch.set_facecolor('#0a0e1a')

    filepath = os.path.join(CHARTS_DIR, f"{match_id}_pressing_heatmap.png")
    fig.savefig(filepath, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    return filepath

def generate_defensive_heatmap(events: pd.DataFrame, match_id: int, team: str) -> str:
    """
    Filter events to type in ['Tackle', 'Interception', 'Clearance'] for given team.
    KDE heatmap. Colormap: 'Blues'. Same pitch settings as above.
    Title: f'Defensive Actions — {team}'
    File: outputs/charts/{match_id}_defensive_heatmap.png
    """
    os.makedirs(CHARTS_DIR, exist_ok=True)
    def_events = events[
        (events['team'] == team) &
        (events['type'].isin(['Tackle', 'Interception', 'Clearance']))
    ].copy()

    # Extract locations
    def_events['location_x'] = def_events['location'].apply(lambda x: x[0] if isinstance(x, list) and len(x) >= 2 else np.nan)
    def_events['location_y'] = def_events['location'].apply(lambda x: x[1] if isinstance(x, list) and len(x) >= 2 else np.nan)
    def_events = def_events.dropna(subset=['location_x', 'location_y'])

    fig, ax = plt.subplots(figsize=(12, 8), dpi=150)
    pitch = Pitch(pitch_type='statsbomb', pitch_color='grass', line_color='white')
    pitch.draw(ax=ax)

    if len(def_events) > 0:
        pitch.kdeplot(
            x=def_events['location_x'], y=def_events['location_y'], ax=ax,
            cmap='Blues', alpha=0.75, levels=100, fill=True
        )

    ax.set_title(f'Defensive Actions — {team}', color='white', fontsize=16)
    fig.patch.set_facecolor('#0a0e1a')

    filepath = os.path.join(CHARTS_DIR, f"{match_id}_defensive_heatmap.png")
    fig.savefig(filepath, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    return filepath

def generate_pass_network(events: pd.DataFrame, match_id: int, team: str) -> str:
    """
    Filter passes for given team.
    Compute average location per player.
    Draw nodes (scatter) sized by total_passes at average position.
    Draw edges for pairs with count > 3; line alpha proportional to count.
    Node color: gold (#FFD700), edge color: white.
    Title: f'Pass Network — {team}'
    File: outputs/charts/{match_id}_pass_network.png
    """
    os.makedirs(CHARTS_DIR, exist_ok=True)
    passes = events[(events['type'] == 'Pass') & (events['team'] == team) & (events.get('pass_outcome').isnull())].copy()

    # Extract locations
    passes['x'] = passes['location'].apply(lambda x: x[0] if isinstance(x, list) and len(x) >= 2 else np.nan)
    passes['y'] = passes['location'].apply(lambda x: x[1] if isinstance(x, list) and len(x) >= 2 else np.nan)
    passes = passes.dropna(subset=['x', 'y', 'player', 'pass_recipient'])

    # Average positions
    avg_loc = passes.groupby('player')[['x', 'y']].mean()
    pass_counts = passes.groupby('player').size().rename('count')
    avg_loc = avg_loc.join(pass_counts)

    # Pass pairs
    pair_counts = passes.groupby(['player', 'pass_recipient']).size().reset_index(name='count')
    pair_counts = pair_counts[pair_counts['count'] > 3]

    fig, ax = plt.subplots(figsize=(12, 8), dpi=150)
    pitch = Pitch(pitch_type='statsbomb', pitch_color='grass', line_color='white')
    pitch.draw(ax=ax)

    max_count = pair_counts['count'].max() if not pair_counts.empty else 1

    for _, row in pair_counts.iterrows():
        p1, p2 = row['player'], row['pass_recipient']
        if p1 in avg_loc.index and p2 in avg_loc.index:
            alpha = max(0.1, min(1.0, row['count'] / max_count))
            pitch.lines(
                avg_loc.loc[p1, 'x'], avg_loc.loc[p1, 'y'],
                avg_loc.loc[p2, 'x'], avg_loc.loc[p2, 'y'],
                lw=2, color='white', alpha=alpha, zorder=1, ax=ax
            )

    if not avg_loc.empty:
        pitch.scatter(
            avg_loc['x'], avg_loc['y'],
            s=avg_loc['count']*20, color='#FFD700', edgecolors='black', linewidth=1, alpha=0.9, zorder=2, ax=ax
        )
        for player, row in avg_loc.iterrows():
            pitch.annotate(player.split()[-1], xy=(row['x'], row['y']), c='black', va='center', ha='center', size=8, zorder=3, ax=ax)

    ax.set_title(f'Pass Network — {team}', color='white', fontsize=16)
    fig.patch.set_facecolor('#0a0e1a')

    filepath = os.path.join(CHARTS_DIR, f"{match_id}_pass_network.png")
    fig.savefig(filepath, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    return filepath

def generate_shot_map(events: pd.DataFrame, match_id: int, team: str) -> str:
    """
    Filter shots for given team.
    Use half=True pitch (attacking half only).
    Blue circles = no goal, Red circles = goal.
    Circle size = shot_statsbomb_xg * 1000 (minimum size 20 so zero-xG shots still visible).
    Add legend and title: f'Shot Map | xG: {total_xg:.2f} — {team}'
    File: outputs/charts/{match_id}_shot_map.png
    """
    os.makedirs(CHARTS_DIR, exist_ok=True)
    shots = events[(events['type'] == 'Shot') & (events['team'] == team)].copy()

    shots['x'] = shots['location'].apply(lambda x: x[0] if isinstance(x, list) and len(x) >= 2 else np.nan)
    shots['y'] = shots['location'].apply(lambda x: x[1] if isinstance(x, list) and len(x) >= 2 else np.nan)
    shots = shots.dropna(subset=['x', 'y'])

    if 'shot_statsbomb_xg' not in shots.columns:
        shots['shot_statsbomb_xg'] = 0.05
    else:
        shots['shot_statsbomb_xg'] = shots['shot_statsbomb_xg'].fillna(0.05)

    total_xg = shots['shot_statsbomb_xg'].sum()

    fig, ax = plt.subplots(figsize=(12, 8), dpi=150)
    pitch = Pitch(pitch_type='statsbomb', pitch_color='grass', line_color='white', half=True)
    pitch.draw(ax=ax)

    goals = shots[shots['shot_outcome'] == 'Goal']
    non_goals = shots[shots['shot_outcome'] != 'Goal']

    if not non_goals.empty:
        pitch.scatter(
            non_goals['x'], non_goals['y'],
            s=np.maximum(20, non_goals['shot_statsbomb_xg'] * 1000),
            color='blue', edgecolors='black', alpha=0.7, ax=ax, label='No Goal'
        )
    if not goals.empty:
        pitch.scatter(
            goals['x'], goals['y'],
            s=np.maximum(20, goals['shot_statsbomb_xg'] * 1000),
            color='red', edgecolors='black', alpha=0.9, ax=ax, label='Goal'
        )

    ax.legend(loc='lower left')
    ax.set_title(f'Shot Map | xG: {total_xg:.2f} — {team}', color='white', fontsize=16)
    fig.patch.set_facecolor('#0a0e1a')

    filepath = os.path.join(CHARTS_DIR, f"{match_id}_shot_map.png")
    fig.savefig(filepath, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    return filepath

def generate_player_touchmap(events: pd.DataFrame, match_id: int, player_name: str) -> str:
    """
    All events for given player_name with non-null location.
    Yellow scatter dots + purple KDE overlay.
    Title: f'Touch Map — {player_name}'
    File: outputs/charts/{match_id}_touchmap_{player_name.replace(' ', '_')}.png
    """
    os.makedirs(CHARTS_DIR, exist_ok=True)
    touches = events[(events['player'] == player_name)].copy()

    touches['x'] = touches['location'].apply(lambda x: x[0] if isinstance(x, list) and len(x) >= 2 else np.nan)
    touches['y'] = touches['location'].apply(lambda x: x[1] if isinstance(x, list) and len(x) >= 2 else np.nan)
    touches = touches.dropna(subset=['x', 'y'])

    fig, ax = plt.subplots(figsize=(12, 8), dpi=150)
    pitch = Pitch(pitch_type='statsbomb', pitch_color='grass', line_color='white')
    pitch.draw(ax=ax)

    if len(touches) > 0:
        pitch.kdeplot(
            x=touches['x'], y=touches['y'], ax=ax,
            cmap='Purples', alpha=0.6, levels=100, fill=True
        )
        pitch.scatter(
            touches['x'], touches['y'], ax=ax,
            color='yellow', edgecolors='black', s=30, alpha=0.8
        )

    ax.set_title(f'Touch Map — {player_name}', color='white', fontsize=16)
    fig.patch.set_facecolor('#0a0e1a')

    clean_name = player_name.replace(' ', '_')
    filepath = os.path.join(CHARTS_DIR, f"{match_id}_touchmap_{clean_name}.png")
    fig.savefig(filepath, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    return filepath

def generate_feature_importance_chart(importances: list[dict], match_id: int) -> str:
    """
    Horizontal bar chart. steelblue bars. Sorted ascending (so most important is at top).
    xlabel: 'Importance Score', title: 'Feature Importance — Press Success Drivers'
    figsize=(10, 6), tight_layout.
    File: outputs/charts/{match_id}_feature_importance.png
    """
    os.makedirs(CHARTS_DIR, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 6), dpi=150)

    df = pd.DataFrame(importances)
    df = df.sort_values(by='importance', ascending=True)

    ax.barh(df['feature'], df['importance'], color='steelblue')
    ax.set_xlabel('Importance Score')
    ax.set_title('Feature Importance — Press Success Drivers')

    plt.tight_layout()

    filepath = os.path.join(CHARTS_DIR, f"{match_id}_feature_importance.png")
    fig.savefig(filepath, bbox_inches='tight')
    plt.close(fig)
    return filepath
