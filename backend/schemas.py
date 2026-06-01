from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class CompetitionBase(BaseModel):
    competition_id: int
    competition_name: str
    country_name: str

class CompetitionCreate(CompetitionBase):
    pass

class Competition(CompetitionBase):
    id: int
    class Config:
        from_attributes = True

class SeasonBase(BaseModel):
    season_id: int
    season_name: str

class SeasonCreate(SeasonBase):
    pass

class Season(SeasonBase):
    id: int
    class Config:
        from_attributes = True

class TeamBase(BaseModel):
    team_id: int
    team_name: str

class TeamCreate(TeamBase):
    pass

class Team(TeamBase):
    id: int
    class Config:
        from_attributes = True

class MatchBase(BaseModel):
    match_id: int
    match_date: date
    home_score: int
    away_score: int

class MatchCreate(MatchBase):
    home_team_id: int
    away_team_id: int
    competition_id: int
    season_id: int

class Match(MatchBase):
    id: int
    home_team: Team
    away_team: Team
    class Config:
        from_attributes = True

class PlayerBase(BaseModel):
    player_id: int
    player_name: str
    nickname: Optional[str] = None

class PlayerCreate(PlayerBase):
    pass

class Player(PlayerBase):
    id: int
    class Config:
        from_attributes = True
