import { query } from '../db/connection.js';

export const advancedResolvers = {
  Query: {
    async opponentComparison(_, { season }) {
      let sql = 'SELECT * FROM metrics.opponent_comparison';
      const params = [];

      if (season) {
        // Need to filter by season through matches
        sql = `
          SELECT 
            oc.*
          FROM metrics.opponent_comparison oc
          INNER JOIN metrics.arsenal_matches m ON oc.opponent = m.opponent
          WHERE m.season = $1
          GROUP BY oc.opponent, oc.matches_played, oc.wins, oc.draws, oc.losses, 
                   oc.win_rate_pct, oc.goals_for, oc.goals_against, oc.avg_goals_for,
                   oc.avg_goals_against, oc.total_xg_for, oc.total_xg_against,
                   oc.avg_xg_for, oc.avg_xg_against, oc.clean_sheets, oc.failed_to_score,
                   oc.last_played, oc.last_result
        `;
        params.push(season);
      }

      sql += ' ORDER BY matches_played DESC, win_rate_pct DESC';

      const result = await query(sql, params);

      return result.rows.map(row => ({
        opponent: row.opponent,
        matchesPlayed: parseInt(row.matches_played) || 0,
        wins: parseInt(row.wins) || 0,
        draws: parseInt(row.draws) || 0,
        losses: parseInt(row.losses) || 0,
        winRatePct: parseFloat(row.win_rate_pct) || 0,
        goalsFor: parseInt(row.goals_for) || 0,
        goalsAgainst: parseInt(row.goals_against) || 0,
        avgGoalsFor: parseFloat(row.avg_goals_for) || 0,
        avgGoalsAgainst: parseFloat(row.avg_goals_against) || 0,
        totalXgFor: parseFloat(row.total_xg_for) || 0,
        totalXgAgainst: parseFloat(row.total_xg_against) || 0,
        avgXgFor: parseFloat(row.avg_xg_for) || 0,
        avgXgAgainst: parseFloat(row.avg_xg_against) || 0,
        cleanSheets: parseInt(row.clean_sheets) || 0,
        failedToScore: parseInt(row.failed_to_score) || 0,
        lastPlayed: row.last_played,
        lastResult: row.last_result,
      }));
    },

    async matchAdvancedStats(_, { matchId }) {
      const result = await query(
        `SELECT * FROM metrics.match_advanced_stats WHERE match_url = $1`,
        [matchId]
      );

      if (result.rows.length === 0) {
        return null;
      }

      const row = result.rows[0];
      return {
        matchUrl: row.match_url,
        matchDate: row.match_date,
        season: row.season,
        opponent: row.opponent,
        venue: row.venue,
        result: row.result,
        arsenalGoals: parseInt(row.arsenal_goals) || 0,
        opponentGoals: parseInt(row.opponent_goals) || 0,
        arsenalXg: parseFloat(row.arsenal_xg) || 0,
        opponentXg: parseFloat(row.opponent_xg) || 0,
        arsenalShots: parseInt(row.arsenal_shots) || 0,
        opponentShots: parseInt(row.opponent_shots) || 0,
        arsenalShotsOnTarget: parseInt(row.arsenal_shots_on_target) || 0,
        opponentShotsOnTarget: parseInt(row.opponent_shots_on_target) || 0,
        arsenalShotAccuracyPct: parseFloat(row.arsenal_shot_accuracy_pct) || 0,
        arsenalBigChances: parseInt(row.arsenal_big_chances) || 0,
        arsenalBigChancesScored: parseInt(row.arsenal_big_chances_scored) || 0,
        arsenalBoxShots: parseInt(row.arsenal_box_shots) || 0,
        arsenalOutsideBoxShots: parseInt(row.arsenal_outside_box_shots) || 0,
        arsenalFirstHalfShots: parseInt(row.arsenal_first_half_shots) || 0,
        arsenalFirstHalfXg: parseFloat(row.arsenal_first_half_xg) || 0,
        arsenalSecondHalfShots: parseInt(row.arsenal_second_half_shots) || 0,
        arsenalSecondHalfXg: parseFloat(row.arsenal_second_half_xg) || 0,
        arsenalAvgShotXg: parseFloat(row.arsenal_avg_shot_xg) || 0,
        opponentAvgShotXg: parseFloat(row.opponent_avg_shot_xg) || 0,
      };
    },

    async performanceTrends(_, { season, windowSize = 5 }) {
      const result = await query(
        `SELECT 
          m.match_date,
          m.opponent,
          m.result,
          m.arsenal_goals as goals,
          m.arsenal_xg as xg,
          mas.arsenal_shots as shots,
          mas.arsenal_shots_on_target as shots_on_target,
          mas.arsenal_big_chances as big_chances,
          AVG(m.arsenal_xg) OVER (
            ORDER BY m.match_date 
            ROWS BETWEEN $1 PRECEDING AND CURRENT ROW
          ) as rolling_avg_xg,
          AVG(m.arsenal_goals) OVER (
            ORDER BY m.match_date 
            ROWS BETWEEN $1 PRECEDING AND CURRENT ROW
          ) as rolling_avg_goals
        FROM metrics.arsenal_matches m
        LEFT JOIN metrics.match_advanced_stats mas ON m.match_url = mas.match_url
        WHERE m.season = $2
        ORDER BY m.match_date ASC`,
        [windowSize - 1, season]
      );

      return result.rows.map(row => ({
        matchDate: row.match_date,
        opponent: row.opponent,
        result: row.result,
        goals: parseInt(row.goals) || 0,
        xg: parseFloat(row.xg) || 0,
        shots: parseInt(row.shots) || 0,
        shotsOnTarget: parseInt(row.shots_on_target) || 0,
        bigChances: parseInt(row.big_chances) || 0,
        rollingAvgXg: parseFloat(row.rolling_avg_xg) || null,
        rollingAvgGoals: parseFloat(row.rolling_avg_goals) || null,
      }));
    },

    async dataQuality() {
      const result = await query(`
        SELECT 
          (SELECT COUNT(*) FROM metrics.arsenal_matches) as total_matches,
          (SELECT COUNT(*) FROM silver.shot_events WHERE team = 'Arsenal') as total_shots,
          (SELECT COUNT(DISTINCT season) FROM metrics.arsenal_matches) as seasons_count,
          (SELECT MAX(match_date) FROM metrics.arsenal_matches) as last_update,
          (SELECT COUNT(DISTINCT season) FROM metrics.arsenal_matches) as seasons_available
      `);

      const row = result.rows[0];
      const totalMatches = parseInt(row.total_matches) || 0;
      const totalShots = parseInt(row.total_shots) || 0;
      const lastUpdate = row.last_update;
      
      // Calculate data completeness (simplified - can be enhanced)
      const dataCompleteness = totalMatches > 0 && totalShots > 0 ? 95.0 : 0.0;
      
      // Get available seasons
      const seasonsResult = await query(`
        SELECT DISTINCT season FROM metrics.arsenal_matches ORDER BY season DESC
      `);
      const seasonsAvailable = seasonsResult.rows.map(r => r.season);

      // Calculate data freshness
      const daysSinceUpdate = lastUpdate 
        ? Math.floor((new Date() - new Date(lastUpdate)) / (1000 * 60 * 60 * 24))
        : 999;
      
      let dataFreshness = 'Unknown';
      if (daysSinceUpdate === 0) dataFreshness = 'Today';
      else if (daysSinceUpdate === 1) dataFreshness = 'Yesterday';
      else if (daysSinceUpdate < 7) dataFreshness = `${daysSinceUpdate} days ago`;
      else if (daysSinceUpdate < 30) dataFreshness = `${Math.floor(daysSinceUpdate / 7)} weeks ago`;
      else dataFreshness = `${Math.floor(daysSinceUpdate / 30)} months ago`;

      return {
        totalMatches,
        totalShots,
        dataCompleteness,
        lastUpdate,
        seasonsAvailable,
        validationErrors: 0, // Can be enhanced with actual validation
        dataFreshness,
      };
    },
  },
};
