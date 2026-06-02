import os
import pandas as pd
import numpy as np
from fpdf import FPDF
from services import analytics_engine

REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

class FootballCoachAI:
    def __init__(self):
        pass
        
    def get_tactical_insights(self, events: pd.DataFrame, team: str) -> dict:
        """
        Calculates and derives structured tactical observations.
        Grounded directly in match statistics.
        """
        teams = events['team'].dropna().unique()
        if len(teams) < 2:
            return {"error": "Insufficient teams data"}
            
        home_team, away_team = teams[0], teams[1]
        opponent = away_team if team == home_team else home_team
        
        # Get advanced metrics
        full_res = analytics_engine.calculate_advanced_metrics(events, 0)
        team_m = full_res["metrics"][team]
        opp_m = full_res["metrics"][opponent]
        
        insights = []
        
        # 1. Goal differential analysis
        xg_diff = team_m["xg"] - opp_m["xg"]
        if xg_diff > 0.4:
            finding = f"Dominant attacking display creating {team_m['xg']:.2f} xG vs opponent's {opp_m['xg']:.2f} xG."
            action = "Keep offensive width; maintain high-intensity vertical transitions."
        elif xg_diff < -0.4:
            finding = f"Attacking deficit, conceded {opp_m['xg']:.2f} xG while generating only {team_m['xg']:.2f} xG."
            action = "Transition to compact mid-block; strengthen central midfield shape."
        else:
            finding = "Even tactical matchup; both teams matched each other in high-quality chances."
            action = "Leverage set-pieces; introduce fresh energetic wingers in the 70th minute."
            
        # 2. Press effectiveness
        pressures = events[(events['type'] == 'Pressure') & (events['team'] == team)]
        recoveries = events[(events['type'] == 'Ball Recovery') & (events['team'] == team)]
        
        if len(pressures) > 0:
            success_pct = team_m["counterpress_efficiency"]
            if success_pct > 40:
                p_find = f"Elite pressing efficiency recovering {success_pct:.1f}% turnovers within 5 seconds."
                p_act = "Maintain aggressive counterpress triggers in final third."
            else:
                p_find = f"Vulnerable press recovery rate of {success_pct:.1f}%; opponent bypassed lines easily."
                p_act = "Optimize pressing timing; instruct front three to delay triggers until backward pass."
        else:
            p_find = "No defensive pressure events registered."
            p_act = "Establish standard defensive block lines."
            
        # 3. Midfield Control (Field Tilt & Possession)
        if team_m["field_tilt"] > 55:
            m_find = f"Superior territorial dominance with {team_m['field_tilt']:.1f}% field tilt."
            m_act = "Utilize diagonal progressive passes; avoid narrow funneling."
        else:
            m_find = f"Territorial disadvantage ({team_m['field_tilt']:.1f}% field tilt); pinned back in own half."
            m_act = "Implement long diagonal switches to escape compact pressure zones."
            
        # 4. Underperforming Players
        underperforming_player = "N/A"
        player_passes = events[(events['type'] == 'Pass') & (events['team'] == team)].copy()
        if not player_passes.empty:
            player_passes['x'] = player_passes['location'].apply(lambda x: x[0] if isinstance(x, list) else 0)
            player_passes_under_p = player_passes[player_passes['under_pressure'] == True]
            if not player_passes_under_p.empty:
                low_p = player_passes_under_p.groupby('player').apply(
                    lambda g: len(g[g['pass_outcome'].notna()]) / len(g)
                )
                if not low_p.empty and low_p.max() > 0:
                    underperforming_player = low_p.idxmax()
                    
        return {
            "team": team,
            "opponent": opponent,
            "team_metrics": team_m,
            "opponent_metrics": opp_m,
            "findings": {
                "attacking": finding,
                "pressing": p_find,
                "midfield": m_find,
                "underperformer": f"Player {underperforming_player} experienced high turnover rates under pressure." if underperforming_player != "N/A" else "All central midfielders maintained high ball security rates."
            },
            "recommendations": {
                "attacking": action,
                "pressing": p_act,
                "midfield": m_act,
                "substitutions": f"Substitute {underperforming_player} with a high press-resistant midfielder." if underperforming_player != "N/A" else "No immediate structural substitutions recommended; maintain tactical shape."
            }
        }
        
    def answer_coaching_query(self, events: pd.DataFrame, team: str, question: str) -> str:
        insights = self.get_tactical_insights(events, team)
        q = question.lower()
        
        if "why did we lose" in q or "weakness" in q:
            return (
                f"**Tactical Retrospective Analysis — {team}**\n\n"
                f"* **Midfield & Territory**: {insights['findings']['midfield']} This compromised our transition control.\n"
                f"* **Defensive Gaps**: {insights['findings']['pressing']} We struggled to retain vertical compactness.\n"
                f"* **Key Recommendation**: {insights['recommendations']['pressing']} We must transition from an aggressive press to a structured mid-block ({insights['recommendations']['attacking']})."
            )
        elif "press" in q or "defend" in q:
            return (
                f"**Defensive & Pressing Assessment — {team}**\n\n"
                f"* **Current Metric Status**: Our counterpress recovery efficiency is currently at **{insights['team_metrics']['counterpress_efficiency']:.1f}%**.\n"
                f"* **Tactical Finding**: {insights['findings']['pressing']}\n"
                f"* **Actionable Adjustment**: {insights['recommendations']['pressing']} Additionally, {insights['recommendations']['midfield']}"
            )
        elif "substitutions" in q or "player" in q or "underperform" in q:
            return (
                f"**Player Performance & Substitutions Insight**\n\n"
                f"* **Analytical Review**: {insights['findings']['underperformer']}\n"
                f"* **Coaching Decision**: {insights['recommendations']['substitutions']}\n"
                f"* **Tactical Change**: Focus progressive actions through players with high press resistance (current squad average: {insights['team_metrics']['press_resistance']:.1f}%)."
            )
        else:
            return (
                f"**Tactical Match Summary Grounding ({team} vs {insights['opponent']})**\n\n"
                f"* **Attack**: {insights['findings']['attacking']} (xG: {insights['team_metrics']['xg']:.2f} vs {insights['opponent_metrics']['xg']:.2f})\n"
                f"* **Defense**: {insights['findings']['pressing']} (Counterpress: {insights['team_metrics']['counterpress_efficiency']:.1f}%)\n"
                f"* **Territory**: Field Tilt at {insights['team_metrics']['field_tilt']:.1f}%; Possession share at {insights['team_metrics']['possession']:.1f}%.\n"
                f"* **Primary Recommendation**: {insights['recommendations']['midfield']}"
            )
            
    def generate_pdf_report(self, events: pd.DataFrame, match_id: int, team: str) -> str:
        insights = self.get_tactical_insights(events, team)
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_text_color(10, 14, 26) # #0a0e1a Dark theme slate color
        
        # Header
        pdf.set_font("Helvetica", "B", 20)
        pdf.cell(190, 12, "AI COACHING & TACTICAL REPORT", ln=True, align="C")
        pdf.set_font("Helvetica", "I", 11)
        pdf.cell(190, 8, f"Match ID: {match_id} | Team analyzed: {team} vs {insights['opponent']}", ln=True, align="C")
        pdf.line(10, 32, 200, 32)
        pdf.ln(10)
        
        # 1. Match Summary Metrics Table
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(190, 8, "1. Core Tactical Metrics Comparison", ln=True)
        pdf.ln(2)
        
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(60, 7, "Metric Name", border=1, align="C")
        pdf.cell(65, 7, f"{team} (Home/Away)", border=1, align="C")
        pdf.cell(65, 7, f"{insights['opponent']} (Opponent)", border=1, align="C")
        pdf.ln()
        
        metrics_list = [
            ("Expected Goals (xG)", "xg"),
            ("Expected Threat (xT)", "xt"),
            ("Field Tilt (%)", "field_tilt"),
            ("Possession (%)", "possession"),
            ("Progressive Passes", "progressive_passes"),
            ("Press Resistance (%)", "press_resistance"),
            ("Counterpress Efficiency (%)", "counterpress_efficiency"),
            ("Transition Speed (m/s)", "transition_speed"),
        ]
        
        pdf.set_font("Helvetica", "", 10)
        for label, key in metrics_list:
            pdf.cell(60, 7, label, border=1)
            pdf.cell(65, 7, str(insights['team_metrics'][key]), border=1, align="C")
            pdf.cell(65, 7, str(insights['opponent_metrics'][key]), border=1, align="C")
            pdf.ln()
            
        pdf.ln(10)
        
        # 2. Detailed Tactical Analysis Sections
        sections = [
            ("2. Possession & Midfield Analysis", insights['findings']['midfield'], insights['recommendations']['midfield']),
            ("3. Attacking Performance & Transitions", insights['findings']['attacking'], insights['recommendations']['attacking']),
            ("4. Defensive & Counterpress Assessment", insights['findings']['pressing'], insights['recommendations']['pressing']),
            ("5. Player & Substitution Adjustments", insights['findings']['underperformer'], insights['recommendations']['substitutions']),
        ]
        
        for title, finding, recommendation in sections:
            pdf.set_font("Helvetica", "B", 13)
            pdf.cell(190, 8, title, ln=True)
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(190, 5, "Finding:", ln=True)
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(190, 5, finding)
            pdf.ln(1)
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(190, 5, "Coaching Action Recommended:", ln=True)
            pdf.set_font("Helvetica", "I", 10)
            pdf.multi_cell(190, 5, recommendation)
            pdf.ln(6)
            
        filepath = os.path.join(REPORTS_DIR, f"{match_id}_coaching_report.pdf")
        pdf.output(filepath)
        return filepath
        
    def generate_markdown_report(self, events: pd.DataFrame, match_id: int, team: str) -> str:
        insights = self.get_tactical_insights(events, team)
        opp = insights['opponent']
        tm = insights['team_metrics']
        om = insights['opponent_metrics']
        
        md = f"""# AI Tactical & Strategy Report
**Match ID:** {match_id} | **Home/Away Analyzed:** {team} vs {opp}

## 1. Core Tactical Metrics Comparison

| Metric Name | {team} | {opp} |
| :--- | :---: | :---: |
| **Expected Goals (xG)** | {tm['xg']:.2f} | {om['xg']:.2f} |
| **Expected Threat (xT)** | {tm['xt']:.2f} | {om['xt']:.2f} |
| **Field Tilt (%)** | {tm['field_tilt']:.1f}% | {om['field_tilt']:.1f}% |
| **Possession (%)** | {tm['possession']:.1f}% | {om['possession']:.1f}% |
| **Progressive Passes** | {tm['progressive_passes']} | {om['progressive_passes']} |
| **Press Resistance (%)** | {tm['press_resistance']:.1f}% | {om['press_resistance']:.1f}% |
| **Counterpress Efficiency (%)** | {tm['counterpress_efficiency']:.1f}% | {om['counterpress_efficiency']:.1f}% |
| **Transition Speed (m/s)** | {tm['transition_speed']:.1f} m/s | {om['transition_speed']:.1f} m/s |

---

## 2. Midfield & Territory Analysis
* **Statistical Finding:** {insights['findings']['midfield']}
* **Coaching Action Plan:** {insights['recommendations']['midfield']}

---

## 3. Attacking Transitions & Penetration
* **Statistical Finding:** {insights['findings']['attacking']}
* **Coaching Action Plan:** {insights['recommendations']['attacking']}

---

## 4. Defensive Pressing & Recovery
* **Statistical Finding:** {insights['findings']['pressing']}
* **Coaching Action Plan:** {insights['recommendations']['pressing']}

---

## 5. Player Profiling & Substitution Adjustments
* **Statistical Finding:** {insights['findings']['underperformer']}
* **Coaching Action Plan:** {insights['recommendations']['substitutions']}

---

*Report generated automatically by Antigravity Tactical Analytics Suite.*
"""
        filepath = os.path.join(REPORTS_DIR, f"{match_id}_coaching_report.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md)
        return filepath
