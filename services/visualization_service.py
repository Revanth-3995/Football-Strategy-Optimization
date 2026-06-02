import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
import seaborn as sns
from mplsoccer import Pitch

CHARTS_DIR = os.environ.get("CHARTS_DIR", "outputs/charts")
os.makedirs(CHARTS_DIR, exist_ok=True)

def _save_and_close(fig, filepath):
    fig.patch.set_facecolor('#0a0e1a')
    fig.savefig(filepath, bbox_inches='tight', facecolor='#0a0e1a', dpi=150)
    plt.close(fig)

def _extract_coords(df, col='location'):
    if col not in df.columns:
        return pd.DataFrame(columns=['x', 'y'])
    x = df[col].apply(lambda loc: loc[0] if isinstance(loc, list) and len(loc) >= 2 else np.nan)
    y = df[col].apply(lambda loc: loc[1] if isinstance(loc, list) and len(loc) >= 2 else np.nan)
    return pd.DataFrame({'x': x, 'y': y}).dropna()

def _format_player_name(fullname: str) -> str:
    if not fullname or not isinstance(fullname, str):
        return ""
    # Standard cleanups for known superstar naming schemas
    if "Messi" in fullname:
        return "Messi"
    if "Cristiano" in fullname or "Ronaldo" in fullname:
        if "dos Santos" in fullname:
            return "C. Ronaldo"
        return "Ronaldo"
    if "Neymar" in fullname:
        return "Neymar"
    if "De Bruyne" in fullname:
        return "De Bruyne"
    if "van Dijk" in fullname:
        return "van Dijk"
    if "Alexander-Arnold" in fullname:
        return "Alexander-Arnold"
    
    parts = fullname.split()
    if len(parts) == 0:
        return ""
    # If last part is junior/senior/suffix, use the second to last part
    if parts[-1].lower() in ["junior", "júnior", "senior", "ii", "iii", "iv", "filho", "neto"]:
        if len(parts) >= 2:
            return parts[-2]
    return parts[-1]


# 1. Pressing Heatmap
def generate_pressing_heatmap(events: pd.DataFrame, match_id: int, team: str) -> str:
    fig, ax = plt.subplots(figsize=(12, 8))
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#0a0e1a', line_color='#c5c5c5')
    pitch.draw(ax=ax)
    
    pressures = events[(events['type'] == 'Pressure') & (events['team'] == team)].copy()
    coords = _extract_coords(pressures)
    
    if len(coords) > 2:
        pitch.kdeplot(coords['x'], coords['y'], ax=ax, cmap='Oranges', fill=True, alpha=0.6, levels=100)
    ax.set_title(f'Pressing Heatmap — {team}', color='white', fontsize=16, pad=10)
    
    filepath = os.path.join(CHARTS_DIR, f"{match_id}_pressing_heatmap.png")
    _save_and_close(fig, filepath)
    return filepath

# 2. Defensive Heatmap
def generate_defensive_heatmap(events: pd.DataFrame, match_id: int, team: str) -> str:
    fig, ax = plt.subplots(figsize=(12, 8))
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#0a0e1a', line_color='#c5c5c5')
    pitch.draw(ax=ax)
    
    def_events = events[
        (events['team'] == team) & 
        (events['type'].isin(['Tackle', 'Interception', 'Clearance', 'Block', 'Shield']))
    ].copy()
    coords = _extract_coords(def_events)
    
    if len(coords) > 2:
        pitch.kdeplot(coords['x'], coords['y'], ax=ax, cmap='Blues', fill=True, alpha=0.6, levels=100)
    ax.set_title(f'Defensive Action Heatmap — {team}', color='white', fontsize=16, pad=10)
    
    filepath = os.path.join(CHARTS_DIR, f"{match_id}_defensive_heatmap.png")
    _save_and_close(fig, filepath)
    return filepath

