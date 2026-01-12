"""
Arsenal Smart Match Scraper DAG

This DAG intelligently schedules itself based on Arsenal's actual match times:
1. Fetches upcoming Arsenal fixtures from Understat
2. Finds the next unplayed match
3. Schedules scraping for 2 hours after match kickoff time
4. Uses Airflow sensors to wait for the right time

Schedule: Dynamic - based on Arsenal's match schedule
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.python import PythonSensor
from airflow.operators.bash import BashOperator
import sys
import uuid
import logging

sys.path.insert(0, '/opt/airflow/scrapers')

from playwright_scraper import UnderstatPlaywrightScraper
from db_loader import DatabaseLoader

logger = logging.getLogger(__name__)


def get_next_arsenal_match(**context):
    """
    Fetch Arsenal's fixture list and find the next match

    Returns:
        dict: Next match details (date, time, opponent, competition)
    """
    scraper = UnderstatPlaywrightScraper()

    # Get current season
    current_year = datetime.now().year
    season = str(current_year) if datetime.now().month >= 8 else str(current_year - 1)

    logger.info(f"Checking Arsenal fixtures for {season}-{int(season)+1} season")

    # Get all fixtures
    fixtures = scraper.scrape_season_fixtures(season)

    # Filter for upcoming matches (not yet played)
    upcoming = [f for f in fixtures if not f['is_result']]

    if not upcoming:
        logger.warning("No upcoming Arsenal matches found!")
        return None

    # Sort by date to get next match
    upcoming.sort(key=lambda x: x['match_date'])
    next_match = upcoming[0]

    logger.info(f"Next Arsenal match: {next_match['home_team']} vs {next_match['away_team']} on {next_match['match_date']}")

    # Push to XCom for other tasks
    context['task_instance'].xcom_push(key='next_match', value=next_match)

    return next_match


def wait_for_match_completion(**context):
    """
    Check if the next match has been completed (data available)

    This runs as a sensor - checks every 10 minutes if match data is ready
    """
    next_match = context['task_instance'].xcom_pull(key='next_match', task_ids='get_next_match')

    if not next_match:
        return True  # No match found, don't wait

    match_date = next_match['match_date']
    match_datetime = datetime.strptime(match_date, '%Y-%m-%d')

    # Assume typical match time: 3:00 PM local time (15:00)
    # Match duration: ~2 hours
    # Data availability: +30 min processing time
    # Total wait: Match time + 2.5 hours

    estimated_match_time = match_datetime.replace(hour=15, minute=0)
    data_available_time = estimated_match_time + timedelta(hours=2, minutes=30)

    current_time = datetime.now()

    logger.info(f"Match date: {match_date}")
    logger.info(f"Estimated data availability: {data_available_time}")
    logger.info(f"Current time: {current_time}")

    # Check if we're past the data availability time
    if current_time >= data_available_time:
        logger.info("Match data should be available now!")
        return True
    else:
        wait_time = (data_available_time - current_time).total_seconds() / 60
        logger.info(f"Waiting {wait_time:.0f} more minutes for match data...")
        return False


def scrape_latest_completed_match(**context):
    """
    Scrape the most recently completed Arsenal match
    """
    scraper = UnderstatPlaywrightScraper()
    loader = DatabaseLoader()

    # Get current season
    current_year = datetime.now().year
    season = str(current_year) if datetime.now().month >= 8 else str(current_year - 1)

    logger.info(f"Scraping latest Arsenal match from {season} season")

    # Get all fixtures
    fixtures = scraper.scrape_season_fixtures(season)
    played_matches = [f for f in fixtures if f['is_result']]

    if not played_matches:
        logger.warning("No played matches found")
        return {"status": "no_matches"}

    # Sort by date (most recent first)
    played_matches.sort(key=lambda x: x['match_date'], reverse=True)

    # Get existing matches from database
    with loader.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT DISTINCT match_url
                FROM bronze.understat_raw
                WHERE match_url IS NOT NULL
            """)
            existing_urls = set(row[0] for row in cur.fetchall())

    # Find the most recent match not in database
    latest_match = None
    for fixture in played_matches:
        if fixture['match_url'] not in existing_urls:
            latest_match = fixture
            break

    if not latest_match:
        logger.info("All matches are already scraped - database is up to date!")
        return {"status": "up_to_date"}

    # Scrape the latest match
    try:
        home = latest_match['home_team']
        away = latest_match['away_team']
        date = latest_match['match_date']

        logger.info(f"Scraping: {date} - {home} vs {away}")

        # Scrape
        match_data = scraper.scrape_match_shots(latest_match['match_url'])

        # Save
        run_id = f"smart_{uuid.uuid4().hex[:8]}"
        match_id = match_data['match_id']

        loader.create_scrape_run(run_id, match_id, 'understat', context['dag_run'].run_id)
        loader.save_understat_raw(match_id, match_data, latest_match['match_url'], run_id)
        loader.update_scrape_run(run_id, 'success', len(match_data['shots']))

        logger.info(f"✓ Successfully scraped {home} vs {away}")
        logger.info(f"  Score: {match_data['home_goals']}-{match_data['away_goals']}")
        logger.info(f"  xG: {match_data['home_xg']:.2f} - {match_data['away_xg']:.2f}")
        logger.info(f"  Shots: {len(match_data['shots'])}")

        return {
            "status": "success",
            "match": f"{home} vs {away}",
            "date": date,
            "shots": len(match_data['shots'])
        }

    except Exception as e:
        logger.error(f"Error scraping match: {e}")
        return {"status": "error", "error": str(e)}


# DAG definition
default_args = {
    'owner': 'arsenal_analytics',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'arsenal_smart_match_scraper',
    default_args=default_args,
    description='Smart scraper that schedules based on Arsenal match times',
    schedule_interval='0 */6 * * *',  # Check every 6 hours for upcoming matches
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['arsenal', 'scraping', 'smart'],
) as dag:

    # Task 1: Get next Arsenal match
    get_next_match = PythonOperator(
        task_id='get_next_match',
        python_callable=get_next_arsenal_match,
    )

    # Task 2: Wait for match to complete (sensor)
    wait_for_match = PythonSensor(
        task_id='wait_for_match_completion',
        python_callable=wait_for_match_completion,
        poke_interval=600,  # Check every 10 minutes
        timeout=86400,  # Timeout after 24 hours
        mode='reschedule',  # Don't block worker slot while waiting
    )

    # Task 3: Scrape the completed match
    scrape_match = PythonOperator(
        task_id='scrape_completed_match',
        python_callable=scrape_latest_completed_match,
    )

    # Task 4: Run dbt transformations
    run_dbt = BashOperator(
        task_id='run_dbt_transformations',
        bash_command='cd /opt/airflow/dbt && dbt run --profiles-dir .',
    )

    # Set dependencies
    get_next_match >> wait_for_match >> scrape_match >> run_dbt
