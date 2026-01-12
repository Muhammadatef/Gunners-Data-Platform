-- Arsenal FC Analytics Platform - Create comprehensive SQL views
-- These views join raw data with match metadata for dashboard consumption

\c arsenalfc_analytics

-- ============================================================================
-- SILVER LAYER: Cleaned and structured shot-level data
-- ============================================================================

CREATE OR REPLACE VIEW silver.shot_events AS
WITH lineup_positions AS (
    -- Flatten FBref lineups to get player positions
    SELECT
        l.match_url,
        lineup_player->>'player_name' AS player_name,
        lineup_player->>'position' AS position,
        lineup_player->>'position_category' AS position_category,
        lineup_player->>'team_side' AS team_side
    FROM bronze.fbref_lineups l,
    jsonb_array_elements(
        COALESCE(l.raw_lineups->'home_lineup', '[]'::jsonb) ||
        COALESCE(l.raw_lineups->'away_lineup', '[]'::jsonb)
    ) AS lineup_player
)
SELECT
    r.match_id,
    r.match_url,
    ref.match_date,
    ref.home_team,
    ref.away_team,
    ref.season,

    -- Match xG totals from raw_shots JSON
    (r.raw_shots->>'home_xg')::DECIMAL(5,2) AS home_xg,
    (r.raw_shots->>'away_xg')::DECIMAL(5,2) AS away_xg,
    (r.raw_shots->>'home_goals')::INTEGER AS home_goals,
    (r.raw_shots->>'away_goals')::INTEGER AS away_goals,

    -- Shot-level details
    shot->>'player_name' AS player_name,
    shot->>'player_id' AS player_id,
    shot->>'h_a' AS home_away,
    CASE
        WHEN shot->>'h_a' = 'h' THEN ref.home_team
        ELSE ref.away_team
    END AS team,

    -- Player position from FBref (if available)
    pos.position,
    pos.position_category,

    COALESCE((shot->>'minute')::INTEGER, 0) AS minute,
    shot->>'result' AS result,
    shot->>'situation' AS situation,
    shot->>'shot_type' AS shot_type,

    COALESCE((shot->>'x_coord')::DECIMAL(5,2), 0) AS x_coord,
    COALESCE((shot->>'y_coord')::DECIMAL(5,2), 0) AS y_coord,
    COALESCE((shot->>'xg')::DECIMAL(5,4), 0) AS xg,

    shot->>'assisted_by' AS assisted_by,
    shot->>'last_action' AS last_action,

    r.scraped_at
FROM bronze.understat_raw r
INNER JOIN bronze.match_reference ref ON r.match_url = ref.match_url
CROSS JOIN jsonb_array_elements(r.raw_shots->'shots') AS shot
LEFT JOIN lineup_positions pos ON (
    r.match_url = pos.match_url
    AND shot->>'player_name' = pos.player_name
    AND CASE WHEN shot->>'h_a' = 'h' THEN 'home' ELSE 'away' END = pos.team_side
)
WHERE shot->>'player_name' IS NOT NULL;


-- ============================================================================
-- METRICS LAYER: Arsenal-specific aggregations and match summaries
-- ============================================================================