# 3. Recovery Heatmap
def generate_recovery_heatmap(events: pd.DataFrame, match_id: int, team: str) -> str:
    fig, ax = plt.subplots(figsize=(12, 8))
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#0a0e1a', line_color='#c5c5c5')
    pitch.draw(ax=ax)
    
    recoveries = events[(events['type'] == 'Ball Recovery') & (events['team'] == team)].copy()
    coords = _extract_coords(recoveries)
    
    if len(coords) > 2:
        pitch.kdeplot(coords['x'], coords['y'], ax=ax, cmap='Greens', fill=True, alpha=0.6, levels=100)
    ax.set_title(f'Ball Recovery Heatmap — {team}', color='white', fontsize=16, pad=10)
    
    filepath = os.path.join(CHARTS_DIR, f"{match_id}_recovery_heatmap.png")
    _save_and_close(fig, filepath)
    return filepath

# 4. Shot Map
def generate_shot_map(events: pd.DataFrame, match_id: int, team: str) -> str:
    fig, ax = plt.subplots(figsize=(12, 8))
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#0a0e1a', line_color='#c5c5c5', half=True)
    pitch.draw(ax=ax)
    
    shots = events[(events['type'] == 'Shot') & (events['team'] == team)].copy()
    coords = _extract_coords(shots)
    if not shots.empty:
        shots['x'] = coords['x']
        shots['y'] = coords['y']
        shots = shots.dropna(subset=['x', 'y'])
        
        shots['shot_statsbomb_xg'] = shots.get('shot_statsbomb_xg', pd.Series(0.05, index=shots.index)).fillna(0.05)
        
        goals = shots[shots['shot_outcome'] == 'Goal']
        no_goals = shots[shots['shot_outcome'] != 'Goal']
        
        if not no_goals.empty:
            pitch.scatter(no_goals['x'], no_goals['y'], s=no_goals['shot_statsbomb_xg']*800, 
                          color='cyan', edgecolors='black', alpha=0.7, ax=ax, label='No Goal')
        if not goals.empty:
            pitch.scatter(goals['x'], goals['y'], s=goals['shot_statsbomb_xg']*800 + 100, 
                          color='magenta', edgecolors='white', marker='*', alpha=0.9, ax=ax, label='Goal')
        ax.legend(loc='lower right', facecolor='#0a0e1a', edgecolor='white', labelcolor='white')
        total_xg = shots['shot_statsbomb_xg'].sum()
        ax.set_title(f'Shot Map — {team} (Total xG: {total_xg:.2f})', color='white', fontsize=16, pad=10)
    else:
        ax.set_title(f'Shot Map — {team} (No Shots Recorded)', color='white', fontsize=16, pad=10)
        
    filepath = os.path.join(CHARTS_DIR, f"{match_id}_shot_map.png")
    _save_and_close(fig, filepath)
    return filepath

