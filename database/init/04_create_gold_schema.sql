-- Gold Layer: Dimensional model (Star Schema)
-- This layer contains dimension and fact tables optimized for analytics

\c arsenalfc_analytics

-- ============================================
-- DIMENSION TABLES
-- ============================================

-- Dimension: Season
CREATE TABLE IF NOT EXISTS gold.dim_season (
    season_id SERIAL PRIMARY KEY,
    season_name VARCHAR(20) UNIQUE NOT NULL, -- '2024-2025'
    start_year INTEGER NOT NULL,
    end_year INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Dimension: Competition
CREATE TABLE IF NOT EXISTS gold.dim_competition (
    competition_id SERIAL PRIMARY KEY,
    competition_name VARCHAR(100) UNIQUE NOT NULL, -- 'Premier League', 'Champions League'
    competition_code VARCHAR(10), -- 'PL', 'UCL', 'FAC'
    country VARCHAR(50),
    tier INTEGER, -- 1 for top tier
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Dimension: Team
CREATE TABLE IF NOT EXISTS gold.dim_team (
    team_id SERIAL PRIMARY KEY,
    team_name VARCHAR(100) UNIQUE NOT NULL,
    team_short_name VARCHAR(50),
    fbref_team_id VARCHAR(50),
    understat_team_id VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Dimension: Player
CREATE TABLE IF NOT EXISTS gold.dim_player (
    player_id SERIAL PRIMARY KEY,
    player_name VARCHAR(200) NOT NULL,
    fbref_player_id VARCHAR(50),
    understat_player_id VARCHAR(50),
    position VARCHAR(20),
    nationality VARCHAR(50),
    birth_date DATE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(player_name, fbref_player_id)
);

-- Dimension: Game State
CREATE TABLE IF NOT EXISTS gold.dim_game_state (
    game_state_id SERIAL PRIMARY KEY,
    state_name VARCHAR(20) UNIQUE NOT NULL, -- 'Leading', 'Drawing', 'Trailing'
    state_code VARCHAR(10), -- 'W', 'D', 'L'
    description TEXT
);

-- Dimension: Match
CREATE TABLE IF NOT EXISTS gold.dim_match (
    match_id VARCHAR(50) PRIMARY KEY,
    season_id INTEGER NOT NULL REFERENCES gold.dim_season(season_id),
    competition_id INTEGER NOT NULL REFERENCES gold.dim_competition(competition_id),

    -- Date and time
    match_date DATE NOT NULL,
    kickoff_time TIME,

    -- Teams
    home_team_id INTEGER NOT NULL REFERENCES gold.dim_team(team_id),
    away_team_id INTEGER NOT NULL REFERENCES gold.dim_team(team_id),

    -- Score
    home_score INTEGER,
    away_score INTEGER,

    -- Match details
    venue VARCHAR(200),
    attendance INTEGER,
    referee VARCHAR(100),
    home_formation VARCHAR(20),
    away_formation VARCHAR(20),

    -- Status
    match_status VARCHAR(20), -- 'scheduled', 'finished', 'postponed'

    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- FACT TABLES
-- ============================================

-- Fact: Team match performance
CREATE TABLE IF NOT EXISTS gold.fact_team_match_performance (
    team_match_id SERIAL PRIMARY KEY,
    match_id VARCHAR(50) NOT NULL REFERENCES gold.dim_match(match_id),
    team_id INTEGER NOT NULL REFERENCES gold.dim_team(team_id),
    opponent_id INTEGER NOT NULL REFERENCES gold.dim_team(team_id),

    -- Result
    is_home BOOLEAN NOT NULL,
    goals_for INTEGER,
    goals_against INTEGER,
    result VARCHAR(1), -- 'W', 'D', 'L'

    -- Expected goals
    xg_for DECIMAL(5,2),
    xg_against DECIMAL(5,2),
    npxg_for DECIMAL(5,2),
    npxg_against DECIMAL(5,2),

    -- Possession
    possession_pct DECIMAL(5,2),

    -- Passing
    passes_completed INTEGER,
    passes_attempted INTEGER,
    pass_completion_pct DECIMAL(5,2),
    progressive_passes INTEGER,

    -- Shooting
    shots INTEGER,
    shots_on_target INTEGER,
    shots_on_target_pct DECIMAL(5,2),

    -- Progressive carries
    progressive_carries INTEGER,

    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(match_id, team_id)
);

-- Fact: Player match performance
CREATE TABLE IF NOT EXISTS gold.fact_player_match_performance (
    player_match_id SERIAL PRIMARY KEY,
    match_id VARCHAR(50) NOT NULL REFERENCES gold.dim_match(match_id),
    player_id INTEGER NOT NULL REFERENCES gold.dim_player(player_id),
    team_id INTEGER NOT NULL REFERENCES gold.dim_team(team_id),

    -- Playing time
    minutes_played INTEGER,
    started BOOLEAN,
    position VARCHAR(20),

    -- Basic stats
    goals INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0,
    shots INTEGER DEFAULT 0,
    shots_on_target INTEGER DEFAULT 0,

    -- Expected goals
    xg DECIMAL(5,2),
    npxg DECIMAL(5,2),
    xa DECIMAL(5,2),
    xag DECIMAL(5,2), -- xG assisted (sum of xG from shots assisted)
    npxg_plus_xa DECIMAL(5,2),

    -- Passing
    passes_completed INTEGER,
    passes_attempted INTEGER,
    pass_completion_pct DECIMAL(5,2),
    progressive_passes INTEGER,
    key_passes INTEGER,
    passes_into_final_third INTEGER,
    passes_into_penalty_area INTEGER,

    -- Progressive actions
    progressive_carries INTEGER,
    carries_into_final_third INTEGER,
    carries_into_penalty_area INTEGER,

    -- Dribbling
    dribbles_completed INTEGER,
    dribbles_attempted INTEGER,
    dribbles_success_pct DECIMAL(5,2),

    -- Shot/Goal creating actions
    sca INTEGER, -- Shot-creating actions
    gca INTEGER, -- Goal-creating actions

    -- Defensive
    tackles INTEGER,
    interceptions INTEGER,
    blocks INTEGER,
    clearances INTEGER,

    -- Possession
    touches INTEGER,

    -- Game state metrics (minutes played in each state)
    minutes_leading INTEGER DEFAULT 0,
    minutes_drawing INTEGER DEFAULT 0,
    minutes_trailing INTEGER DEFAULT 0,

    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(match_id, player_id)
);

-- Fact: Match events (granular event-level data)
CREATE TABLE IF NOT EXISTS gold.fact_match_events (
    event_id SERIAL PRIMARY KEY,
    match_id VARCHAR(50) NOT NULL REFERENCES gold.dim_match(match_id),
    player_id INTEGER REFERENCES gold.dim_player(player_id),
    team_id INTEGER NOT NULL REFERENCES gold.dim_team(team_id),

    -- Event details
    event_type VARCHAR(50) NOT NULL, -- 'shot', 'pass', 'dribble', 'tackle', etc.
    minute INTEGER NOT NULL,
    second INTEGER,

    -- Position on pitch (normalized 0-1)
    x_coord DECIMAL(5,2),
    y_coord DECIMAL(5,2),

    -- Event outcome
    outcome VARCHAR(20), -- 'success', 'fail', 'goal', 'saved', etc.

    -- Event-specific metrics
    xg_value DECIMAL(5,4), -- For shots
    xt_value DECIMAL(5,4), -- For passes and carries

    -- Additional context
    result_type VARCHAR(50), -- Shot result: 'Goal', 'SavedShot', etc.
    situation VARCHAR(50), -- Shot situation: 'OpenPlay', 'SetPiece', etc.
    shot_type VARCHAR(50), -- 'RightFoot', 'LeftFoot', 'Head'
    assist_type VARCHAR(50), -- 'Pass', 'Cross', 'Throughball'

    -- Game state at time of event
    score_diff INTEGER, -- Team's score minus opponent's score at this moment
    game_state_id INTEGER REFERENCES gold.dim_game_state(game_state_id),

    -- Metadata
    source_system VARCHAR(20), -- 'fbref', 'understat'
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Ensure uniqueness for shots (can have multiple events per minute)
    UNIQUE(match_id, player_id, event_type, minute, x_coord, y_coord)
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

-- dim_match indexes
CREATE INDEX IF NOT EXISTS idx_dim_match_season ON gold.dim_match(season_id);
CREATE INDEX IF NOT EXISTS idx_dim_match_competition ON gold.dim_match(competition_id);
CREATE INDEX IF NOT EXISTS idx_dim_match_date ON gold.dim_match(match_date DESC);
CREATE INDEX IF NOT EXISTS idx_dim_match_home_team ON gold.dim_match(home_team_id);
CREATE INDEX IF NOT EXISTS idx_dim_match_away_team ON gold.dim_match(away_team_id);

-- fact_team_match_performance indexes
CREATE INDEX IF NOT EXISTS idx_fact_team_match_match ON gold.fact_team_match_performance(match_id);
CREATE INDEX IF NOT EXISTS idx_fact_team_match_team ON gold.fact_team_match_performance(team_id);

-- fact_player_match_performance indexes
CREATE INDEX IF NOT EXISTS idx_fact_player_match_match ON gold.fact_player_match_performance(match_id);
CREATE INDEX IF NOT EXISTS idx_fact_player_match_player ON gold.fact_player_match_performance(player_id);
CREATE INDEX IF NOT EXISTS idx_fact_player_match_team ON gold.fact_player_match_performance(team_id);

-- fact_match_events indexes
CREATE INDEX IF NOT EXISTS idx_fact_events_match ON gold.fact_match_events(match_id);
CREATE INDEX IF NOT EXISTS idx_fact_events_player ON gold.fact_match_events(player_id);
CREATE INDEX IF NOT EXISTS idx_fact_events_team ON gold.fact_match_events(team_id);
CREATE INDEX IF NOT EXISTS idx_fact_events_type ON gold.fact_match_events(event_type);
CREATE INDEX IF NOT EXISTS idx_fact_events_minute ON gold.fact_match_events(match_id, minute);

-- ============================================
-- GRANT PERMISSIONS
-- ============================================

GRANT ALL ON ALL TABLES IN SCHEMA gold TO analytics_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA gold TO analytics_user;