-- Arsenal match results with xG performance
CREATE OR REPLACE VIEW metrics.arsenal_matches AS
WITH match_base AS (
    SELECT DISTINCT
        ref.match_url,
        ref.match_date,
        ref.home_team,
        ref.away_team,
        ref.season,

        (r.raw_shots->>'home_goals')::INTEGER AS home_goals,
        (r.raw_shots->>'away_goals')::INTEGER AS away_goals,
        (r.raw_shots->>'home_xg')::DECIMAL(5,2) AS home_xg,
        (r.raw_shots->>'away_xg')::DECIMAL(5,2) AS away_xg,

        -- Arsenal-specific columns
        CASE
            WHEN ref.home_team = 'Arsenal' THEN 'H'
            WHEN ref.away_team = 'Arsenal' THEN 'A'
        END AS venue,

        CASE
            WHEN ref.home_team = 'Arsenal' THEN ref.away_team
            ELSE ref.home_team
        END AS opponent

    FROM bronze.understat_raw r
    INNER JOIN bronze.match_reference ref ON r.match_url = ref.match_url
    WHERE ref.home_team = 'Arsenal' OR ref.away_team = 'Arsenal'
)
SELECT
    match_url,
    match_date,
    season,
    opponent,
    venue,

    -- Arsenal stats
    CASE WHEN venue = 'H' THEN home_goals ELSE away_goals END AS arsenal_goals,
    CASE WHEN venue = 'A' THEN home_goals ELSE away_goals END AS opponent_goals,

    CASE WHEN venue = 'H' THEN home_xg ELSE away_xg END AS arsenal_xg,
    CASE WHEN venue = 'A' THEN home_xg ELSE away_xg END AS opponent_xg,

    -- Match result
    CASE
        WHEN (venue = 'H' AND home_goals > away_goals) OR (venue = 'A' AND away_goals > home_goals) THEN 'W'
        WHEN home_goals = away_goals THEN 'D'
        ELSE 'L'
    END AS result,

    -- xG performance (actual goals minus expected)
    CASE
        WHEN venue = 'H' THEN (home_goals - home_xg)
        ELSE (away_goals - away_xg)
    END AS xg_overperformance

FROM match_base
ORDER BY match_date DESC;


-- Arsenal player statistics
CREATE OR REPLACE VIEW metrics.arsenal_player_stats AS
SELECT
    player_name,
    season,

    COUNT(*) FILTER (WHERE result = 'Goal') AS goals,
    COUNT(*) AS shots,
    SUM(xg) AS total_xg,

    ROUND(COUNT(*) FILTER (WHERE result = 'Goal')::DECIMAL / NULLIF(COUNT(*), 0), 3) AS conversion_rate,
    ROUND(SUM(xg)::DECIMAL / NULLIF(COUNT(*), 0), 3) AS avg_xg_per_shot,
    ROUND((COUNT(*) FILTER (WHERE result = 'Goal') - SUM(xg)), 2) AS xg_overperformance,

    COUNT(*) FILTER (WHERE situation = 'OpenPlay') AS open_play_shots,
    COUNT(*) FILTER (WHERE situation = 'FromCorner') AS from_corner,
    COUNT(*) FILTER (WHERE situation = 'SetPiece') AS set_piece,
    COUNT(*) FILTER (WHERE situation = 'Penalty') AS penalties,

    COUNT(*) FILTER (WHERE shot_type = 'RightFoot') AS right_foot,
    COUNT(*) FILTER (WHERE shot_type = 'LeftFoot') AS left_foot,
    COUNT(*) FILTER (WHERE shot_type = 'Head') AS headers,
    COUNT(*) FILTER (WHERE shot_type = 'OtherBodyPart') AS other,

    COUNT(DISTINCT match_url) AS matches_played

FROM silver.shot_events
WHERE team = 'Arsenal'
GROUP BY player_name, season
HAVING COUNT(*) >= 3  -- Minimum 3 shots
ORDER BY season DESC, goals DESC, total_xg DESC;


-- Season summary statistics for Arsenal
CREATE OR REPLACE VIEW metrics.season_summary AS
SELECT
    season,

    -- Match record
    COUNT(*) AS matches_played,
    COUNT(*) FILTER (WHERE result = 'W') AS wins,
    COUNT(*) FILTER (WHERE result = 'D') AS draws,
    COUNT(*) FILTER (WHERE result = 'L') AS losses,

    -- Goals
    SUM(arsenal_goals) AS goals_for,
    SUM(opponent_goals) AS goals_against,
    SUM(arsenal_goals) - SUM(opponent_goals) AS goal_difference,

    -- xG stats
    ROUND(SUM(arsenal_xg), 2) AS total_xg_for,
    ROUND(SUM(opponent_xg), 2) AS total_xg_against,
    ROUND(AVG(arsenal_xg), 2) AS avg_xg_per_match,
    ROUND(SUM(xg_overperformance), 2) AS total_xg_overperformance,

    -- Home/Away split
    COUNT(*) FILTER (WHERE venue = 'H') AS home_matches,
    COUNT(*) FILTER (WHERE venue = 'A') AS away_matches,
    COUNT(*) FILTER (WHERE venue = 'H' AND result = 'W') AS home_wins,
    COUNT(*) FILTER (WHERE venue = 'A' AND result = 'W') AS away_wins,

    -- Points (W=3, D=1, L=0)
    (COUNT(*) FILTER (WHERE result = 'W') * 3 + COUNT(*) FILTER (WHERE result = 'D')) AS points

