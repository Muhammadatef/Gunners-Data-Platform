# ⚡ Quick Start Guide

## 🔑 Database Credentials (DBeaver)

### For Queries & Analysis (Read-Only) ✅ **RECOMMENDED**

```
Host:     localhost
Port:     5432
Database: arsenalfc_analytics
Username: analytics_user
Password: analytics_pass
```

### For Administration (Full Access)

```
Host:     localhost
Port:     5432
Database:   
Username: arsenal_admin
Password: arsenal_pass
```

---

## 🚀 Platform URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| **Dashboard** | http://localhost:8501 | None (public) |
| **Airflow UI** | http://localhost:8080 | airflow / airflow |
| **PostgreSQL** | localhost:5432 | See above |

---

## 📊 Quick Commands

### Start Platform
```bash
docker compose up -d
```

### Load Historical Data (First Time)
```bash
docker exec arsenalfc_airflow_scheduler python /opt/airflow/scripts/backfill_all.py
```

### View Dashboard
```bash
# Open browser to:
http://localhost:8501
```

### Check Database
```bash
docker exec -it arsenalfc_postgres psql -U analytics_user -d arsenalfc_analytics
```

### Stop Platform
```bash
docker compose down
```

---

## 🎯 Recommended DAG: arsenal_smart_match_scraper ⭐

```bash
docker exec arsenalfc_airflow_scheduler airflow dags unpause arsenal_smart_match_scraper
```

---

Happy analyzing! 🏆⚽
