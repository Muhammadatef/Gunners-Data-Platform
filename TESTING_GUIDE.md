# Testing Guide - Arsenal FC Analytics Platform

**Test with Real Match Data**

This guide walks through testing the platform with actual Arsenal FC matches from the 2025-26 season.

---

## Test Match: Arsenal vs Bournemouth

**Match Details:**
- **Date**: January 3, 2026
- **Competition**: Premier League
- **Result**: Bournemouth 2-3 Arsenal (Away win!)
- **xG**: 0.95 - 1.28 (Arsenal deserved win)
- **FBref URL**: https://fbref.com/en/matches/db124c87/Bournemouth-Arsenal-January-3-2026-Premier-League
- **Understat ID**: 28971

---

## Quick Test (Manual Script)

### Option 1: Python Script (Fastest)

```bash
# Start the platform
make start

# Wait for services to be ready (~2 minutes)
docker-compose logs -f airflow-init
# Wait for "exited with code 0"

# Run test script
docker exec arsenalfc_airflow_scheduler python /opt/airflow/scripts/test_bournemouth_match.py
```

**What the script does:**
1. Scrapes FBref match report → Player stats, team stats, metadata
2. Scrapes Understat shots → Shot coordinates, xG per shot
3. Saves to Bronze layer (`fbref_raw`, `understat_raw`)
4. Verifies data in database

**Expected Output:**
```
[1/4] Scraping FBref match report...
✓ FBref data scraped successfully
  - Players: 28
  - Home team: Bournemouth
  - Away team: Arsenal
  - Score: 2-3

[2/4] Scraping Understat shot data...
✓ Understat data scraped successfully
  - Total shots: 27
  - Home shots: 15
  - Away shots: 12

[3/4] Saving to Bronze layer...
✓ FBref data saved to bronze.fbref_raw
✓ Understat data saved to bronze.understat_raw

[4/4] Verifying data in database...
✓ Match data verified in database

SUCCESS! Match data scraped and loaded
```

---

### Option 2: Airflow DAG (Production-like)

```bash
# 1. Access Airflow UI
open http://localhost:8080
# Login: admin / admin

# 2. Navigate to DAGs → arsenal_match_scraper

# 3. Click "Trigger DAG w/ config"

# 4. Paste this JSON:
{
  "match_id": "20260103_bournemouth_vs_arsenal",
  "match_report_url": "https://fbref.com/en/matches/db124c87/Bournemouth-Arsenal-January-3-2026-Premier-League",
  "home_team": "Bournemouth",
  "away_team": "Arsenal",
  "match_date": "2026-01-03"
}

# 5. Click "Trigger"
```

**What the DAG does:**
1. Scrapes FBref + Understat (parallel)
2. Validates data quality
3. Runs dbt transformations (Bronze → Silver → Gold)
4. Computes metrics
5. Runs data quality tests

**Expected Duration**: ~30 seconds

**Monitor Progress**:
- Airflow UI → DAGs → arsenal_match_scraper → Graph View
- Watch tasks turn green (success) or red (failure)

---

## Verify Data in Database

### Check Bronze Layer (Raw Data)

```bash
# Open database shell
make db-shell

# Or manually:
docker exec -it arsenalfc_postgres psql -U analytics_user -d arsenalfc_analytics
```

```sql
-- Check FBref data
SELECT
    match_id,
    scraped_at,
    jsonb_pretty(raw_data->'match_metadata') AS metadata
FROM bronze.fbref_raw
WHERE match_id LIKE '%bournemouth%';

-- Check Understat shots
SELECT
    match_id,
    jsonb_array_length(raw_shots->'home_shots') AS home_shots,
    jsonb_array_length(raw_shots->'away_shots') AS away_shots
FROM bronze.understat_raw
WHERE match_id LIKE '%bournemouth%';
```

**Expected Results:**
- **FBref**: 1 row with match_id `20260103_bournemouth_vs_arsenal`
- **Understat**: 1 row with ~15 home shots, ~12 away shots

---

### Check Silver Layer (Cleaned Data)