# 5. Pass Network
def generate_pass_network(events: pd.DataFrame, match_id: int, team: str) -> str:
    fig, ax = plt.subplots(figsize=(12, 8))
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#0a0e1a', line_color='#c5c5c5')
    pitch.draw(ax=ax)
    
    passes = events[(events['type'] == 'Pass') & (events['team'] == team) & (events.get('pass_outcome').isnull())].copy()
    coords = _extract_coords(passes)
    
    if len(passes) > 5 and not coords.empty:
        passes['x'] = coords['x']
        passes['y'] = coords['y']
        passes = passes.dropna(subset=['x', 'y', 'player', 'pass_recipient'])
        
        avg_loc = passes.groupby('player')[['x', 'y']].mean()
        pass_counts = passes.groupby('player').size().rename('count')
        avg_loc = avg_loc.join(pass_counts)
        
        pair_counts = passes.groupby(['player', 'pass_recipient']).size().reset_index(name='count')
        pair_counts = pair_counts[pair_counts['count'] > 2]
        
        max_count = pair_counts['count'].max() if not pair_counts.empty else 1
        
        for _, row in pair_counts.iterrows():
            p1, p2 = row['player'], row['pass_recipient']
            if p1 in avg_loc.index and p2 in avg_loc.index:
                alpha = max(0.1, min(0.9, row['count'] / max_count))
                pitch.lines(avg_loc.loc[p1, 'x'], avg_loc.loc[p1, 'y'],
                            avg_loc.loc[p2, 'x'], avg_loc.loc[p2, 'y'],
                            lw=2, color='white', alpha=alpha, zorder=1, ax=ax)
                            
        pitch.scatter(avg_loc['x'], avg_loc['y'], s=avg_loc['count']*15, color='#FFD700', 
                      edgecolors='black', linewidth=1.5, alpha=0.9, zorder=2, ax=ax)
                      
        for player, row in avg_loc.iterrows():
            pitch.annotate(_format_player_name(player), xy=(row['x'], row['y']), c='black', va='center', 
                           ha='center', size=8, weight='bold', zorder=3, ax=ax)
        ax.set_title(f'Pass Network — {team}', color='white', fontsize=16, pad=10)
    else:
        ax.set_title(f'Pass Network — {team} (Insufficient Data)', color='white', fontsize=16, pad=10)
        
    filepath = os.path.join(CHARTS_DIR, f"{match_id}_pass_network.png")
    _save_and_close(fig, filepath)
    return filepath

# 6. Player Touch Map
def generate_player_touchmap(events: pd.DataFrame, match_id: int, player_name: str) -> str:
    fig, ax = plt.subplots(figsize=(12, 8))
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#0a0e1a', line_color='#c5c5c5')
    pitch.draw(ax=ax)
    
    touches = events[events['player'] == player_name].copy()
    coords = _extract_coords(touches)
    
    if len(coords) > 0:
        if len(coords) > 2:
            pitch.kdeplot(coords['x'], coords['y'], ax=ax, cmap='Purples', fill=True, alpha=0.5, levels=100)
        pitch.scatter(coords['x'], coords['y'], ax=ax, color='#FFD700', edgecolors='black', s=40, alpha=0.8)
        ax.set_title(f'Touch Map — {player_name}', color='white', fontsize=16, pad=10)
    else:
        ax.set_title(f'Touch Map — {player_name} (No Touches)', color='white', fontsize=16, pad=10)
        
    clean_name = player_name.replace(' ', '_')
    filepath = os.path.join(CHARTS_DIR, f"{match_id}_touchmap_{clean_name}.png")
    _save_and_close(fig, filepath)
    return filepath

# 7. Zone Control Map
def generate_zone_control_map(events: pd.DataFrame, match_id: int, home_team: str, away_team: str) -> str:
    fig, ax = plt.subplots(figsize=(12, 8))
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#0a0e1a', line_color='#c5c5c5')
    pitch.draw(ax=ax)
    
    # Divide pitch into a 6x5 grid (30 zones)
    x_bins = np.linspace(0, 120, 7)
    y_bins = np.linspace(0, 80, 6)
    
    valid_events = events[events['team'].isin([home_team, away_team]) & events['location'].notna()].copy()
    coords = _extract_coords(valid_events)
    
    if not coords.empty:
        valid_events['x'] = coords['x']
        valid_events['y'] = coords['y']
        
        # Calculate event counts per team per grid cell
        for i in range(6):
            for j in range(5):
                zone_events = valid_events[
                    (valid_events['x'] >= x_bins[i]) & (valid_events['x'] < x_bins[i+1]) &
                    (valid_events['y'] >= y_bins[j]) & (valid_events['y'] < y_bins[j+1])
                ]
                total = len(zone_events)
                if total > 0:
                    home_pct = len(zone_events[zone_events['team'] == home_team]) / total
                    # Draw zone rectangle color coded by control
                    color = 'red' if home_pct > 0.55 else ('blue' if home_pct < 0.45 else 'grey')
                    alpha = abs(home_pct - 0.5) * 1.5
                    alpha = max(0.1, min(0.6, alpha))
                    ax.fill_between([x_bins[i], x_bins[i+1]], y_bins[j], y_bins[j+1], color=color, alpha=alpha, zorder=0)
                    ax.text((x_bins[i]+x_bins[i+1])/2, (y_bins[j]+y_bins[j+1])/2, f"{home_pct:.0%}", 
                            color='white', ha='center', va='center', fontsize=8, weight='bold', alpha=0.8)
                            
        ax.set_title(f'Zone Control Map — {home_team} (Red) vs {away_team} (Blue)', color='white', fontsize=16, pad=10)
    else:
        ax.set_title('Zone Control Map — Insufficient Events', color='white', fontsize=16, pad=10)
        
    filepath = os.path.join(CHARTS_DIR, f"{match_id}_zone_control.png")
    _save_and_close(fig, filepath)
    return filepath

