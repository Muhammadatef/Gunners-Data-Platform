import { query } from '../db/connection.js';

export const tacticalResolvers = {
  Query: {
    async tacticalAnalysis(_, { season }) {
      const result = await query(
        `SELECT * FROM metrics.tactical_analysis WHERE season = $1`,
        [season]
      );

      if (result.rows.length === 0) {
        return null;
      }

      const row = result.rows[0];
      return {
        season: row.season,
        arsenalShots0_15: parseInt(row.arsenal_shots_0_15) || 0,
        arsenalShots16_30: parseInt(row.arsenal_shots_16_30) || 0,
        arsenalShots31_45: parseInt(row.arsenal_shots_31_45) || 0,
        arsenalShots46_60: parseInt(row.arsenal_shots_46_60) || 0,
        arsenalShots61_75: parseInt(row.arsenal_shots_61_75) || 0,
        arsenalShots76_90: parseInt(row.arsenal_shots_76_90) || 0,
        arsenalGoals0_15: parseInt(row.arsenal_goals_0_15) || 0,
        arsenalGoals16_30: parseInt(row.arsenal_goals_16_30) || 0,
        arsenalGoals31_45: parseInt(row.arsenal_goals_31_45) || 0,
        arsenalGoals46_60: parseInt(row.arsenal_goals_46_60) || 0,
        arsenalGoals61_75: parseInt(row.arsenal_goals_61_75) || 0,
        arsenalGoals76_90: parseInt(row.arsenal_goals_76_90) || 0,
        shotsFromPass: parseInt(row.shots_from_pass) || 0,
        shotsFromDribble: parseInt(row.shots_from_dribble) || 0,
        shotsFromRebound: parseInt(row.shots_from_rebound) || 0,
        shotsFromChip: parseInt(row.shots_from_chip) || 0,
        shotsFromCross: parseInt(row.shots_from_cross) || 0,
        openPlayTotal: parseInt(row.open_play_total) || 0,
        openPlayGoals: parseInt(row.open_play_goals) || 0,
        openPlayXg: parseFloat(row.open_play_xg) || 0,
        cornerTotal: parseInt(row.corner_total) || 0,
        cornerGoals: parseInt(row.corner_goals) || 0,
        cornerXg: parseFloat(row.corner_xg) || 0,
        setPieceTotal: parseInt(row.set_piece_total) || 0,
        setPieceGoals: parseInt(row.set_piece_goals) || 0,
        setPieceXg: parseFloat(row.set_piece_xg) || 0,
        penaltyTotal: parseInt(row.penalty_total) || 0,
        penaltyGoals: parseInt(row.penalty_goals) || 0,
        bigChancesCreated: parseInt(row.big_chances_created) || 0,
        bigChancesConverted: parseInt(row.big_chances_converted) || 0,
      };
    },
  },
};
