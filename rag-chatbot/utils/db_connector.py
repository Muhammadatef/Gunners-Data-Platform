import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any

class DatabaseConnector:
    def __init__(self):
        self.conn_params = {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': os.getenv('POSTGRES_PORT', '5432'),
            'database': os.getenv('POSTGRES_DB', 'arsenalfc_analytics'),
            'user': os.getenv('POSTGRES_USER', 'analytics_user'),
            'password': os.getenv('POSTGRES_PASSWORD', 'analytics_pass')
        }

    def get_connection(self):
        return psycopg2.connect(**self.conn_params)

    def fetch_all_matches(self) -> List[Dict[str, Any]]:
        """Fetch all Arsenal matches with detailed statistics"""
        query = """
        SELECT
            m.match_date,
            m.season,
            m.opponent,
            m.venue,
            m.result,
            m.arsenal_goals,
            m.opponent_goals,
            m.arsenal_xg,
            m.opponent_xg,

            -- Shot statistics
            COUNT(s.xg) FILTER (WHERE s.team = 'Arsenal') as total_shots,
            COUNT(s.xg) FILTER (WHERE s.team = 'Arsenal' AND s.result IN ('Goal', 'SavedShot', 'ShotOnPost')) as shots_on_target,
            COUNT(s.xg) FILTER (WHERE s.team = 'Arsenal' AND s.result = 'Goal') as goals,

            -- Conversion and quality metrics
            ROUND(AVG(s.xg) FILTER (WHERE s.team = 'Arsenal'), 3) as avg_shot_xg,
            COUNT(s.xg) FILTER (WHERE s.team = 'Arsenal' AND s.xg >= 0.35) as big_chances,

            -- Top scorers in match
            STRING_AGG(DISTINCT s.player_name, ', ') FILTER (WHERE s.team = 'Arsenal' AND s.result = 'Goal') as scorers

        FROM metrics.arsenal_matches m
        LEFT JOIN metrics.match_shots_detail s
            ON m.match_date = s.match_date
        GROUP BY
            m.match_date,
            m.season,
            m.opponent,
            m.venue,
            m.result,
            m.arsenal_goals,
            m.opponent_goals,
            m.arsenal_xg,
            m.opponent_xg
        ORDER BY m.match_date DESC
        """

        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query)
                return cursor.fetchall()

    def fetch_player_stats(self, season: str = None) -> List[Dict[str, Any]]:
        """Fetch player performance statistics"""
        query = """
        SELECT
            player_name,
            season,
            total_shots,
            goals,
            total_xg,
            conversion_pct,
            big_chances,
            big_chance_conversion_pct
        FROM metrics.arsenal_player_stats
        """

        if season:
            query += f" WHERE season = '{season}'"
        query += " ORDER BY goals DESC, total_xg DESC"

        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query)
                return cursor.fetchall()

    def fetch_opponent_analysis(self) -> List[Dict[str, Any]]:
        """Fetch head-to-head opponent statistics"""
        query = """
        SELECT
            opponent,
            matches_played,
            wins,
            draws,
            losses,
            goals_for,
            goals_against,
            avg_xg_for,
            avg_xg_against,
            win_rate
        FROM metrics.opponent_comparison
        ORDER BY matches_played DESC, win_rate DESC
        """

        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query)
                return cursor.fetchall()
