from pydantic import BaseModel
from typing import Optional

class MatchAnalyticsResponse(BaseModel):
    id: int
    match_id: int
    team_name: str
    total_passes: int
    completed_passes: int
    pass_completion_rate: int
    total_shots: int
    goals: int
    press_success_rate: int
    total_pressures: int

    class Config:
        from_attributes = True

class ProcessMatchRequest(BaseModel):
    match_id: int
    team_name: str
