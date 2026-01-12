#!/usr/bin/env python3
"""
Fixed Historical Backfill Script - Passes team metadata to scraper
"""
import sys
sys.path.insert(0, '/opt/airflow/scrapers')

import uuid
import time
from playwright_scraper import UnderstatPlaywrightScraper
from db_loader import DatabaseLoader

print('=== Arsenal Complete Season Backfill (Fixed) ===')
print('Scraping 2024-25 season with metadata')
print()

scraper = UnderstatPlaywrightScraper()
loader = DatabaseLoader()

# Get fixtures from 2024-25 season
print('[1/1] Fetching 2024-25 fixtures...')
fixtures_2024 = scraper.scrape_season_fixtures('2024')
played_2024 = [f for f in fixtures_2024 if f['is_result']]
print(f'      Found {len(played_2024)} played matches')
print()

print(f'=== Starting scrape of {len(played_2024)} matches ===')
print()

success_count = 0
error_count = 0
errors = []

for i, fixture in enumerate(played_2024, 1):
    home = fixture['home_team']
    away = fixture['away_team']
    date = fixture['match_date']

    print(f'[{i}/{len(played_2024)}] {date}: {home} vs {away}', end=' ')

    try:
        # Scrape match WITH metadata from fixtures
        match_data = scraper.scrape_match_shots(
            fixture['match_url'],
            home_team=home,
            away_team=away,
            match_date=date
        )

        # Save to database
        run_id = f'backfill_fixed_{uuid.uuid4().hex[:8]}'
        match_id = match_data['match_id']

        loader.create_scrape_run(run_id, match_id, 'understat', None)
        loader.save_understat_raw(match_id, match_data, fixture['match_url'], run_id)
        loader.update_scrape_run(run_id, 'success', len(match_data['shots']))

        shots = len(match_data['shots'])
        xg_home = match_data['home_xg']
        xg_away = match_data['away_xg']
        print(f'✓ ({shots} shots, xG: {xg_home:.2f}-{xg_away:.2f})')

        success_count += 1

        # Rate limit
        time.sleep(2)

    except Exception as e:
        error_msg = str(e)[:100]
        print(f'✗ Error: {error_msg}')
        errors.append(f'{home} vs {away}: {error_msg}')
        error_count += 1
        continue

print()
print('=== Backfill Complete ===')
print(f'✓ Success: {success_count} matches')
print(f'✗ Errors: {error_count} matches')

if errors:
    print('\nFailed matches:')
    for error in errors:
        print(f'  - {error}')

print()
print('Dashboard: http://localhost:8501')
