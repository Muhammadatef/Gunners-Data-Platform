import { query } from '../db/connection.js';

export const playerResolvers = {
  Query: {
    async playerStats(_, { season, limit = 50 }) {
      const result = await query(
        `SELECT * FROM metrics.player_advanced_stats 
         WHERE season = $1 
         ORDER BY total_xg DESC 
         LIMIT $2`,
        [season, limit]
      );

      return result.rows.map(row => ({
        playerName: row.player_name,
        season: row.season,
        matchesPlayed: parseInt(row.matches_played) || 0,
        totalShots: parseInt(row.total_shots) || 0,
        goals: parseInt(row.goals) || 0,
        totalXg: parseFloat(row.total_xg) || 0,
        avgXgPerShot: parseFloat(row.avg_xg_per_shot) || 0,
        conversionPct: parseFloat(row.conversion_pct) || 0,
        shotsOnTarget: parseInt(row.shots_on_target) || 0,
        shotAccuracyPct: parseFloat(row.shot_accuracy_pct) || 0,
        missedShots: parseInt(row.missed_shots) || 0,
        blockedShots: parseInt(row.blocked_shots) || 0,
        savedShots: parseInt(row.saved_shots) || 0,
        bigChances: parseInt(row.big_chances) || 0,
        bigChancesScored: parseInt(row.big_chances_scored) || 0,
        bigChanceConversionPct: parseFloat(row.big_chance_conversion_pct) || 0,
        boxShots: parseInt(row.box_shots) || 0,
        outsideBoxShots: parseInt(row.outside_box_shots) || 0,
        avgShotDistance: parseFloat(row.avg_shot_distance) || 0,
        rightFootShots: parseInt(row.right_foot_shots) || 0,
        rightFootGoals: parseInt(row.right_foot_goals) || 0,
        leftFootShots: parseInt(row.left_foot_shots) || 0,
        leftFootGoals: parseInt(row.left_foot_goals) || 0,
        headers: parseInt(row.headers) || 0,
        headerGoals: parseInt(row.header_goals) || 0,
        openPlayShots: parseInt(row.open_play_shots) || 0,
        openPlayGoals: parseInt(row.open_play_goals) || 0,
        cornerShots: parseInt(row.corner_shots) || 0,
        setPieceShots: parseInt(row.set_piece_shots) || 0,
        penaltiesTaken: parseInt(row.penalties_taken) || 0,
        penaltiesScored: parseInt(row.penalties_scored) || 0,
        assists: parseInt(row.assists) || 0,
        xgOverperformance: parseFloat(row.xg_overperformance) || 0,
        shotsPerMatch: parseFloat(row.shots_per_match) || 0,
        goalsPerMatch: parseFloat(row.goals_per_match) || 0,
        xgPerMatch: parseFloat(row.xg_per_match) || 0,
      }));
    },

    async playerShots(_, { season, playerName }) {
      const result = await query(
        `SELECT * FROM silver.shot_events 
         WHERE season = $1 AND player_name = $2 AND team = 'Arsenal'
         ORDER BY match_date DESC, minute ASC`,
        [season, playerName]
      );

      return result.rows.map(row => ({
        matchId: row.match_url,
        matchUrl: row.match_url,
        matchDate: row.match_date,
        season: row.season,
        homeTeam: row.home_team,
        awayTeam: row.away_team,
        homeGoals: parseInt(row.home_goals) || 0,
        awayGoals: parseInt(row.away_goals) || 0,
        homeXg: parseFloat(row.home_xg) || 0,
        awayXg: parseFloat(row.away_xg) || 0,
        playerName: row.player_name,
        playerId: row.player_id,
        team: row.team,
        minute: parseInt(row.minute) || 0,
        result: row.result,
        situation: row.situation,
        shotType: row.shot_type,
        x: parseFloat(row.x_coord) || 0,
        y: parseFloat(row.y_coord) || 0,
        xg: parseFloat(row.xg) || 0,
        assistedBy: row.assisted_by,
        lastAction: row.last_action,
      }));
    },

    async assistNetwork(_, { season, limit = 50 }) {
      // Create assist network from shot_events
      const result = await query(
        `SELECT 
          assisted_by as assister,
          player_name as shooter,
          season,
          COUNT(*) as assists_count,
          COUNT(*) FILTER (WHERE result = 'Goal') as goals_from_assists,
          ROUND(SUM(xg), 2) as total_xg_assisted
        FROM silver.shot_events
        WHERE season = $1 
          AND team = 'Arsenal'
          AND assisted_by IS NOT NULL
          AND assisted_by != ''
        GROUP BY assisted_by, player_name, season
        ORDER BY assists_count DESC
        LIMIT $2`,
        [season, limit]
      );

      return result.rows.map(row => ({
        assister: row.assister,
        shooter: row.shooter,
        season: row.season,
        assistsCount: parseInt(row.assists_count) || 0,
        goalsFromAssists: parseInt(row.goals_from_assists) || 0,
        totalXgAssisted: parseFloat(row.total_xg_assisted) || 0,
      }));
    },

    async playerXTStats(_, { season, limit = 50 }) {
      const result = await query(
        `SELECT * FROM metrics.player_xt_stats 
         WHERE season = $1 
         ORDER BY total_xt DESC 
         LIMIT $2`,
        [season, limit]
      );

      return result.rows.map(row => ({
        playerName: row.player_name,
        positionCategory: row.position_category,
        season: row.season,
        totalShots: parseInt(row.total_shots) || 0,
        goals: parseInt(row.goals) || 0,
        totalXt: parseFloat(row.total_xt) || 0,
        avgXtPerShot: parseFloat(row.avg_xt_per_shot) || 0,
        maxXtShot: parseFloat(row.max_xt_shot) || 0,
        totalXg: parseFloat(row.total_xg) || 0,
        avgXgPerShot: parseFloat(row.avg_xg_per_shot) || 0,
        highThreatShots: parseInt(row.high_threat_shots) || 0,
        highThreatPct: parseFloat(row.high_threat_pct) || 0,
        xtEfficiency: parseFloat(row.xt_efficiency) || 0,
      }));
    },
  },
};
