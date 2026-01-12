# Real Data Testing - Arsenal vs Bournemouth + Full Season Backfill

## ✅ **Ready to Test with Real Arsenal FC Data**

The platform is now configured to test with **actual match data** from the 2025-26 season:

---

## 🎯 **Test Match: Arsenal vs Bournemouth**

**Match Information:**
- **Date**: January 3, 2026
- **Competition**: Premier League (Away fixture)
- **Final Score**: Bournemouth 2-3 Arsenal ⚽
- **Expected Goals**: 0.95 - 1.28 (Arsenal deserved win)
- **Shots**: 15 - 12 (Bournemouth more volume, Arsenal better quality)
- **Possession**: 36% - 64% (Arsenal controlled the game)

**Data Sources Available:**
- ✅ **FBref**: Match report with full statistics
- ✅ **Understat**: Shot-level xG data (match ID 28971)

---

## 🚀 **Quick Start - Test Single Match**

### Method 1: One-Command Test (Recommended)

```bash
# Start platform
make start

# Wait ~2 minutes for initialization
# Then run test
make test-bournemouth
```

**What happens:**
1. Scrapes FBref match report → Player stats, team stats
2. Scrapes Understat shots → 27 shots with coordinates & xG
3. Saves to Bronze layer
4. Verifies in database

**Expected Duration**: ~10 seconds

---

### Method 2: Run dbt Transformations

After scraping, transform the data:

```bash
# Run transformations
make dbt-run

# Expected output:
# bronze → silver: 3 models (matches, player_stats, shot_events)
# silver → gold: Dimensional model populated
# gold → metrics: Season summary computed
```

---

### Method 3: View Dashboard

```bash
# Open dashboard
open http://localhost:8501
```

**What you'll see:**

**Season Overview:**
- Points: 3 (1 win)
- Goals: 3-2 (+1 goal difference)
- xG: 1.28 (vs 3 goals = +1.72 overperformance!)

**Match Detail:**
- Select: "2026-01-03: Bournemouth vs Arsenal"
- View team stats, player performance, shot data

**Player Performance:**
- Arsenal squad with match stats
- Sortable by goals, xG, progressive passes, etc.

---

## 📦 **Full Season Backfill**

After testing with 1 match, backfill the entire 2025-26 season:

### Step 1: Check What Will Be Scraped (Dry Run)

```bash
make backfill-dry-run
```

**Output:**
```
Fetching Arsenal fixtures for season 2026...
Found 38 fixtures
Finished matches: 20

[1/20] Processing match...
[DRY RUN] Would scrape: https://understat.com/match/28956
...
[20/20] Processing match...

BACKFILL SUMMARY
Total matches: 20
✓ Success: 0 (dry run)
⊘ Skipped: 0
✗ Failed: 0
```

---

### Step 2: Run Actual Backfill

```bash
make trigger-backfill
```

**Or via Airflow UI:**
```
http://localhost:8080
→ DAGs
→ arsenal_backfill_season
→ Trigger DAG
```

**What happens:**
1. Scrapes all 20 Arsenal matches from Understat
2. Gets shot-level xG data for each match
3. Saves to Bronze layer
4. Runs dbt transformations
5. Computes season metrics

**Expected Duration**: ~3-5 minutes

**Progress Monitoring:**
```bash
# Watch Airflow logs
docker-compose logs -f airflow-scheduler

# Or Airflow UI → arsenal_backfill_season → Graph View
```

---

### Step 3: Verify Backfilled Data

```bash
# Open database
make db-shell
```

```sql
-- Count total matches
SELECT COUNT(*) FROM bronze.understat_raw;
-- Expected: ~20 matches

-- Check match list
SELECT
    match_id,
    scraped_at,
    jsonb_array_length(raw_shots->'home_shots') AS home_shots,
    jsonb_array_length(raw_shots->'away_shots') AS away_shots
FROM bronze.understat_raw
ORDER BY scraped_at DESC
LIMIT 10;

-- Season aggregates
SELECT
    matches_played,
    wins,
    draws,
    losses,
    goals_for,
    goals_against,
    xg_for,
    xg_against,
    xg_difference
FROM metrics.season_team_summary sts
JOIN gold.dim_team dt ON sts.team_id = dt.team_id
WHERE dt.team_name = 'Arsenal';
```

---

## 📊 **Dashboard with Full Season Data**

After backfill completes:

### Season Overview
```
┌─────────────────────────────────────────────────────────┐
│         Arsenal FC - 2025-26 Season                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Points: 45     Record: 14W 3D 2L                      │
│  Goals: 40-15 (+25)    xG: 38.5-12.3 (+26.2)          │
│                                                         │
│  Recent Matches (Last 10):                              │
│  • Jan 03: Bournemouth 2-3 Arsenal (xG: 0.95-1.28)     │
│  • Dec 30: Arsenal 5-1 Brentford (xG: 3.2-0.6)         │
│  • Dec 26: Fulham 1-1 Arsenal (xG: 1.1-1.8) ← Unlucky  │
│  ...                                                    │
│                                                         │
│  xG Trend (Last 10 matches):                            │
│  [Line chart showing Arsenal xG vs Opponents]           │
└─────────────────────────────────────────────────────────┘
```

### Match Detail (Any match)
- Full stats for all 20 matches
- Player performance for each game
- Shot maps (data ready, visualization pending)

### Player Performance (Season totals)
```
Player      | Matches | Goals | Assists | xG   | xA   | Prog.Pass
------------|---------|-------|---------|------|------|----------
Saka        |   19    |  10   |    7    | 9.2  | 8.1  |   152
Ødegaard    |   18    |   4   |   10    | 5.8  | 11.2 |   216
Havertz     |   17    |   8   |    3    | 7.5  | 3.2  |    68
...
```

