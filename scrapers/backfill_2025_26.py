"""
Enhanced Backfill Script for Arsenal FC 2025-26 Season

Scrapes all played matches from Understat and FBref for the 2025-26 season.
"""

import logging
import sys
import uuid
import time
from typing import List, Dict, Any
from datetime import datetime

from playwright_scraper import UnderstatPlaywrightScraper
from fbref_scraper import FBrefScraper
from db_loader import DatabaseLoader

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def scrape_all_2025_26_matches():
    """
    Scrape all played matches from 2025-26 season from both Understat and FBref
    """
    logger.info("="*60)
    logger.info("ARSENAL FC 2025-26 SEASON BACKFILL")
    logger.info("="*60)
    
    # Initialize scrapers and loader
    understat_scraper = UnderstatPlaywrightScraper()
    fbref_scraper = FBrefScraper()
    loader = DatabaseLoader()
    
    # Get all fixtures for 2025 season
    logger.info("Fetching fixtures from Understat for 2025 season...")
    fixtures = understat_scraper.scrape_season_fixtures("2025")
    
    if not fixtures:
        logger.error("No fixtures found! Check Understat URL.")
        return
    
    logger.info(f"Found {len(fixtures)} total fixtures")
    
    # Filter for completed matches
    played_matches = [f for f in fixtures if f.get('is_result', False)]
    logger.info(f"Found {len(played_matches)} completed matches")
    
    if not played_matches:
        logger.warning("No completed matches found for 2025-26 season")
        return
    
    # Check which matches are already in database
    with loader.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT DISTINCT match_id
                FROM bronze.understat_raw
                WHERE match_id LIKE '2025%'
            """)
            existing_match_ids = set(row[0] for row in cur.fetchall())
    
    logger.info(f"Found {len(existing_match_ids)} existing matches in database")
    
    # Filter out existing matches
    matches_to_scrape = [
        m for m in played_matches 
        if m.get('match_id') not in existing_match_ids
    ]
    
    logger.info(f"Will scrape {len(matches_to_scrape)} new matches")
    
    if not matches_to_scrape:
        logger.info("All matches already scraped!")
        return
    
    # Statistics
    success_count = 0
    error_count = 0
    errors = []
    
    # Scrape each match
    for i, fixture in enumerate(matches_to_scrape, 1):
        match_id = fixture.get('match_id')
        match_url = fixture.get('match_url')
        home_team = fixture.get('home_team', '')
        away_team = fixture.get('away_team', '')
        match_date = fixture.get('match_date', '')
        
        logger.info(f"\n[{i}/{len(matches_to_scrape)}] Scraping: {match_date} - {home_team} vs {away_team}")
        logger.info(f"Match URL: {match_url}")
        
        try:
            # Scrape Understat match data
            logger.info("Scraping Understat match data...")
            match_data = understat_scraper.scrape_match_shots(
                match_url,
                home_team=home_team,
                away_team=away_team,
                match_date=match_date
            )
            
            if not match_data or not match_data.get('shots'):
                logger.warning(f"No shot data found for {match_id}")
                error_count += 1
                errors.append(f"{home_team} vs {away_team}: No shot data")
                continue
            
            # Save Understat data
            run_id = f"backfill_2025_26_{uuid.uuid4().hex[:8]}"
            loader.create_scrape_run(run_id, match_id, 'understat', None)
            loader.save_understat_raw(
                match_id,
                match_data,
                match_url,
                run_id
            )
            loader.update_scrape_run(run_id, 'success', len(match_data['shots']))
            
            logger.info(f"✓ Understat: {len(match_data['shots'])} shots, xG: {match_data.get('home_xg', 0):.2f}-{match_data.get('away_xg', 0):.2f}")
            
            # Scrape FBref data (optional - may not be available for all matches)
            try:
                logger.info("Scraping FBref match data...")
                # Note: FBref scraping would go here when implemented
                # For now, we'll skip it and focus on Understat data
                logger.info("FBref scraping skipped (to be implemented)")
            except Exception as e:
                logger.warning(f"FBref scraping failed (non-critical): {e}")
            
            success_count += 1
            
            # Rate limiting
            if i < len(matches_to_scrape):
                time.sleep(3)  # Be respectful to servers
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"✗ Error scraping {home_team} vs {away_team}: {error_msg}")
            error_count += 1
            errors.append(f"{home_team} vs {away_team}: {error_msg}")
            continue
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("BACKFILL SUMMARY")
    logger.info("="*60)
    logger.info(f"Total matches: {len(played_matches)}")
    logger.info(f"Already in DB: {len(existing_match_ids)}")
    logger.info(f"Attempted: {len(matches_to_scrape)}")
    logger.info(f"✓ Success: {success_count}")
    logger.info(f"✗ Errors: {error_count}")
    
    if errors:
        logger.info("\nFailed matches:")
        for error in errors[:10]:  # Show first 10 errors
            logger.info(f"  - {error}")
        if len(errors) > 10:
            logger.info(f"  ... and {len(errors) - 10} more")
    
    logger.info("\nBackfill complete!")


if __name__ == "__main__":
    try:
        scrape_all_2025_26_matches()
    except KeyboardInterrupt:
        logger.info("\nBackfill interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