FROM metrics.arsenal_matches
GROUP BY season
ORDER BY season DESC;


-- ============================================================================
-- ADVANCED METRICS: Deeper tactical and performance analysis
-- ============================================================================

-- Match-level advanced statistics
CREATE OR REPLACE VIEW metrics.match_advanced_stats AS
SELECT
    m.match_url,
    m.match_date,
    m.season,
    m.opponent,
    m.venue,
    m.result,
    m.arsenal_goals,
    m.opponent_goals,
    m.arsenal_xg,
    m.opponent_xg,

    -- Shot volumes
    COUNT(*) FILTER (WHERE s.team = 'Arsenal') AS arsenal_shots,
    COUNT(*) FILTER (WHERE s.team != 'Arsenal') AS opponent_shots,

    -- Shot accuracy
    COUNT(*) FILTER (WHERE s.team = 'Arsenal' AND s.result IN ('Goal', 'SavedShot')) AS arsenal_shots_on_target,
    COUNT(*) FILTER (WHERE s.team != 'Arsenal' AND s.result IN ('Goal', 'SavedShot')) AS opponent_shots_on_target,
    ROUND(COUNT(*) FILTER (WHERE s.team = 'Arsenal' AND s.result IN ('Goal', 'SavedShot'))::DECIMAL /
          NULLIF(COUNT(*) FILTER (WHERE s.team = 'Arsenal'), 0) * 100, 1) AS arsenal_shot_accuracy_pct,

    -- Big chances (xG > 0.3)
    COUNT(*) FILTER (WHERE s.team = 'Arsenal' AND s.xg > 0.3) AS arsenal_big_chances,
    COUNT(*) FILTER (WHERE s.team = 'Arsenal' AND s.xg > 0.3 AND s.result = 'Goal') AS arsenal_big_chances_scored,
    COUNT(*) FILTER (WHERE s.team != 'Arsenal' AND s.xg > 0.3) AS opponent_big_chances,

    -- Shot locations
    COUNT(*) FILTER (WHERE s.team = 'Arsenal' AND s.x_coord >= 0.83) AS arsenal_box_shots,
    COUNT(*) FILTER (WHERE s.team = 'Arsenal' AND s.x_coord < 0.83) AS arsenal_outside_box_shots,

    -- Shot situations
    COUNT(*) FILTER (WHERE s.team = 'Arsenal' AND s.situation = 'OpenPlay') AS arsenal_open_play_shots,
    COUNT(*) FILTER (WHERE s.team = 'Arsenal' AND s.situation = 'FromCorner') AS arsenal_corner_shots,
    COUNT(*) FILTER (WHERE s.team = 'Arsenal' AND s.situation = 'SetPiece') AS arsenal_set_piece_shots,
    COUNT(*) FILTER (WHERE s.team = 'Arsenal' AND s.situation = 'Penalty') AS arsenal_penalties,

    -- First vs second half
    COUNT(*) FILTER (WHERE s.team = 'Arsenal' AND s.minute <= 45) AS arsenal_first_half_shots,
    SUM(s.xg) FILTER (WHERE s.team = 'Arsenal' AND s.minute <= 45) AS arsenal_first_half_xg,
    COUNT(*) FILTER (WHERE s.team = 'Arsenal' AND s.minute > 45) AS arsenal_second_half_shots,
    SUM(s.xg) FILTER (WHERE s.team = 'Arsenal' AND s.minute > 45) AS arsenal_second_half_xg,

    -- Average shot quality
    ROUND(AVG(s.xg) FILTER (WHERE s.team = 'Arsenal'), 3) AS arsenal_avg_shot_xg,
    ROUND(AVG(s.xg) FILTER (WHERE s.team != 'Arsenal'), 3) AS opponent_avg_shot_xg

