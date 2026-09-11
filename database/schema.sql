-- Database Schema for IPL Performance Analytics
-- Supports SQLite relational storage of matches, players, teams, and innings events

CREATE TABLE IF NOT EXISTS teams (
    team_id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS players (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS matches (
    match_id INTEGER PRIMARY KEY,
    season TEXT NOT NULL,
    date TEXT,
    venue TEXT,
    city TEXT,
    team1 TEXT,
    team2 TEXT,
    toss_winner TEXT,
    toss_decision TEXT,
    winner TEXT,
    result TEXT,
    win_by_runs INTEGER DEFAULT 0,
    win_by_wickets INTEGER DEFAULT 0,
    player_of_match TEXT
);

CREATE TABLE IF NOT EXISTS batting_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id INTEGER,
    batsman TEXT,
    runs INTEGER,
    balls INTEGER,
    fours INTEGER,
    sixes INTEGER,
    strike_rate REAL,
    FOREIGN KEY (match_id) REFERENCES matches(match_id)
);

CREATE TABLE IF NOT EXISTS bowling_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id INTEGER,
    bowler TEXT,
    overs TEXT,
    legal_balls INTEGER,
    runs_conceded INTEGER,
    wickets INTEGER,
    economy REAL,
    FOREIGN KEY (match_id) REFERENCES matches(match_id)
);

CREATE INDEX IF NOT EXISTS idx_matches_season ON matches(season);
CREATE INDEX IF NOT EXISTS idx_matches_winner ON matches(winner);
CREATE INDEX IF NOT EXISTS idx_batting_batsman ON batting_performance(batsman);
CREATE INDEX IF NOT EXISTS idx_bowling_bowler ON bowling_performance(bowler);