```sql
-- Match metadata
SELECT
    match_id,
    home_team,
    away_team,
    home_score,
    away_score,
    match_date
FROM silver.stg_matches
WHERE match_id LIKE '%bournemouth%';

-- Player stats (top performers)
SELECT
    player_name,
    team,
    goals,
    assists,
    xg,
    shots,
    progressive_passes
FROM silver.stg_player_stats
WHERE match_id LIKE '%bournemouth%'
ORDER BY xg DESC
LIMIT 10;

-- Shot events
SELECT
    player_name,
    team,
    minute,
    xg,
    result
FROM silver.stg_shot_events
WHERE match_id LIKE '%bournemouth%'
ORDER BY xg DESC;
```

**Expected Results:**
- **stg_matches**: 1 row (Bournemouth 2-3 Arsenal)
- **stg_player_stats**: ~28 rows (players from both teams)
- **stg_shot_events**: ~27 rows (all shots)

---

### Check Gold Layer (Dimensional Model)

```sql
-- Match in dimensional model
SELECT
    dm.match_id,
    dm.match_date,
    ht.team_name AS home_team,
    at.team_name AS away_team,
    dm.home_score,
    dm.away_score
FROM gold.dim_match dm
JOIN gold.dim_team ht ON dm.home_team_id = ht.team_id
JOIN gold.dim_team at ON dm.away_team_id = at.team_id
WHERE dm.match_id LIKE '%bournemouth%';

-- Arsenal player performance
SELECT
    dp.player_name,
    fpmp.goals,
    fpmp.assists,
    fpmp.xg,
    fpmp.shots,
    fpmp.progressive_passes
FROM gold.fact_player_match_performance fpmp
JOIN gold.dim_player dp ON fpmp.player_id = dp.player_id
JOIN gold.dim_team dt ON fpmp.team_id = dt.team_id
WHERE dt.team_name = 'Arsenal'
  AND fpmp.match_id LIKE '%bournemouth%'
ORDER BY fpmp.xg DESC;
```

---

### Check Metrics Layer (Pre-computed Analytics)

```sql
-- Season summary (should show 1 match)
SELECT
    matches_played,
    wins,
    goals_for,
    goals_against,
    xg_for,
    xg_against
FROM metrics.season_team_summary sts
JOIN gold.dim_team dt ON sts.team_id = dt.team_id
WHERE dt.team_name = 'Arsenal';
```

---

## View Dashboard

```bash
# Open dashboard
open http://localhost:8501
```

### Season Overview Page

**What you should see:**
- **Points**: 3 (1 win)
- **Record**: 1W 0D 0L
- **Goals**: 3 - 2 (+1 GD)
- **xG**: 1.28 (vs 3 actual goals = +1.72 overperformance!)

**Recent Matches Table:**
```
Date       | Result                  | xG
-----------|-------------------------|----------
2026-01-03 | Bournemouth 2-3 Arsenal | 0.95-1.28
```

**Interpretation**:
- Arsenal won 3-2 (deserved based on xG)
- Overperformed slightly (+1.72 goals vs xG)
- Away win at difficult ground

---

### Match Detail Page

1. **Select match**: "2026-01-03: Bournemouth vs Arsenal"

**What you should see:**

**Match Header:**
```
Bournemouth    2 - 3    Arsenal
xG: 0.95              xG: 1.28
Shots: 15 (3 on)      Shots: 12 (5 on)
Possession: 36%       Possession: 64%
```

**Analysis**:
- Arsenal dominated possession (64%)
- Higher shot quality (1.28 xG from 12 shots vs 0.95 xG from 15 shots)
- Better shot accuracy (5/12 = 42% vs 3/15 = 20%)

**Player Statistics Table** (sortable):
- **Top xG**: Who created best chances?
- **Goals**: Who scored the 3 Arsenal goals?
- **Progressive passes**: Who progressed the ball?

---

### Player Performance Page

**What you should see:**
- All Arsenal players from the Bournemouth match
- Season totals (1 match so far)
- Per-90 metrics

