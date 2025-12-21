# Tokenmetrics
Python-based ingestion pipeline that periodically fetches funding rates from Hyperliquid, models them as hourly snapshots, and pushes them to PostgreSQL.

# Funding Rate Ingestion Pipeline

This project implements a small yet complete data ingestion pipeline that fetches funding rate data from the Hyperliquid API and stores it in PostgreSQL.  

## What this pipeline does

The pipeline fetches funding rates for all available symbols from the Hyperliquid API.  
Each run captures a point in time snapshot of funding rates and writes them into a Postgres table.

The ingestion is idempotent. Running the job multiple times for the same timestamp will not create duplicate rows.

Scheduling is handled using cron inside a Docker container and the database is provisioned using Docker Compose.

## High level design

There are two Docker containers running together.

1. A PostgreSQL container that stores the data and persists it using a Docker volume  
2. A Python ingestion container that fetches data and writes it to the database

The ingestion container connects to Postgres using Docker service discovery and environment variables.  
Cron runs inside the ingestion container and triggers the job every hour.

## Database schema

The table used for storage is called funding_rates.

Columns are

timestamp stored as TIMESTAMPTZ  
symbol stored as text  
rate stored as numeric  

A unique constraint on timestamp and symbol ensures idempotency at the database level.

## How idempotency works

Each ingestion run computes a snapshot timestamp rounded to the hour in UTC.

The database enforces uniqueness on the combination of timestamp and symbol.  
If the same snapshot is ingested again, the insert is ignored using ON CONFLICT DO NOTHING.

This makes retries and restarts safe.

## Scheduling behavior

The ingestion container runs as a long lived service.  
Cron is started when the container starts and handles scheduling internally.

The job is executed every hour while the container is running.  
If the container is stopped, scheduled runs during that downtime are skipped.  
When the container restarts, ingestion resumes from the current hour.

This pipeline is snapshot based and does not attempt to backfill missed hours.

## Error handling and logging

The ingestion logic is capable of handling common failure scenarios such as

API timeouts  
Malformed or partial responses  
Database write failures  

Errors are logged to a file inside the ingestion container.  
Database transactions are rolled back on failure to avoid partial writes.

## How to run the project

Make sure Docker is running locally.

Build and start the services using Docker Compose.

docker compose up --build

This starts both the Postgres container and the ingestion container.

To manually trigger an ingestion run for testing, execute the following.

docker exec -it funding_ingester python /app/api-fetch.py

You can inspect logs inside the ingestion container and query the database using psql inside the Postgres container.

## Notes on production considerations
Please note that in real production systems, scheduling would typically be handled by an external orchestrator such as Airflow or Kubernetes CronJobs we won't be having a cronfile inside a container.  

Cron inside the container was used here to keep the setup minimal while still demonstrating scheduling logic.

Backfilling missed time windows could also be added if required, but was intentionally left out to keep the pipeline focused.

## Monitoring and alerting

Alerting is not implemented in this project.  
In a production setting, alerts would be configured externally based on logs and metrics.

Examples include
- repeated ingestion failures across multiple runs
- no new data ingested within an expected time window
- database connectivity failures
- elevated API error rates


##AI Usage
I used AI as a review and refinement tool, not as a replacement for design or implementation decisions.
To be precise, AI helped with:

1) Validating edge cases around network failures, HTTP errors, and incorrect API responses

2) Sanity-checking PostgreSQL behaviors.

3) Refining error-handling structure

4) Improving clarity of logging and understanding good practices while implementing logging.

5) Reviewing code structure to keep the solution simple and readable.
