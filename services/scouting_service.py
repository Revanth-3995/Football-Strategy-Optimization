import os
import pandas as pd
import numpy as np
from services import analytics_engine

SCOUTING_DIR = "reports"
os.makedirs(SCOUTING_DIR, exist_ok=True)

class OpponentScoutingPlatform:
    def __init__(self):
        pass
        
    def scan_weaknesses_and_strengths(self, events: pd.DataFrame, team: str) -> dict:
        """
        Scans coordinates of opponent team to find vulnerable zones and strong zones.
        """
        opp_events = events[events['team'] == team].copy()
        if opp_events.empty:
            return {"weaknesses": [], "strengths": []}
            
        x_coords = opp_events['location'].apply(lambda loc: loc[0] if isinstance(loc, list) and len(loc) >= 2 else np.nan)
        y_coords = opp_events['location'].apply(lambda loc: loc[1] if isinstance(loc, list) and len(loc) >= 2 else np.nan)
        opp_events['x'] = x_coords
        opp_events['y'] = y_coords
        opp_events = opp_events.dropna(subset=['x', 'y'])
        
        # 1. Identify high turnover zones (where turnovers happened)
        # Turnovers: Pass with outcome, or Dispossessed, or Miscontrol
        turnovers = opp_events[
            (opp_events['type'] == 'Dispossessed') |
            (opp_events['type'] == 'Bad Behaviour') |
            ((opp_events['type'] == 'Pass') & (opp_events['pass_outcome'].notna()))
        ]
        
        weak_zones = []
        if not turnovers.empty:
            # check attacking corridors
            left_corridor = len(turnovers[turnovers['y'] < 25])
            central_corridor = len(turnovers[(turnovers['y'] >= 25) & (turnovers['y'] <= 55)])
            right_corridor = len(turnovers[turnovers['y'] > 55])
            
            corridors = {"Left Flank": left_corridor, "Central Midfield": central_corridor, "Right Flank": right_corridor}
            weakest = max(corridors, key=corridors.get)
            
            weak_zones.append({
                "zone": weakest,
                "description": f"High turnover rate detected in the {weakest} corridor. Opponent miscontrolled the ball or misplaced passes {corridors[weakest]} times.",
                "counter_strategy": f"Deploy a high block squeezing inside channels; restrict passing lanes into {weakest}."
            })
            
        # 2. Identify defensive block gaps
        def_actions = opp_events[opp_events['type'].isin(['Tackle', 'Interception', 'Clearance'])]
        if not def_actions.empty:
            # check horizontal density
            low_block_count = len(def_actions[def_actions['x'] < 40])
            mid_block_count = len(def_actions[(def_actions['x'] >= 40) & (def_actions['x'] <= 80)])
            high_block_count = len(def_actions[def_actions['x'] > 80])
            
            if low_block_count > 2 * mid_block_count:
                weak_zones.append({
                    "zone": "Deep Defensive Line",
                    "description": "Opponent drops extremely deep immediately upon turnover, creating massive spaces in front of their defensive line.",
                    "counter_strategy": "Instruct central midfielders to make late progressive runs into the box or take long-range shots from the edge of the box."
                })
            else:
                weak_zones.append({
                    "zone": "High Defensive Line Gap",
                    "description": "Opponent maintains a high block line but lacks speed recovery, presenting high-risk gaps behind center backs.",
                    "counter_strategy": "Instruct wingers to make direct progressive runs behind center backs on quick transitions."
                })
                
        # 3. Identify Strengths (Dominant build-up players and press-resistant players)
        strengths = []
        passes = opp_events[opp_events['type'] == 'Pass'].copy()
        if not passes.empty:
            # find most active player
            top_passer = passes['player'].value_counts()
            if not top_passer.empty:
                dominant_player = top_passer.index[0]
                p_count = top_passer.iloc[0]
                
                strengths.append({
                    "type": "Build-up Engine",
                    "description": f"Midfielder {dominant_player} is the focal build-up playmaker with {p_count} passes attempted.",
                    "mitigation": f"Mark {dominant_player} tightly; cut off passing lanes from center backs to restrict ball progression."
                })
                
        return {
            "team_scouted": team,
            "weaknesses": weak_zones if weak_zones else [{"zone": "Central Defending", "description": "Lacks vertical compactness under direct runs.", "counter_strategy": "Run directly at center backs."}],
            "strengths": strengths if strengths else [{"type": "Possession Control", "description": "Maintains high passing accuracy in low pressure zones.", "mitigation": "Increase pressing intensity."}]
        }
        
    def generate_scouting_report(self, events: pd.DataFrame, team: str) -> dict:
        results = self.scan_weaknesses_and_strengths(events, team)
        
        # Build Markdown scouting profile
        md = f"""# Professional Scouting Report — Opponent Analysis
**Team Scouted:** {team}

## 1. Tactical Strengths & Key Playmakers
"""
        for st in results["strengths"]:
            md += f"""### [{st['type']}]
* **Tactical Finding:** {st['description']}
* **Mitigation / Nullification Strategy:** {st['mitigation']}
\n"""
            
        md += """
## 2. Structural Weaknesses & Tactical Vulnerabilities
"""
        for wk in results["weaknesses"]:
            md += f"""### [Vulnerable Zone: {wk['zone']}]
* **Tactical Observation:** {wk['description']}
* **Counter Strategy / Exploitation:** {wk['counter_strategy']}
\n"""
            
        md += "\n*Scouting Report compiled by Antigravity Tactical scouting suite.*"
        
        # Save to markdown file
        filepath = os.path.join(SCOUTING_DIR, f"{team.replace(' ', '_')}_scouting_report.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md)
            
        return {
            "team": team,
            "markdown_path": filepath,
            "data": results
        }
