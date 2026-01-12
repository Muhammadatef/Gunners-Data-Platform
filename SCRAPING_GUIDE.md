# Arsenal Match Data Scraping System

## ✅ What You Have:

### Scrapers (in `/scrapers/`):
1. **`understat_scraper.py`** - Gets shot-level xG data from Understat.com
2. **`fbref_scraper.py`** - Gets match stats from FBref
3. **`playwright_scraper.py`** - Browser automation to bypass anti-bot protection
4. **`db_loader.py`** - Loads data into PostgreSQL

### Airflow DAGs (in `/airflow/dags/`):
1. **`arsenal_smart_match_scraper.py`** - ⭐ MAIN DAG
   - Checks for new matches every 6 hours
   - Waits 2.5 hours after match time
   - Automatically scrapes when data is available
   - Schedule: `0 */6 * * *` (every 6 hours)

2. **`arsenal_auto_match_scraper.py`** - Backup automatic scraper
3. **`arsenal_manual_match_scraper.py`** - Manual trigger option

---

## 🚀 How to Get Current Data:

### Option 1: Enable Automatic Scraping (RECOMMENDED)
```bash
# Unpause the smart scraper DAG
docker compose exec airflow-scheduler airflow dags unpause arsenal_smart_match_scraper

# Check status
docker compose exec airflow-scheduler airflow dags list | grep arsenal
```

The DAG will now:
- Check every 6 hours for new Arsenal matches
- Wait 2.5 hours after each match
- Automatically scrape the data
- Load it into your database

### Option 2: Manual Trigger (For Missing Data)
```bash
# Trigger the DAG manually to scrape latest match
docker compose exec airflow-scheduler airflow dags trigger arsenal_smart_match_scraper

# Check the run status
docker compose logs airflow-scheduler --tail 50 | grep -i "arsenal\|scraping"
```

### Option 3: Backfill All Missing Matches
```bash
# Run the backfill script to get ALL 2025-26 season matches
docker compose exec airflow-scheduler python /opt/airflow/scrapers/backfill_historical.py

# This will scrape all matches from the current season
```

---

## 📊 Current Status:

**Data Available:**
- Season: 2024-25
- Matches: 38
- Last Match: May 25, 2025 (Southampton)

**Missing Data:**
- 2025-26 season (Aug 2025 - Jan 2026)
- Portsmouth match (Jan 11, 2026) - This is in the current season!

---

## ⚙️ How the System Works:

1. **Arsenal plays a match** (e.g., vs Portsmouth on Jan 11, 2026)
2. **2 hours after match ends**, data becomes available on Understat/FBref
3. **Smart DAG checks every 6 hours** for new matches
4. **When detected**, it scrapes the data automatically
5. **Data flows**: Understat → Bronze → Silver → Gold → Metrics → Dashboard
6. **Dashboard updates** with new match data

---

## 🎯 Next Steps:

1. **Enable the DAG** (I just did this)
2. **Trigger manual scrape** for all missing 2025-26 matches
3. **Verify data** appears in dashboard
4. **Let it run automatically** going forward

**Run this now to get all missing data:**
```bash
docker compose exec airflow-scheduler python /opt/airflow/scrapers/backfill_historical.py
```

This will take ~5-10 minutes to scrape all missing matches!
