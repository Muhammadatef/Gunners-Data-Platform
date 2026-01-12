"""
Arsenal Match Auto-Scraper DAG

This DAG automatically scrapes Arsenal match data after matches finish.
It runs every 2 hours and checks for new completed matches.

Schedule: Every 2 hours
- Checks for newly completed matches
- Scrapes shot data from Understat using Playwright
- Loads data to bronze.understat_raw
- Triggers dbt transformations
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import sys
import uuid
import logging

# Add scrapers to path
sys.path.insert(0, '/opt/airflow/scrapers')

from playwright_scraper import UnderstatPlaywrightScraper
from db_loader import DatabaseLoader

logger = logging.getLogger(__name__)


def check_and_scrape_new_matches(**context):
    """
    Check for newly completed Arsenal matches and scrape them

    Logic:
    1. Get all Arsenal fixtures for current season
    2. Filter for played matches (is_result=True)
    3. Check which matches are NOT in database
    4. Scrape and load new matches
    """
    scraper = UnderstatPlaywrightScraper()
    loader = DatabaseLoader()

    # Get current season (e.g., "2025" for 2025-26 season)
    current_year = datetime.now().year
    season = str(current_year) if datetime.now().month >= 8 else str(current_year - 1)

    logger.info(f"Checking for new Arsenal matches in {season}-{int(season)+1} season")

    # Get all fixtures for current season
    fixtures = scraper.scrape_season_fixtures(season)
    played_matches = [f for f in fixtures if f['is_result']]

    logger.info(f"Found {len(played_matches)} played matches in {season}-{int(season)+1}")

    # Get existing matches from database
    with loader.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT DISTINCT match_url
                FROM bronze.understat_raw
                WHERE match_url IS NOT NULL
            """)
            existing_urls = set(row[0] for row in cur.fetchall())

    logger.info(f"Found {len(existing_urls)} existing matches in database")

    # Find new matches
    new_matches = [f for f in played_matches if f['match_url'] not in existing_urls]

    if not new_matches:
        logger.info("No new matches to scrape")
        return {"new_matches": 0, "scraped": 0}

    logger.info(f"Found {len(new_matches)} new matches to scrape")

    # Scrape new matches
    scraped = 0
    for fixture in new_matches:
        try:
            home = fixture['home_team']
            away = fixture['away_team']
            date = fixture['match_date']

            logger.info(f"Scraping {date}: {home} vs {away}")

            # Scrape match data
            match_data = scraper.scrape_match_shots(fixture['match_url'])

            # Save to database
            run_id = f"auto_{uuid.uuid4().hex[:8]}"
            match_id = match_data['match_id']

            loader.create_scrape_run(run_id, match_id, 'understat', context['dag_run'].run_id)
            loader.save_understat_raw(match_id, match_data, fixture['match_url'], run_id)
            loader.update_scrape_run(run_id, 'success', len(match_data['shots']))

            logger.info(f"✓ Scraped {home} vs {away}: {len(match_data['shots'])} shots")
            scraped += 1

            # Small delay to be polite
            import time
            time.sleep(2)

        except Exception as e:
            logger.error(f"Error scraping {fixture['match_url']}: {e}")
            continue

    logger.info(f"Scraping complete: {scraped}/{len(new_matches)} matches scraped")

    return {
        "new_matches": len(new_matches),
        "scraped": scraped,
        "season": f"{season}-{int(season)+1}"
    }


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
    'arsenal_auto_match_scraper',
    default_args=default_args,
    description='Automatically scrape Arsenal matches after they finish',
    schedule_interval='0 */2 * * *',  # Every 2 hours
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['arsenal', 'scraping', 'auto'],
) as dag:

    # Task 1: Check for and scrape new matches
    scrape_new_matches = PythonOperator(
        task_id='scrape_new_matches',
        python_callable=check_and_scrape_new_matches,
        provide_context=True,
    )

    # Task 2: Run dbt transformations on new data
    run_dbt_transformations = BashOperator(
        task_id='run_dbt_transformations',
        bash_command='cd /opt/airflow/dbt && dbt run --profiles-dir .',
    )

    # Task 3: Run dbt tests
    run_dbt_tests = BashOperator(
        task_id='run_dbt_tests',
        bash_command='cd /opt/airflow/dbt && dbt test --profiles-dir .',
    )

    # Set dependencies
    scrape_new_matches >> run_dbt_transformations >> run_dbt_tests
