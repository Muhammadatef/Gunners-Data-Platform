# Migration to React.js/Node.js - Complete ✅

The Arsenal FC Analytics Platform has been successfully migrated from Streamlit to a modern React.js (Next.js) frontend with Node.js/GraphQL backend.

## What's New

### Backend (Node.js + GraphQL)
- **GraphQL API** at `http://localhost:4000/graphql`
- **Apollo Server** with Express
- **PostgreSQL** connection pooling
- **Health check** endpoint at `/health`

### Frontend (Next.js + React)
- **Modern React** application with Next.js 14
- **Chakra UI** components with Arsenal branding
- **6 Dashboard Tabs**:
  1. Season Overview
  2. Match Detail
  3. Player Stats
  4. Tactical Analysis
  5. Shot Networks
  6. Expected Threat
- **Responsive design** for all devices
- **Arsenal cannon logo** and branding

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Build and start all services
docker compose up --build

# Access the platform
# Frontend: http://localhost:3000
# Backend GraphQL: http://localhost:4000/graphql
# GraphQL Playground: http://localhost:4000/graphql
# Airflow: http://localhost:8080
# PostgreSQL: localhost:5432
```

### Manual Development Setup

#### Backend
```bash
cd backend
npm install
# Create .env file with database credentials
npm start
# Server runs on http://localhost:4000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
# App runs on http://localhost:3000
```

## Environment Variables

### Backend (.env)
```
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=arsenalfc_analytics
POSTGRES_USER=analytics_user
POSTGRES_PASSWORD=analytics_pass
PORT=4000
NODE_ENV=development
```

### Frontend (.env.local)
```
NEXT_PUBLIC_GRAPHQL_URL=http://localhost:4000/graphql
```

## Architecture

```
Frontend (Next.js) → GraphQL API (Node.js) → PostgreSQL
```

- **Frontend**: React components, Chakra UI, Recharts, D3.js
- **Backend**: Apollo Server, GraphQL, Express, PostgreSQL client
- **Database**: Existing PostgreSQL with metrics views (unchanged)

## Features

✅ All 6 dashboard tabs implemented
✅ Arsenal branding with cannon logo
✅ Responsive design
✅ Interactive visualizations
✅ Season selector in header
✅ GraphQL API with all queries
✅ Docker integration
✅ Health checks

## Migration Notes

- **Streamlit dashboard** is deprecated but kept in docker-compose.yml (commented out)
- **Database schema** unchanged - uses existing views
- **All features** from Streamlit dashboard preserved
- **New features** can be added via GraphQL schema extensions

## Troubleshooting

### Backend won't start
- Check PostgreSQL is running: `docker ps | grep postgres`
- Verify database credentials in `.env`
- Check logs: `docker logs arsenalfc_backend`

### Frontend won't connect
- Verify `NEXT_PUBLIC_GRAPHQL_URL` is set correctly
- Check backend is running: `curl http://localhost:4000/health`
- Check browser console for errors

### No data showing
- Ensure database has data: `docker exec arsenalfc_postgres psql -U analytics_user -d arsenalfc_analytics -c "SELECT COUNT(*) FROM metrics.season_summary;"`
- Run backfill if needed: `docker exec arsenalfc_airflow_scheduler python /opt/airflow/scripts/backfill_all.py`

## Next Steps

1. Replace placeholder Arsenal cannon logo with official SVG
2. Add authentication if needed
3. Deploy to production
4. Add more analytics features via GraphQL

---

**Migration completed successfully!** 🎉
