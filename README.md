# ⚽ Arsenal FC Analytics Platform

> **Production-ready football analytics platform** providing comprehensive performance insights through automated data collection, transformation, and interactive visualization.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![Airflow](https://img.shields.io/badge/Airflow-2.8.1-red.svg)](https://airflow.apache.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28-red.svg)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

## 📊 Overview

A comprehensive football analytics platform that automatically scrapes, processes, and visualizes Arsenal FC's performance data. Built with enterprise-grade tools and best practices, this platform provides deep tactical insights using Expected Goals (xG) and advanced shooting metrics.

**Live Data**: 58 matches | 1,394 shots | 30+ metrics per player | 48 points (2025-26 season)

### Key Features

- 🤖 **Automated Data Collection** - Intelligent scheduling with Airflow DAGs
- 🎯 **Advanced Metrics** - xG, shot accuracy, big chances, tactical patterns
- 📈 **Real-time Dashboard** - 4 interactive pages with Plotly visualizations
- 🏗️ **Medallion Architecture** - Bronze → Silver → Gold → Metrics layers
- 🔄 **Smart Scraping** - Playwright browser automation bypassing anti-bot protection
- 🐳 **Dockerized Deployment** - One-command setup with docker-compose

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose (v2.0+)
- 8GB RAM minimum
- Ports available: 8080 (Airflow), 8501 (Dashboard), 5432 (PostgreSQL)

### Installation

\`\`\`bash
# Clone the repository
git clone https://github.com/Muhammadatef/Gunners-Data-Platform.git
cd arsenal-analytics-platform

# Start all services
docker compose up -d

# Run historical data backfill (58 matches, ~5 minutes)
docker exec arsenalfc_airflow_scheduler python /opt/airflow/scripts/backfill_all.py

# Access the platform
# Airflow UI: http://localhost:8080 (airflow/airflow)
# Dashboard:  http://localhost:8501
\`\`\`

That's it! The platform is now running with 58 matches of historical data.

---

## 🏗️ Architecture

### System Diagram

\`\`\`
┌─────────────────────────────────────────────────────────────┐
│                   DATA INGESTION LAYER                       │
│  📊 Understat.com → 🌐 Playwright → 🔄 Airflow              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              POSTGRESQL DATA LAYERS                          │
│  🥉 Bronze (Raw) → 🥈 Silver (Clean) → 🥇 Gold (Business)  │
│  → 💎 Metrics (Advanced Analytics)                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  STREAMLIT DASHBOARD                         │
│  Season Overview | Match Detail | Player Stats | Tactical   │
└─────────────────────────────────────────────────────────────┘
\`\`\`

### Technology Stack

- **Data Collection**: Playwright, Python 3.11
- **Orchestration**: Apache Airflow 2.8.1  
- **Database**: PostgreSQL 16 (JSONB support)
- **Transformation**: SQL Views (real-time)
- **Visualization**: Streamlit, Plotly
- **Deployment**: Docker Compose

---

## 📈 Dashboard Features

### 1. Season Overview
- W/D/L record, points, win rate %
- Goals For/Against with xG comparison
- Recent form chart (last 10 matches)
- xG trend visualization

### 2. Match Detail Analysis
- Interactive shot maps (sized by xG)
- Cumulative xG timeline by minute
- Shot quality distribution
- Shot type breakdown

### 3. Player Performance
- Top scorers with xG analysis
- Goals vs xG scatter plots
- 30+ metrics per player
- Shot accuracy and efficiency

### 4. Tactical Analysis
- Shot timing by 15-minute periods
- Situation effectiveness
- Big chance conversion rates
- Build-up pattern analysis

---

## 🔄 Airflow DAGs

### Recommended: arsenal_smart_match_scraper ⭐

**Intelligent scheduling based on actual match times**

- Automatically finds next Arsenal match
- Schedules scraping 2 hours after kickoff
- Self-updating and production-ready

**Enable:**
\`\`\`bash
docker exec arsenalfc_airflow_scheduler airflow dags unpause arsenal_smart_match_scraper
\`\`\`

### Backup Options

- **arsenal_auto_match_scraper**: Runs every 2 hours (backup)
- **arsenal_manual_match_scraper**: Manual trigger for backfills

---

## 📊 Database Schema

### Data Layers

| Layer | Purpose | Example Tables/Views |
|-------|---------|---------------------|
| **Bronze** | Raw data | understat_raw, match_reference |
| **Silver** | Cleaned data | shot_events |
| **Gold** | Business metrics | arsenal_matches, season_summary |
| **Metrics** | Advanced analytics | player_advanced_stats, tactical_analysis |

### Key Metrics Available

- Match-level: Shot accuracy %, big chances, timing patterns
- Player-level: Goals, xG, conversion %, assists, shot types
- Tactical: Situation effectiveness, build-up patterns
- Opponent: Head-to-head records, win rates

---

## 🛠️ Development

### Project Structure

\`\`\`
arsenal-analytics-platform/
├── dags/                  # Airflow DAG definitions
├── scrapers/              # Web scraping modules
├── dashboard/             # Streamlit application
├── database/init/         # SQL schema and views
├── docs/                  # Documentation
├── docker-compose.yml     # Container orchestration
└── README.md             # This file
\`\`\`

### Common Commands

\`\`\`bash
# View logs
docker logs arsenalfc_airflow_scheduler --tail 100
docker logs arsenalfc_dashboard --tail 50

# Access database
docker exec -it arsenalfc_postgres psql -U analytics_user -d arsenalfc_analytics

# Trigger manual scrape
docker exec arsenalfc_airflow_scheduler airflow dags trigger arsenal_manual_match_scraper

# Restart services
docker compose restart
\`\`\`

---

## 🚨 Troubleshooting

### Dashboard shows "No data"

\`\`\`bash
# Check if data exists
docker exec arsenalfc_postgres psql -U analytics_user -d arsenalfc_analytics \\
  -c "SELECT COUNT(*) FROM bronze.understat_raw;"

# If 0, run backfill
docker exec arsenalfc_airflow_scheduler python /opt/airflow/scripts/backfill_all.py
\`\`\`

### Playwright browser errors

\`\`\`bash
# Reinstall Playwright
docker exec arsenalfc_airflow_scheduler python -m pip install playwright
docker exec arsenalfc_airflow_scheduler python -m playwright install chromium
\`\`\`

---

## 📝 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- Data provided by [Understat.com](https://understat.com)
- Built with [Apache Airflow](https://airflow.apache.org/), [Streamlit](https://streamlit.io/), and [Playwright](https://playwright.dev/)

---

## 🎯 Roadmap

- [ ] Add FBref data source for player positions
- [ ] Implement xT (Expected Threat) calculations
- [ ] Add passing network visualizations
- [ ] ML models for match prediction
- [ ] Support for multiple teams
- [ ] CI/CD pipeline with GitHub Actions

---

<p align="center">
  Made with ❤️ for Arsenal FC fans and data enthusiasts
</p>
