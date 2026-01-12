"""
Database connection utilities for dashboard
"""

import os
import logging
from typing import Optional
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
import streamlit as st

logger = logging.getLogger(__name__)


@st.cache_resource
def get_db_engine() -> Engine:
    """
    Get SQLAlchemy database engine (cached)

    Returns:
        SQLAlchemy Engine
    """
    # Get connection parameters from environment
    db_host = os.getenv("POSTGRES_HOST", "postgres")
    db_port = os.getenv("POSTGRES_PORT", "5432")
    db_name = os.getenv("POSTGRES_DB", "arsenalfc_analytics")
    db_user = os.getenv("POSTGRES_USER", "analytics_user")
    db_password = os.getenv("POSTGRES_PASSWORD", "analytics_pass")

    connection_string = (
        f"postgresql://{db_user}:{db_password}"
        f"@{db_host}:{db_port}/{db_name}"
    )

    logger.info(f"Connecting to database: {db_host}:{db_port}/{db_name}")

    engine = create_engine(
        connection_string,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True
    )

    return engine


@st.cache_data(ttl=300)  # Cache for 5 minutes
def run_query(query: str, params: Optional[dict] = None) -> pd.DataFrame:
    """
    Execute SQL query and return DataFrame

    Args:
        query: SQL query string
        params: Query parameters

    Returns:
        pandas DataFrame with results
    """
    engine = get_db_engine()

    try:
        with engine.connect() as conn:
            df = pd.read_sql_query(
                sql=text(query),
                con=conn,
                params=params or {}
            )
        return df
    except Exception as e:
        logger.error(f"Query error: {e}")
        st.error(f"Database error: {e}")
        return pd.DataFrame()


def get_season_summary(season: str = "2024-2025") -> pd.DataFrame:
    """Get Arsenal's season summary"""
    query = """
        SELECT
            matches_played,
            wins,
            draws,
            losses,
            points,
            goals_for,
            goals_against,
            goal_difference,
            xg_for,
            xg_against,
            xg_difference,
            goals_vs_xg,
            xg_per_match,
            xga_per_match,
            possession_avg
        FROM metrics.season_team_summary sts
        JOIN gold.dim_team dt ON sts.team_id = dt.team_id
        JOIN gold.dim_season ds ON sts.season_id = ds.season_id
        WHERE dt.team_name = 'Arsenal'
          AND ds.season_name = :season
        LIMIT 1
    """
    return run_query(query, {"season": season})


def get_recent_matches(season: str = "2024-2025", limit: int = 10) -> pd.DataFrame:
    """Get recent Arsenal matches"""
    query = """
        SELECT
            dm.match_id,
            dm.match_date,
            ht.team_name AS home_team,
            at.team_name AS away_team,
            dm.home_score,
            dm.away_score,
            CASE
                WHEN ht.team_name = 'Arsenal' THEN ftmp_home.xg_for
                ELSE ftmp_away.xg_for
            END AS arsenal_xg,
            CASE
                WHEN ht.team_name = 'Arsenal' THEN ftmp_home.xg_against
                ELSE ftmp_away.xg_against
            END AS opponent_xg
        FROM gold.dim_match dm
        JOIN gold.dim_team ht ON dm.home_team_id = ht.team_id
        JOIN gold.dim_team at ON dm.away_team_id = at.team_id
        JOIN gold.dim_season ds ON dm.season_id = ds.season_id
        LEFT JOIN gold.fact_team_match_performance ftmp_home
            ON dm.match_id = ftmp_home.match_id AND ftmp_home.team_id = ht.team_id
        LEFT JOIN gold.fact_team_match_performance ftmp_away
            ON dm.match_id = ftmp_away.match_id AND ftmp_away.team_id = at.team_id
        WHERE (ht.team_name = 'Arsenal' OR at.team_name = 'Arsenal')
          AND ds.season_name = :season
          AND dm.match_status = 'finished'
        ORDER BY dm.match_date DESC
        LIMIT :limit
    """
    return run_query(query, {"season": season, "limit": limit})


