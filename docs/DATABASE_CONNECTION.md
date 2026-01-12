# Database Connection Guide

## DBeaver Connection Settings

### Connection Details

| Setting | Value |
|---------|-------|
| **Host** | `localhost` |
| **Port** | `5432` |
| **Database** | `arsenalfc_analytics` |
| **Username** | `analytics_user` |
| **Password** | `analytics_pass` |
| **Driver** | PostgreSQL |

### Step-by-Step Setup in DBeaver

1. **Create New Connection**
   - Click "New Database Connection" button
   - Select "PostgreSQL" driver
   - Click "Next"

2. **Main Tab Settings**
   ```
   Host:     localhost
   Port:     5432
   Database: arsenalfc_analytics
   Username: analytics_user
   Password: analytics_pass
   ```

3. **Driver Properties Tab** (Advanced)
   ```
   SSL: false
   ```

4. **Test Connection**
   - Click "Test Connection" button
   - Should show "Connected" if successful

5. **Finish**
   - Click "Finish" to save connection

---

## Available Users

### 1. Analytics User (Read-Only) ✅ RECOMMENDED

**Use this for querying and analysis**

```
Username: analytics_user
Password: analytics_pass
Permissions: SELECT on all tables and views
```

**Why use this:**
- Safe for queries (can't accidentally modify data)
- Has access to all schemas: bronze, silver, gold, metrics
- Recommended for DBeaver, dashboards, reporting tools

### 2. Admin User (Full Access)

**Use only for schema changes and administration**

```
Username: arsenal_admin
Password: arsenal_pass
Permissions: Full (CREATE, DROP, ALTER, etc.)
```

**When to use:**
- Creating new tables or views
- Modifying schema
- Granting permissions
- Database maintenance

---

## Quick Connection Tests

### Using psql (Command Line)

```bash
# Connect as analytics_user
docker exec -it arsenalfc_postgres psql -U analytics_user -d arsenalfc_analytics

# Connect as admin
docker exec -it arsenalfc_postgres psql -U arsenal_admin -d arsenalfc_analytics
```

### Using Python

```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="arsenalfc_analytics",
    user="analytics_user",
    password="analytics_pass"
)

cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM bronze.understat_raw")
print(f"Total matches: {cursor.fetchone()[0]}")
conn.close()
```

### Using pgAdmin

1. Right-click "Servers" → Create → Server
2. General Tab:
   - Name: `Arsenal Analytics`
3. Connection Tab:
   ```
   Host:     localhost
   Port:     5432
   Database: arsenalfc_analytics
   Username: analytics_user
   Password: analytics_pass
   ```

---

## Database Schemas

### Available Schemas

| Schema | Purpose | Tables/Views |
|--------|---------|--------------|
| **bronze** | Raw data storage | understat_raw, match_reference, scrape_runs |
| **silver** | Cleaned data | shot_events (view) |
| **gold** | Business metrics | arsenal_matches, arsenal_player_stats, season_summary (views) |
| **metrics** | Advanced analytics | match_advanced_stats, player_advanced_stats, opponent_comparison, tactical_analysis (views) |
| **public** | System tables | (default schema) |

### Query Examples

**Season summary:**
```sql
SELECT * FROM metrics.season_summary;
```

**Recent matches:**
```sql
SELECT match_date, opponent, result, arsenal_goals, opponent_goals, arsenal_xg
FROM metrics.arsenal_matches
ORDER BY match_date DESC
LIMIT 10;
```

**Top scorers:**
```sql
SELECT player_name, goals, total_xg, conversion_pct
FROM metrics.player_advanced_stats
WHERE season = '2025-26'
ORDER BY goals DESC
LIMIT 10;
```

**All shots from a match:**
```sql
SELECT player_name, minute, result, xg, shot_type
FROM silver.shot_events
WHERE match_date = '2026-01-03'
ORDER BY minute;
```

---

## Troubleshooting

### Connection Refused

**Problem:** Can't connect to localhost:5432

**Solution:**
```bash
# Check if PostgreSQL container is running
docker ps | grep postgres

# If not running, start it
docker compose up -d postgres

# Check port mapping
docker port arsenalfc_postgres
```

### Authentication Failed

**Problem:** Wrong password or user doesn't exist

**Solution:**
```bash
# Check environment variables
docker exec arsenalfc_postgres env | grep POSTGRES

# Reset password (if needed)
docker exec arsenalfc_postgres psql -U postgres -c "ALTER USER analytics_user WITH PASSWORD 'analytics_pass';"
```

### Can't See Tables

**Problem:** Connected but no tables visible

**Solution:**
1. Make sure you're connected to `arsenalfc_analytics` database (not `postgres`)
2. Refresh schema in DBeaver (F5 or right-click → Refresh)
3. Check if data has been loaded:
   ```sql
   SELECT COUNT(*) FROM bronze.understat_raw;
   ```
4. If 0 rows, run backfill:
   ```bash
   docker exec arsenalfc_airflow_scheduler python /opt/airflow/scripts/backfill_all.py
   ```

### SSL Error

**Problem:** SSL connection error

**Solution:**
- In DBeaver, go to connection settings
- Navigate to "Driver properties" tab
- Find "ssl" property and set to `false`
- Or add to connection URL: `?ssl=false`

---

## Security Notes

⚠️ **Important for Production:**

1. **Change Default Passwords** - The credentials here are for development only
2. **Use SSL/TLS** - Enable SSL for remote connections
3. **Firewall Rules** - Only expose port 5432 to trusted networks
4. **Read-Only User** - Use analytics_user for queries, never share admin credentials
5. **Environment Variables** - Store credentials in .env file, not in code

**For production deployment:**
```bash
# Generate secure passwords
openssl rand -base64 32

# Update docker-compose.yml with strong passwords
# Use Docker secrets or cloud secret managers
```

---

## Connection String Formats

### Standard Connection String
```
postgresql://analytics_user:analytics_pass@localhost:5432/arsenalfc_analytics
```

### SQLAlchemy Format
```python
from sqlalchemy import create_engine

engine = create_engine('postgresql://analytics_user:analytics_pass@localhost:5432/arsenalfc_analytics')
```

### Django Settings
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'arsenalfc_analytics',
        'USER': 'analytics_user',
        'PASSWORD': 'analytics_pass',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

---

## Useful Queries for Exploration

### Database Size
```sql
SELECT pg_size_pretty(pg_database_size('arsenalfc_analytics'));
```

### Table Sizes
```sql
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname IN ('bronze', 'silver', 'gold', 'metrics')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### View Definitions
```sql
SELECT
    schemaname,
    viewname,
    definition
FROM pg_views
WHERE schemaname = 'metrics';
```

### Recent Activity
```sql
SELECT
    match_date,
    COUNT(*) as shots,
    SUM(CASE WHEN result = 'Goal' THEN 1 ELSE 0 END) as goals,
    ROUND(SUM(xg), 2) as total_xg
FROM silver.shot_events
WHERE team = 'Arsenal'
GROUP BY match_date
ORDER BY match_date DESC
LIMIT 10;
```