FROM metrics.arsenal_matches m
LEFT JOIN silver.shot_events s ON m.match_url = s.match_url
GROUP BY m.match_url, m.match_date, m.season, m.opponent, m.venue, m.result,
         m.arsenal_goals, m.opponent_goals, m.arsenal_xg, m.opponent_xg
ORDER BY m.match_date DESC;


-- Player advanced statistics with shot placement and efficiency
CREATE OR REPLACE VIEW metrics.player_advanced_stats AS
WITH player_matches AS (
    SELECT
        player_name,
        season,
        COUNT(DISTINCT match_url) as matches_played
    FROM silver.shot_events
    WHERE team = 'Arsenal'
    GROUP BY player_name, season
),
player_assists AS (
    SELECT
        assisted_by as player_name,
        season,
        COUNT(DISTINCT match_url || '-' || minute) as assists
    FROM silver.shot_events
    WHERE team = 'Arsenal' AND assisted_by IS NOT NULL
    GROUP BY assisted_by, season
)
SELECT
    s.player_name,
    s.season,
    pm.matches_played,

    -- Basic stats
    COUNT(*) AS total_shots,
    COUNT(*) FILTER (WHERE s.result = 'Goal') AS goals,
    ROUND(SUM(s.xg), 2) AS total_xg,
    ROUND(AVG(s.xg), 3) AS avg_xg_per_shot,
    ROUND(COUNT(*) FILTER (WHERE s.result = 'Goal')::DECIMAL / NULLIF(COUNT(*), 0) * 100, 1) AS conversion_pct,

    -- Shot accuracy and outcomes
    COUNT(*) FILTER (WHERE s.result IN ('Goal', 'SavedShot')) AS shots_on_target,
    ROUND(COUNT(*) FILTER (WHERE s.result IN ('Goal', 'SavedShot'))::DECIMAL / NULLIF(COUNT(*), 0) * 100, 1) AS shot_accuracy_pct,
    COUNT(*) FILTER (WHERE s.result = 'MissedShots') AS missed_shots,
    COUNT(*) FILTER (WHERE s.result = 'BlockedShot') AS blocked_shots,
    COUNT(*) FILTER (WHERE s.result = 'SavedShot') AS saved_shots,

    -- Big chances
    COUNT(*) FILTER (WHERE s.xg > 0.3) AS big_chances,
    COUNT(*) FILTER (WHERE s.xg > 0.3 AND s.result = 'Goal') AS big_chances_scored,
    ROUND(COUNT(*) FILTER (WHERE s.xg > 0.3 AND s.result = 'Goal')::DECIMAL /
          NULLIF(COUNT(*) FILTER (WHERE s.xg > 0.3), 0) * 100, 1) AS big_chance_conversion_pct,

    -- Shot locations
    COUNT(*) FILTER (WHERE s.x_coord >= 0.83) AS box_shots,
    COUNT(*) FILTER (WHERE s.x_coord < 0.83) AS outside_box_shots,
    ROUND(AVG(s.x_coord), 3) AS avg_shot_distance,

    -- Shot types efficiency
    COUNT(*) FILTER (WHERE s.shot_type = 'RightFoot') AS right_foot_shots,
    COUNT(*) FILTER (WHERE s.shot_type = 'RightFoot' AND s.result = 'Goal') AS right_foot_goals,
    COUNT(*) FILTER (WHERE s.shot_type = 'LeftFoot') AS left_foot_shots,
    COUNT(*) FILTER (WHERE s.shot_type = 'LeftFoot' AND s.result = 'Goal') AS left_foot_goals,
    COUNT(*) FILTER (WHERE s.shot_type = 'Head') AS headers,
    COUNT(*) FILTER (WHERE s.shot_type = 'Head' AND s.result = 'Goal') AS header_goals,

    -- Situations
    COUNT(*) FILTER (WHERE s.situation = 'OpenPlay') AS open_play_shots,
    COUNT(*) FILTER (WHERE s.situation = 'OpenPlay' AND s.result = 'Goal') AS open_play_goals,
    COUNT(*) FILTER (WHERE s.situation = 'FromCorner') AS corner_shots,
    COUNT(*) FILTER (WHERE s.situation = 'SetPiece') AS set_piece_shots,
    COUNT(*) FILTER (WHERE s.situation = 'Penalty') AS penalties_taken,
    COUNT(*) FILTER (WHERE s.situation = 'Penalty' AND s.result = 'Goal') AS penalties_scored,

    -- Assists given
    COALESCE(pa.assists, 0) AS assists,

    -- xG overperformance
    ROUND((COUNT(*) FILTER (WHERE s.result = 'Goal') - SUM(s.xg)), 2) AS xg_overperformance,

    -- Per 90 metrics (normalized)
    ROUND(COUNT(*)::DECIMAL / NULLIF(pm.matches_played, 0), 2) AS shots_per_match,
    ROUND(COUNT(*) FILTER (WHERE s.result = 'Goal')::DECIMAL / NULLIF(pm.matches_played, 0), 2) AS goals_per_match,
    ROUND(SUM(s.xg)::DECIMAL / NULLIF(pm.matches_played, 0), 2) AS xg_per_match

