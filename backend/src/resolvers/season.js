import { query } from '../db/connection.js';

export const seasonResolvers = {
  Query: {
    async seasons() {
      const result = await query(`
        SELECT DISTINCT season 
        FROM metrics.arsenal_matches 
        ORDER BY season DESC
      `);
      return result.rows.map(row => row.season);
    },

    async seasonSummary(_, { season }) {
      const result = await query(
        `SELECT * FROM metrics.season_summary WHERE season = $1`,
        [season]
      );

      if (result.rows.length === 0) {
        return null;
      }

      const row = result.rows[0];
      return {
        season: row.season,
        matchesPlayed: parseInt(row.matches_played) || 0,
        wins: parseInt(row.wins) || 0,
        draws: parseInt(row.draws) || 0,
        losses: parseInt(row.losses) || 0,
        points: parseInt(row.points) || 0,
        goalsFor: parseInt(row.goals_for) || 0,
        goalsAgainst: parseInt(row.goals_against) || 0,
        goalDifference: parseInt(row.goal_difference) || 0,
        totalXgFor: parseFloat(row.total_xg_for) || 0,
        totalXgAgainst: parseFloat(row.total_xg_against) || 0,
        avgXgPerMatch: parseFloat(row.avg_xg_per_match) || 0,
        totalXgOverperformance: parseFloat(row.total_xg_overperformance) || 0,
        homeMatches: parseInt(row.home_matches) || 0,
        awayMatches: parseInt(row.away_matches) || 0,
        homeWins: parseInt(row.home_wins) || 0,
        awayWins: parseInt(row.away_wins) || 0,
      };
    },
  },
};