# 8. Ball Recovery Map
def generate_ball_recovery_map(events: pd.DataFrame, match_id: int, team: str) -> str:
    fig, ax = plt.subplots(figsize=(12, 8))
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#0a0e1a', line_color='#c5c5c5')
    pitch.draw(ax=ax)
    
    recoveries = events[(events['type'] == 'Ball Recovery') & (events['team'] == team)].copy()
    coords = _extract_coords(recoveries)
    
    if len(coords) > 0:
        pitch.scatter(coords['x'], coords['y'], color='#00FFCC', edgecolors='black', s=60, alpha=0.9, zorder=2, ax=ax)
        ax.set_title(f'Ball Recovery Locations — {team}', color='white', fontsize=16, pad=10)
    else:
        ax.set_title(f'Ball Recovery Locations — {team} (No recoveries)', color='white', fontsize=16, pad=10)
        
    filepath = os.path.join(CHARTS_DIR, f"{match_id}_ball_recovery_map.png")
    _save_and_close(fig, filepath)
    return filepath

# 9. Possession Flow Map
def generate_possession_flow_map(events: pd.DataFrame, match_id: int, home_team: str, away_team: str) -> str:
    fig, ax = plt.subplots(figsize=(12, 5))
    
    # Calculate rolling momentum throughout the match
    events_sorted = events.sort_values(by=['minute', 'second']).copy()
    events_sorted['x'] = _extract_coords(events_sorted)['x']
    events_sorted = events_sorted.dropna(subset=['x'])
    
    events_sorted['val'] = events_sorted.apply(
        lambda r: r['x'] if r['team'] == home_team else -r['x'], axis=1
    )
    
    if not events_sorted.empty:
        rolling = events_sorted.groupby('minute')['val'].mean().rolling(window=5, min_periods=1).mean()
        ax.plot(rolling.index, rolling.values, color='#00FFCC', lw=2.5, label='Match Momentum')
        ax.axhline(0, color='white', linestyle='--', alpha=0.5)
        ax.fill_between(rolling.index, rolling.values, 0, where=(rolling.values >= 0), color='red', alpha=0.3, label=f'{home_team} Dominance')
        ax.fill_between(rolling.index, rolling.values, 0, where=(rolling.values < 0), color='blue', alpha=0.3, label=f'{away_team} Dominance')
        
        ax.set_xlabel('Match Minute', color='white')
        ax.set_ylabel('Territorial Dominance (Field Position)', color='white')
        ax.tick_params(colors='white')
        ax.legend(facecolor='#0a0e1a', edgecolor='white', labelcolor='white')
        ax.set_title(f'Possession Flow / Momentum Map', color='white', fontsize=16, pad=10)
    else:
        ax.text(0.5, 0.5, 'Insufficient Data for Momentum Map', color='white', ha='center', va='center')
        
    filepath = os.path.join(CHARTS_DIR, f"{match_id}_possession_flow.png")
    _save_and_close(fig, filepath)
    return filepath