FROM silver.shot_events s
INNER JOIN player_matches pm ON s.player_name = pm.player_name AND s.season = pm.season
LEFT JOIN player_assists pa ON s.player_name = pa.player_name AND s.season = pa.season
WHERE s.team = 'Arsenal'
GROUP BY s.player_name, s.season, pm.matches_played, pa.assists
HAVING COUNT(*) >= 3
ORDER BY s.season DESC, total_xg DESC;


-- Opponent analysis and head-to-head records
CREATE OR REPLACE VIEW metrics.opponent_comparison AS
SELECT
    opponent,

    -- Match record
    COUNT(*) AS matches_played,
    COUNT(*) FILTER (WHERE result = 'W') AS wins,
    COUNT(*) FILTER (WHERE result = 'D') AS draws,
    COUNT(*) FILTER (WHERE result = 'L') AS losses,
    ROUND(COUNT(*) FILTER (WHERE result = 'W')::DECIMAL / NULLIF(COUNT(*), 0) * 100, 1) AS win_rate_pct,

    -- Goals
    SUM(arsenal_goals) AS goals_for,
    SUM(opponent_goals) AS goals_against,
    ROUND(AVG(arsenal_goals), 2) AS avg_goals_for,
    ROUND(AVG(opponent_goals), 2) AS avg_goals_against,

    -- xG stats
    ROUND(SUM(arsenal_xg), 2) AS total_xg_for,
    ROUND(SUM(opponent_xg), 2) AS total_xg_against,
    ROUND(AVG(arsenal_xg), 2) AS avg_xg_for,
    ROUND(AVG(opponent_xg), 2) AS avg_xg_against,

    -- Clean sheets and scoring
    COUNT(*) FILTER (WHERE opponent_goals = 0) AS clean_sheets,
    COUNT(*) FILTER (WHERE arsenal_goals = 0) AS failed_to_score,

    -- Most recent result
    MAX(match_date) AS last_played,
    (ARRAY_AGG(result ORDER BY match_date DESC))[1] AS last_result

FROM metrics.arsenal_matches
GROUP BY opponent
HAVING COUNT(*) >= 1
ORDER BY matches_played DESC, win_rate_pct DESC;


