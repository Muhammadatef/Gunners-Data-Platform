# ⚽ Arsenal FC Analytics Platform

> **Production-ready football analytics platform** with AI-powered chatbot, 11 interactive dashboards, and automated data collection.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![Airflow](https://img.shields.io/badge/Airflow-2.8.1-red.svg)](https://airflow.apache.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

## 📊 Overview

A comprehensive football analytics platform that automatically scrapes, processes, and visualizes Arsenal FC's performance data with an AI-powered RAG chatbot for natural language queries.

### Key Features

- 🤖 **AI Chatbot** - RAG-powered analytics assistant using Claude
- 📊 **11 Dashboards** - Season overview, player stats, tactical analysis, and more
- 🎯 **Advanced Metrics** - xG, xT, shot networks, conversion rates
- 🔄 **Automated Scraping** - Airflow DAGs scrape 2 hours after each match
- 🏗️ **Medallion Architecture** - Bronze → Silver → Gold data layers
- 🐳 **Dockerized** - One-command deployment

---

## 🚀 Quick Start

```bash
# Start all services
make up

# Or manually:
docker compose up -d

# Check status
make status
```

### Access Points

| Service | URL |
|---------|-----|
| **Dashboard** | http://localhost:3000 |
| **GraphQL API** | http://localhost:4000/graphql |
| **Airflow UI** | http://localhost:8080  |
| **RAG Chatbot API** | http://localhost:5000 |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     DATA SOURCES                                 │
│   Understat.com (xG/shots)  •  FBref.com (advanced stats)       │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   APACHE AIRFLOW                                 │
│   Scheduled scraping • 2 hours after each match                 │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    POSTGRESQL                                    │
│   Bronze (raw) → Silver (cleaned) → Gold (metrics)              │
└────────────────┬──────────────────────────┬─────────────────────┘
                 │                          │
                 ▼                          ▼
┌────────────────────────┐     ┌────────────────────────────────┐
│   GraphQL Backend      │     │      RAG Chatbot               │
│   (Node.js:4000)       │     │   (Python/FastAPI:5000)        │
└───────────┬────────────┘     └──────────────┬─────────────────┘
            │                                  │
            └─────────────┬────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   REACT FRONTEND                                 │
│   11 Dashboards  •  AI Chatbot  •  Chakra UI  (Port 3000)       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📈 Dashboard Features

| Dashboard | Description |
|-----------|-------------|
| **Season Overview** | W/D/L record, points, xG trends |
| **Match Detail** | Shot maps, xG timeline, scorers |
| **Player Stats** | Goals, xG, conversion rates |
| **Tactical Analysis** | Formation patterns, situation breakdown |
| **Shot Networks** | Passing and shooting connections |
| **Expected Threat** | Zone-based xT analysis |
| **Player Match** | Per-match player breakdown |
| **Opponent Analysis** | Head-to-head comparisons |
| **Performance Trends** | Rolling averages |
| **Player Comparison** | Side-by-side stats |
| **Match Insights** | AI-generated observations |

---

## 🤖 AI Chatbot (RAG)

Ask questions in natural language:

> "How did Arsenal perform against Liverpool this season?"
> "Who is our top scorer?"
> "What's our xG trend in away games?"

The chatbot uses:
- **ChromaDB** for vector search
- **Claude 3.5 Sonnet** for responses
- Real match data from your database

See [DOCUMENTATION.md](DOCUMENTATION.md) for a complete RAG tutorial.

---

## 🛠️ Development

### Project Structure

```
Gunners-Platform/
├── frontend-vite/     # React + Vite + Chakra UI
├── backend/           # Node.js + GraphQL
├── rag-chatbot/       # Python FastAPI + RAG
├── scrapers/          # Playwright + BeautifulSoup
├── airflow/           # DAGs and scheduling
├── database/          # SQL schemas
├── docker-compose.yml
├── Makefile          
└── DOCUMENTATION.md   # Complete guide + RAG tutorial
```

### Makefile Commands

```bash
make up              # Start all services
make down            # Stop all services
make status          # Show container status
make logs            # Follow all logs
make rebuild-frontend # Rebuild frontend
make db-shell        # PostgreSQL shell
make clean           # Remove everything
```

---

## 📝 Environment Variables

Create `.env` in project root:

```env
# Required for RAG chatbot
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Database (defaults work with Docker)
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=arsenalfc_analytics
POSTGRES_USER=analytics_user
POSTGRES_PASSWORD=analytics_pass
```

---

## 📚 Documentation

See **[DOCUMENTATION.md](DOCUMENTATION.md)** for:
- Complete architecture details
- Data flow diagrams
- RAG tutorial (beginner-friendly)
- Troubleshooting guide

---

## 📝 License

MIT License

---

<p align="center">
  Made with ❤️ for Arsenal FC
</p>
