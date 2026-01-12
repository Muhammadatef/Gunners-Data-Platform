-- Metrics Layer: Computed analytics and aggregated metrics
-- Pre-computed tables for dashboard performance

\c arsenalfc_analytics

-- Rolling xG metrics per player
CREATE TABLE IF NOT EXISTS metrics.player_rolling_xg (
    player_rolling_id SERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL REFERENCES gold.dim_player(player_id),
    season_id INTEGER NOT NULL REFERENCES gold.dim_season(season_id),
    competition_id INTEGER REFERENCES gold.dim_competition(competition_id),

    -- Rolling window end (last match in window)
    last_match_date DATE NOT NULL,
    window_size INTEGER NOT NULL, -- 5, 10, etc.

    -- Matches in window
    matches_played INTEGER,
    minutes_played INTEGER,

    -- Rolling xG metrics
    rolling_xg DECIMAL(6,2),
    rolling_npxg DECIMAL(6,2),
    rolling_xa DECIMAL(6,2),
    rolling_goals INTEGER,
    rolling_assists INTEGER,

    -- Per 90 minutes
    xg_per_90 DECIMAL(5,2),
    npxg_per_90 DECIMAL(5,2),
    xa_per_90 DECIMAL(5,2),
    goals_per_90 DECIMAL(5,2),
    assists_per_90 DECIMAL(5,2),

    -- Computed at
    computed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(player_id, season_id, last_match_date, window_size, competition_id)
);

-- Match xG flow (minute-by-minute cumulative xG)
CREATE TABLE IF NOT EXISTS metrics.match_xg_flow (
    flow_id SERIAL PRIMARY KEY,
    match_id VARCHAR(50) NOT NULL REFERENCES gold.dim_match(match_id),
    minute INTEGER NOT NULL,

    -- Cumulative xG for each team
    home_cumulative_xg DECIMAL(5,2),
    away_cumulative_xg DECIMAL(5,2),

    -- Score at this minute
    home_score INTEGER,
    away_score INTEGER,

    -- Number of shots in this minute
    home_shots INTEGER DEFAULT 0,
    away_shots INTEGER DEFAULT 0,

    computed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(match_id, minute)
);

-- Team game state metrics
CREATE TABLE IF NOT EXISTS metrics.team_game_state_metrics (
    team_game_state_id SERIAL PRIMARY KEY,
    team_id INTEGER NOT NULL REFERENCES gold.dim_team(team_id),
    season_id INTEGER NOT NULL REFERENCES gold.dim_season(season_id),
    game_state_id INTEGER NOT NULL REFERENCES gold.dim_game_state(game_state_id),
    competition_id INTEGER REFERENCES gold.dim_competition(competition_id),

    -- Time spent in state
    total_minutes INTEGER,

    -- Performance in state
    shots INTEGER,
    shots_on_target INTEGER,
    xg DECIMAL(6,2),
    goals INTEGER,

    -- Passing in state
    passes_completed INTEGER,
    passes_attempted INTEGER,
    pass_completion_pct DECIMAL(5,2),
    progressive_passes INTEGER,

    -- Per 90 in state
    shots_per_90 DECIMAL(5,2),
    xg_per_90 DECIMAL(5,2),
    goals_per_90 DECIMAL(5,2),

    computed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(team_id, season_id, game_state_id, competition_id)
);

-- Season team performance summary
CREATE TABLE IF NOT EXISTS metrics.season_team_summary (
    summary_id SERIAL PRIMARY KEY,
    team_id INTEGER NOT NULL REFERENCES gold.dim_team(team_id),
    season_id INTEGER NOT NULL REFERENCES gold.dim_season(season_id),
    competition_id INTEGER REFERENCES gold.dim_competition(competition_id),

    -- Matches
    matches_played INTEGER,
    wins INTEGER,
    draws INTEGER,
    losses INTEGER,
    points INTEGER,

    -- Goals
    goals_for INTEGER,
    goals_against INTEGER,
    goal_difference INTEGER,

    -- Expected goals
    xg_for DECIMAL(6,2),
    xg_against DECIMAL(6,2),
    xg_difference DECIMAL(6,2),

    -- Over/underperformance
    goals_vs_xg DECIMAL(6,2), -- goals_for - xg_for
    goals_conceded_vs_xga DECIMAL(6,2), -- goals_against - xg_against

    -- Per match averages
    xg_per_match DECIMAL(5,2),
    xga_per_match DECIMAL(5,2),
    possession_avg DECIMAL(5,2),

    -- Home vs Away
    home_matches INTEGER,
    home_wins INTEGER,
    home_xg DECIMAL(6,2),
    away_matches INTEGER,
    away_wins INTEGER,
    away_xg DECIMAL(6,2),

    -- Last updated
    last_match_date DATE,
    computed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(team_id, season_id, competition_id)
);

