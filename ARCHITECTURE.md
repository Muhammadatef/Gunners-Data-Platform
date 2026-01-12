# Arsenal FC Analytics Platform - Architecture & Data Flow

## 📊 Platform Overview

The Arsenal FC Analytics Platform is a comprehensive football analytics system that automatically collects, processes, and visualizes Arsenal FC's match performance data. It provides deep tactical insights using Expected Goals (xG), advanced shooting metrics, player statistics, and pass networks.

### What It Does

1. **Automated Data Collection**: Scrapes match data from Understat.com and FBref.com after each Arsenal match
2. **Data Processing**: Transforms raw data through a medallion architecture (Bronze → Silver → Gold → Metrics)
3. **Analytics Dashboard**: Provides interactive visualizations and insights through a modern web interface
4. **Real-time Updates**: Automatically updates when new match data is available

---

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA INGESTION LAYER                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Understat   │  │    FBref     │  │   Playwright │          │
│  │   Scraper    │  │   Scraper    │  │   Browser    │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                   │
│         └──────────────────┴──────────────────┘                  │
│                            │                                      │
│                    ┌───────▼────────┐                            │
│                    │  Apache Airflow │                            │
│                    │  (Orchestration)│                            │
│                    └───────┬────────┘                            │
└────────────────────────────┼────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATA STORAGE LAYER                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              PostgreSQL Database                         │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐│  │
│  │  │  Bronze  │→ │  Silver  │→ │   Gold   │→ │ Metrics  ││  │
│  │  │  (Raw)   │  │ (Cleaned)│  │(Business)│  │(Analytics)│  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘│  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API LAYER                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Node.js + GraphQL API                        │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐              │  │
│  │  │ Apollo   │  │ GraphQL  │  │ PostgreSQL│              │  │
│  │  │ Server   │  │ Resolvers│  │  Client   │              │  │
│  │  └──────────┘  └──────────┘  └──────────┘              │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Next.js + React Frontend                     │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐              │  │
│  │  │  React   │  │  Chakra  │  │  Charts   │              │  │
│  │  │ Components│ │    UI    │  │ (Recharts)│              │  │
│  │  └──────────┘  └──────────┘  └──────────┘              │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow

### 1. Data Collection Phase

```
Match Ends → Airflow DAG Triggered → Scrapers Execute
```

**Process:**
1. **Match Completion**: Arsenal match finishes
2. **Airflow Scheduling**: Smart DAG detects match completion and schedules scraping 2 hours after kickoff
3. **Web Scraping**: 
   - **Understat Scraper**: Uses Playwright to scrape shot-level xG data
   - **FBref Scraper**: Scrapes player statistics and match metadata
4. **Data Extraction**: Raw JSON data extracted from websites

**Key Components:**
- `scrapers/understat_scraper.py` - Scrapes shot data with xG values
- `scrapers/fbref_scraper.py` - Scrapes player stats and lineups
- `scrapers/playwright_scraper.py` - Browser automation (bypasses anti-bot)
- `airflow/dags/arsenal_smart_match_scraper.py` - Intelligent scheduling

### 2. Data Ingestion Phase

```
Raw Data → Database Loader → Bronze Layer (PostgreSQL)
```

**Process:**
1. **Data Validation**: Validate scraped data structure
2. **Database Loading**: Insert raw data into Bronze layer
3. **Metadata Linking**: Link shots to match references
4. **Run Tracking**: Track scrape runs for audit

**Bronze Layer Tables:**
- `bronze.understat_raw` - Raw shot data with JSONB
- `bronze.match_reference` - Match metadata (date, teams, season)
- `bronze.fbref_lineups` - Player lineup information
- `bronze.scrape_runs` - Audit log of all scrapes

### 3. Data Transformation Phase

```
Bronze → Silver → Gold → Metrics (SQL Views)
```

**Silver Layer** (`silver.shot_events`):
- Cleans and structures shot-level data
- Joins with match metadata
- Normalizes coordinates and xG values
- Links player positions from FBref

**Gold Layer** (`gold.*`):
- Business-level aggregations
- Match summaries
- Player statistics
- Team performance metrics

**Metrics Layer** (`metrics.*`):
- Advanced analytics views
- Pre-computed aggregations
- Tactical analysis
- Expected Threat (xT) calculations

**Key Views:**
- `metrics.season_summary` - Season-level statistics
- `metrics.arsenal_matches` - Match results with xG
- `metrics.player_advanced_stats` - 30+ metrics per player
- `metrics.match_shots_detail` - Detailed shot data
- `metrics.assist_network` - Pass/assist networks
- `metrics.player_xt_stats` - Expected Threat metrics
- `metrics.tactical_analysis` - Tactical patterns

### 4. API Layer

```
PostgreSQL Views → GraphQL Resolvers → GraphQL API
```

**Process:**
1. **GraphQL Schema**: Defines data types and queries
2. **Resolvers**: Map GraphQL queries to SQL queries
3. **Data Fetching**: Execute SQL against PostgreSQL views
4. **Response**: Return JSON data to frontend