---

## 🔍 **Data Quality Insights**

### What Backfill Provides:
- ✅ **Shot-level xG data** (Understat)
- ✅ **Match results and scores**
- ✅ **xG flow timeline data**
- ✅ **Season aggregates**

### What's Limited (Backfill Only):
- ⚠️ **No player stats** (passes, dribbles, tackles)
  - *Reason*: Backfill uses Understat only (no FBref)
  - *Workaround*: Forward matches have full FBref data

- ⚠️ **No team possession stats**
  - *Reason*: Understat doesn't provide possession %
  - *Impact*: Limited context for some analyses

### Future Matches (Post-Backfill):
- ✅ **Full FBref data** (fixture monitor DAG)
- ✅ **Player-level statistics**
- ✅ **All progressive actions metrics**

---

## 🎯 **Use Cases After Backfill**

### 1. **Performance Trends**
```sql
-- Arsenal's xG trend over season
SELECT
    dm.match_date,
    ftmp.xg_for AS arsenal_xg,
    ftmp.xg_against AS opponent_xg
FROM gold.fact_team_match_performance ftmp
JOIN gold.dim_match dm ON ftmp.match_id = dm.match_id
JOIN gold.dim_team dt ON ftmp.team_id = dt.team_id
WHERE dt.team_name = 'Arsenal'
ORDER BY dm.match_date;
```

### 2. **Home vs Away Analysis**
```sql
-- Home vs Away performance
SELECT
    CASE WHEN ftmp.is_home THEN 'Home' ELSE 'Away' END AS venue_type,
    COUNT(*) AS matches,
    AVG(ftmp.xg_for) AS avg_xg_for,
    AVG(ftmp.xg_against) AS avg_xg_against,
    SUM(CASE WHEN ftmp.result = 'W' THEN 1 ELSE 0 END) AS wins
FROM gold.fact_team_match_performance ftmp
JOIN gold.dim_team dt ON ftmp.team_id = dt.team_id
WHERE dt.team_name = 'Arsenal'
GROUP BY venue_type;
```

### 3. **Over/Underperformance**
```sql
-- Goals vs xG (luck vs skill)
SELECT
    SUM(goals_for) AS actual_goals,
    SUM(xg_for) AS expected_goals,
    SUM(goals_for) - SUM(xg_for) AS overperformance
FROM gold.fact_team_match_performance ftmp
JOIN gold.dim_team dt ON ftmp.team_id = dt.team_id
WHERE dt.team_name = 'Arsenal';

-- If positive: Arsenal scoring more than expected (clinical or lucky)
-- If negative: Underperforming xG (poor finishing or unlucky)
```

---

## 📈 **Expected Results Summary**

| Metric | After 1 Match | After Backfill (~20 matches) |
|--------|---------------|------------------------------|
| **Matches in DB** | 1 | ~20 |
| **Dashboard - Season** | Limited (1 match) | Full season context |
| **xG Trend** | 1 point | 20-point trend line |
| **Statistical Power** | Low | High (meaningful insights) |
| **Player Totals** | 1 match only | Season aggregates |
| **Form Analysis** | N/A | Rolling averages possible |

---

## 🚨 **Important Notes**

### Backfill Limitations:
1. **Understat only**: No FBref player stats for historical matches
2. **Forward compatibility**: New matches (from fixture monitor) WILL have full data
3. **Data quality**: Shot-level xG is accurate, but missing possession/passing context

### Why This Approach?
- **Speed**: Backfill completes in ~5 minutes (vs hours for full FBref scraping)
- **Compliance**: Respects FBref rate limits (only current matches)
- **Value**: 80% of insights from 20% of data (xG is most important metric)

### When to Use Full FBref Backfill?
If you need historical player stats (passes, dribbles, tackles):
- Manually trigger `arsenal_match_scraper` for each historical match
- Provide FBref match URLs (requires manual lookup)
- **Time**: ~20 matches × 15 sec = ~5 minutes

---

## ✅ **Testing Checklist**

- [ ] Platform started (`make start`)
- [ ] Test Bournemouth match (`make test-bournemouth`)
- [ ] View data in database (`make db-shell`)
- [ ] Run dbt transformations (`make dbt-run`)
- [ ] Check dashboard (http://localhost:8501)
- [ ] Trigger full backfill (`make trigger-backfill`)
- [ ] Verify ~20 matches in database
- [ ] Explore season overview dashboard
- [ ] View individual match details
- [ ] Check player season totals

---

## 🎉 **Success Criteria**

**Platform is working correctly if:**
- ✅ Bournemouth match scrapes successfully
- ✅ Database shows 1 match in all layers (Bronze/Silver/Gold)
- ✅ Dashboard displays match result (3-2 Arsenal win)
- ✅ Backfill DAG completes in ~5 minutes
- ✅ Season overview shows ~20 matches
- ✅ xG trends visible in dashboard

---

## 📚 **Next Steps**

After successful testing:

1. **Enable Automatic Scraping**:
   - Airflow UI → `arsenal_fixture_monitor` → Toggle ON
   - Runs daily, auto-scrapes new matches

2. **Add Visualizations**:
   - Shot maps (Plotly)
   - xG flow timeline
   - League comparisons

3. **Extend to Other Teams** (optional):
   - Scrape all PL teams
   - League-wide xG rankings
   - Opponent analysis context

---

**Ready to test!** Run `make test-bournemouth` to see your platform process real Arsenal FC data! 🔴⚪⚽