-- Player season performance summary
CREATE TABLE IF NOT EXISTS metrics.season_player_summary (
    summary_id SERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL REFERENCES gold.dim_player(player_id),
    team_id INTEGER NOT NULL REFERENCES gold.dim_team(team_id),
    season_id INTEGER NOT NULL REFERENCES gold.dim_season(season_id),
    competition_id INTEGER REFERENCES gold.dim_competition(competition_id),

    -- Matches and time
    matches_played INTEGER,
    matches_started INTEGER,
    minutes_played INTEGER,

    -- Goals and assists
    goals INTEGER,
    assists INTEGER,
    xg DECIMAL(6,2),
    xa DECIMAL(6,2),
    xag DECIMAL(6,2),

    -- Per 90
    goals_per_90 DECIMAL(5,2),
    assists_per_90 DECIMAL(5,2),
    xg_per_90 DECIMAL(5,2),
    xa_per_90 DECIMAL(5,2),

    -- Finishing
    goals_vs_xg DECIMAL(5,2), -- goals - xg
    conversion_rate DECIMAL(5,2), -- goals / shots * 100

    -- Creativity
    key_passes INTEGER,
    key_passes_per_90 DECIMAL(5,2),
    sca INTEGER,
    sca_per_90 DECIMAL(5,2),

    -- Progressive actions
    progressive_passes INTEGER,
    progressive_carries INTEGER,
    progressive_actions_per_90 DECIMAL(5,2),

    -- Dribbling
    dribbles_completed INTEGER,
    dribbles_success_pct DECIMAL(5,2),

    -- Last updated
    last_match_date DATE,
    computed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(player_id, team_id, season_id, competition_id)
);

-- Expected Threat (xT) grid
-- Pre-computed probability of scoring from each pitch zone
CREATE TABLE IF NOT EXISTS metrics.xt_grid (
    grid_id SERIAL PRIMARY KEY,
    x_bin INTEGER NOT NULL, -- 0-11 (12 columns)
    y_bin INTEGER NOT NULL, -- 0-7 (8 rows)

    -- Probabilities
    move_to_shot_prob DECIMAL(6,4), -- Probability of taking shot from this zone
    shot_to_goal_prob DECIMAL(6,4), -- Probability shot from this zone scores
    xt_value DECIMAL(6,4), -- Expected threat value

    -- Computed from
    season_id INTEGER REFERENCES gold.dim_season(season_id),
    competition_id INTEGER REFERENCES gold.dim_competition(competition_id),

    computed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(x_bin, y_bin, season_id, competition_id)
);

-- ============================================
-- INDEXES
-- ============================================

CREATE INDEX IF NOT EXISTS idx_player_rolling_xg_player ON metrics.player_rolling_xg(player_id);
CREATE INDEX IF NOT EXISTS idx_player_rolling_xg_season ON metrics.player_rolling_xg(season_id);
CREATE INDEX IF NOT EXISTS idx_match_xg_flow_match ON metrics.match_xg_flow(match_id);
CREATE INDEX IF NOT EXISTS idx_team_game_state_team ON metrics.team_game_state_metrics(team_id);
CREATE INDEX IF NOT EXISTS idx_team_game_state_season ON metrics.team_game_state_metrics(season_id);
CREATE INDEX IF NOT EXISTS idx_season_team_summary_team ON metrics.season_team_summary(team_id);
CREATE INDEX IF NOT EXISTS idx_season_team_summary_season ON metrics.season_team_summary(season_id);
CREATE INDEX IF NOT EXISTS idx_season_player_summary_player ON metrics.season_player_summary(player_id);
CREATE INDEX IF NOT EXISTS idx_season_player_summary_season ON metrics.season_player_summary(season_id);
CREATE INDEX IF NOT EXISTS idx_xt_grid_coords ON metrics.xt_grid(x_bin, y_bin);

-- ============================================
-- GRANT PERMISSIONS
-- ============================================

GRANT ALL ON ALL TABLES IN SCHEMA metrics TO analytics_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA metrics TO analytics_user;
