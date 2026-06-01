# EC2 Deployment Design: Phase 1 Congressional Source

## 1. Purpose

This document defines the first deployment shape for the `2026+` congressional Phase 1 backend on AWS EC2.

The goal is to deploy the current validated backend in the simplest production-shaped form that supports:

- GraphQL API access
- daily congressional ingestion
- local-to-cloud parity for normalization and validation behavior
- operational recovery without unnecessary infrastructure

This is a deployment blueprint for the current source phase, not the final multi-source platform design.

## 2. Scope

### 2.1 In Scope

- one EC2-based runtime for the congressional Phase 1 backend
- FastAPI + Strawberry GraphQL API process
- cron-triggered ingestion jobs
- PostgreSQL-backed structured storage
- S3-backed raw and derived artifact storage
- `2026+` congressional PTR data only
- environment-driven configuration and secrets
- simple operator runbook and recovery path

### 2.2 Out of Scope

- Kubernetes
- autoscaling groups
- load-balanced multi-instance API
- Redis, Celery, or queue infrastructure
- advanced CI/CD
- pre-2026 congressional ingestion
- other data domains

## 3. Deployment Principles

- keep the first deployment operationally simple
- prefer one-instance clarity over premature distribution
- preserve the same normalization and validation contract used locally
- keep ingestion and API roles separate in code, even if they share one host
- treat this as a staging-shaped production foundation, not a throwaway setup

## 4. Recommended MVP Topology

### 4.1 Single-Instance Shape

Run the Phase 1 backend on one EC2 instance with:

- `Nginx`
- one `uvicorn` API process
- one cron schedule for ingestion jobs
- one PostgreSQL instance
- S3 for artifact storage

### 4.2 Why This Shape

- matches the current backend architecture
- keeps debugging and recovery simple
- minimizes infrastructure overhead while the product is still proving source quality
- still supports a later split into separate API and ingestion hosts if needed

## 5. Runtime Components

### 5.1 API Process

Run:

- `uvicorn market_copilot.api.app:app`

Responsibilities:

- GraphQL product queries
- admin queries
- health endpoint
- auth/profile access checks

Recommended process model:

- one systemd service for the API
- bind to localhost behind `Nginx`

### 5.2 Ingestion Execution

Run ingestion via cron-triggered Python commands rather than a long-running worker service.

Responsibilities:

- fetch House XML
- discover new PTR source documents
- download PDFs
- extract text
- normalize and validate
- publish valid records

Recommended process model:

- one cron entry for scheduled ingestion
- manual rerun commands available for operator use

### 5.3 PostgreSQL

Use PostgreSQL for:

- structured filings and transactions
- ingestion runs
- source document metadata
- normalization jobs
- validation results
- user/auth data

For the first EC2 deployment, PostgreSQL may run:

- on the same EC2 host for simplicity, or
- on a managed database later if operational needs justify it

For Phase 1, same-host PostgreSQL is acceptable if backup and access controls are handled properly.

### 5.4 S3 Artifact Storage

Use S3 for:

- raw House XML
- raw PTR PDFs
- extracted text artifacts
- normalization output artifacts

The application should treat artifact location as configuration, not a hardcoded local path.

## 6. Network and Access Shape

### 6.1 Public Entry

Expose only:

- `443` for HTTPS
- optionally `80` for HTTP-to-HTTPS redirect

Do not expose:

- PostgreSQL to the public internet
- the application process directly

### 6.2 Internal Binding

- `uvicorn` binds to `127.0.0.1:8000`
- `Nginx` proxies public requests to the API

### 6.3 Admin Access

- SSH access restricted to known operators
- admin GraphQL access remains application-controlled

## 7. Configuration Model

Use environment variables only. Do not rely on development defaults in EC2.

### 7.1 Required Environment Variables

- `MARKET_COPILOT_ENVIRONMENT=production`
- `MARKET_COPILOT_DATABASE_URL`
- `MARKET_COPILOT_API_HOST=127.0.0.1`
- `MARKET_COPILOT_API_PORT=8000`
- `MARKET_COPILOT_NORMALIZATION_PROVIDER=openai`
- `MARKET_COPILOT_OPENAI_API_KEY`
- `MARKET_COPILOT_OPENAI_MODEL`

### 7.2 Recommended Additional Variables

The current settings module should be extended before EC2 deployment to include:

- `MARKET_COPILOT_ARTIFACT_STORAGE_MODE`
- `MARKET_COPILOT_LOCAL_ARTIFACT_ROOT`
- `MARKET_COPILOT_S3_BUCKET`
- `MARKET_COPILOT_S3_REGION`
- `MARKET_COPILOT_HOUSE_XML_SOURCE_URL`
- `MARKET_COPILOT_LOG_LEVEL`

These should be added before deployment rather than improvised on-host.

## 8. Service Management

### 8.1 API Service

Recommended systemd unit:

- `market-copilot-api.service`

Responsibilities:

- load environment file
- run the API process
- restart on failure

### 8.2 Cron Jobs

Recommended cron responsibilities:

- daily House XML ingestion
- optional retry job for failed normalization cases if later needed

Do not add background daemons for ingestion until the current source proves cron is insufficient.

## 9. Deployment Workflow

### 9.1 First Deployment Order

1. provision EC2 host
2. install Python runtime and PostgreSQL
3. create application user and directories
4. configure environment file
5. install backend package and dependencies
6. run Alembic migrations
7. configure S3 access
8. configure systemd API service
9. configure `Nginx`
10. configure cron ingestion command
11. run health check and a manual ingestion smoke test

### 9.2 Update Workflow

For Phase 1, a simple update flow is acceptable:

1. pull or copy the new backend code
2. refresh the Python environment if dependencies changed
3. run Alembic migrations
4. restart the API service
5. run a manual ingestion smoke test when deployment affects ingestion logic

## 10. Operator Commands

The first EC2 deployment should support these operator actions clearly.

### 10.1 Health Check

- check API health endpoint
- inspect API systemd status

### 10.2 Manual Ingestion Rerun

- run a manual congressional ingestion command
- run one or more normalization cycles manually if needed

### 10.3 Failure Inspection

- inspect cron logs
- inspect API logs
- inspect `ingestion_runs`
- inspect `normalization_jobs`
- inspect `validation_results`

## 11. Data Safety

### 11.1 Database

- back up PostgreSQL regularly
- restrict local DB access to the application user and operators
- run migrations before enabling new code paths

### 11.2 Artifacts

- keep raw and derived artifacts in S3
- do not rely on ephemeral local disk as the system of record

## 12. Pre-Deployment Gaps To Close

Before first EC2 deployment, the current backend should close these gaps:

1. replace local artifact-root assumptions with configurable storage settings
2. implement S3-backed artifact read/write support
3. replace placeholder ingestion entrypoint with a real scheduled ingestion command
4. document exact cron commands
5. document exact environment file contents

These are not architecture pivots. They are the minimum deployment hardening tasks for the current source.

## 13. Recommended Next Build Order

The next steps after this design should be:

1. extend settings for artifact storage and source URL configuration
2. add S3 storage support
3. implement a real scheduled ingestion CLI entrypoint
4. create a short operator runbook
5. prepare the first EC2 setup checklist and command set

Supporting execution docs:

- [operator-runbook-phase1-congressional.md](/Users/dev/Documents/market-copilot/docs/operator-runbook-phase1-congressional.md)
- [ec2-setup-checklist-phase1-congressional.md](/Users/dev/Documents/market-copilot/docs/ec2-setup-checklist-phase1-congressional.md)