**GraphQL Queries:**
- `seasons` - List all available seasons
- `seasonSummary(season)` - Season statistics
- `matches(season)` - Match results
- `playerStats(season)` - Player statistics
- `matchShots(matchId)` - Shots for a match
- `assistNetwork(season)` - Assist networks
- `playerXTStats(season)` - Expected Threat stats
- `tacticalAnalysis(season)` - Tactical metrics

**Backend Components:**
- `backend/src/server.js` - Express + Apollo Server
- `backend/src/schema/schema.js` - GraphQL type definitions
- `backend/src/resolvers/` - Query resolvers
- `backend/src/db/connection.js` - PostgreSQL connection pool

### 5. Presentation Layer

```
GraphQL API → Apollo Client → React Components → User Interface
```

**Process:**
1. **GraphQL Queries**: Frontend sends GraphQL queries
2. **Apollo Client**: Manages caching and state
3. **React Components**: Render data with Chakra UI
4. **Visualizations**: Display charts using Recharts, D3.js, Plotly

**Frontend Components:**
- `frontend/src/app/page.tsx` - Main dashboard with tabs
- `frontend/src/components/dashboards/` - Dashboard tab components
- `frontend/src/components/Pitch.tsx` - Football pitch visualization
- `frontend/src/lib/apollo-client.ts` - GraphQL client setup

**Dashboard Tabs:**
1. **Season Overview** - Season statistics, form charts, xG trends
2. **Match Detail** - Shot maps, xG timeline, match analysis
3. **Player Stats** - Player leaderboards, heatmaps, metrics
4. **Tactical Analysis** - Shot zones, outcomes, situation effectiveness
5. **Shot Networks** - Assist networks with D3.js graphs
6. **Expected Threat** - xT leaders and comparisons
7. **Player Match Analysis** - Individual player heat maps and pass networks per match

---

## 🧩 Component Details

### Data Collection Components

#### 1. Understat Scraper
- **Purpose**: Scrape shot-level xG data
- **Technology**: Playwright (headless browser)
- **Data Collected**:
  - Shot coordinates (x, y normalized 0-1)
  - xG values
  - Shot outcomes (Goal, Saved, Blocked, Missed)
  - Shot situations (Open Play, Corner, Set Piece)
  - Assist information
- **Frequency**: After each match (2 hours post-kickoff)

#### 2. FBref Scraper
- **Purpose**: Scrape player statistics and lineups
- **Technology**: BeautifulSoup + Requests
- **Data Collected**:
  - Player lineups and positions
  - Match metadata
  - Team statistics
- **Frequency**: After each match

#### 3. Airflow Orchestration
- **DAGs**:
  - `arsenal_smart_match_scraper` - Intelligent scheduling (recommended)
  - `arsenal_auto_match_scraper` - Runs every 2 hours (backup)
  - `arsenal_manual_match_scraper` - Manual trigger for backfills
- **Scheduling**: Automatically finds next match and schedules scraping

### Database Architecture

#### Medallion Architecture

**Bronze Layer** (Raw Data):
- Stores raw scraped data as-is
- JSONB format for flexibility
- No transformations
- Source of truth

**Silver Layer** (Cleaned Data):
- Structured and validated data
- Joined with metadata
- Normalized formats
- SQL views for easy querying

**Gold Layer** (Business Logic):
- Business-level aggregations
- Match summaries
- Player statistics
- Optimized for analytics

**Metrics Layer** (Advanced Analytics):
- Pre-computed metrics
- Tactical analysis
- Advanced statistics
- Performance optimized views

### API Architecture

#### GraphQL Schema
- **Type System**: Strongly typed schema
- **Queries**: Read-only operations
- **Scalars**: Custom Date and Decimal types
- **Resolvers**: Map queries to SQL

#### Resolvers
- `season.js` - Season-related queries
- `match.js` - Match and shot queries
- `player.js` - Player statistics queries
- `tactical.js` - Tactical analysis queries

### Frontend Architecture

#### Next.js App Router
- **Pages**: Server-side rendering ready
- **Components**: Client-side React components
- **Routing**: File-based routing

#### State Management
- **Apollo Client**: GraphQL state and caching
- **React Context**: Season selection state
- **Local State**: Component-level state

#### UI Components
- **Chakra UI**: Component library
- **Recharts**: Chart visualizations
- **D3.js**: Network graphs
- **Custom**: Pitch visualization component

---

## 🔄 Complete Data Flow Example

### Scenario: New Match Data Available

