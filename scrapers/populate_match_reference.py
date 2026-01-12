"""
Populate bronze.match_reference table with match metadata
"""

import sys
sys.path.insert(0, '/opt/airflow/scrapers')

from playwright_scraper import UnderstatPlaywrightScraper
from db_loader import DatabaseLoader

def populate_match_reference():
    """Populate match reference table from scraped fixtures"""
    scraper = UnderstatPlaywrightScraper()
    loader = DatabaseLoader()

    print('Fetching fixtures metadata...')

    # Get fixtures from both seasons
    fixtures_2024 = scraper.scrape_season_fixtures('2024')
    played_2024 = [f for f in fixtures_2024 if f['is_result']]

    fixtures_2025 = scraper.scrape_season_fixtures('2025')
    played_2025 = [f for f in fixtures_2025 if f['is_result']]

    all_matches = played_2024 + played_2025

    print(f'Found {len(all_matches)} matches to populate')

    inserted = 0
    with loader.get_connection() as conn:
        with conn.cursor() as cur:
            for match in all_matches:
                try:
                    # Determine season based on date
                    match_year = int(match['match_date'][:4])
                    match_month = int(match['match_date'][5:7])

                    # English season runs Aug-May, so Aug 2024 - May 2025 is "2024-25"
                    if match_month >= 8:
                        season = f"{match_year}-{str(match_year + 1)[-2:]}"
                    else:
                        season = f"{match_year - 1}-{str(match_year)[-2:]}"

                    cur.execute("""
                        INSERT INTO bronze.match_reference
                        (match_url, match_date, home_team, away_team, season)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (match_url) DO UPDATE SET
                            match_date = EXCLUDED.match_date,
                            home_team = EXCLUDED.home_team,
                            away_team = EXCLUDED.away_team,
                            season = EXCLUDED.season
                    """, (
                        match['match_url'],
                        match['match_date'],
                        match['home_team'],
                        match['away_team'],
                        season
                    ))
                    inserted += 1
                except Exception as e:
                    print(f"Error inserting {match['match_url']}: {e}")
                    continue

    print(f'✓ Inserted/updated {inserted} match records')

if __name__ == '__main__':
    populate_match_reference()
