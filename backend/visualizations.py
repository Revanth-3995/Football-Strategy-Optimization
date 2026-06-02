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

def generate_expected_threat_map(events: pd.DataFrame, match_id: int, team: str) -> str:
    """
    Expected Threat (xT) visualization.
    We proxy xT using pass distance toward goal since we don't have a pre-trained xT matrix loaded.
    This creates a grid showing areas where passes generated the most forward progression.
    """
    os.makedirs(CHARTS_DIR, exist_ok=True)
    passes = events[(events['type'] == 'Pass') & (events['team'] == team) & (events.get('pass_outcome').isnull())].copy()

    if 'location' not in passes.columns or 'pass_end_location' not in passes.columns:
        return ""

    passes['x'] = passes['location'].apply(lambda x: x[0] if isinstance(x, list) and len(x) >= 2 else np.nan)
    passes['y'] = passes['location'].apply(lambda x: x[1] if isinstance(x, list) and len(x) >= 2 else np.nan)
    passes['end_x'] = passes['pass_end_location'].apply(lambda x: x[0] if isinstance(x, list) and len(x) >= 2 else np.nan)

    passes = passes.dropna(subset=['x', 'y', 'end_x'])

    # Proxy xT = (end_x - start_x) * weight. Only positive progression counts.
    passes['xt_proxy'] = np.maximum(0, passes['end_x'] - passes['x'])

    fig, ax = plt.subplots(figsize=(12, 8), dpi=150)
    pitch = Pitch(pitch_type='statsbomb', pitch_color='grass', line_color='white')
    pitch.draw(ax=ax)

    if not passes.empty:
        bins = (12, 8)
        stats = pitch.bin_statistic(passes['x'], passes['y'], values=passes['xt_proxy'], statistic='sum', bins=bins)
        pitch.heatmap(stats, ax=ax, cmap='magma', alpha=0.75, edgecolors='black')

    ax.set_title(f'Expected Threat (xT) Generation — {team}', color='white', fontsize=16)
    fig.patch.set_facecolor('#0a0e1a')

    filepath = os.path.join(CHARTS_DIR, f"{match_id}_expected_threat_map.png")
    fig.savefig(filepath, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    return filepath

def generate_possession_flow_map(events: pd.DataFrame, match_id: int, team: str) -> str:
    """
    Visualizes the general flow of possession using streamlines based on average pass trajectories in spatial bins.
    """
    os.makedirs(CHARTS_DIR, exist_ok=True)
    passes = events[(events['type'] == 'Pass') & (events['team'] == team) & (events.get('pass_outcome').isnull())].copy()

    if 'location' not in passes.columns or 'pass_end_location' not in passes.columns:
        return ""

    passes['x'] = passes['location'].apply(lambda x: x[0] if isinstance(x, list) and len(x) >= 2 else np.nan)
    passes['y'] = passes['location'].apply(lambda x: x[1] if isinstance(x, list) and len(x) >= 2 else np.nan)
    passes['end_x'] = passes['pass_end_location'].apply(lambda x: x[0] if isinstance(x, list) and len(x) >= 2 else np.nan)
    passes['end_y'] = passes['pass_end_location'].apply(lambda x: x[1] if isinstance(x, list) and len(x) >= 2 else np.nan)

    passes = passes.dropna(subset=['x', 'y', 'end_x', 'end_y'])

    fig, ax = plt.subplots(figsize=(12, 8), dpi=150)
    pitch = Pitch(pitch_type='statsbomb', pitch_color='grass', line_color='white')
    pitch.draw(ax=ax)

    if not passes.empty:
        # Create flow arrows using bin statistics
        stats = pitch.bin_statistic(passes['x'], passes['y'], statistic='count', bins=(8, 6))

        # Calculate average end locations per bin to determine flow direction
        stats_x = pitch.bin_statistic(passes['x'], passes['y'], values=passes['end_x'], statistic='mean', bins=(8, 6))
        stats_y = pitch.bin_statistic(passes['x'], passes['y'], values=passes['end_y'], statistic='mean', bins=(8, 6))

        pitch.flow(
            stats['cx'], stats['cy'],
            stats_x['statistic'] - stats['cx'],
            stats_y['statistic'] - stats['cy'],
            ax=ax, color='white', arrow_type='same', arrow_length=5, cmap='Blues'
        )

    ax.set_title(f'Possession Flow Map — {team}', color='white', fontsize=16)
    fig.patch.set_facecolor('#0a0e1a')

    filepath = os.path.join(CHARTS_DIR, f"{match_id}_possession_flow_map.png")
    fig.savefig(filepath, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    return filepath

def generate_team_shape_map(events: pd.DataFrame, match_id: int, team: str) -> str:
    """
    Visualizes the convex hull of the team's average positions to show their defensive/attacking shape.
    """
    os.makedirs(CHARTS_DIR, exist_ok=True)
    team_events = events[events['team'] == team].copy()

    if 'location' not in team_events.columns:
        return ""

    team_events['x'] = team_events['location'].apply(lambda x: x[0] if isinstance(x, list) and len(x) >= 2 else np.nan)
    team_events['y'] = team_events['location'].apply(lambda x: x[1] if isinstance(x, list) and len(x) >= 2 else np.nan)
    team_events = team_events.dropna(subset=['x', 'y', 'player'])

    # Exclude goalkeeper if possible
    if 'position' in team_events.columns:
        team_events = team_events[team_events['position'] != 'Goalkeeper']

    fig, ax = plt.subplots(figsize=(12, 8), dpi=150)
    pitch = Pitch(pitch_type='statsbomb', pitch_color='grass', line_color='white')
    pitch.draw(ax=ax)

    if not team_events.empty:
        avg_pos = team_events.groupby('player')[['x', 'y']].mean().reset_index()

        if len(avg_pos) >= 3:
            pitch.convexhull(avg_pos['x'], avg_pos['y'], color='blue', alpha=0.3, ax=ax)
            pitch.scatter(avg_pos['x'], avg_pos['y'], color='blue', edgecolors='white', s=100, ax=ax, zorder=2)

            for _, row in avg_pos.iterrows():
                name_parts = row['player'].split()
                short_name = name_parts[-1] if name_parts else row['player']
                pitch.annotate(short_name, xy=(row['x'], row['y'] - 2), c='white', va='center', ha='center', size=8, ax=ax, zorder=3)

    ax.set_title(f'Team Shape (Convex Hull) — {team}', color='white', fontsize=16)
    fig.patch.set_facecolor('#0a0e1a')

    filepath = os.path.join(CHARTS_DIR, f"{match_id}_team_shape_map.png")
    fig.savefig(filepath, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    return filepath

def generate_formation_overlay_map(events: pd.DataFrame, match_id: int, team: str) -> str:
    """
    Visualizes the player average positions overlaid with generic positional grid lines.
    """
    os.makedirs(CHARTS_DIR, exist_ok=True)
    team_events = events[events['team'] == team].copy()

    if 'location' not in team_events.columns:
        return ""

    team_events['x'] = team_events['location'].apply(lambda x: x[0] if isinstance(x, list) and len(x) >= 2 else np.nan)
    team_events['y'] = team_events['location'].apply(lambda x: x[1] if isinstance(x, list) and len(x) >= 2 else np.nan)
    team_events = team_events.dropna(subset=['x', 'y', 'player'])

    if 'position' in team_events.columns:
        team_events = team_events[team_events['position'] != 'Goalkeeper']

    fig, ax = plt.subplots(figsize=(12, 8), dpi=150)
    pitch = Pitch(pitch_type='statsbomb', pitch_color='grass', line_color='white')
    pitch.draw(ax=ax)

    # Draw positional grid lines (thirds vertically, channels horizontally)
    pitch.lines(40, 0, 40, 80, lw=1, color='white', alpha=0.3, linestyle='--', ax=ax)
    pitch.lines(80, 0, 80, 80, lw=1, color='white', alpha=0.3, linestyle='--', ax=ax)
    pitch.lines(0, 18, 120, 18, lw=1, color='white', alpha=0.3, linestyle='--', ax=ax)
    pitch.lines(0, 62, 120, 62, lw=1, color='white', alpha=0.3, linestyle='--', ax=ax)

    if not team_events.empty:
        avg_pos = team_events.groupby('player')[['x', 'y']].mean().reset_index()
        pitch.scatter(avg_pos['x'], avg_pos['y'], color='blue', edgecolors='white', s=150, alpha=0.8, ax=ax, zorder=2)

        for _, row in avg_pos.iterrows():
            name_parts = row['player'].split()
            short_name = name_parts[-1] if name_parts else row['player']
            pitch.annotate(short_name, xy=(row['x'], row['y'] - 3), c='white', va='center', ha='center', size=9, ax=ax, zorder=3)

    ax.set_title(f'Formation Grid Overlay — {team}', color='white', fontsize=16)
    fig.patch.set_facecolor('#0a0e1a')

    filepath = os.path.join(CHARTS_DIR, f"{match_id}_formation_overlay_map.png")
    fig.savefig(filepath, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    return filepath

def generate_defensive_block_map(events: pd.DataFrame, match_id: int, team: str) -> str:
    """
    Visualizes the average height of the defensive line during opposition possession.
    """
    os.makedirs(CHARTS_DIR, exist_ok=True)
    # Get opposition events where our team is out of possession
    opp_events = events[events['team'] != team].copy()

    fig, ax = plt.subplots(figsize=(12, 8), dpi=150)
    pitch = Pitch(pitch_type='statsbomb', pitch_color='grass', line_color='white')
    pitch.draw(ax=ax)

    if not opp_events.empty and 'location' in opp_events.columns:
        opp_events['x'] = opp_events['location'].apply(lambda x: x[0] if isinstance(x, list) and len(x) >= 2 else np.nan)
        opp_events = opp_events.dropna(subset=['x'])

        # Calculate the average x-coordinate of the opposition's actions as a proxy for how deep the block is
        avg_opp_x = opp_events['x'].mean()

        # Draw a vertical line representing the defensive engagement line
        pitch.lines(avg_opp_x, 0, avg_opp_x, 80, lw=3, color='red', linestyle='--', ax=ax)

        # Shade the defensive block area
        ax.fill_between([0, avg_opp_x], [0, 0], [80, 80], color='red', alpha=0.2)

        pitch.annotate(f"Avg Block Height: {avg_opp_x:.1f}m", xy=(avg_opp_x + 2, 75), c='white', size=12, weight='bold', ax=ax)

    ax.set_title(f'Defensive Block Height — {team}', color='white', fontsize=16)
    fig.patch.set_facecolor('#0a0e1a')

    filepath = os.path.join(CHARTS_DIR, f"{match_id}_defensive_block_map.png")
    fig.savefig(filepath, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    return filepath

def generate_progressive_pass_map(events: pd.DataFrame, match_id: int, team: str) -> str:
    os.makedirs(CHARTS_DIR, exist_ok=True)
    passes = events[(events['type'] == 'Pass') & (events['team'] == team) & (events.get('pass_outcome').isnull())].copy()

    if 'location' not in passes.columns or 'pass_end_location' not in passes.columns:
        return ""

    passes['x_start'] = passes['location'].apply(lambda x: x[0] if isinstance(x, list) and len(x) >= 2 else np.nan)
    passes['y_start'] = passes['location'].apply(lambda x: x[1] if isinstance(x, list) and len(x) >= 2 else np.nan)
    passes['x_end'] = passes['pass_end_location'].apply(lambda x: x[0] if isinstance(x, list) and len(x) >= 2 else np.nan)
    passes['y_end'] = passes['pass_end_location'].apply(lambda x: x[1] if isinstance(x, list) and len(x) >= 2 else np.nan)

    passes = passes.dropna(subset=['x_start', 'y_start', 'x_end', 'y_end'])

    # Simple progressive pass definition: moves ball at least 25% closer to center of opponent goal (120, 40)
    passes['dist_start'] = np.sqrt((120 - passes['x_start'])**2 + (40 - passes['y_start'])**2)
    passes['dist_end'] = np.sqrt((120 - passes['x_end'])**2 + (40 - passes['y_end'])**2)
    progressive = passes[passes['dist_end'] <= passes['dist_start'] * 0.75]

    fig, ax = plt.subplots(figsize=(12, 8), dpi=150)
    pitch = Pitch(pitch_type='statsbomb', pitch_color='grass', line_color='white')
    pitch.draw(ax=ax)

    if not progressive.empty:
        pitch.arrows(
            progressive['x_start'], progressive['y_start'],
            progressive['x_end'], progressive['y_end'],
            width=2, headwidth=4, headlength=4, color='cyan', ax=ax, label='Progressive Pass'
        )

    ax.legend(loc='lower left')
    ax.set_title(f'Progressive Passes — {team}', color='white', fontsize=16)
    fig.patch.set_facecolor('#0a0e1a')

    filepath = os.path.join(CHARTS_DIR, f"{match_id}_progressive_pass_map.png")
    fig.savefig(filepath, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    return filepath

def generate_tactical_occupancy_map(events: pd.DataFrame, match_id: int, team: str) -> str:
    os.makedirs(CHARTS_DIR, exist_ok=True)
    touches = events[(events['team'] == team) & (events['type'].isin(['Pass', 'Carry', 'Ball Receipt*']))].copy()

    if 'location' not in touches.columns:
        return ""

    touches['x'] = touches['location'].apply(lambda x: x[0] if isinstance(x, list) and len(x) >= 2 else np.nan)
    touches['y'] = touches['location'].apply(lambda x: x[1] if isinstance(x, list) and len(x) >= 2 else np.nan)
    touches = touches.dropna(subset=['x', 'y'])

    fig, ax = plt.subplots(figsize=(12, 8), dpi=150)
    pitch = Pitch(pitch_type='statsbomb', pitch_color='grass', line_color='white')
    pitch.draw(ax=ax)

    if not touches.empty:
        bins = (5, 5) # Divide pitch into 25 tactical zones
        stats = pitch.bin_statistic(touches['x'], touches['y'], statistic='count', bins=bins)
        pitch.heatmap(stats, ax=ax, cmap='viridis', alpha=0.6, edgecolors='black')

        # Display the raw count or percentage
        total_touches = len(touches)
        for i in range(len(stats['cx'])):
            for j in range(len(stats['cy'])):
                val = stats['statistic'][i][j]
                if val > 0:
                    pct = (val / total_touches) * 100
                    pitch.annotate(f"{pct:.1f}%", xy=(stats['cx'][i][j], stats['cy'][i][j]),
                                  c='white', va='center', ha='center', size=10, weight='bold', ax=ax)

    ax.set_title(f'Tactical Zone Occupancy — {team}', color='white', fontsize=16)
    fig.patch.set_facecolor('#0a0e1a')

    filepath = os.path.join(CHARTS_DIR, f"{match_id}_tactical_occupancy_map.png")
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

def generate_recovery_heatmap(events: pd.DataFrame, match_id: int, team: str) -> str:
    """
    KDE heatmap for ball recoveries.
    """
    os.makedirs(CHARTS_DIR, exist_ok=True)
    recoveries = events[
        (events['team'] == team) &
        (events['type'] == 'Ball Recovery')
    ].copy()

    recoveries['x'] = recoveries['location'].apply(lambda x: x[0] if isinstance(x, list) and len(x) >= 2 else np.nan)
    recoveries['y'] = recoveries['location'].apply(lambda x: x[1] if isinstance(x, list) and len(x) >= 2 else np.nan)
    recoveries = recoveries.dropna(subset=['x', 'y'])

    fig, ax = plt.subplots(figsize=(12, 8), dpi=150)
    pitch = Pitch(pitch_type='statsbomb', pitch_color='grass', line_color='white')
    pitch.draw(ax=ax)

    if not recoveries.empty:
        pitch.kdeplot(
            x=recoveries['x'], y=recoveries['y'], ax=ax,
            cmap='Greens', alpha=0.75, levels=100, fill=True
        )

    ax.set_title(f'Recovery Heatmap — {team}', color='white', fontsize=16)
    fig.patch.set_facecolor('#0a0e1a')

    filepath = os.path.join(CHARTS_DIR, f"{match_id}_recovery_heatmap.png")
    fig.savefig(filepath, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    return filepath

def generate_zone_control_map(events: pd.DataFrame, match_id: int, team: str) -> str:
    """
    A simplified zone control map using raw passes to establish dominance.
    """
    os.makedirs(CHARTS_DIR, exist_ok=True)
    passes = events[(events['type'] == 'Pass') & (events.get('pass_outcome').isnull())].copy()

    passes['x'] = passes['location'].apply(lambda x: x[0] if isinstance(x, list) and len(x) >= 2 else np.nan)
    passes['y'] = passes['location'].apply(lambda x: x[1] if isinstance(x, list) and len(x) >= 2 else np.nan)
    passes = passes.dropna(subset=['x', 'y', 'team'])

    fig, ax = plt.subplots(figsize=(12, 8), dpi=150)
    pitch = Pitch(pitch_type='statsbomb', pitch_color='grass', line_color='white')
    pitch.draw(ax=ax)

    if not passes.empty:
        bins = (6, 4)

        team_passes = passes[passes['team'] == team]
        other_passes = passes[passes['team'] != team]

        team_stats = pitch.bin_statistic(team_passes['x'], team_passes['y'], statistic='count', bins=bins)
        other_stats = pitch.bin_statistic(other_passes['x'], other_passes['y'], statistic='count', bins=bins)

        control_stats = team_stats.copy()

        with np.errstate(divide='ignore', invalid='ignore'):
            total_stats = team_stats['statistic'] + other_stats['statistic']
            ratio = np.divide(team_stats['statistic'], total_stats)
            ratio = np.nan_to_num(ratio, nan=0.5)

        control_stats['statistic'] = ratio

        cmap = plt.cm.RdBu
        pitch.heatmap(control_stats, ax=ax, cmap=cmap, alpha=0.7, vmin=0, vmax=1)

        for i in range(len(control_stats['cx'])):
            for j in range(len(control_stats['cy'])):
                val = control_stats['statistic'][i][j]
                if total_stats[i][j] > 0:
                    pitch.annotate(f"{val*100:.0f}%", xy=(control_stats['cx'][i][j], control_stats['cy'][i][j]),
                                  c='white', va='center', ha='center', size=12, weight='bold', ax=ax)

    ax.set_title(f'Zone Control Map — {team}', color='white', fontsize=16)
    fig.patch.set_facecolor('#0a0e1a')

    filepath = os.path.join(CHARTS_DIR, f"{match_id}_zone_control_map.png")
    fig.savefig(filepath, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    return filepath