-- Tactical analysis with shot timing and build-up patterns
CREATE OR REPLACE VIEW metrics.tactical_analysis AS
SELECT
    season,

    -- Shot timing by period (15-min intervals)
    COUNT(*) FILTER (WHERE minute BETWEEN 0 AND 15 AND team = 'Arsenal') AS arsenal_shots_0_15,
    COUNT(*) FILTER (WHERE minute BETWEEN 16 AND 30 AND team = 'Arsenal') AS arsenal_shots_16_30,
    COUNT(*) FILTER (WHERE minute BETWEEN 31 AND 45 AND team = 'Arsenal') AS arsenal_shots_31_45,
    COUNT(*) FILTER (WHERE minute BETWEEN 46 AND 60 AND team = 'Arsenal') AS arsenal_shots_46_60,
    COUNT(*) FILTER (WHERE minute BETWEEN 61 AND 75 AND team = 'Arsenal') AS arsenal_shots_61_75,
    COUNT(*) FILTER (WHERE minute BETWEEN 76 AND 90 AND team = 'Arsenal') AS arsenal_shots_76_90,

    -- Goals by period
    COUNT(*) FILTER (WHERE minute BETWEEN 0 AND 15 AND team = 'Arsenal' AND result = 'Goal') AS arsenal_goals_0_15,
    COUNT(*) FILTER (WHERE minute BETWEEN 16 AND 30 AND team = 'Arsenal' AND result = 'Goal') AS arsenal_goals_16_30,
    COUNT(*) FILTER (WHERE minute BETWEEN 31 AND 45 AND team = 'Arsenal' AND result = 'Goal') AS arsenal_goals_31_45,
    COUNT(*) FILTER (WHERE minute BETWEEN 46 AND 60 AND team = 'Arsenal' AND result = 'Goal') AS arsenal_goals_46_60,
    COUNT(*) FILTER (WHERE minute BETWEEN 61 AND 75 AND team = 'Arsenal' AND result = 'Goal') AS arsenal_goals_61_75,
    COUNT(*) FILTER (WHERE minute BETWEEN 76 AND 90 AND team = 'Arsenal' AND result = 'Goal') AS arsenal_goals_76_90,

    -- Build-up patterns (last action before shot)
    COUNT(*) FILTER (WHERE last_action = 'Pass' AND team = 'Arsenal') AS shots_from_pass,
    COUNT(*) FILTER (WHERE last_action = 'Dribble' AND team = 'Arsenal') AS shots_from_dribble,
    COUNT(*) FILTER (WHERE last_action = 'Rebound' AND team = 'Arsenal') AS shots_from_rebound,
    COUNT(*) FILTER (WHERE last_action = 'Chipped' AND team = 'Arsenal') AS shots_from_chip,
    COUNT(*) FILTER (WHERE last_action = 'Cross' AND team = 'Arsenal') AS shots_from_cross,

    -- Shot situation effectiveness
    COUNT(*) FILTER (WHERE situation = 'OpenPlay' AND team = 'Arsenal') AS open_play_total,
    COUNT(*) FILTER (WHERE situation = 'OpenPlay' AND team = 'Arsenal' AND result = 'Goal') AS open_play_goals,
    ROUND(SUM(xg) FILTER (WHERE situation = 'OpenPlay' AND team = 'Arsenal'), 2) AS open_play_xg,

    COUNT(*) FILTER (WHERE situation = 'FromCorner' AND team = 'Arsenal') AS corner_total,
    COUNT(*) FILTER (WHERE situation = 'FromCorner' AND team = 'Arsenal' AND result = 'Goal') AS corner_goals,
    ROUND(SUM(xg) FILTER (WHERE situation = 'FromCorner' AND team = 'Arsenal'), 2) AS corner_xg,

    COUNT(*) FILTER (WHERE situation = 'SetPiece' AND team = 'Arsenal') AS set_piece_total,
    COUNT(*) FILTER (WHERE situation = 'SetPiece' AND team = 'Arsenal' AND result = 'Goal') AS set_piece_goals,
    ROUND(SUM(xg) FILTER (WHERE situation = 'SetPiece' AND team = 'Arsenal'), 2) AS set_piece_xg,

    COUNT(*) FILTER (WHERE situation = 'Penalty' AND team = 'Arsenal') AS penalty_total,
    COUNT(*) FILTER (WHERE situation = 'Penalty' AND team = 'Arsenal' AND result = 'Goal') AS penalty_goals,

    -- High-quality chance creation (xG > 0.3)
    COUNT(*) FILTER (WHERE xg > 0.3 AND team = 'Arsenal') AS big_chances_created,
    COUNT(*) FILTER (WHERE xg > 0.3 AND team = 'Arsenal' AND result = 'Goal') AS big_chances_converted

FROM silver.shot_events
GROUP BY season
ORDER BY season DESC;


-- ============================================================================
-- PLAYER INVOLVEMENT NETWORKS (Phase 4)
-- ============================================================================

