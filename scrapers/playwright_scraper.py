"""
Playwright-based web scraper for FBref and Understat

This module uses Playwright to bypass anti-bot protection and handle
JavaScript-rendered content.
"""

import logging
import json
import re
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from contextlib import contextmanager

from playwright.sync_api import sync_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError

from config import config
from utils import (
    rate_limit,
    safe_extract_text,
    safe_extract_int,
    safe_extract_float,
    clean_player_name,
    generate_match_id,
    ScraperException,
    DataValidationException
)

logger = logging.getLogger(__name__)


class PlaywrightScraper:
    """Base class for Playwright-based web scraping"""

    def __init__(self):
        self.headless = True
        self.viewport = {'width': 1920, 'height': 1080}
        self.user_agent = config.USER_AGENT

    @contextmanager
    def get_browser(self):
        """Context manager for browser instance"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            try:
                yield browser
            finally:
                browser.close()

    @contextmanager
    def get_page(self, browser: Browser) -> Page:
        """Context manager for page instance"""
        context = browser.new_context(
            viewport=self.viewport,
            user_agent=self.user_agent
        )
        page = context.new_page()
        try:
            yield page
        finally:
            page.close()
            context.close()


class UnderstatPlaywrightScraper(PlaywrightScraper):
    """Scrape Understat using Playwright for JavaScript rendering"""

    def __init__(self):
        super().__init__()
        self.base_url = config.UNDERSTAT_BASE_URL

    @rate_limit(config.UNDERSTAT_REQUEST_DELAY)
    def scrape_season_fixtures(self, season: str = "2024") -> List[Dict[str, Any]]:
        """
        Scrape all Arsenal fixtures from Understat for a season

        Args:
            season: Season year (e.g., "2024" for 2024-2025)

        Returns:
            List of fixture dictionaries with match URLs
        """
        arsenal_url = f"{self.base_url}/team/Arsenal/{season}"

        logger.info(f"Scraping Understat fixtures: {arsenal_url}")

        with self.get_browser() as browser:
            with self.get_page(browser) as page:
                try:
                    # Load page
                    page.goto(arsenal_url, wait_until='domcontentloaded', timeout=60000)

                    # Wait for JavaScript to execute
                    page.wait_for_timeout(3000)

                    # Extract datesData from JavaScript
                    matches_data = page.evaluate('() => window.datesData || []')

                    if not matches_data:
                        logger.warning("No match data found on page")
                        return []

                    fixtures = []
                    for match_data in matches_data:
                        fixture = {
                            'match_id': match_data.get('id'),
                            'match_url': f"{self.base_url}/match/{match_data.get('id')}",
                            'home_team': match_data.get('h', {}).get('title', ''),
                            'away_team': match_data.get('a', {}).get('title', ''),
                            'match_date': match_data.get('datetime', '')[:10],
                            'is_result': match_data.get('isResult', False)
                        }
                        fixtures.append(fixture)

                    logger.info(f"Scraped {len(fixtures)} fixtures from Understat")
                    return fixtures

                except PlaywrightTimeoutError as e:
                    raise ScraperException(f"Timeout loading {arsenal_url}: {e}")
                except Exception as e:
                    raise ScraperException(f"Error scraping Understat fixtures: {e}")

    @rate_limit(config.UNDERSTAT_REQUEST_DELAY)
    def scrape_match_shots(self, match_url: str, home_team: str = None, away_team: str = None, match_date: str = None) -> Dict[str, Any]:
        """
        Scrape shot-level data for a specific match

        Args:
            match_url: Full URL to the match page
            home_team: Optional home team name (from fixture list)
            away_team: Optional away team name (from fixture list)
            match_date: Optional match date (from fixture list)

        Returns:
            Dictionary containing match info and shot data
        """
        logger.info(f"Scraping match shots: {match_url}")

        with self.get_browser() as browser:
            with self.get_page(browser) as page:
                try:
                    # Load page and wait for content
                    page.goto(match_url, wait_until='networkidle', timeout=60000)
                    page.wait_for_timeout(2000)

                    # Extract shots data from JavaScript (this still works)
                    shots_data = page.evaluate('() => window.shotsData || {}')

                    # Use provided team names or try to extract from page
                    match_id = match_url.split('/')[-1]

                    if not home_team or not away_team:
                        # Try getting from page title
                        page_title = page.title()
                        if ' vs ' in page_title:
                            teams = page_title.split(' - ')[0].split(' vs ')
                            if len(teams) == 2:
                                home_team = home_team or teams[0].strip()
                                away_team = away_team or teams[1].strip()

                    # Get match date from page if not provided
                    if not match_date:
                        try:
                            date_element = page.query_selector('.breadcrumb')
                            if date_element:
                                date_text = date_element.text_content()
                                import re
                                date_match = re.search(r'\\d{4}-\\d{2}-\\d{2}', date_text)
                                if date_match:
                                    match_date = date_match.group(0)
                        except:
                            pass

                    # Parse shots
                    home_shots = shots_data.get('h', [])
                    away_shots = shots_data.get('a', [])

                    all_shots = []

                    # Process home shots
                    for shot in home_shots:
                        all_shots.append(self._parse_shot(shot, 'h', home_team, away_team))

                    # Process away shots
                    for shot in away_shots:
                        all_shots.append(self._parse_shot(shot, 'a', home_team, away_team))

                    # Calculate xG totals
                    home_xg = sum(s['xg'] for s in all_shots if s['h_a'] == 'h')
                    away_xg = sum(s['xg'] for s in all_shots if s['h_a'] == 'a')

                    # Count goals
                    home_goals = sum(1 for s in all_shots if s['h_a'] == 'h' and s['result'] == 'Goal')
                    away_goals = sum(1 for s in all_shots if s['h_a'] == 'a' and s['result'] == 'Goal')

                    match_data = {
                        'match_id': generate_match_id(home_team, away_team, match_date),
                        'understat_match_id': match_id,
                        'match_date': match_date if match_date else '',
                        'match_url': match_url,
                        'home_team': home_team,
                        'away_team': away_team,
                        'home_goals': home_goals,
                        'away_goals': away_goals,
                        'home_xg': round(home_xg, 2),
                        'away_xg': round(away_xg, 2),
                        'shots': all_shots
                    }

                    logger.info(f"Scraped {len(all_shots)} shots for {home_team} vs {away_team}")
                    return match_data

                except PlaywrightTimeoutError as e:
                    raise ScraperException(f"Timeout loading {match_url}: {e}")
                except Exception as e:
                    raise ScraperException(f"Error scraping match shots: {e}")

    def _parse_shot(self, shot: Dict, h_a: str, home_team: str, away_team: str) -> Dict[str, Any]:
        """Parse a single shot dictionary"""
        return {
            'shot_id': shot.get('id'),
            'minute': safe_extract_int(shot.get('minute')),
            'player_name': shot.get('player', ''),
            'player_id': shot.get('player_id'),
            'x_coord': safe_extract_float(shot.get('X')),
            'y_coord': safe_extract_float(shot.get('Y')),
            'xg': safe_extract_float(shot.get('xG')),
            'result': shot.get('result', ''),
            'situation': shot.get('situation', ''),
            'shot_type': shot.get('shotType', ''),
            'assisted_by': shot.get('player_assisted', ''),
            'last_action': shot.get('lastAction', ''),
            'h_a': h_a,
            'h_team': home_team,
            'a_team': away_team
        }


class FBrefPlaywrightScraper(PlaywrightScraper):
    """Scrape FBref using Playwright to bypass anti-bot protection"""

    def __init__(self):
        super().__init__()
        self.base_url = config.FBREF_BASE_URL
        self.arsenal_id = config.ARSENAL_FBREF_ID

    @rate_limit(config.FBREF_REQUEST_DELAY)
    def scrape_fixtures(self, season: str = "2024-2025") -> List[Dict[str, Any]]:
        """
        Scrape Arsenal's fixture schedule from FBref

        Args:
            season: Season string (e.g., "2024-2025")

        Returns:
            List of fixture dictionaries
        """
        url = f"{self.base_url}/en/squads/{self.arsenal_id}/{season}/Arsenal-Stats"

        logger.info(f"Scraping FBref fixtures: {url}")

        with self.get_browser() as browser:
            with self.get_page(browser) as page:
                try:
                    # Load page
                    page.goto(url, wait_until='domcontentloaded', timeout=60000)
                    page.wait_for_timeout(2000)

                    # Get page HTML
                    html = page.content()

                    if 'Arsenal' not in html:
                        raise ScraperException("Arsenal not found in page - possible blocking")

                    # Extract fixture table (simplified - full implementation would parse HTML)
                    fixtures = []
                    logger.info(f"FBref page loaded successfully")

                    return fixtures

                except PlaywrightTimeoutError as e:
                    raise ScraperException(f"Timeout loading {url}: {e}")
                except Exception as e:
                    raise ScraperException(f"Error scraping FBref: {e}")
