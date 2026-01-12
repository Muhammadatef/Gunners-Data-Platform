import { query } from '../db/connection.js';

export const matchResolvers = {
  Query: {
    async matches(_, { season, limit = 100 }) {
      let sql = 'SELECT * FROM metrics.arsenal_matches';
      const params = [];

      if (season) {
        sql += ' WHERE season = $1';
        params.push(season);
      }

      sql += ' ORDER BY match_date DESC LIMIT $' + (params.length + 1);
      params.push(limit);

      const result = await query(sql, params);

      return result.rows.map(row => ({
        matchUrl: row.match_url,
        matchId: row.match_url, // Using match_url as matchId for now
        matchDate: row.match_date,
        season: row.season,
        opponent: row.opponent,
        venue: row.venue,
        result: row.result,
        arsenalGoals: parseInt(row.arsenal_goals) || 0,
        opponentGoals: parseInt(row.opponent_goals) || 0,
        arsenalXg: parseFloat(row.arsenal_xg) || 0,
        opponentXg: parseFloat(row.opponent_xg) || 0,
        xgOverperformance: parseFloat(row.xg_overperformance) || 0,
      }));
    },

    async matchList(_, { season }) {
      const result = await query(
        `SELECT 
          match_url as match_id,
          home_team || ' vs ' || away_team as match_name,
          match_date,
          season
        FROM metrics.arsenal_matches 
        WHERE season = $1 
        ORDER BY match_date DESC`,
        [season]
      );

      return result.rows.map(row => ({
        matchId: row.match_id,
        matchName: row.match_name,
        matchDate: row.match_date,
        season: row.season,
      }));
    },

    async matchShots(_, { matchId }) {
      // matchId is actually match_url in the database
      const result = await query(
        `SELECT * FROM silver.shot_events 
         WHERE match_url = $1 
         ORDER BY minute ASC`,
        [matchId]
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

    async matchShotsBySeason(_, { season, team = 'Arsenal' }) {
      const result = await query(
        `SELECT * FROM silver.shot_events 
         WHERE season = $1 AND team = $2 
         ORDER BY match_date DESC, minute ASC`,
        [season, team]
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

    async matchPlayerShots(_, { matchId, playerName }) {
      const result = await query(
        `SELECT * FROM silver.shot_events 
         WHERE match_url = $1 AND player_name = $2 AND team = 'Arsenal'
         ORDER BY minute ASC`,
        [matchId, playerName]
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

    async matchPlayerNetwork(_, { matchId }) {
      const result = await query(
        `SELECT 
          assisted_by as assister,
          player_name as shooter,
          COUNT(*) as assists_count,
          COUNT(*) FILTER (WHERE result = 'Goal') as goals_from_assists,
          ROUND(SUM(xg), 2) as total_xg_assisted
        FROM silver.shot_events
        WHERE match_url = $1 
          AND team = 'Arsenal'
          AND assisted_by IS NOT NULL
          AND assisted_by != ''
        GROUP BY assisted_by, player_name
        ORDER BY assists_count DESC`,
        [matchId]
      );

      return result.rows.map(row => ({
        assister: row.assister,
        shooter: row.shooter,
        season: '', // Not applicable for single match
        assistsCount: parseInt(row.assists_count) || 0,
        goalsFromAssists: parseInt(row.goals_from_assists) || 0,
        totalXgAssisted: parseFloat(row.total_xg_assisted) || 0,
      }));
    },

    async matchPlayers(_, { matchId }) {
      const result = await query(
        `SELECT DISTINCT player_name 
         FROM silver.shot_events 
         WHERE match_url = $1 AND team = 'Arsenal' AND player_name IS NOT NULL
         ORDER BY player_name`,
        [matchId]
      );

      return result.rows.map(row => row.player_name);
    },
  },
};
