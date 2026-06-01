from sqlalchemy import Column, Integer, String, Date, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database.session import Base

class Competition(Base):
    __tablename__ = "competitions"
    id = Column(Integer, primary_key=True, index=True)
    competition_id = Column(Integer, unique=True, index=True)
    competition_name = Column(String, index=True)
    country_name = Column(String)
    matches = relationship("Match", back_populates="competition")

class Season(Base):
    __tablename__ = "seasons"
    id = Column(Integer, primary_key=True, index=True)
    season_id = Column(Integer, unique=True, index=True)
    season_name = Column(String)
    matches = relationship("Match", back_populates="season")

class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, unique=True, index=True)
    team_name = Column(String, index=True)

class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, unique=True, index=True)
    match_date = Column(Date)
    home_team_id = Column(Integer, ForeignKey("teams.id"))
    away_team_id = Column(Integer, ForeignKey("teams.id"))
    home_score = Column(Integer)
    away_score = Column(Integer)
    competition_id = Column(Integer, ForeignKey("competitions.id"))
    season_id = Column(Integer, ForeignKey("seasons.id"))

    home_team = relationship("Team", foreign_keys=[home_team_id])
    away_team = relationship("Team", foreign_keys=[away_team_id])
    competition = relationship("Competition", back_populates="matches")
    season = relationship("Season", back_populates="matches")

class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, unique=True, index=True)
    player_name = Column(String, index=True)
    nickname = Column(String, nullable=True)

class MatchAnalytics(Base):
    __tablename__ = "match_analytics"
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.match_id"), index=True)
    team_name = Column(String, index=True)
    total_passes = Column(Integer, default=0)
    completed_passes = Column(Integer, default=0)
    pass_completion_rate = Column(Integer, default=0) # As percentage
    total_shots = Column(Integer, default=0)
    goals = Column(Integer, default=0)
    press_success_rate = Column(Integer, default=0)
    total_pressures = Column(Integer, default=0)

    # Note: StatsBomb match_id is not the auto-increment id, using ForeignKey on match_id requires it to be unique, which it is.