# 10. Progressive Pass Map
def generate_progressive_pass_map(events: pd.DataFrame, match_id: int, team: str) -> str:
    fig, ax = plt.subplots(figsize=(12, 8))
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#0a0e1a', line_color='#c5c5c5')
    pitch.draw(ax=ax)
    
    passes = events[(events['type'] == 'Pass') & (events['team'] == team) & (events.get('pass_outcome').isnull())].copy()
    if not passes.empty:
        coords = _extract_coords(passes)
        passes['x'] = coords['x']
        passes['y'] = coords['y']
        
        end_coords = passes['pass_end_location'].dropna()
        passes['end_x'] = end_coords.apply(lambda loc: loc[0] if isinstance(loc, list) and len(loc) >= 2 else np.nan)
        passes['end_y'] = end_coords.apply(lambda loc: loc[1] if isinstance(loc, list) and len(loc) >= 2 else np.nan)
        passes = passes.dropna(subset=['x', 'y', 'end_x', 'end_y'])
        
        # StatsBomb standard progressive pass definition: passes that move ball 25% closer to goal
        passes['dist_start'] = np.sqrt((passes['x'] - 120)**2 + (passes['y'] - 40)**2)
        passes['dist_end'] = np.sqrt((passes['end_x'] - 120)**2 + (passes['end_y'] - 40)**2)
        prog_passes = passes[passes['dist_end'] < 0.75 * passes['dist_start']].copy()
        
        if not prog_passes.empty:
            pitch.arrows(prog_passes['x'], prog_passes['y'], prog_passes['end_x'], prog_passes['end_y'],
                         color='#FF4444', width=2, headwidth=4, headlength=5, alpha=0.8, ax=ax)
            pitch.scatter(prog_passes['x'], prog_passes['y'], color='#FF9999', edgecolors='black', s=20, ax=ax)
            ax.set_title(f'Progressive Passes Map — {team} ({len(prog_passes)} passes)', color='white', fontsize=16, pad=10)
        else:
            ax.set_title(f'Progressive Passes Map — {team} (No progressive passes)', color='white', fontsize=16, pad=10)
    else:
        ax.set_title(f'Progressive Passes Map — {team} (No passes)', color='white', fontsize=16, pad=10)
        
    filepath = os.path.join(CHARTS_DIR, f"{match_id}_progressive_passes.png")
    _save_and_close(fig, filepath)
    return filepath

# 11. Expected Threat (xT) Map
def generate_expected_threat_map(events: pd.DataFrame, match_id: int, team: str) -> str:
    fig, ax = plt.subplots(figsize=(12, 8))
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#0a0e1a', line_color='#c5c5c5')
    pitch.draw(ax=ax)
    
    # Simplified xT grid computation overlay (12 x 8)
    passes = events[(events['type'] == 'Pass') & (events['team'] == team)].copy()
    coords = _extract_coords(passes)
    
    if not passes.empty and not coords.empty:
        passes['x'] = coords['x']
        passes['y'] = coords['y']
        
        # Calculate simplified xT (higher closer to attacking center)
        passes['xt_val'] = passes.apply(
            lambda r: (r['x'] / 120.0) * (1.0 - abs(r['y'] - 40.0) / 40.0) * 0.5, axis=1
        )
        passes = passes.dropna(subset=['x', 'y'])
        
        x_bins = np.linspace(0, 120, 13)
        y_bins = np.linspace(0, 80, 9)
        
        xt_grid = np.zeros((8, 12))
        
        for i in range(12):
            for j in range(8):
                cell_passes = passes[
                    (passes['x'] >= x_bins[i]) & (passes['x'] < x_bins[i+1]) &
                    (passes['y'] >= y_bins[j]) & (passes['y'] < y_bins[j+1])
                ]
                if not cell_passes.empty:
                    xt_grid[j, i] = cell_passes['xt_val'].mean()
                    
        # Draw grid heatmap overlay
        sns.heatmap(xt_grid, cmap='hot', alpha=0.5, cbar=False, ax=ax, xticklabels=False, yticklabels=False)
        ax.set_title(f'Expected Threat (xT) Visualizer — {team}', color='white', fontsize=16, pad=10)
    else:
        ax.set_title(f'Expected Threat (xT) Visualizer — {team} (No data)', color='white', fontsize=16, pad=10)
        
    filepath = os.path.join(CHARTS_DIR, f"{match_id}_expected_threat.png")
    _save_and_close(fig, filepath)
    return filepath

