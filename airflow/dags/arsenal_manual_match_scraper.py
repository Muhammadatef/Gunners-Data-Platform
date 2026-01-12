"""
Arsenal Manual Match Scraper DAG

This DAG allows manual triggering to scrape a specific match or all new matches.
Use this right after a match finishes to immediately get the data.

Trigger: Manual (no schedule)
Use case: Arsenal just played, you want data NOW for the dashboard
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.models import Variable
import sys
import uuid
import logging

sys.path.insert(0, '/opt/airflow/scrapers')

from playwright_scraper import UnderstatPlaywrightScraper
from db_loader import DatabaseLoader

logger = logging.getLogger(__name__)


def scrape_latest_match(**context):
    """
    Scrape the most recent Arsenal match

    This will scrape the latest completed match that's not in the database.
    Perfect for running 2 hours after a match finishes.
    """
    scraper = UnderstatPlaywrightScraper()
    loader = DatabaseLoader()

    # Get current season
    current_year = datetime.now().year
    season = str(current_year) if datetime.now().month >= 8 else str(current_year - 1)

    logger.info(f"Looking for latest Arsenal match in {season}-{int(season)+1}")

    # Get fixtures
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
    latest_new_match = None
    for fixture in played_matches:
        if fixture['match_url'] not in existing_urls:
            latest_new_match = fixture
            break

    if not latest_new_match:
        logger.info("No new matches to scrape - all matches up to date!")
        return {"status": "up_to_date"}

    # Scrape the latest match
    try:
        home = latest_new_match['home_team']
        away = latest_new_match['away_team']
        date = latest_new_match['match_date']

        logger.info(f"Scraping latest match: {date} - {home} vs {away}")

        # Scrape
        match_data = scraper.scrape_match_shots(latest_new_match['match_url'])

        # Save
        run_id = f"manual_{uuid.uuid4().hex[:8]}"
        match_id = match_data['match_id']

        loader.create_scrape_run(run_id, match_id, 'understat', context['dag_run'].run_id)
        loader.save_understat_raw(match_id, match_data, latest_new_match['match_url'], run_id)
        loader.update_scrape_run(run_id, 'success', len(match_data['shots']))

        logger.info(f"✓ Successfully scraped {home} vs {away}")
        logger.info(f"  Score: {match_data['home_goals']}-{match_data['away_goals']}")
        logger.info(f"  xG: {match_data['home_xg']:.2f} - {match_data['away_xg']:.2f}")
        logger.info(f"  Shots: {len(match_data['shots'])}")

        return {
            "status": "success",
            "match": f"{home} vs {away}",
            "date": date,
            "shots": len(match_data['shots']),
            "xg_home": match_data['home_xg'],
            "xg_away": match_data['away_xg']
        }

    except Exception as e:
        logger.error(f"Error scraping match: {e}")
        return {"status": "error", "error": str(e)}


def scrape_all_missing_matches(**context):
    """
    Scrape ALL missing matches from current season

    Use this if multiple matches were played and you want to catch up.
    """
    scraper = UnderstatPlaywrightScraper()
    loader = DatabaseLoader()

    current_year = datetime.now().year
    season = str(current_year) if datetime.now().month >= 8 else str(current_year - 1)

    logger.info(f"Scraping all missing matches for {season}-{int(season)+1}")

    # Get fixtures
    fixtures = scraper.scrape_season_fixtures(season)
    played_matches = [f for f in fixtures if f['is_result']]

    # Get existing matches
    with loader.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT DISTINCT match_url
                FROM bronze.understat_raw
                WHERE match_url IS NOT NULL
            """)
            existing_urls = set(row[0] for row in cur.fetchall())

    # Find missing matches
    missing_matches = [f for f in played_matches if f['match_url'] not in existing_urls]

    if not missing_matches:
        logger.info("All matches up to date!")
        return {"status": "up_to_date", "missing": 0}

    logger.info(f"Found {len(missing_matches)} missing matches")

    # Scrape all missing
    scraped = 0
    for fixture in missing_matches:
        try:
            match_data = scraper.scrape_match_shots(fixture['match_url'])
            run_id = f"manual_{uuid.uuid4().hex[:8]}"
            match_id = match_data['match_id']

            loader.create_scrape_run(run_id, match_id, 'understat', context['dag_run'].run_id)
            loader.save_understat_raw(match_id, match_data, fixture['match_url'], run_id)
            loader.update_scrape_run(run_id, 'success', len(match_data['shots']))

            logger.info(f"✓ {fixture['home_team']} vs {fixture['away_team']}")
            scraped += 1

            import time
            time.sleep(2)

        except Exception as e:
            logger.error(f"Error scraping {fixture['match_url']}: {e}")
            continue

    return {"status": "success", "missing": len(missing_matches), "scraped": scraped}


# DAG definition
default_args = {
    'owner': 'arsenal_analytics',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

with DAG(
    'arsenal_manual_match_scraper',
    default_args=default_args,
    description='Manually trigger scraping of latest Arsenal match',
    schedule_interval=None,  # Manual trigger only
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['arsenal', 'scraping', 'manual'],
) as dag:

    # Task 1: Scrape latest match
    scrape_latest = PythonOperator(
        task_id='scrape_latest_match',
        python_callable=scrape_latest_match,
        provide_context=True,
    )

    # Task 2: Run dbt transformations
    run_dbt = BashOperator(
        task_id='run_dbt_transformations',
        bash_command='cd /opt/airflow/dbt && dbt run --profiles-dir .',
    )

    # Task 3: Test data quality
    test_dbt = BashOperator(
        task_id='test_data_quality',
        bash_command='cd /opt/airflow/dbt && dbt test --profiles-dir .',
    )

    scrape_latest >> run_dbt >> test_dbt
