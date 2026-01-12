# Quick Data Update Commands

## ✅ Your scrapers are ready! Run this to get all 2025-26 season data:

```bash
# This will scrape ALL missing matches from the current season
docker compose exec airflow-scheduler python /opt/airflow/scrapers/backfill_historical.py
```

This script will:
1. Check what season it is (2025-26)
2. Get all Arsenal matches from Understat
3. Check which ones are already in your database
4. Scrape only the missing ones
5. Load them into Bronze → Silver → Gold → Metrics layers

**Expected time:** 5-10 minutes for ~20 matches

---

## Check Progress:

```bash
# Watch the scraping in real-time
docker compose logs airflow-scheduler --follow

# Check how many matches you have
docker compose exec postgres psql -U analytics_user -d arsenalfc_analytics -c "SELECT season, COUNT(*) FROM metrics.arsenal_matches GROUP BY season ORDER BY season;"
```

---

## After Scraping Completes:

**Refresh your dashboard at http://localhost:3000** and you'll see:
- All 2025-26 season matches
- Portsmouth game (Jan 11, 2026)
- Updated stats and analytics

The dashboard will automatically show the latest data!
