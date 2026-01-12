-- Create missing views for Opponent Analysis and Performance Trends

-- ============================================================================
-- View: opponent_comparison
-- Purpose: Compare Arsenal's performance against different opponents
-- ============================================================================
CREATE OR REPLACE VIEW metrics.opponent_comparison AS
SELECT
    opponent,
    COUNT(*) as matches_played,
    SUM(CASE WHEN result = 'W' THEN 1 ELSE 0 END) as wins,
    SUM(CASE WHEN result = 'D' THEN 1 ELSE 0 END) as draws,
    SUM(CASE WHEN result = 'L' THEN 1 ELSE 0 END) as losses,
    SUM(arsenal_goals) as goals_for,
    SUM(opponent_goals) as goals_against,
    ROUND(AVG(arsenal_xg)::numeric, 2) as avg_xg_for,
    ROUND(AVG(opponent_xg)::numeric, 2) as avg_xg_against,
    ROUND((SUM(arsenal_goals)::numeric / NULLIF(COUNT(*), 0)), 2) as avg_goals_per_match,
    ROUND((SUM(CASE WHEN result = 'W' THEN 1 ELSE 0 END)::numeric / NULLIF(COUNT(*), 0) * 100), 1) as win_rate
FROM metrics.arsenal_matches
GROUP BY opponent
ORDER BY matches_played DESC, win_rate DESC;

-- ============================================================================
-- View: match_advanced_stats
-- Purpose: Advanced match statistics for performance trends analysis
-- ============================================================================
CREATE OR REPLACE VIEW metrics.match_advanced_stats AS
SELECT
    m.match_date,
    m.opponent,
    m.venue,
    m.result,
    m.arsenal_goals,
    m.opponent_goals,
    m.arsenal_xg,
    m.opponent_xg,

    -- Shot statistics
    COUNT(CASE WHEN s.team = 'Arsenal' THEN 1 END) as shots,
    COUNT(CASE WHEN s.team = 'Arsenal' AND s.result = 'Goal' THEN 1 END) as goals,
    COUNT(CASE WHEN s.team = 'Arsenal' AND s.result IN ('Goal', 'SavedShot', 'ShotOnPost') THEN 1 END) as shots_on_target,

    -- Shot quality metrics
    ROUND(AVG(CASE WHEN s.team = 'Arsenal' THEN s.xg END)::numeric, 3) as avg_shot_xg,
    MAX(CASE WHEN s.team = 'Arsenal' THEN s.xg END) as max_shot_xg,

    -- Conversion rate
    ROUND(
        (COUNT(CASE WHEN s.team = 'Arsenal' AND s.result = 'Goal' THEN 1 END)::numeric /
         NULLIF(COUNT(CASE WHEN s.team = 'Arsenal' THEN 1 END), 0) * 100),
        1
    ) as conversion_rate,

    -- xG performance
    ROUND((m.arsenal_goals - m.arsenal_xg)::numeric, 2) as xg_overperformance,

    -- Big chances
    COUNT(CASE WHEN s.team = 'Arsenal' AND s.xg >= 0.35 THEN 1 END) as big_chances,
    COUNT(CASE WHEN s.team = 'Arsenal' AND s.xg >= 0.35 AND s.result = 'Goal' THEN 1 END) as big_chances_scored

FROM metrics.arsenal_matches m
LEFT JOIN metrics.match_shots_detail s
    ON m.match_date = s.match_date
    AND (s.home_team = 'Arsenal' OR s.away_team = 'Arsenal')
    AND s.team = 'Arsenal'
GROUP BY
    m.match_date,
    m.opponent,
    m.venue,
    m.result,
    m.arsenal_goals,
    m.opponent_goals,
    m.arsenal_xg,
    m.opponent_xg
ORDER BY m.match_date DESC;

-- Grant permissions
GRANT SELECT ON metrics.opponent_comparison TO analytics_user;
GRANT SELECT ON metrics.match_advanced_stats TO analytics_user;
