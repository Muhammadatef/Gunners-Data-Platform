# 🚀 Arsenal FC Analytics Platform - Startup Guide

Complete guide to get the entire platform up and running.

## Prerequisites

- Docker & Docker Compose (v2.0+)
- 8GB RAM minimum
- Ports available: 3000 (Frontend), 4000 (Backend), 8080 (Airflow), 5432 (PostgreSQL)

---

## Quick Start (All Services)

### 1. Start All Services

```bash
# Navigate to project directory
cd /home/maf/maf/Gunners-Platform

# Build and start all services (first time)
docker compose up --build -d

# Or if already built, just start
docker compose up -d
```

This starts:
- ✅ PostgreSQL database
- ✅ Airflow (webserver + scheduler)
- ✅ Backend (GraphQL API)
- ✅ Frontend (Next.js React app)

### 2. Check Service Status

```bash
# Check all containers are running
docker compose ps

# Check logs for any service
docker compose logs backend
docker compose logs frontend
docker compose logs postgres
docker compose logs airflow-webserver
```

### 3. Access the Platform

| Service | URL | Credentials |
|---------|-----|-------------|
| **Frontend (Website)** | http://localhost:3000 | None |
| **Backend GraphQL API** | http://localhost:4000/graphql | None |
| **GraphQL Playground** | http://localhost:4000/graphql | None |
| **Airflow UI** | http://localhost:8080 | admin / admin |
| **PostgreSQL** | localhost:5432 | See below |

---

## Database Setup

### First Time: Load Historical Data

```bash
# Run backfill to load historical match data (58 matches, ~5 minutes)
docker exec arsenalfc_airflow_scheduler python /opt/airflow/scripts/backfill_all.py
```

### Database Credentials

**For Read-Only Access (Recommended):**
```
Host:     localhost
Port:     5432
Database: arsenalfc_analytics
Username: analytics_user
Password: analytics_pass
```

**For Admin Access:**
```
Host:     localhost
Port:     5432
Database: arsenalfc_analytics
Username: arsenal_admin
Password: arsenal_pass
```

### Verify Database Has Data

```bash
# Check if data exists
docker exec arsenalfc_postgres psql -U analytics_user -d arsenalfc_analytics \
  -c "SELECT COUNT(*) FROM bronze.understat_raw;"

# Check season summary
docker exec arsenalfc_postgres psql -U analytics_user -d arsenalfc_analytics \
  -c "SELECT * FROM metrics.season_summary;"
```

---

## Individual Service Commands

### Start Specific Services

```bash
# Start only database
docker compose up -d postgres

# Start database + backend
docker compose up -d postgres backend

# Start database + frontend
docker compose up -d postgres frontend

# Start everything except Airflow
docker compose up -d postgres backend frontend
```

### Stop Services

```bash
# Stop all services
docker compose down

# Stop and remove volumes (⚠️ deletes data)
docker compose down -v

# Stop specific service
docker compose stop backend
docker compose stop frontend
```

### Restart Services

```bash
# Restart all services
docker compose restart

# Restart specific service
docker compose restart backend
docker compose restart frontend
```

---

## View Logs

### All Services

```bash
# Follow all logs
docker compose logs -f

# Follow specific service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f postgres
docker compose logs -f airflow-webserver
docker compose logs -f airflow-scheduler
```

### Last N Lines

```bash
# Last 100 lines
docker compose logs --tail=100 backend
docker compose logs --tail=100 frontend
```

---

## Airflow Setup

### Enable Smart Match Scraper DAG

```bash
# Enable the recommended DAG (auto-scrapes after matches)
docker exec arsenalfc_airflow_scheduler airflow dags unpause arsenal_smart_match_scraper

# Check DAG status
docker exec arsenalfc_airflow_scheduler airflow dags list

# Trigger manual scrape
docker exec arsenalfc_airflow_scheduler airflow dags trigger arsenal_manual_match_scraper
```

### Airflow Access

- **URL**: http://localhost:8080
- **Username**: admin
- **Password**: admin

---

## Development Mode

### Backend Development

```bash
# Enter backend container
docker exec -it arsenalfc_backend sh

# Install new packages (from host)
cd backend
docker compose exec backend npm install <package-name>

# View backend logs
docker compose logs -f backend
```

