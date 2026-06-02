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
            
            # Midfielders
            {"name": "Kevin De Bruyne", "position": "Midfielder", "age": 30, "market_value": 90000000, "style": "Deep Lying Playmaker", 
             "vector": np.array([0.85, 0.98, 0.40, 0.65, 0.85, 0.75]), "strengths": "Chances creation, elite progressive passing", "weaknesses": "Aerial duels"},
            {"name": "N'Golo Kante", "position": "Midfielder", "age": 30, "market_value": 50000000, "style": "Defensive Midfielder", 
             "vector": np.array([0.40, 0.75, 0.98, 0.98, 0.70, 0.80]), "strengths": "Elite recoveries, press intensity, coverage", "weaknesses": "Long-range shooting"},
            {"name": "Jude Bellingham", "position": "Midfielder", "age": 18, "market_value": 75000000, "style": "Box-to-Box", 
             "vector": np.array([0.78, 0.85, 0.78, 0.85, 0.82, 0.88]), "strengths": "Engine volume, ball progression, defensive duels", "weaknesses": "Overcommitting triggers"},
            
            # Wingers
            {"name": "Kylian Mbappe", "position": "Winger", "age": 23, "market_value": 160000000, "style": "Inverted Winger", 
             "vector": np.array([0.96, 0.75, 0.08, 0.40, 0.98, 0.90]), "strengths": "Explosive acceleration, 1v1 dribbles, xG threat", "weaknesses": "Trackback cover"},
            {"name": "Bukayo Saka", "position": "Winger", "age": 20, "market_value": 70000000, "style": "Traditional Winger", 
             "vector": np.array([0.78, 0.88, 0.65, 0.80, 0.90, 0.78]), "strengths": "Ball security under pressure, crosses, high workrate", "weaknesses": "Header conversion"},
             
            # Defenders
            {"name": "Virgil van Dijk", "position": "Defender", "age": 30, "market_value": 55000000, "style": "Ball Playing Defender", 
             "vector": np.array([0.20, 0.85, 0.96, 0.50, 0.60, 0.98]), "strengths": "Aerial dominance, calmness, spatial reading", "weaknesses": "Acceleration on wide turns"},
            {"name": "Trent Alexander-Arnold", "position": "Defender", "age": 23, "market_value": 80000000, "style": "Wing Back", 
             "vector": np.array([0.65, 0.96, 0.60, 0.70, 0.80, 0.75]), "strengths": "Crossing accuracy, dead-ball switches", "weaknesses": "1v1 defensive positioning"}
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
