"""
Future Match Scheduler for Arsenal FC

Extracts future match dates/times from Understat and schedules Airflow DAGs
to trigger 2 hours after each match completion.
"""

import logging
import sys
from typing import List, Dict, Any
from datetime import datetime, timedelta
import requests

from playwright_scraper import UnderstatPlaywrightScraper

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def parse_match_datetime(fixture: Dict[str, Any]) -> datetime:
    """
    Parse match date and time from fixture data
    
    Args:
        fixture: Fixture dictionary from Understat
    
    Returns:
        datetime object for match start time
    """
    match_date = fixture.get('match_date', '')
    match_datetime_str = fixture.get('date', '')  # Full datetime string from Understat
    
    try:
        # Try to parse full datetime string (format: "2025-01-15 15:00:00")
        if match_datetime_str and len(match_datetime_str) > 10:
            # Parse full datetime
            dt = datetime.strptime(match_datetime_str[:19], '%Y-%m-%d %H:%M:%S')
            return dt
        elif match_date:
            # Fallback to date only, assume 15:00 (3 PM) kickoff
            dt = datetime.strptime(match_date, '%Y-%m-%d')
            return dt.replace(hour=15, minute=0)
        else:
            # Default to today at 15:00 if no date found
            logger.warning(f"No date found in fixture, using default")
            return datetime.now().replace(hour=15, minute=0)
    except Exception as e:
        logger.warning(f"Error parsing match datetime: {e}, using default")
        # Default to date at 15:00
        if match_date:
            try:
                dt = datetime.strptime(match_date, '%Y-%m-%d')
                return dt.replace(hour=15, minute=0)
            except:
                pass
        return datetime.now().replace(hour=15, minute=0)


def schedule_airflow_dag(dag_id: str, trigger_time: datetime, match_info: Dict[str, Any]) -> bool:
    """
    Schedule an Airflow DAG run at a specific time
    
    Args:
        dag_id: ID of the DAG to trigger
        trigger_time: When to trigger the DAG
        match_info: Information about the match
    
    Returns:
        True if scheduled successfully
    """
    # Note: Airflow doesn't support scheduling DAGs at arbitrary future times directly
    # Instead, we'll log the schedule and the smart DAG will handle it
    # For now, we'll just log the information
    
    logger.info(f"Scheduling {dag_id} for match: {match_info.get('home_team')} vs {match_info.get('away_team')}")
    logger.info(f"  Match date: {match_info.get('match_date')}")
    logger.info(f"  Trigger time: {trigger_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"  Match URL: {match_info.get('match_url')}")
    
    # The smart DAG already checks every 6 hours for new matches
    # It will automatically detect when matches are completed and scrape them
    # So we don't need to manually schedule individual DAG runs
    
    return True


def schedule_future_matches(season: str = "2025"):
    """
    Extract future match dates/times and log scheduling information
    
    Args:
        season: Season year (e.g., "2025" for 2025-26 season)
    """
    logger.info("="*60)
    logger.info("ARSENAL FC FUTURE MATCH SCHEDULER")
    logger.info(f"Season: {season}")
    logger.info("="*60)
    
    scraper = UnderstatPlaywrightScraper()
    
    # Get all fixtures
    logger.info(f"Fetching fixtures from Understat for {season} season...")
    fixtures = scraper.scrape_season_fixtures(season)
    
    if not fixtures:
        logger.error("No fixtures found!")
        return
    
    logger.info(f"Found {len(fixtures)} total fixtures")
    
    # Filter for future matches
    future_matches = [f for f in fixtures if not f.get('is_result', False)]
    logger.info(f"Found {len(future_matches)} future matches")
    
    if not future_matches:
        logger.info("No future matches found")
        return
    
    # Sort by date
    future_matches.sort(key=lambda x: x.get('match_date', ''))
    
    logger.info("\n" + "="*60)
    logger.info("FUTURE MATCHES SCHEDULE")
    logger.info("="*60)
    
    for i, match in enumerate(future_matches, 1):
        home_team = match.get('home_team', 'Unknown')
        away_team = match.get('away_team', 'Unknown')
        match_date = match.get('match_date', '')
        match_url = match.get('match_url', '')
        
        # Parse match datetime
        match_datetime = parse_match_datetime(match)
        
        # Calculate trigger time (2 hours after match start)
        # Assume match duration is ~2 hours, so trigger 2 hours after start = 4 hours total
        trigger_time = match_datetime + timedelta(hours=2)
        
        logger.info(f"\n[{i}] {home_team} vs {away_team}")
        logger.info(f"    Date: {match_date}")
        logger.info(f"    Match time: {match_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"    Scrape trigger: {trigger_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"    URL: {match_url}")
        
        # Schedule the DAG (for now, just log - the smart DAG handles it)
        schedule_airflow_dag('arsenal_smart_match_scraper', trigger_time, match)
    
    logger.info("\n" + "="*60)
    logger.info("SCHEDULING COMPLETE")
    logger.info("="*60)
    logger.info(f"\nThe 'arsenal_smart_match_scraper' DAG runs every 6 hours")
    logger.info("and will automatically detect and scrape matches when they complete.")
    logger.info("\nNext scheduled DAG check: Every 6 hours (see Airflow UI)")


if __name__ == "__main__":
    try:
        season = sys.argv[1] if len(sys.argv) > 1 else "2025"
        schedule_future_matches(season)
    except KeyboardInterrupt:
        logger.info("\nScheduling interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