-- Shot involvement connections (assister → scorer)
CREATE OR REPLACE VIEW metrics.shot_involvement_network AS
SELECT
    s.match_url,
    s.match_date,
    s.season,
    s.home_team || ' vs ' || s.away_team AS match_name,

    -- Network edge: from assister to scorer
    s.assisted_by AS from_player,
    s.player_name AS to_player,

    -- Player positions
    pos_from.position_category AS from_position,
    pos_to.position_category AS to_position,

    -- Shot outcome
    s.result,
    s.xg,

    -- Shot details
    s.minute,
    s.situation,
    s.shot_type

FROM silver.shot_events s
LEFT JOIN LATERAL (
    SELECT position_category
    FROM silver.shot_events s2
    WHERE s2.match_url = s.match_url
      AND s2.player_name = s.assisted_by
    LIMIT 1
) pos_from ON true
LEFT JOIN LATERAL (
    SELECT s.position_category
) pos_to ON true
WHERE s.assisted_by IS NOT NULL
  AND s.assisted_by != ''
  AND s.team = 'Arsenal';


-- Aggregated involvement network stats (season-level)
CREATE OR REPLACE VIEW metrics.involvement_network_stats AS
SELECT
    from_player,
    to_player,
    from_position,
    to_position,
    season,

    -- Connection strength
    COUNT(*) AS total_connections,
    COUNT(*) FILTER (WHERE result = 'Goal') AS goals_created,
    ROUND(SUM(xg), 2) AS total_xg_created,
    ROUND(AVG(xg), 3) AS avg_xg_per_connection,

    -- Conversion rate
    ROUND(COUNT(*) FILTER (WHERE result = 'Goal')::DECIMAL / NULLIF(COUNT(*), 0) * 100, 1) AS conversion_rate_pct

FROM metrics.shot_involvement_network
GROUP BY from_player, to_player, from_position, to_position, season
HAVING COUNT(*) >= 1
ORDER BY season DESC, total_connections DESC;


-- ============================================================================
-- EXPECTED THREAT (xT) CALCULATIONS (Phase 5)
-- ============================================================================