```
1. Match Ends (Arsenal vs Liverpool, 3-1)
   │
   ▼
2. Airflow DAG Triggered (2 hours after kickoff)
   │
   ▼
3. Understat Scraper Executes
   - Playwright opens match page
   - Extracts shot data (25 shots, 3 goals)
   - Extracts xG data (2.8 total xG)
   │
   ▼
4. FBref Scraper Executes
   - Scrapes player lineups
   - Scrapes match metadata
   │
   ▼
5. Data Loaded into Bronze Layer
   - Raw JSON stored in bronze.understat_raw
   - Match reference created in bronze.match_reference
   │
   ▼
6. SQL Views Automatically Update
   - silver.shot_events view includes new shots
   - metrics.arsenal_matches view includes new match
   - metrics.season_summary recalculates
   │
   ▼
7. Frontend Queries GraphQL API
   - User opens dashboard
   - Apollo Client queries seasonSummary
   │
   ▼
8. GraphQL Resolver Executes
   - Queries metrics.season_summary view
   - Returns updated statistics
   │
   ▼
9. React Component Renders
   - Displays updated match count
   - Shows new match in recent matches table
   - Updates all visualizations
```

---

## 📊 Data Models

### Shot Event Model
```typescript
{
  matchId: string
  playerName: string
  minute: number
  x: number (0-1 normalized)
  y: number (0-1 normalized)
  xg: number (0-1)
  result: "Goal" | "SavedShot" | "BlockedShot" | "MissedShots"
  situation: "OpenPlay" | "FromCorner" | "SetPiece" | "Penalty"
  shotType: "RightFoot" | "LeftFoot" | "Head" | "OtherBodyPart"
  assistedBy: string | null
}
```

### Match Model
```typescript
{
  matchUrl: string
  matchDate: Date
  season: string
  opponent: string
  venue: "H" | "A"
  result: "W" | "D" | "L"
  arsenalGoals: number
  opponentGoals: number
  arsenalXg: number
  opponentXg: number
}
```

### Player Stats Model
```typescript
{
  playerName: string
  season: string
  goals: number
  totalXg: number
  assists: number
  totalShots: number
  conversionPct: number
  shotAccuracyPct: number
  // ... 30+ more metrics
}
```

---

## 🛠️ Technology Stack

### Backend
- **Node.js 20** - Runtime
- **Express** - Web framework
- **Apollo Server** - GraphQL server
- **PostgreSQL 15** - Database
- **pg** - PostgreSQL client

### Frontend
- **Next.js 14** - React framework
- **React 18** - UI library
- **Chakra UI** - Component library
- **Apollo Client** - GraphQL client
- **Recharts** - Chart library
- **D3.js** - Network graphs
- **TypeScript** - Type safety

### Data Pipeline
- **Python 3.11** - Scraping scripts
- **Playwright** - Browser automation
- **BeautifulSoup** - HTML parsing
- **Apache Airflow 2.8.1** - Orchestration
- **PostgreSQL** - Data warehouse

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Orchestration
- **PostgreSQL** - Database

---

## 🔐 Security & Access

### Database Access
- **Read-Only User**: `analytics_user` (for API)
- **Admin User**: `arsenal_admin` (for schema changes)
- **Airflow User**: `airflow` (for Airflow metadata)

### API Access
- **GraphQL Endpoint**: Public (no authentication currently)
- **Health Check**: `/health` endpoint
- **CORS**: Enabled for frontend

### Network
- All services on `arsenalfc_network` Docker network
- Services communicate via service names
- Frontend accessible on `localhost:3000`

---

## 📈 Performance Considerations

### Database
- **Indexes**: On match_date, season, player_name
- **Views**: Pre-computed aggregations
- **Connection Pooling**: 20 max connections

### API
- **Apollo Caching**: Client-side query caching
- **Query Optimization**: Efficient SQL queries
- **Connection Pooling**: Reused database connections

### Frontend
- **Code Splitting**: Next.js automatic splitting
- **Lazy Loading**: Components loaded on demand
- **Caching**: Apollo Client cache for queries

---

## 🚀 Deployment

### Development
```bash
make quick-start  # Build, start, load data
```

### Production Considerations
- Environment variables for secrets
- Database backups scheduled
- Monitoring and logging
- SSL/TLS for HTTPS
- Authentication/authorization
- Rate limiting on API

---

## 📝 Key Metrics Tracked

### Match Level
- Goals, xG, xG overperformance
- Shot accuracy, big chances
- Situation effectiveness
- Shot timing patterns

### Player Level
- Goals, xG, assists
- Shot accuracy, conversion rate
- Big chance conversion
- Shot locations and types
- Expected Threat (xT)

### Tactical Level
- Shot zones and heatmaps
- Pass networks
- Build-up patterns
- Game state analysis

---

## 🔄 Update Cycle

1. **Match Completion** → 2 hours delay
2. **Scraping** → ~2-5 minutes
3. **Data Loading** → ~30 seconds
4. **View Updates** → Real-time (SQL views)
5. **Frontend Refresh** → User-triggered or auto-refresh

---

## 📚 Related Documentation

- `README.md` - Project overview
- `QUICKSTART.md` - Quick start guide
- `METRICS_GLOSSARY.md` - Metric definitions
- `Makefile` - Command reference
- `START_PLATFORM.md` - Detailed startup guide

---

**Last Updated**: 2025-01-08
**Platform Version**: 2.0.0
