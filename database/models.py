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

class ModelRun(Base):
    __tablename__ = "model_runs"
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.match_id"), index=True)
    model_type = Column(String, index=True) # "press_success", "outcome_xgboost", "outcome_lightgbm", "formation", "role", "clustering"
    accuracy = Column(JSON, nullable=True) # holds metric values
    precision_ = Column(JSON, nullable=True)
    recall = Column(JSON, nullable=True)
    f1_score = Column(JSON, nullable=True)
    n_samples = Column(Integer, default=0)
    ran_at = Column(String)

class PlayerMetric(Base):
    __tablename__ = "player_metrics"
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.match_id"), index=True)
    player_name = Column(String, index=True)
    xg = Column(Integer, default=0) # scaled by 100 or actual float * 100 stored as int
    xt = Column(Integer, default=0)
    press_resistance = Column(Integer, default=0)
    touches = Column(Integer, default=0)
    completions = Column(Integer, default=0)
    progressive_passes = Column(Integer, default=0)

class TeamMetric(Base):
    __tablename__ = "team_metrics"
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.match_id"), index=True)
    team_name = Column(String, index=True)
    field_tilt = Column(Integer, default=0)
    counterpress_efficiency = Column(Integer, default=0)
    transition_speed = Column(Integer, default=0) # scaled or raw
    possession = Column(Integer, default=0)
    zone_dominance = Column(JSON, nullable=True) # dictionary of zone indices -> dominance values

class PlayerClustering(Base):
    __tablename__ = "player_clustering"
    id = Column(Integer, primary_key=True, index=True)
    player_name = Column(String, unique=True, index=True)
    cluster_id = Column(Integer, index=True)
    role_detected = Column(String, index=True)

class ScoutingProfile(Base):
    __tablename__ = "scouting_profiles"
    id = Column(Integer, primary_key=True, index=True)
    player_name = Column(String, unique=True, index=True)
    position = Column(String, index=True)
    age = Column(Integer, default=0)
    budget = Column(Integer, default=0)
    playing_style = Column(String)

