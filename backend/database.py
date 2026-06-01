import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.environ.get("DB_PATH", "data/analytics.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            match_id     INTEGER PRIMARY KEY,
            competition  TEXT NOT NULL,
            season       TEXT NOT NULL,
            home_team    TEXT NOT NULL,
            away_team    TEXT NOT NULL,
            home_score   INTEGER,
            away_score   INTEGER,
            match_date   TEXT,
            created_at   TEXT DEFAULT (datetime('now'))
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS model_runs (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id     INTEGER NOT NULL,
            accuracy     REAL,
            precision_   REAL,
            recall       REAL,
            f1_score     REAL,
            n_samples    INTEGER,
            ran_at       TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (match_id) REFERENCES matches(match_id)
        );
        """)
        conn.commit()


def upsert_match(match_dict):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO matches (match_id, competition, season, home_team, away_team, home_score, away_score, match_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            match_dict['match_id'],
            match_dict.get('competition', ''),
            match_dict.get('season', ''),
            match_dict['home_team'],
            match_dict['away_team'],
            match_dict.get('home_score'),
            match_dict.get('away_score'),
            match_dict.get('match_date')
        ))
        conn.commit()

def save_model_run(match_id, metrics_dict):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO model_runs (match_id, accuracy, precision_, recall, f1_score, n_samples)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            match_id,
            metrics_dict['accuracy'],
            metrics_dict['precision'],
            metrics_dict['recall'],
            metrics_dict['f1'],
            metrics_dict['n_samples']
        ))
        conn.commit()

def get_all_matches():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM matches ORDER BY match_date DESC")
        return [dict(row) for row in cursor.fetchall()]

def get_model_runs(match_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM model_runs WHERE match_id = ? ORDER BY ran_at DESC", (match_id,))
        return [dict(row) for row in cursor.fetchall()]
