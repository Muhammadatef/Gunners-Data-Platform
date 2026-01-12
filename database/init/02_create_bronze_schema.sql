-- Bronze Layer: Raw scraped data
-- This layer stores unprocessed data exactly as received from sources

\c arsenalfc_analytics

-- FBref raw match data
CREATE TABLE IF NOT EXISTS bronze.fbref_raw (
    id SERIAL PRIMARY KEY,
    match_id VARCHAR(50) UNIQUE NOT NULL,
    scraped_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    scrape_run_id VARCHAR(100),
    match_url TEXT,
    raw_data JSONB NOT NULL,

    -- Metadata for tracking
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Understat raw shot data
CREATE TABLE IF NOT EXISTS bronze.understat_raw (
    id SERIAL PRIMARY KEY,
    match_id VARCHAR(50) NOT NULL,
    scraped_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    scrape_run_id VARCHAR(100),
    match_url TEXT,
    raw_shots JSONB NOT NULL,

    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Constraint to allow multiple scrapes but track them
    UNIQUE(match_id, scraped_at)
);

-- Scrape run metadata for tracking and debugging
CREATE TABLE IF NOT EXISTS bronze.scrape_runs (
    run_id VARCHAR(100) PRIMARY KEY,
    dag_run_id VARCHAR(100),
    match_id VARCHAR(50),
    scrape_type VARCHAR(50), -- 'fbref', 'understat', 'fixture'
    status VARCHAR(20), -- 'success', 'failed', 'partial'
    error_message TEXT,
    records_scraped INTEGER,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_fbref_raw_match_id ON bronze.fbref_raw(match_id);
CREATE INDEX IF NOT EXISTS idx_fbref_raw_scraped_at ON bronze.fbref_raw(scraped_at DESC);
CREATE INDEX IF NOT EXISTS idx_understat_raw_match_id ON bronze.understat_raw(match_id);
CREATE INDEX IF NOT EXISTS idx_understat_raw_scraped_at ON bronze.understat_raw(scraped_at DESC);
CREATE INDEX IF NOT EXISTS idx_scrape_runs_match_id ON bronze.scrape_runs(match_id);
CREATE INDEX IF NOT EXISTS idx_scrape_runs_status ON bronze.scrape_runs(status);

-- FBref lineup data with player positions
CREATE TABLE IF NOT EXISTS bronze.fbref_lineups (
    id SERIAL PRIMARY KEY,
    match_id VARCHAR(50),
    match_url TEXT NOT NULL,
    scraped_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    scrape_run_id VARCHAR(100),
    raw_lineups JSONB NOT NULL,  -- Contains home_lineup and away_lineup arrays

    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Allow multiple scrapes for tracking
    UNIQUE(match_url, scraped_at)
);

CREATE INDEX IF NOT EXISTS idx_fbref_lineups_match_id ON bronze.fbref_lineups(match_id);
CREATE INDEX IF NOT EXISTS idx_fbref_lineups_scraped_at ON bronze.fbref_lineups(scraped_at DESC);

-- Match reference table for linking Understat and FBref data
CREATE TABLE IF NOT EXISTS bronze.match_reference (
    id SERIAL PRIMARY KEY,
    match_url TEXT UNIQUE NOT NULL,
    match_date DATE NOT NULL,
    home_team VARCHAR(100) NOT NULL,
    away_team VARCHAR(100) NOT NULL,
    season VARCHAR(20) NOT NULL,
    fbref_url TEXT,  -- FBref match report URL

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_match_reference_date ON bronze.match_reference(match_date DESC);
CREATE INDEX IF NOT EXISTS idx_match_reference_season ON bronze.match_reference(season);

-- Grant permissions
GRANT ALL ON ALL TABLES IN SCHEMA bronze TO analytics_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA bronze TO analytics_user;
