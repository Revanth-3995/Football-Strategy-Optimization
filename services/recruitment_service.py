import numpy as np
from typing import List, Dict, Any

class RecruitmentEngine:
    def __init__(self):
        # High fidelity dataset of 15 top global players across positions with precise playstyle metrics
        # Vector metrics: [Attacking, Passing, Defensive, Pressing, Dribbling, Physical]
        self.players_database = [
            # Strikers
            {"name": "Robert Lewandowski", "position": "Forward", "age": 32, "market_value": 45000000, "style": "Poacher", 
             "vector": np.array([0.95, 0.45, 0.10, 0.35, 0.65, 0.85]), "strengths": "Clinical finishing, positioning", "weaknesses": "Defensive workrate"},
            {"name": "Harry Kane", "position": "Forward", "age": 28, "market_value": 85000000, "style": "Target Man", 
             "vector": np.array([0.90, 0.80, 0.20, 0.45, 0.70, 0.80]), "strengths": "Link-up play, finishing, passing range", "weaknesses": "Sprint recovery"},
            {"name": "Erling Haaland", "position": "Forward", "age": 21, "market_value": 150000000, "style": "Poacher", 
             "vector": np.array([0.98, 0.35, 0.05, 0.50, 0.75, 0.95]), "strengths": "Speed, physical dominance, box presence", "weaknesses": "Short passing under pressure"},
            {"name": "Julian Alvarez", "position": "Forward", "age": 22, "market_value": 50000000, "style": "Pressing Forward", 
             "vector": np.array([0.85, 0.70, 0.40, 0.88, 0.75, 0.82]), "strengths": "High pressing workrate, tactical flexibility", "weaknesses": "Aerial duels"},
            {"name": "Lautaro Martinez", "position": "Forward", "age": 24, "market_value": 75000000, "style": "Poacher", 
             "vector": np.array([0.88, 0.65, 0.30, 0.75, 0.70, 0.80]), "strengths": "Box presence, clinical finishing, tenacity", "weaknesses": "Aerial duels height disadvantage"},
            {"name": "Karim Benzema", "position": "Forward", "age": 34, "market_value": 35000000, "style": "False Nine", 
             "vector": np.array([0.92, 0.88, 0.15, 0.40, 0.82, 0.75]), "strengths": "World-class linkup play, deep drop space creation", "weaknesses": "Low defensive workrate"},
            {"name": "Rasmus Hojlund", "position": "Forward", "age": 19, "market_value": 40000000, "style": "Target Man", 
             "vector": np.array([0.80, 0.40, 0.15, 0.50, 0.68, 0.85]), "strengths": "Raw sprint speed, physical size, box entry", "weaknesses": "First touch consistency"},
            
            # Midfielders
            {"name": "Kevin De Bruyne", "position": "Midfielder", "age": 30, "market_value": 90000000, "style": "Deep Lying Playmaker", 
             "vector": np.array([0.85, 0.98, 0.40, 0.65, 0.85, 0.75]), "strengths": "Chances creation, elite progressive passing", "weaknesses": "Aerial duels"},
            {"name": "N'Golo Kante", "position": "Midfielder", "age": 30, "market_value": 50000000, "style": "Defensive Midfielder", 
             "vector": np.array([0.40, 0.75, 0.98, 0.98, 0.70, 0.80]), "strengths": "Elite recoveries, press intensity, coverage", "weaknesses": "Long-range shooting"},
            {"name": "Jude Bellingham", "position": "Midfielder", "age": 18, "market_value": 75000000, "style": "Box-to-Box", 
             "vector": np.array([0.78, 0.85, 0.78, 0.85, 0.82, 0.88]), "strengths": "Engine volume, ball progression, defensive duels", "weaknesses": "Overcommitting triggers"},
            {"name": "Pedri", "position": "Midfielder", "age": 19, "market_value": 80000000, "style": "Advanced Playmaker", 
             "vector": np.array([0.72, 0.95, 0.60, 0.85, 0.92, 0.68]), "strengths": "Elite press resistance, half-space turns, vision", "weaknesses": "Physical strength in duels"},
            {"name": "Declan Rice", "position": "Midfielder", "age": 23, "market_value": 85000000, "style": "Defensive Midfielder", 
             "vector": np.array([0.55, 0.82, 0.94, 0.88, 0.78, 0.88]), "strengths": "Interceptions, defensive coverage, ball carrying", "weaknesses": "Elite final-third creation"},
            {"name": "Luka Modric", "position": "Midfielder", "age": 36, "market_value": 10000000, "style": "Deep Lying Playmaker", 
             "vector": np.array([0.75, 0.96, 0.65, 0.70, 0.88, 0.68]), "strengths": "Trivela crosses, escape pressure, game tempo control", "weaknesses": "Sprint recovery pace"},
            {"name": "Enzo Fernandez", "position": "Midfielder", "age": 21, "market_value": 85000000, "style": "Deep Lying Playmaker", 
             "vector": np.array([0.70, 0.92, 0.75, 0.78, 0.75, 0.78]), "strengths": "Elite passing range, progressive switches", "weaknesses": "1v1 defensive speed"},
            {"name": "Martin Odegaard", "position": "Midfielder", "age": 23, "market_value": 80000000, "style": "Advanced Playmaker", 
             "vector": np.array([0.82, 0.94, 0.45, 0.85, 0.88, 0.70]), "strengths": "Chances created, high counterpress triggers", "weaknesses": "Defensive tackles"},
            
            # Wingers
            {"name": "Kylian Mbappe", "position": "Winger", "age": 23, "market_value": 160000000, "style": "Inverted Winger", 
             "vector": np.array([0.96, 0.75, 0.08, 0.40, 0.98, 0.90]), "strengths": "Explosive acceleration, 1v1 dribbles, xG threat", "weaknesses": "Trackback cover"},
            {"name": "Bukayo Saka", "position": "Winger", "age": 20, "market_value": 70000000, "style": "Traditional Winger", 
             "vector": np.array([0.78, 0.88, 0.65, 0.80, 0.90, 0.78]), "strengths": "Ball security under pressure, crosses, high workrate", "weaknesses": "Header conversion"},
            {"name": "Vinicius Jr", "position": "Winger", "age": 21, "market_value": 120000000, "style": "Inverted Winger", 
             "vector": np.array([0.92, 0.72, 0.15, 0.65, 0.98, 0.82]), "strengths": "Pace on direct runs, 1v1 isolation dribbling", "weaknesses": "Final decision consistency"},
            {"name": "Mohamed Salah", "position": "Winger", "age": 29, "market_value": 90000000, "style": "Inside Forward", 
             "vector": np.array([0.95, 0.80, 0.20, 0.55, 0.88, 0.80]), "strengths": "Inside runs finishing, pace, chance creation", "weaknesses": "Defensive trackback"},
            {"name": "Phil Foden", "position": "Winger", "age": 21, "market_value": 90000000, "style": "Inverted Winger", 
             "vector": np.array([0.85, 0.90, 0.35, 0.80, 0.92, 0.72]), "strengths": "Perfect first touch, close-quarters control", "weaknesses": "Physical shielding"},
             
            # Defenders
            {"name": "Virgil van Dijk", "position": "Defender", "age": 30, "market_value": 55000000, "style": "Ball Playing Defender", 
             "vector": np.array([0.20, 0.85, 0.96, 0.50, 0.60, 0.98]), "strengths": "Aerial dominance, calmness, spatial reading", "weaknesses": "Acceleration on wide turns"},
            {"name": "Trent Alexander-Arnold", "position": "Defender", "age": 23, "market_value": 80000000, "style": "Wing Back", 
             "vector": np.array([0.65, 0.96, 0.60, 0.70, 0.80, 0.75]), "strengths": "Crossing accuracy, dead-ball switches", "weaknesses": "1v1 defensive positioning"},
            {"name": "Ruben Dias", "position": "Defender", "age": 25, "market_value": 75000000, "style": "Ball Playing Defender", 
             "vector": np.array([0.15, 0.75, 0.96, 0.65, 0.50, 0.94]), "strengths": "Defensive blocks, leadership, box clearance", "weaknesses": "Top sprint recovery"},
            {"name": "Alphonso Davies", "position": "Defender", "age": 21, "market_value": 70000000, "style": "Wing Back", 
             "vector": np.array([0.60, 0.78, 0.75, 0.78, 0.92, 0.88]), "strengths": "Recovery pace, progressive direct carries", "weaknesses": "Defensive tactical shape discipline"},
            {"name": "Achraf Hakimi", "position": "Defender", "age": 23, "market_value": 65000000, "style": "Wing Back", 
             "vector": np.array([0.68, 0.85, 0.70, 0.75, 0.82, 0.82]), "strengths": "Overlapping runs, crossing accuracy, speed", "weaknesses": "Defensive tracking depth"}
        ]

    def search_similar_players(self, position: str, age_max: int, budget_max: int, target_style_weights: List[float]) -> List[Dict[str, Any]]:
        """
        Uses Cosine Similarity to find similar players based on a play style target weights vector.
        Vector indices: [Attacking, Passing, Defensive, Pressing, Dribbling, Physical]
        """
        target_vec = np.array(target_style_weights)
        norm_target = np.linalg.norm(target_vec)
        
        results = []
        for player in self.players_database:
            # Filter criteria
            if position != "All" and player["position"] != position:
                continue
            if player["age"] > age_max:
                continue
            if player["market_value"] > budget_max:
                continue
                
            p_vec = player["vector"]
            norm_p = np.linalg.norm(p_vec)
            
            if norm_target > 0 and norm_p > 0:
                similarity = np.dot(target_vec, p_vec) / (norm_target * norm_p)
            else:
                similarity = 0.5
                
            results.append({
                "name": player["name"],
                "position": player["position"],
                "age": player["age"],
                "market_value": player["market_value"],
                "style": player["style"],
                "similarity_score": round(float(similarity), 3),
                "tactical_fit": "Excellent" if similarity > 0.85 else ("Good" if similarity > 0.75 else "Moderate"),
                "strengths": player["strengths"],
                "weaknesses": player["weaknesses"]
            })
            
        # Sort descending by similarity
        return sorted(results, key=lambda x: x["similarity_score"], reverse=True)