# 12. Team Shape Map
def generate_team_shape_map(events: pd.DataFrame, match_id: int, team: str) -> str:
    fig, ax = plt.subplots(figsize=(12, 8))
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#0a0e1a', line_color='#c5c5c5')
    pitch.draw(ax=ax)
    
    passes = events[(events['type'] == 'Pass') & (events['team'] == team)].copy()
    coords = _extract_coords(passes)
    
    if len(passes) > 5 and not coords.empty:
        passes['x'] = coords['x']
        passes['y'] = coords['y']
        passes = passes.dropna(subset=['x', 'y', 'player'])
        
        avg_loc = passes.groupby('player')[['x', 'y']].mean().reset_index()
        
        if len(avg_loc) >= 3:
            points = avg_loc[['x', 'y']].values
            try:
                hull = ConvexHull(points)
                # Draw Convex Hull shape
                pitch.polygon([points[hull.vertices]], color='#00FFCC', alpha=0.2, ax=ax)
                pitch.polygon([points[hull.vertices]], color='#00FFCC', fill=False, lw=2, ax=ax)
            except Exception:
                pass
                
            pitch.scatter(avg_loc['x'], avg_loc['y'], color='#00FFCC', edgecolors='black', s=80, ax=ax)
            for _, row in avg_loc.iterrows():
                pitch.annotate(_format_player_name(row['player']), xy=(row['x'], row['y']), c='white', 
                               va='bottom', ha='center', size=9, weight='bold', ax=ax)
            ax.set_title(f'Tactical Team Shape & Convex Hull — {team}', color='white', fontsize=16, pad=10)
        else:
            ax.set_title(f'Team Shape — {team} (Insufficient players)', color='white', fontsize=16, pad=10)
    else:
        ax.set_title(f'Team Shape — {team} (No data)', color='white', fontsize=16, pad=10)
        
    filepath = os.path.join(CHARTS_DIR, f"{match_id}_team_shape.png")
    _save_and_close(fig, filepath)
    return filepath

# 13. Formation Overlay Visualization
def generate_formation_overlay(events: pd.DataFrame, match_id: int, team: str) -> str:
    fig, ax = plt.subplots(figsize=(12, 8))
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#0a0e1a', line_color='#c5c5c5')
    pitch.draw(ax=ax)
    
    # Draw a lineup formation map using average locations
    passes = events[(events['type'] == 'Pass') & (events['team'] == team)].copy()
    coords = _extract_coords(passes)
    
    if len(passes) > 5 and not coords.empty:
        passes['x'] = coords['x']
        passes['y'] = coords['y']
        passes = passes.dropna(subset=['x', 'y', 'player'])
        
        avg_loc = passes.groupby('player')[['x', 'y']].mean().sort_values(by='x')
        
        # Assign formations (e.g. GK, DEF, MID, FWD based on X averages)
        pitch.scatter(avg_loc['x'], avg_loc['y'], color='#FFD700', edgecolors='black', s=100, zorder=2, ax=ax)
        for player, row in avg_loc.iterrows():
            pitch.annotate(_format_player_name(player), xy=(row['x'], row['y']), c='white', va='top', 
                           ha='center', size=8, weight='bold', ax=ax)
            
        ax.set_title(f'Formation Overlay Visualizer — {team}', color='white', fontsize=16, pad=10)
    else:
        ax.set_title(f'Formation Overlay — {team} (Insufficient data)', color='white', fontsize=16, pad=10)
        
    filepath = os.path.join(CHARTS_DIR, f"{match_id}_formation_overlay.png")
    _save_and_close(fig, filepath)
    return filepath