-- xT Grid function: Maps normalized coordinates to threat values
CREATE OR REPLACE FUNCTION metrics.calculate_xt_value(x DECIMAL, y DECIMAL)
RETURNS DECIMAL AS $$
DECLARE
    grid_x INTEGER;
    grid_y INTEGER;
    xt_value DECIMAL;
    -- xT grid (12 length zones × 8 width zones)
    -- Values based on research: higher near opponent's goal
    xt_grid DECIMAL[][] := ARRAY[
        -- Zone 1-4 (Own half - very low threat)
        ARRAY[0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
        ARRAY[0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01],
        ARRAY[0.01, 0.01, 0.02, 0.02, 0.02, 0.02, 0.01, 0.01],
        ARRAY[0.02, 0.02, 0.03, 0.03, 0.03, 0.03, 0.02, 0.02],
        -- Zone 5-8 (Midfield - low to medium threat)
        ARRAY[0.03, 0.04, 0.05, 0.05, 0.05, 0.05, 0.04, 0.03],
        ARRAY[0.05, 0.06, 0.08, 0.08, 0.08, 0.08, 0.06, 0.05],
        ARRAY[0.07, 0.09, 0.12, 0.13, 0.13, 0.12, 0.09, 0.07],
        ARRAY[0.10, 0.13, 0.16, 0.18, 0.18, 0.16, 0.13, 0.10],
        -- Zone 9-11 (Attacking third - high threat)
        ARRAY[0.14, 0.18, 0.22, 0.25, 0.25, 0.22, 0.18, 0.14],
        ARRAY[0.19, 0.24, 0.30, 0.35, 0.35, 0.30, 0.24, 0.19],
        ARRAY[0.25, 0.32, 0.40, 0.50, 0.50, 0.40, 0.32, 0.25],
        -- Zone 12 (6-yard box - very high threat)
        ARRAY[0.35, 0.45, 0.58, 0.70, 0.70, 0.58, 0.45, 0.35]
    ];
BEGIN
    -- Map x (0-1) to grid_x (1-12)
    grid_x := LEAST(12, GREATEST(1, FLOOR(x * 12) + 1));

    -- Map y (0-1) to grid_y (1-8)
    grid_y := LEAST(8, GREATEST(1, FLOOR(y * 8) + 1));

    -- Lookup xT value
    xt_value := xt_grid[grid_x][grid_y];

    RETURN xt_value;
END;
$$ LANGUAGE plpgsql IMMUTABLE;


-- Shot events with xT values
CREATE OR REPLACE VIEW metrics.shot_events_with_xt AS
SELECT
    *,
    metrics.calculate_xt_value(x_coord, y_coord) AS xt_value
FROM silver.shot_events;


-- Player xT statistics
CREATE OR REPLACE VIEW metrics.player_xt_stats AS
SELECT
    player_name,
    position_category,
    season,

    -- Shot volume
    COUNT(*) AS total_shots,
    COUNT(*) FILTER (WHERE result = 'Goal') AS goals,

    -- xT metrics
    ROUND(SUM(xt_value), 2) AS total_xt,
    ROUND(AVG(xt_value), 3) AS avg_xt_per_shot,
    ROUND(MAX(xt_value), 3) AS max_xt_shot,

    -- xG for comparison
    ROUND(SUM(xg), 2) AS total_xg,
    ROUND(AVG(xg), 3) AS avg_xg_per_shot,

    -- Dangerous shots (high xT zones)
    COUNT(*) FILTER (WHERE xt_value > 0.30) AS high_threat_shots,
    ROUND(COUNT(*) FILTER (WHERE xt_value > 0.30)::DECIMAL / NULLIF(COUNT(*), 0) * 100, 1) AS high_threat_pct,

    -- xT efficiency (goals per xT generated)
    ROUND(COUNT(*) FILTER (WHERE result = 'Goal')::DECIMAL / NULLIF(SUM(xt_value), 0), 3) AS xt_efficiency

FROM metrics.shot_events_with_xt
WHERE team = 'Arsenal'
GROUP BY player_name, position_category, season
HAVING COUNT(*) >= 3
ORDER BY season DESC, total_xt DESC;


-- Match-level xT timeline (cumulative threat over time)
CREATE OR REPLACE VIEW metrics.match_xt_timeline AS
SELECT
    match_url,
    match_date,
    home_team,
    away_team,
    minute,

    -- Cumulative xT by minute
    SUM(xt_value) FILTER (WHERE team = 'Arsenal') AS arsenal_cumulative_xt,
    SUM(xt_value) FILTER (WHERE team != 'Arsenal') AS opponent_cumulative_xt,

    -- Shot count by minute
    COUNT(*) FILTER (WHERE team = 'Arsenal') AS arsenal_shots_in_minute,
    COUNT(*) FILTER (WHERE team != 'Arsenal') AS opponent_shots_in_minute

FROM metrics.shot_events_with_xt
GROUP BY match_url, match_date, home_team, away_team, minute
ORDER BY match_url, minute;


-- ============================================================================
-- GRANT PERMISSIONS
-- ============================================================================

GRANT SELECT ON silver.shot_events TO analytics_user;
GRANT SELECT ON metrics.arsenal_matches TO analytics_user;
GRANT SELECT ON metrics.arsenal_player_stats TO analytics_user;
GRANT SELECT ON metrics.season_summary TO analytics_user;
GRANT SELECT ON metrics.match_advanced_stats TO analytics_user;
GRANT SELECT ON metrics.player_advanced_stats TO analytics_user;
GRANT SELECT ON metrics.opponent_comparison TO analytics_user;
GRANT SELECT ON metrics.tactical_analysis TO analytics_user;
GRANT SELECT ON metrics.shot_involvement_network TO analytics_user;
GRANT SELECT ON metrics.involvement_network_stats TO analytics_user;
GRANT SELECT ON metrics.shot_events_with_xt TO analytics_user;
GRANT SELECT ON metrics.player_xt_stats TO analytics_user;
GRANT SELECT ON metrics.match_xt_timeline TO analytics_user;
