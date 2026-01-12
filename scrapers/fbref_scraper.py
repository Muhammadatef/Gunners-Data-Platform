"""
FBref Scraper - Primary data source for match statistics

This module scrapes:
- Arsenal's fixture schedule
- Match-level statistics (team performance, xG)
- Player-level statistics (goals, assists, xG, xA, progressive actions, etc.)
- Advanced metrics (SCA, GCA, PSxG)
"""

import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import json

from config import config
from utils import (
    get_session_with_retries,
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


class FBrefScraper:
    """Scraper for FBref football statistics"""

    def __init__(self):
        self.session = get_session_with_retries()
        self.base_url = config.FBREF_BASE_URL
        self.arsenal_id = config.ARSENAL_FBREF_ID

    @rate_limit(config.FBREF_REQUEST_DELAY)
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

    def scrape_fixtures(self, season: str = "2024-2025") -> List[Dict[str, Any]]:
        """
        Scrape Arsenal's fixtures for the season

        Args:
            season: Season string (e.g., "2024-2025")

        Returns:
            List of fixture dictionaries
        """
        # Construct URL for Arsenal's schedule
        # Example: https://fbref.com/en/squads/18bb7c10/2024-2025/Arsenal-Stats
        url = f"{self.base_url}/en/squads/{self.arsenal_id}/{season}/Arsenal-Stats"

        response = self._make_request(url)
        soup = BeautifulSoup(response.content, 'lxml')

        fixtures = []

        # Find the scores and fixtures table
        # FBref uses id="matchlogs_for" for match logs
        table = soup.find('table', {'id': 'matchlogs_for'})

        if not table:
            logger.warning("Could not find fixtures table")
            return fixtures

        tbody = table.find('tbody')
        if not tbody:
            return fixtures

        rows = tbody.find_all('tr')

        for row in rows:
            # Skip header rows
            if row.get('class') and 'thead' in row.get('class'):
                continue

            try:
                fixture = self._parse_fixture_row(row, season)
                if fixture:
                    fixtures.append(fixture)
            except Exception as e:
                logger.warning(f"Error parsing fixture row: {e}")
                continue

        logger.info(f"Scraped {len(fixtures)} fixtures for Arsenal {season}")
        return fixtures

    def _parse_fixture_row(self, row, season: str) -> Optional[Dict[str, Any]]:
        """
        Parse a single fixture row from FBref table

        Args:
            row: BeautifulSoup row element
            season: Season string

        Returns:
            Fixture dictionary or None
        """
        cells = row.find_all(['th', 'td'])
        if len(cells) < 10:
            return None

        # Extract cells (FBref table structure)
        # [0: Matchweek, 1: Date, 2: Time, 3: Comp, 4: Round, 5: Day, 6: Venue,
        #  7: Result, 8: GF, 9: GA, 10: Opponent, ...]

        date_str = safe_extract_text(cells[1], '')
        time_str = safe_extract_text(cells[2], '')
        competition = safe_extract_text(cells[3], '')
        venue = safe_extract_text(cells[6], '')  # Home/Away
        result = safe_extract_text(cells[7], '')  # W/D/L or blank if not played
        opponent = safe_extract_text(cells[10], 'a', '')

        # Parse score
        gf_str = safe_extract_text(cells[8], '')
        ga_str = safe_extract_text(cells[9], '')

        # Parse date
        try:
            match_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            logger.warning(f"Invalid date format: {date_str}")
            return None

        # Parse time if available
        kickoff_time = None
        if time_str and time_str != '':
            try:
                kickoff_time = datetime.strptime(time_str, '%H:%M').time()
            except ValueError:
                pass

        # Determine if match is finished
        match_status = 'finished' if result else 'scheduled'

        # Determine home/away teams
        is_home = venue.lower() == 'home'
        home_team = 'Arsenal' if is_home else opponent
        away_team = opponent if is_home else 'Arsenal'

        # Parse scores
        home_score = safe_extract_int(gf_str) if is_home else safe_extract_int(ga_str)
        away_score = safe_extract_int(ga_str) if is_home else safe_extract_int(gf_str)

        # Generate match ID
        match_id = generate_match_id(home_team, away_team, str(match_date))

        # Find match report link if available
        match_report_link = None
        report_cell = cells[11] if len(cells) > 11 else None
        if report_cell:
            report_link = report_cell.find('a', text='Match Report')
            if report_link and report_link.get('href'):
                match_report_link = self.base_url + report_link['href']

        fixture = {
            'match_id': match_id,
            'season': season,
            'competition': competition,
            'match_date': str(match_date),
            'kickoff_time': str(kickoff_time) if kickoff_time else None,
            'home_team': home_team,
            'away_team': away_team,
            'home_score': home_score if match_status == 'finished' else None,
            'away_score': away_score if match_status == 'finished' else None,
            'match_status': match_status,
            'venue': venue,
            'match_report_url': match_report_link
        }

        return fixture

    def scrape_match_stats(self, match_report_url: str) -> Dict[str, Any]:
        """
        Scrape detailed match statistics from FBref match report

        Args:
            match_report_url: URL to match report page

        Returns:
            Dictionary containing match statistics

        Raises:
            ScraperException: If scraping fails
            DataValidationException: If data validation fails
        """
        response = self._make_request(match_report_url)
        soup = BeautifulSoup(response.content, 'lxml')

        match_data = {
            'match_url': match_report_url,
            'scraped_at': datetime.utcnow().isoformat(),
            'match_metadata': {},
            'team_stats': {},
            'player_stats': []
        }

        # Extract match metadata
        match_data['match_metadata'] = self._extract_match_metadata(soup)

        # Extract team-level statistics
        match_data['team_stats'] = self._extract_team_stats(soup)

        # Extract player-level statistics
        match_data['player_stats'] = self._extract_player_stats(soup)

        # Validate data
        self._validate_match_data(match_data)

        return match_data

    def _extract_match_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract match metadata (score, teams, date, venue, etc.)"""
        metadata = {}

        # Find scorebox (contains teams, score, date, etc.)
        scorebox = soup.find('div', {'class': 'scorebox'})
        if not scorebox:
            logger.warning("Could not find scorebox")
            return metadata

        # Extract teams and scores
        teams = scorebox.find_all('div', recursive=False)
        if len(teams) >= 2:
            # Home team
            home_div = teams[0]
            home_team_elem = home_div.find('strong')
            metadata['home_team'] = home_team_elem.get_text(strip=True) if home_team_elem else None

            home_score_elem = home_div.find('div', {'class': 'score'})
            metadata['home_score'] = safe_extract_int(
                home_score_elem.get_text(strip=True) if home_score_elem else None
            )

            # Away team
            away_div = teams[1]
            away_team_elem = away_div.find('strong')
            metadata['away_team'] = away_team_elem.get_text(strip=True) if away_team_elem else None

            away_score_elem = away_div.find('div', {'class': 'score'})
            metadata['away_score'] = safe_extract_int(
                away_score_elem.get_text(strip=True) if away_score_elem else None
            )

        # Extract other metadata
        scorebox_meta = scorebox.find('div', {'class': 'scorebox_meta'})
        if scorebox_meta:
            # Venue, attendance, referee
            for div in scorebox_meta.find_all('div'):
                text = div.get_text(strip=True)
                if 'Venue:' in text:
                    metadata['venue'] = text.replace('Venue:', '').strip()
                elif 'Attendance:' in text:
                    attendance_str = text.replace('Attendance:', '').strip()
                    metadata['attendance'] = safe_extract_int(attendance_str)
                elif 'Referee:' in text:
                    metadata['referee'] = text.replace('Referee:', '').strip()

        return metadata

    def _extract_team_stats(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract team-level statistics (possession, xG, shots, etc.)"""
        team_stats = {'home': {}, 'away': {}}

        # Team stats are typically in "team_stats" table
        stats_table = soup.find('div', {'id': 'team_stats'})
        if not stats_table:
            logger.warning("Could not find team stats table")
            return team_stats

        # Extract key stats from table rows
        rows = stats_table.find_all('tr')
        for row in rows:
            header = row.find('th')
            if not header:
                continue

            stat_name = header.get_text(strip=True).lower()
            cells = row.find_all('td')

            if len(cells) >= 2:
                home_value = cells[0].get_text(strip=True)
                away_value = cells[1].get_text(strip=True)

                # Map stat names and parse values
                if 'possession' in stat_name:
                    team_stats['home']['possession'] = safe_extract_float(home_value.replace('%', ''))
                    team_stats['away']['possession'] = safe_extract_float(away_value.replace('%', ''))
                elif 'xg' in stat_name and 'xa' not in stat_name:
                    team_stats['home']['xg'] = safe_extract_float(home_value)
                    team_stats['away']['xg'] = safe_extract_float(away_value)
                elif 'shots' in stat_name and 'on target' not in stat_name:
                    team_stats['home']['shots'] = safe_extract_int(home_value)
                    team_stats['away']['shots'] = safe_extract_int(away_value)
                elif 'on target' in stat_name:
                    team_stats['home']['shots_on_target'] = safe_extract_int(home_value)
                    team_stats['away']['shots_on_target'] = safe_extract_int(away_value)

        return team_stats

    def _extract_player_stats(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract player-level statistics from all stat tables"""
        player_stats = []

        # Find all player stat tables (summary, passing, defense, etc.)
        # FBref uses multiple tables with different IDs
        stat_tables = [
            ('stats_', 'summary'),  # Basic stats (goals, assists, shots)
            ('passing_', 'passing'),  # Passing stats
            ('defense_', 'defense'),  # Defensive stats
            ('possession_', 'possession'),  # Possession stats
            ('gca_', 'gca')  # Goal and shot creating actions
        ]

        # We'll merge stats by player
        player_data_map = {}

        for table_prefix, stat_type in stat_tables:
            # Tables are typically ID'd as "stats_<home_team_id>" and "stats_<away_team_id>"
            # We'll find all tables starting with the prefix
            tables = soup.find_all('table', id=lambda x: x and x.startswith(table_prefix))

            for table in tables:
                # Determine if home or away team
                table_id = table.get('id', '')
                team = 'home' if 'home' in table_id or table_prefix + 'home' in table_id else 'away'

                tbody = table.find('tbody')
                if not tbody:
                    continue

                rows = tbody.find_all('tr')
                for row in rows:
                    # Skip header rows
                    if 'thead' in row.get('class', []):
                        continue

                    player_name_cell = row.find('th', {'data-stat': 'player'})
                    if not player_name_cell:
                        continue

                    player_name = clean_player_name(player_name_cell.get_text(strip=True))

                    # Create unique key for player in this match
                    player_key = f"{player_name}_{team}"

                    if player_key not in player_data_map:
                        player_data_map[player_key] = {
                            'player_name': player_name,
                            'team': team
                        }

                    # Extract all data-stat attributes
                    cells = row.find_all(['th', 'td'])
                    for cell in cells:
                        stat = cell.get('data-stat')
                        if stat and stat != 'player':
                            value = cell.get_text(strip=True)
                            player_data_map[player_key][stat] = value

        # Convert map to list
        player_stats = list(player_data_map.values())

        logger.info(f"Extracted stats for {len(player_stats)} players")
        return player_stats

    def _validate_match_data(self, match_data: Dict[str, Any]) -> None:
        """
        Validate scraped match data

        Raises:
            DataValidationException: If validation fails
        """
        metadata = match_data.get('match_metadata', {})

        # Check essential fields
        if not metadata.get('home_team') or not metadata.get('away_team'):
            raise DataValidationException("Missing team names")

        if metadata.get('home_score') is None or metadata.get('away_score') is None:
            raise DataValidationException("Missing scores")

        # Check team stats
        team_stats = match_data.get('team_stats', {})
        if not team_stats.get('home') or not team_stats.get('away'):
            logger.warning("Missing team stats")

        # Check player stats
        player_stats = match_data.get('player_stats', [])
        if len(player_stats) < 14:  # Should have at least 11 starters per team
            logger.warning(f"Only {len(player_stats)} player records found")

        logger.info("Match data validation passed")

    def scrape_match_lineups(self, match_report_url: str) -> Dict[str, Any]:
        """
        Scrape player lineups and positions from FBref match report

        Args:
            match_report_url: URL to match report page

        Returns:
            Dictionary with lineup data including player positions
        """
        response = self._make_request(match_report_url)
        soup = BeautifulSoup(response.content, 'lxml')

        lineup_data = {
            'match_url': match_report_url,
            'scraped_at': datetime.utcnow().isoformat(),
            'home_lineup': [],
            'away_lineup': []
        }

        # Extract metadata
        metadata = self._extract_match_metadata(soup)
        lineup_data['home_team'] = metadata.get('home_team')
        lineup_data['away_team'] = metadata.get('away_team')

        # Find lineup tables
        # FBref has two tables with class "lineup" - first for home, second for away
        lineup_tables = soup.find_all('table', {'class': 'lineup'})

        if len(lineup_tables) >= 2:
            lineup_data['home_lineup'] = self._parse_lineup_table(lineup_tables[0], 'home')
            lineup_data['away_lineup'] = self._parse_lineup_table(lineup_tables[1], 'away')
        else:
            logger.warning(f"Could not find lineup tables (found {len(lineup_tables)})")

        total_players = len(lineup_data['home_lineup']) + len(lineup_data['away_lineup'])
        logger.info(f"Scraped lineups: {total_players} players")

        return lineup_data

    def _parse_lineup_table(self, table, team_side: str) -> List[Dict[str, str]]:
        """
        Parse lineup table to extract player positions

        Args:
            table: BeautifulSoup table element
            team_side: 'home' or 'away'

        Returns:
            List of player dictionaries with name and position
        """
        lineup = []

        tbody = table.find('tbody')
        if not tbody:
            return lineup

        rows = tbody.find_all('tr')

        for row in rows:
            try:
                # Get player name (in th with data-stat="player")
                player_cell = row.find('th', {'data-stat': 'player'})
                if not player_cell:
                    continue

                player_name = clean_player_name(player_cell.get_text(strip=True))

                # Get jersey number (in th with data-stat="jersey_number")
                number_cell = row.find('th', {'data-stat': 'jersey_number'})
                jersey_number = number_cell.get_text(strip=True) if number_cell else ''

                # Get position (in td with data-stat="position")
                position_cell = row.find('td', {'data-stat': 'position'})
                position = position_cell.get_text(strip=True) if position_cell else 'Unknown'

                # Normalize position to category
                position_category = self._normalize_position(position)

                player_data = {
                    'player_name': player_name,
                    'position': position,  # Raw position (e.g., "CM", "LW")
                    'position_category': position_category,  # Normalized (GK, DEF, MID, FWD)
                    'jersey_number': jersey_number,
                    'team_side': team_side
                }

                lineup.append(player_data)

            except Exception as e:
                logger.debug(f"Error parsing lineup row: {e}")
                continue

        return lineup

    def scrape_match_logs(self, season: str = "2025-2026", log_type: str = "passing") -> List[Dict[str, Any]]:
        """
        Scrape match logs from FBref for a season
        
        Args:
            season: Season string (e.g., "2025-2026")
            log_type: Type of log to scrape - "passing", "standard", "shooting", etc.
        
        Returns:
            List of match log dictionaries with player statistics per match
        """
        # Construct URL for match logs
        # Example: https://fbref.com/en/squads/18bb7c10/2025-2026/matchlogs/c9/passing/Arsenal-Match-Logs-Premier-League
        url = f"{self.base_url}/en/squads/{self.arsenal_id}/{season}/matchlogs/c9/{log_type}/Arsenal-Match-Logs-Premier-League"
        
        logger.info(f"Scraping FBref match logs: {url}")
        response = self._make_request(url)
        soup = BeautifulSoup(response.content, 'lxml')
        
        match_logs = []
        
        # Find the match logs table
        table = soup.find('table', {'id': f'matchlogs_{log_type}'})
        
        if not table:
            logger.warning(f"Could not find match logs table for {log_type}")
            return match_logs
        
        tbody = table.find('tbody')
        if not tbody:
            return match_logs
        
        rows = tbody.find_all('tr')
        
        for row in rows:
            # Skip header rows
            if row.get('class') and 'thead' in row.get('class'):
                continue
            
            try:
                cells = row.find_all(['th', 'td'])
                if len(cells) < 5:
                    continue
                
                # Extract match date
                date_cell = cells[0]
                match_date = safe_extract_text(date_cell.find('a')) if date_cell.find('a') else safe_extract_text(date_cell)
                
                # Extract opponent
                opponent_cell = cells[1]
                opponent = safe_extract_text(opponent_cell.find('a')) if opponent_cell.find('a') else safe_extract_text(opponent_cell)
                
                # Extract venue (H/A)
                venue_cell = cells[2]
                venue = safe_extract_text(venue_cell).upper()
                
                # Extract result
                result_cell = cells[3]
                result = safe_extract_text(result_cell)
                
                # Extract score
                score_cell = cells[4]
                score = safe_extract_text(score_cell)
                
                # Extract match report URL if available
                match_url = None
                match_link = date_cell.find('a')
                if match_link and match_link.get('href'):
                    match_url = f"{self.base_url}{match_link['href']}"
                
                # Extract additional stats based on log type
                stats = {}
                if len(cells) > 5:
                    # Get column headers to map stats
                    header_row = table.find('thead')
                    if header_row:
                        headers = [safe_extract_text(th) for th in header_row.find_all('th')]
                        for i, header in enumerate(headers[5:], start=5):
                            if i < len(cells):
                                value = safe_extract_text(cells[i])
                                # Try to parse as number
                                num_value = safe_extract_float(value)
                                stats[header] = num_value if num_value is not None else value
                
                match_log = {
                    'match_date': match_date,
                    'opponent': opponent,
                    'venue': venue,
                    'result': result,
                    'score': score,
                    'match_url': match_url,
                    'log_type': log_type,
                    'season': season,
                    'stats': stats
                }
                
                match_logs.append(match_log)
                
            except Exception as e:
                logger.debug(f"Error parsing match log row: {e}")
                continue
        
        logger.info(f"Scraped {len(match_logs)} match logs from FBref")
        return match_logs

    def _normalize_position(self, position: str) -> str:
        """
        Normalize FBref positions to categories

        Args:
            position: Raw position string (e.g., "CM", "LW", "GK")

        Returns:
            Normalized category: GK, DEF, MID, FWD
        """
        position = position.upper()

        if 'GK' in position:
            return 'GK'
        elif any(x in position for x in ['CB', 'LB', 'RB', 'WB', 'DF', 'FB']):
            return 'DEF'
        elif any(x in position for x in ['CM', 'DM', 'AM', 'MF', 'CDM', 'CAM']):
            return 'MID'
        elif any(x in position for x in ['FW', 'LW', 'RW', 'CF', 'ST', 'W', 'F']):
            return 'FWD'
        else:
            return 'UNKNOWN'