# 14. Defensive Block Map
def generate_defensive_block_map(events: pd.DataFrame, match_id: int, team: str) -> str:
    fig, ax = plt.subplots(figsize=(12, 8))
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#0a0e1a', line_color='#c5c5c5')
    pitch.draw(ax=ax)
    
    # Find all defensive actions and draw their vertical & horizontal bounds
    def_events = events[
        (events['team'] == team) & 
        (events['type'].isin(['Tackle', 'Interception', 'Clearance']))
    ].copy()
    coords = _extract_coords(def_events)
    
    if len(coords) > 3:
        x_min, x_max = coords['x'].quantile(0.15), coords['x'].quantile(0.85)
        y_min, y_max = coords['y'].quantile(0.15), coords['y'].quantile(0.85)
        
        # Draw defensive block bounding box
        pitch.polygon([[(x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max)]], 
                      color='yellow', alpha=0.15, ax=ax)
        pitch.polygon([[(x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max)]], 
                      color='yellow', fill=False, lw=2.5, linestyle='--', ax=ax)
                      
        pitch.scatter(coords['x'], coords['y'], color='yellow', edgecolors='black', s=45, ax=ax)
        
        ax.set_title(f'Defensive Block Compactness — {team}', color='white', fontsize=16, pad=10)
    else:
        ax.set_title(f'Defensive Block Compactness — {team} (No data)', color='white', fontsize=16, pad=10)
        
    filepath = os.path.join(CHARTS_DIR, f"{match_id}_defensive_block.png")
    _save_and_close(fig, filepath)
    return filepath

# 15. Tactical Zone Occupancy Map
def generate_tactical_zone_occupancy_map(events: pd.DataFrame, match_id: int, team: str) -> str:
    fig, ax = plt.subplots(figsize=(12, 8))
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#0a0e1a', line_color='#c5c5c5')
    pitch.draw(ax=ax)
    
    # Calculates density of player actions in 18 standardized tactical zones
    team_events = events[events['team'] == team].copy()
    coords = _extract_coords(team_events)
    
    if len(coords) > 5:
        # Create an 18-zone overlay (6 horizontal zones, 3 vertical corridors)
        x_bins = np.linspace(0, 120, 7)
        y_bins = np.linspace(0, 80, 4)
        
        density = np.zeros((3, 6))
        for i in range(6):
            for j in range(3):
                zone_events = coords[
                    (coords['x'] >= x_bins[i]) & (coords['x'] < x_bins[i+1]) &
                    (coords['y'] >= y_bins[j]) & (coords['y'] < y_bins[j+1])
                ]
                density[j, i] = len(zone_events)
                
        if density.sum() > 0:
            density_pct = density / density.sum()
            for i in range(6):
                for j in range(3):
                    alpha = density_pct[j, i] * 4
                    alpha = max(0.05, min(0.65, alpha))
                    ax.fill_between([x_bins[i], x_bins[i+1]], y_bins[j], y_bins[j+1], color='orange', alpha=alpha, zorder=0)
                    ax.text((x_bins[i]+x_bins[i+1])/2, (y_bins[j]+y_bins[j+1])/2, f"{density_pct[j, i]:.1%}",
                            color='white', ha='center', va='center', weight='bold', fontsize=9, alpha=0.8)
                            
        ax.set_title(f'Tactical Zone Occupancy map — {team}', color='white', fontsize=16, pad=10)
    else:
        ax.set_title(f'Tactical Zone Occupancy — {team} (No data)', color='white', fontsize=16, pad=10)
        
    filepath = os.path.join(CHARTS_DIR, f"{match_id}_tactical_occupancy.png")
    _save_and_close(fig, filepath)
    return filepath
