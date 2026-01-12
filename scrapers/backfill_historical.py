"""
Historical Data Backfill - Arsenal FC Season 2025-26

This module scrapes all Arsenal matches for the current season from Understat,
enabling immediate dashboard usability with full season context.
"""

import logging
import re
import json
from typing import List, Dict, Any
from datetime import datetime
import time

from understat_scraper import UnderstatScraper
from fbref_scraper import FBrefScraper
from db_loader import DatabaseLoader
from config import config
from utils import generate_match_id, rate_limit

logger = logging.getLogger(__name__)


class HistoricalDataBackfill:
    """Backfill historical Arsenal match data for current season"""

    def __init__(self, season: str = "2026"):
        """
        Initialize backfill scraper

        Args:
            season: Season year (e.g., "2026" for 2025-26 season)
        """
        self.season = season
        self.understat_scraper = UnderstatScraper()
        self.fbref_scraper = FBrefScraper()
        self.loader = DatabaseLoader()

    def get_season_fixtures(self) -> List[Dict[str, Any]]:
        """
        Get all Arsenal fixtures for the season from Understat

        Returns:
            List of fixture dictionaries with match details
        """
        logger.info(f"Fetching Arsenal fixtures for season {self.season}...")

        fixtures = self.understat_scraper.scrape_season_fixtures(self.season)

        logger.info(f"Found {len(fixtures)} fixtures")

        # Filter only finished matches
        finished_matches = [f for f in fixtures if f.get('is_result', False)]

        logger.info(f"Finished matches: {len(finished_matches)}")

        return finished_matches

    def backfill_all_matches(
        self,
        dry_run: bool = False,
        skip_existing: bool = True
    ) -> Dict[str, Any]:
        """
        Backfill all historical matches for the season

        Args:
            dry_run: If True, only print what would be done (no actual scraping)
            skip_existing: If True, skip matches already in database

        Returns:
            Summary dictionary with success/failure counts
        """
        logger.info("="*60)
        logger.info("ARSENAL FC HISTORICAL DATA BACKFILL")
        logger.info(f"Season: {self.season}")
        logger.info(f"Dry run: {dry_run}")
        logger.info("="*60)

        # Get all finished matches
        fixtures = self.get_season_fixtures()

        if not fixtures:
            logger.warning("No fixtures found. Exiting.")
            return {'success': 0, 'skipped': 0, 'failed': 0}

        summary = {
            'total': len(fixtures),
            'success': 0,
            'skipped': 0,
            'failed': 0,
            'matches': []
        }

        for i, fixture in enumerate(fixtures, 1):
            logger.info(f"\n[{i}/{len(fixtures)}] Processing match...")

            try:
                result = self.backfill_single_match(
                    fixture,
                    dry_run=dry_run,
                    skip_existing=skip_existing
                )

                summary['matches'].append(result)

                if result['status'] == 'success':
                    summary['success'] += 1
                elif result['status'] == 'skipped':
                    summary['skipped'] += 1
                else:
                    summary['failed'] += 1

            except Exception as e:
                logger.error(f"Error processing match: {e}")
                summary['failed'] += 1
                summary['matches'].append({
                    'match_id': fixture.get('match_id'),
                    'status': 'failed',
                    'error': str(e)
                })

            # Rate limiting between matches
            if i < len(fixtures) and not dry_run:
                logger.debug(f"Rate limiting: waiting {config.UNDERSTAT_REQUEST_DELAY}s...")
                time.sleep(config.UNDERSTAT_REQUEST_DELAY)

        # Print summary
        logger.info("\n" + "="*60)
        logger.info("BACKFILL SUMMARY")
        logger.info("="*60)
        logger.info(f"Total matches: {summary['total']}")
        logger.info(f"✓ Success: {summary['success']}")
        logger.info(f"⊘ Skipped: {summary['skipped']}")
        logger.info(f"✗ Failed: {summary['failed']}")
        logger.info("="*60)

        return summary

    def backfill_single_match(
        self,
        fixture: Dict[str, Any],
        dry_run: bool = False,
        skip_existing: bool = True
    ) -> Dict[str, Any]:
        """
        Backfill a single match

        Args:
            fixture: Fixture dictionary from Understat
            dry_run: If True, only print (no scraping)
            skip_existing: If True, skip if already in database

        Returns:
            Result dictionary with status
        """
        home_team = fixture.get('home_team', '')
        away_team = fixture.get('away_team', '')
        date_str = fixture.get('date', '')

        # Parse date (Understat format: "2026-01-03 20:00:00")
        try:
            match_date = datetime.strptime(date_str.split()[0], '%Y-%m-%d').date()
        except:
            match_date_str = date_str[:10] if date_str else "unknown"
            match_date = None

        match_id = generate_match_id(home_team, away_team, str(match_date))
        understat_match_url = fixture.get('match_url', '')

        logger.info(f"Match: {home_team} vs {away_team} ({match_date})")
        logger.info(f"Match ID: {match_id}")

        # Check if already exists
        if skip_existing:
            exists = self.loader.check_match_exists(match_id)
            if exists:
                logger.info(f"⊘ Skipped (already in database)")
                return {
                    'match_id': match_id,
                    'home_team': home_team,
                    'away_team': away_team,
                    'date': str(match_date),
                    'status': 'skipped',
                    'reason': 'already_exists'
                }

        if dry_run:
            logger.info(f"[DRY RUN] Would scrape: {understat_match_url}")
            return {
                'match_id': match_id,
                'status': 'dry_run'
            }

        # Scrape Understat shot data
        logger.info(f"Scraping Understat: {understat_match_url}")
        try:
            understat_data = self.understat_scraper.scrape_match_shots(understat_match_url)
            shot_count = (
                len(understat_data.get('home_shots', [])) +
                len(understat_data.get('away_shots', []))
            )
            logger.info(f"✓ Understat: {shot_count} shots scraped")
        except Exception as e:
            logger.warning(f"⚠ Understat scraping failed: {e}")
            understat_data = None

        # Try to find FBref match URL
        # Note: This requires mapping Understat match to FBref
        # For now, we'll skip FBref in backfill (can add later)
        # The fixture monitor DAG will handle FBref going forward

        logger.info(f"⚠ FBref scraping skipped for backfill (Understat only)")
        logger.info(f"  → Reason: FBref match URL mapping not implemented yet")
        logger.info(f"  → Impact: Player stats limited, but xG data available")

        # Save Understat data
        if understat_data:
            scrape_run_id = f"backfill_{self.season}_{match_id}"

            success = self.loader.save_understat_raw(
                match_id=match_id,
                raw_shots=understat_data,
                match_url=understat_match_url,
                scrape_run_id=scrape_run_id
            )

            if success:
                logger.info(f"✓ Data saved to bronze layer")
                return {
                    'match_id': match_id,
                    'home_team': home_team,
                    'away_team': away_team,
                    'date': str(match_date),
                    'status': 'success',
                    'shots_scraped': shot_count,
                    'fbref_scraped': False
                }
            else:
                logger.error(f"✗ Failed to save data")
                return {
                    'match_id': match_id,
                    'status': 'failed',
                    'error': 'database_save_failed'
                }
        else:
            return {
                'match_id': match_id,
                'status': 'failed',
                'error': 'understat_scraping_failed'
            }

    def create_stub_fbref_data(
        self,
        fixture: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create minimal FBref-like data structure from Understat fixture

        This allows the pipeline to run even without FBref data.
        Player-level stats will be missing, but team-level xG is available.

        Args:
            fixture: Understat fixture dictionary

        Returns:
            Minimal FBref-compatible data structure
        """
        home_team = fixture.get('home_team', '')
        away_team = fixture.get('away_team', '')

        # Extract score from fixture (if available)
        # Understat includes goals in fixture data
        home_goals = fixture.get('goals', {}).get('h', 0)
        away_goals = fixture.get('goals', {}).get('a', 0)

        stub_data = {
            'match_url': 'backfill_stub',
            'scraped_at': datetime.utcnow().isoformat(),
            'match_metadata': {
                'home_team': home_team,
                'away_team': away_team,
                'home_score': home_goals,
                'away_score': away_goals,
                'venue': None,
                'attendance': None,
                'referee': None
            },
            'team_stats': {
                'home': {},
                'away': {}
            },
            'player_stats': []  # Empty - no player data from backfill
        }

        return stub_data


# CLI interface for manual backfill
if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Parse args
    season = sys.argv[1] if len(sys.argv) > 1 else "2026"
    dry_run = "--dry-run" in sys.argv

    # Run backfill
    backfiller = HistoricalDataBackfill(season=season)
    summary = backfiller.backfill_all_matches(dry_run=dry_run)

    # Exit code
    sys.exit(0 if summary['failed'] == 0 else 1)
