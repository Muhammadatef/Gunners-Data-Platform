-- Create databases and users for Arsenal FC Analytics Platform

-- Create Airflow database
CREATE DATABASE airflow;

-- Create analytics database
CREATE DATABASE arsenalfc_analytics;

-- Create analytics user
CREATE USER analytics_user WITH PASSWORD 'analytics_pass';

-- Create Airflow user
CREATE USER airflow WITH PASSWORD 'airflow';

-- Grant privileges on airflow database
GRANT ALL PRIVILEGES ON DATABASE airflow TO airflow;

-- Grant privileges on analytics database
GRANT ALL PRIVILEGES ON DATABASE arsenalfc_analytics TO analytics_user;

-- Connect to airflow database to grant schema privileges
\c airflow

-- Grant all privileges on public schema to airflow user
GRANT ALL ON SCHEMA public TO airflow;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO airflow;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO airflow;

-- Make airflow owner of public schema
ALTER SCHEMA public OWNER TO airflow;

-- Connect to analytics database to set up schemas
\c arsenalfc_analytics

-- Create schemas
CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;
CREATE SCHEMA IF NOT EXISTS metrics;

-- Grant schema privileges
GRANT ALL ON SCHEMA bronze TO analytics_user;
GRANT ALL ON SCHEMA silver TO analytics_user;
GRANT ALL ON SCHEMA gold TO analytics_user;
GRANT ALL ON SCHEMA metrics TO analytics_user;

-- Grant future table privileges
ALTER DEFAULT PRIVILEGES IN SCHEMA bronze GRANT ALL ON TABLES TO analytics_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA silver GRANT ALL ON TABLES TO analytics_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA gold GRANT ALL ON TABLES TO analytics_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA metrics GRANT ALL ON TABLES TO analytics_user;