**Sort by**:
- Goals → Who scored?
- xG → Who got into best positions?
- Progressive passes → Who advanced the ball?

---

## Full Season Backfill

After testing with 1 match, backfill the entire season:

### Step 1: Trigger Backfill DAG

```bash
# Option A: Airflow UI
open http://localhost:8080
# DAGs → arsenal_backfill_season → Trigger DAG

# Option B: CLI
docker exec arsenalfc_airflow_scheduler airflow dags trigger arsenal_backfill_season
```

### Step 2: Monitor Progress

```bash
# Watch logs
docker exec arsenalfc_airflow_scheduler airflow dags list-runs -d arsenal_backfill_season

# Or Airflow UI
# DAGs → arsenal_backfill_season → Graph View
```

**Expected Duration**: ~3-5 minutes for ~20 matches

### Step 3: Verify Backfill

```sql
-- Count total matches
SELECT COUNT(*) FROM bronze.understat_raw;
-- Expected: ~20 matches

-- Check match distribution
SELECT
    DATE_TRUNC('month', scraped_at) AS month,
    COUNT(*) AS matches
FROM bronze.understat_raw
GROUP BY month
ORDER BY month;
```

### Step 4: View Full Season Dashboard

```bash
open http://localhost:8501
```

**Season Overview** should now show:
- **Points**: Actual Arsenal points so far
- **Matches**: ~20 matches
- **xG Trend**: Line chart with 20 data points
- **Recent Matches**: Last 10 matches listed

---

## Troubleshooting

### Problem: "403 Forbidden" when scraping FBref

**Cause**: FBref blocking requests (rate limit or bot detection)

**Solution**:
```bash
# Increase delay in config
# Edit: scrapers/config.py
FBREF_REQUEST_DELAY: float = 5.0  # Was 3.0

# Restart services
make restart
```

---

### Problem: No data in dashboard after scraping

**Cause**: dbt transformations not run

**Solution**:
```bash
# Run dbt manually
make dbt-run

# Check dbt logs
docker exec arsenalfc_airflow_scheduler bash -c "cd /opt/airflow/dbt && dbt run --profiles-dir . --debug"
```

---

### Problem: "Table does not exist" errors

**Cause**: Database schema not initialized

**Solution**:
```bash
# Stop services
make stop

# Remove volumes (WARNING: deletes all data)
docker-compose down -v

# Restart (will re-initialize database)
make start
```

---

### Problem: Understat data missing

**Cause**: Match not finished or Understat hasn't published data

**Solution**:
- Check match status on Understat manually
- Wait 1-2 hours after full-time
- Re-run scraper

---

## Next Steps

After successful test:

1. **Enable Auto-Scraping**:
   ```bash
   # Airflow UI → arsenal_fixture_monitor → Toggle "Auto-refresh" ON
   ```

2. **Schedule Regular Checks**:
   - DAG runs daily at 2 AM UTC
   - Scrapes finished matches automatically

3. **Add More Visualizations**:
   - Shot maps (data ready, just needs Plotly code)
   - xG flow timeline (data ready)
   - Pass networks (need additional scraping)

4. **Backfill Previous Seasons** (optional):
   ```bash
   # Trigger backfill for 2024-25 season
   docker exec arsenalfc_airflow_scheduler airflow dags trigger arsenal_backfill_season -c '{"season": "2025"}'
   ```

---

## Expected Test Results Summary

| Component | Expected Result |
|-----------|-----------------|
| **Bronze Tables** | 1 FBref row + 1 Understat row |
| **Silver Tables** | 1 match, ~28 players, ~27 shots |
| **Gold Tables** | Dimensional model populated |
| **Metrics** | Season summary shows 1 match |
| **Dashboard - Season** | 3 points, 1 win, 3 goals, 1.28 xG |
| **Dashboard - Match** | 2-3 result, player stats, shot table |
| **Dashboard - Players** | Arsenal squad with match stats |

---

**Ready to test!** 🚀

Run the test script and watch your Arsenal FC analytics platform come to life with real match data.

**COYG!** 🔴⚪
