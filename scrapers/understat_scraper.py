"""
Understat Scraper - Secondary data source for shot-level xG data

This module scrapes:
- Shot events with exact coordinates (x, y)
- Shot-by-shot xG values
- Shot metadata (situation, result, body part)
"""

import logging
import re
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import requests
from bs4 import BeautifulSoup

from config import config
from utils import (
    get_session_with_retries,
    rate_limit,
    safe_extract_int,
    safe_extract_float,
    ScraperException,
    DataValidationException
)

logger = logging.getLogger(__name__)


class UnderstatScraper:
    """Scraper for Understat shot-level xG data"""

    def __init__(self):
        self.session = get_session_with_retries()
        self.base_url = config.UNDERSTAT_BASE_URL

    @rate_limit(config.UNDERSTAT_REQUEST_DELAY)
    def _make_request(self, url: str) -> requests.Response:
        """
        Make HTTP request with rate limiting

        Args:
            url: URL to fetch

        Returns:
            Response object

        Raises:
            ScraperException: If request fails
        """
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            raise ScraperException(f"Failed to fetch {url}: {e}")

    def find_match_url(
        self,
        home_team: str,
        away_team: str,
        match_date: str,
        season: str = "2024"
    ) -> Optional[str]:
        """
        Find Understat match URL for a given fixture

        Understat URLs are like: https://understat.com/match/12345

        Args:
            home_team: Home team name
            away_team: Away team name
            match_date: Match date (YYYY-MM-DD)
            season: Season year (e.g., "2024" for 2024-2025)

        Returns:
            Match URL if found, None otherwise
        """
        # Get Arsenal's season page
        arsenal_url = f"{self.base_url}/team/Arsenal/{season}"

        try:
            response = self._make_request(arsenal_url)
            soup = BeautifulSoup(response.content, 'lxml')

            # Understat embeds match data in JavaScript
            # Find the script containing match data
            scripts = soup.find_all('script')

            for script in scripts:
                script_text = script.string
                if not script_text or 'datesData' not in script_text:
                    continue

                # Extract JSON data from JavaScript
                # Pattern: var datesData = JSON.parse('...')
                match = re.search(r"var datesData\s*=\s*JSON\.parse\('(.+?)'\)", script_text)
                if not match:
                    continue

                # Decode escaped JSON string
                json_str = match.group(1).encode().decode('unicode_escape')
                matches_data = json.loads(json_str)

                # Search for matching fixture
                for match_data in matches_data:
                    match_home = match_data.get('h', {}).get('title', '')
                    match_away = match_data.get('a', {}).get('title', '')
                    match_id = match_data.get('id')

                    # Check if teams match (case-insensitive, flexible matching)
                    if (self._teams_match(match_home, home_team) and
                        self._teams_match(match_away, away_team)):
                        match_url = f"{self.base_url}/match/{match_id}"
                        logger.info(f"Found Understat match: {match_url}")
                        return match_url

            logger.warning(f"Could not find Understat match for {home_team} vs {away_team}")
            return None

        except Exception as e:
            logger.error(f"Error finding Understat match URL: {e}")
            return None

    def _teams_match(self, team1: str, team2: str) -> bool:
        """Check if two team names match (flexible comparison)"""
        # Normalize: lowercase, remove common words
        def normalize(name: str) -> str:
            normalized = name.lower()
            for word in [' fc', ' afc', ' united', ' city']:
                normalized = normalized.replace(word, '')
            return normalized.strip()

        return normalize(team1) == normalize(team2) or team1.lower() == team2.lower()

    def scrape_match_shots(self, match_url: str) -> Dict[str, Any]:
        """
        Scrape shot-level data from Understat match page

        Args:
            match_url: URL to Understat match page

        Returns:
            Dictionary containing shot events

        Raises:
            ScraperException: If scraping fails
        """
        response = self._make_request(match_url)
        soup = BeautifulSoup(response.content, 'lxml')

        match_data = {
            'match_url': match_url,
            'scraped_at': datetime.utcnow().isoformat(),
            'home_shots': [],
            'away_shots': []
        }

        # Extract match info
        match_info = self._extract_match_info(soup)
        match_data.update(match_info)

        # Extract shot data from JavaScript
        shot_data = self._extract_shot_data(soup)
        match_data['home_shots'] = shot_data.get('home', [])
        match_data['away_shots'] = shot_data.get('away', [])

        # Validate
        total_shots = len(match_data['home_shots']) + len(match_data['away_shots'])
        logger.info(f"Scraped {total_shots} shots from {match_url}")

        if total_shots == 0:
            logger.warning("No shots found - data may not be available yet")

        return match_data

    def _extract_match_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract basic match information"""
        info = {}

        # Find team names and scores
        # Understat structure: div.header with team names
        header = soup.find('div', {'class': 'header-wrapper'})
        if header:
            teams = header.find_all('div', {'class': 'team-name'})
            if len(teams) >= 2:
                info['home_team'] = teams[0].get_text(strip=True)
                info['away_team'] = teams[1].get_text(strip=True)

        return info

    def _extract_shot_data(self, soup: BeautifulSoup) -> Dict[str, List[Dict]]:
        """
        Extract shot data from JavaScript embedded in page

        Understat embeds shot data in JavaScript variables
        """
        shot_data = {'home': [], 'away': []}

        scripts = soup.find_all('script')

        for script in scripts:
            script_text = script.string
            if not script_text or 'shotsData' not in script_text:
                continue

            # Extract home shots
            home_match = re.search(r"var shotsData\s*=\s*JSON\.parse\('(.+?)'\)", script_text)
            if home_match:
                try:
                    json_str = home_match.group(1).encode().decode('unicode_escape')
                    shots = json.loads(json_str)

                    # Parse shots
                    home_shots = shots.get('h', [])
                    away_shots = shots.get('a', [])

                    shot_data['home'] = self._parse_shots(home_shots)
                    shot_data['away'] = self._parse_shots(away_shots)

                except Exception as e:
                    logger.error(f"Error parsing shot data: {e}")

        return shot_data

    def _parse_shots(self, shots: List[Dict]) -> List[Dict[str, Any]]:
        """
        Parse and normalize shot data

        Args:
            shots: List of raw shot dictionaries from Understat

        Returns:
            List of normalized shot dictionaries
        """
        parsed_shots = []

        for shot in shots:
            try:
                parsed_shot = {
                    'shot_id': shot.get('id'),
                    'minute': safe_extract_int(shot.get('minute')),
                    'player_name': shot.get('player', ''),
                    'player_id': shot.get('player_id'),

                    # Shot coordinates (0-1 normalized)
                    'x_coord': safe_extract_float(shot.get('X')),
                    'y_coord': safe_extract_float(shot.get('Y')),

                    # xG value
                    'xg': safe_extract_float(shot.get('xG')),

                    # Shot details
                    'result': shot.get('result', ''),  # Goal, SavedShot, MissedShots, BlockedShot, ShotOnPost
                    'situation': shot.get('situation', ''),  # OpenPlay, FromCorner, SetPiece, DirectFreekick
                    'shot_type': shot.get('shotType', ''),  # RightFoot, LeftFoot, Head, OtherBodyPart

                    # Assist information
                    'assisted_by': shot.get('player_assisted', ''),
                    'last_action': shot.get('lastAction', '')  # Pass, Throughball, Cross, Chipped, etc.
                }

                parsed_shots.append(parsed_shot)

            except Exception as e:
                logger.warning(f"Error parsing shot: {e}")
                continue

        return parsed_shots

    def scrape_season_fixtures(self, season: str = "2024") -> List[Dict[str, Any]]:
        """
        Scrape all Arsenal fixtures from Understat for a season

        Args:
            season: Season year (e.g., "2024" for 2024-2025)

        Returns:
            List of fixture dictionaries with match URLs
        """
        arsenal_url = f"{self.base_url}/team/Arsenal/{season}"

        response = self._make_request(arsenal_url)
        soup = BeautifulSoup(response.content, 'lxml')

        fixtures = []

        scripts = soup.find_all('script')

        for script in scripts:
            script_text = script.string
            if not script_text or 'datesData' not in script_text:
                continue

            try:
                # Extract fixtures data
                match = re.search(r"var datesData\s*=\s*JSON\.parse\('(.+?)'\)", script_text)
                if not match:
                    continue

                json_str = match.group(1).encode().decode('unicode_escape')
                matches_data = json.loads(json_str)

                for match_data in matches_data:
                    fixture = {
                        'match_id': match_data.get('id'),
                        'match_url': f"{self.base_url}/match/{match_data.get('id')}",
                        'home_team': match_data.get('h', {}).get('title', ''),
                        'away_team': match_data.get('a', {}).get('title', ''),
                        'date': match_data.get('datetime', ''),
                        'is_result': match_data.get('isResult', False)
                    }
                    fixtures.append(fixture)

                break

            except Exception as e:
                logger.error(f"Error parsing fixtures: {e}")

        logger.info(f"Scraped {len(fixtures)} fixtures from Understat")
        return fixtures