def get_player_season_stats(season: str = "2024-2025") -> pd.DataFrame:
    """Get player season statistics"""
    query = """
        SELECT
            dp.player_name,
            sps.position,
            sps.matches_played,
            sps.minutes_played,
            sps.goals,
            sps.assists,
            sps.xg,
            sps.xa,
            sps.goals_per_90,
            sps.assists_per_90,
            sps.xg_per_90,
            sps.xa_per_90,
            sps.progressive_passes,
            sps.progressive_carries,
            sps.dribbles_completed,
            sps.sca,
            sps.gca
        FROM metrics.season_player_summary sps
        JOIN gold.dim_player dp ON sps.player_id = dp.player_id
        JOIN gold.dim_team dt ON sps.team_id = dt.team_id
        JOIN gold.dim_season ds ON sps.season_id = ds.season_id
        WHERE dt.team_name = 'Arsenal'
          AND ds.season_name = :season
          AND sps.minutes_played > 90
        ORDER BY sps.minutes_played DESC
    """
    return run_query(query, {"season": season})


def get_match_detail(match_id: str) -> pd.DataFrame:
    """Get detailed match information"""
    query = """
        SELECT
            dm.match_id,
            dm.match_date,
            ht.team_name AS home_team,
            at.team_name AS away_team,
            dm.home_score,
            dm.away_score,
            dm.venue,
            dm.attendance,
            dm.referee,
            ftmp_home.xg_for AS home_xg,
            ftmp_home.shots AS home_shots,
            ftmp_home.shots_on_target AS home_shots_on_target,
            ftmp_home.possession_pct AS home_possession,
            ftmp_away.xg_for AS away_xg,
            ftmp_away.shots AS away_shots,
            ftmp_away.shots_on_target AS away_shots_on_target,
            ftmp_away.possession_pct AS away_possession
        FROM gold.dim_match dm
        JOIN gold.dim_team ht ON dm.home_team_id = ht.team_id
        JOIN gold.dim_team at ON dm.away_team_id = at.team_id
        LEFT JOIN gold.fact_team_match_performance ftmp_home
            ON dm.match_id = ftmp_home.match_id AND ftmp_home.team_id = ht.team_id
        LEFT JOIN gold.fact_team_match_performance ftmp_away
            ON dm.match_id = ftmp_away.match_id AND ftmp_away.team_id = at.team_id
        WHERE dm.match_id = :match_id
    """
    return run_query(query, {"match_id": match_id})


def get_match_player_stats(match_id: str) -> pd.DataFrame:
    """Get player statistics for a specific match"""
    query = """
        SELECT
            dp.player_name,
            dt.team_name AS team,
            fpmp.position,
            fpmp.minutes_played,
            fpmp.goals,
            fpmp.assists,
            fpmp.shots,
            fpmp.shots_on_target,
            fpmp.xg,
            fpmp.xa,
            fpmp.progressive_passes,
            fpmp.progressive_carries,
            fpmp.key_passes,
            fpmp.dribbles_completed,
            fpmp.sca,
            fpmp.gca,
            fpmp.touches
        FROM gold.fact_player_match_performance fpmp
        JOIN gold.dim_player dp ON fpmp.player_id = dp.player_id
        JOIN gold.dim_team dt ON fpmp.team_id = dt.team_id
        WHERE fpmp.match_id = :match_id
          AND fpmp.minutes_played > 0
        ORDER BY dt.team_name, fpmp.started DESC, fpmp.minutes_played DESC
    """
    return run_query(query, {"match_id": match_id})


def get_match_shots(match_id: str) -> pd.DataFrame:
    """Get shot events for a match"""
    query = """
        SELECT
            player_name,
            team,
            minute,
            x_coord,
            y_coord,
            xg,
            result,
            situation,
            shot_type
        FROM gold.fact_match_events
        WHERE match_id = :match_id
          AND event_type = 'shot'
        ORDER BY minute
    """
    return run_query(query, {"match_id": match_id})
