"""
Database Loader - Persist scraped data to PostgreSQL Bronze layer
"""

import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import psycopg2
from psycopg2.extras import Json, execute_values
from contextlib import contextmanager

from config import config

logger = logging.getLogger(__name__)


class DatabaseLoader:
    """Handle loading scraped data into PostgreSQL"""

    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize database loader

        Args:
            connection_string: PostgreSQL connection string
                             (defaults to config value)
        """
        self.connection_string = connection_string or config.db_connection_string

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = psycopg2.connect(self.connection_string)
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def save_fbref_raw(
        self,
        match_id: str,
        raw_data: Dict[str, Any],
        match_url: str,
        scrape_run_id: Optional[str] = None
    ) -> bool:
        """
        Save FBref raw data to bronze layer

        Args:
            match_id: Unique match identifier
            raw_data: Raw scraped data dictionary
            match_url: URL of match report
            scrape_run_id: ID of scrape run for tracking

        Returns:
            True if successful
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    query = """
                        INSERT INTO bronze.fbref_raw
                            (match_id, match_url, raw_data, scrape_run_id, scraped_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (match_id)
                        DO UPDATE SET
                            raw_data = EXCLUDED.raw_data,
                            match_url = EXCLUDED.match_url,
                            scrape_run_id = EXCLUDED.scrape_run_id,
                            scraped_at = EXCLUDED.scraped_at,
                            updated_at = CURRENT_TIMESTAMP
                        RETURNING id
                    """

                    cur.execute(query, (
                        match_id,
                        match_url,
                        Json(raw_data),
                        scrape_run_id,
                        datetime.utcnow(),
                        datetime.utcnow()
                    ))

                    result = cur.fetchone()
                    logger.info(f"Saved FBref data for match {match_id} (ID: {result[0]})")

            return True

        except Exception as e:
            logger.error(f"Failed to save FBref data: {e}")
            return False

    def save_understat_raw(
        self,
        match_id: str,
        raw_shots: Dict[str, Any],
        match_url: str,
        scrape_run_id: Optional[str] = None
    ) -> bool:
        """
        Save Understat raw shot data to bronze layer

        Args:
            match_id: Unique match identifier
            raw_shots: Raw shot data dictionary
            match_url: URL of Understat match page
            scrape_run_id: ID of scrape run for tracking

        Returns:
            True if successful
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    query = """
                        INSERT INTO bronze.understat_raw
                            (match_id, match_url, raw_shots, scrape_run_id, scraped_at)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (match_id)
                        DO UPDATE SET
                            raw_shots = EXCLUDED.raw_shots,
                            match_url = EXCLUDED.match_url,
                            scraped_at = EXCLUDED.scraped_at,
                            updated_at = CURRENT_TIMESTAMP
                        RETURNING id
                    """

                    cur.execute(query, (
                        match_id,
                        match_url,
                        Json(raw_shots),
                        scrape_run_id,
                        datetime.utcnow()
                    ))

                    result = cur.fetchone()
                    logger.info(f"Saved Understat data for match {match_id} (ID: {result[0]})")

            return True

        except Exception as e:
            logger.error(f"Failed to save Understat data: {e}")
            return False

    def create_scrape_run(
        self,
        run_id: str,
        match_id: str,
        scrape_type: str,
        dag_run_id: Optional[str] = None
    ) -> bool:
        """
        Create a scrape run record for tracking

        Args:
            run_id: Unique run ID
            match_id: Match being scraped
            scrape_type: Type of scrape ('fbref', 'understat', 'fixture')
            dag_run_id: Airflow DAG run ID

        Returns:
            True if successful
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    query = """
                        INSERT INTO bronze.scrape_runs
                            (run_id, dag_run_id, match_id, scrape_type, status, started_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (run_id) DO NOTHING
                    """

                    cur.execute(query, (
                        run_id,
                        dag_run_id,
                        match_id,
                        scrape_type,
                        'running',
                        datetime.utcnow()
                    ))

            logger.info(f"Created scrape run: {run_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to create scrape run: {e}")
            return False

    def update_scrape_run(
        self,
        run_id: str,
        status: str,
        records_scraped: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Update scrape run status

        Args:
            run_id: Scrape run ID
            status: Status ('success', 'failed', 'partial')
            records_scraped: Number of records scraped
            error_message: Error message if failed

        Returns:
            True if successful
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    query = """
                        UPDATE bronze.scrape_runs
                        SET status = %s,
                            records_scraped = %s,
                            error_message = %s,
                            completed_at = %s
                        WHERE run_id = %s
                    """

                    cur.execute(query, (
                        status,
                        records_scraped,
                        error_message,
                        datetime.utcnow(),
                        run_id
                    ))

            logger.info(f"Updated scrape run {run_id}: {status}")
            return True

        except Exception as e:
            logger.error(f"Failed to update scrape run: {e}")
            return False

    def get_latest_scrape_for_match(self, match_id: str, scrape_type: str) -> Optional[Dict]:
        """
        Get latest successful scrape for a match

        Args:
            match_id: Match ID
            scrape_type: Type of scrape

        Returns:
            Scrape run dict or None
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    query = """
                        SELECT run_id, status, scraped_at, records_scraped
                        FROM bronze.scrape_runs
                        WHERE match_id = %s
                          AND scrape_type = %s
                          AND status = 'success'
                        ORDER BY completed_at DESC
                        LIMIT 1
                    """

                    cur.execute(query, (match_id, scrape_type))
                    row = cur.fetchone()

                    if row:
                        return {
                            'run_id': row[0],
                            'status': row[1],
                            'scraped_at': row[2],
                            'records_scraped': row[3]
                        }

            return None

        except Exception as e:
            logger.error(f"Failed to get latest scrape: {e}")
            return None

    def check_match_exists(self, match_id: str) -> bool:
        """
        Check if match data already exists in bronze layer

        Args:
            match_id: Match ID to check

        Returns:
            True if exists
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    query = "SELECT 1 FROM bronze.fbref_raw WHERE match_id = %s LIMIT 1"
                    cur.execute(query, (match_id,))
                    return cur.fetchone() is not None

        except Exception as e:
            logger.error(f"Failed to check match existence: {e}")
            return False

    def save_fbref_lineups(
        self,
        match_url: str,
        lineup_data: Dict[str, Any],
        match_id: Optional[str] = None,
        scrape_run_id: Optional[str] = None
    ) -> bool:
        """
        Save FBref lineup data to bronze layer

        Args:
            match_url: FBref match report URL
            lineup_data: Lineup data dictionary with home_lineup and away_lineup
            match_id: Optional match ID
            scrape_run_id: ID of scrape run for tracking

        Returns:
            True if successful
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    query = """
                        INSERT INTO bronze.fbref_lineups
                            (match_id, match_url, raw_lineups, scrape_run_id, scraped_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (match_url, scraped_at)
                        DO UPDATE SET
                            raw_lineups = EXCLUDED.raw_lineups,
                            match_id = EXCLUDED.match_id,
                            scrape_run_id = EXCLUDED.scrape_run_id,
                            updated_at = CURRENT_TIMESTAMP
                        RETURNING id
                    """

                    cur.execute(query, (
                        match_id,
                        match_url,
                        Json(lineup_data),
                        scrape_run_id,
                        datetime.utcnow(),
                        datetime.utcnow()
                    ))

                    result = cur.fetchone()
                    logger.info(f"Saved FBref lineups (ID: {result[0]})")

            return True

        except Exception as e:
            logger.error(f"Failed to save FBref lineups: {e}")
            return False