### Frontend Development

```bash
# Enter frontend container
docker exec -it arsenalfc_frontend sh

# Install new packages (from host)
cd frontend
docker compose exec frontend npm install <package-name>

# View frontend logs
docker compose logs -f frontend
```

### Rebuild After Code Changes

```bash
# Rebuild specific service
docker compose up --build -d backend
docker compose up --build -d frontend

# Rebuild everything
docker compose up --build -d
```

---

## Troubleshooting

### Services Won't Start

```bash
# Check if ports are in use
lsof -i :3000  # Frontend
lsof -i :4000  # Backend
lsof -i :8080  # Airflow
lsof -i :5432  # PostgreSQL

# Kill process using port (if needed)
kill -9 <PID>
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker compose ps postgres

# Test connection
docker exec arsenalfc_postgres psql -U analytics_user -d arsenalfc_analytics -c "SELECT 1;"

# Restart PostgreSQL
docker compose restart postgres
```

### Frontend Can't Connect to Backend

```bash
# Check backend is running
curl http://localhost:4000/health

# Check backend logs
docker compose logs backend

# Verify GraphQL endpoint
curl -X POST http://localhost:4000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ seasons }"}'
```

### No Data Showing

```bash
# Check if data exists in database
docker exec arsenalfc_postgres psql -U analytics_user -d arsenalfc_analytics \
  -c "SELECT COUNT(*) FROM metrics.season_summary;"

# If 0, run backfill
docker exec arsenalfc_airflow_scheduler python /opt/airflow/scripts/backfill_all.py

# Check specific view
docker exec arsenalfc_postgres psql -U analytics_user -d arsenalfc_analytics \
  -c "SELECT * FROM metrics.arsenal_matches LIMIT 5;"
```

### Clear Everything and Start Fresh

```bash
# ⚠️ WARNING: This deletes all data
docker compose down -v
docker compose up --build -d

# Then reload data
docker exec arsenalfc_airflow_scheduler python /opt/airflow/scripts/backfill_all.py
```

---

## Health Checks

### Quick Health Check Script

```bash
#!/bin/bash
echo "Checking services..."

# Frontend
echo -n "Frontend: "
curl -s http://localhost:3000 > /dev/null && echo "✅" || echo "❌"

# Backend
echo -n "Backend: "
curl -s http://localhost:4000/health > /dev/null && echo "✅" || echo "❌"

# GraphQL
echo -n "GraphQL: "
curl -s -X POST http://localhost:4000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ seasons }"}' > /dev/null && echo "✅" || echo "❌"

# Airflow
echo -n "Airflow: "
curl -s http://localhost:8080/health > /dev/null && echo "✅" || echo "❌"

# PostgreSQL
echo -n "PostgreSQL: "
docker exec arsenalfc_postgres pg_isready -U analytics_user > /dev/null && echo "✅" || echo "❌"
```

Save as `check-services.sh` and run: `chmod +x check-services.sh && ./check-services.sh`

---

## Complete Startup Sequence

```bash
# 1. Navigate to project
cd /home/maf/maf/Gunners-Platform

# 2. Start all services
docker compose up --build -d

# 3. Wait for services to be ready (~30 seconds)
sleep 30

# 4. Check services are running
docker compose ps

# 5. Load historical data (first time only)
docker exec arsenalfc_airflow_scheduler python /opt/airflow/scripts/backfill_all.py

# 6. Enable Airflow DAG
docker exec arsenalfc_airflow_scheduler airflow dags unpause arsenal_smart_match_scraper

# 7. Access the platform
echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:4000/graphql"
echo "Airflow: http://localhost:8080"
```

---

## Useful Commands Summary

```bash
# Start everything
docker compose up -d

# Stop everything
docker compose down

# View logs
docker compose logs -f

# Rebuild after code changes
docker compose up --build -d

# Check status
docker compose ps

# Access database
docker exec -it arsenalfc_postgres psql -U analytics_user -d arsenalfc_analytics

# Load data
docker exec arsenalfc_airflow_scheduler python /opt/airflow/scripts/backfill_all.py
```

---

**That's it! Your platform should now be running at http://localhost:3000** 🎉
