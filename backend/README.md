# Backend

This directory contains the Phase 1 backend foundation for Market Intelligence Copilot.

Scope note:
- congressional PTR ingestion and evaluation are limited to `2026` and forward data for MVP
- pre-2026 congressional disclosures are intentionally out of scope

Initial scope:
- API service skeleton
- ingestion service skeleton
- SQLAlchemy models
- Alembic migrations

Current implemented backend surface:
- congressional ingestion over `2026+` House PTR data
- published product-facing GraphQL queries
- admin-only operational GraphQL queries
- deterministic ticker signal aggregation
- anomaly review queue for future-dated transaction records
- password-based sign-in endpoint for application sessions

Planned runtime split:
- API service
- ingestion/normalization service

Both services currently share a single Python project to keep the MVP simple while preserving a clean service boundary in code.

## Local Setup

1. Copy `.env.example` to `.env`.
2. Keep `MARKET_COPILOT_NORMALIZATION_PROVIDER=stub` for local-safe development.
3. To use the live OpenAI-backed normalization adapter, set:

```bash
MARKET_COPILOT_NORMALIZATION_PROVIDER=openai
MARKET_COPILOT_OPENAI_API_KEY=your_key_here
MARKET_COPILOT_OPENAI_MODEL=gpt-4.1-mini
```

4. Artifact storage is configuration-driven:

```bash
MARKET_COPILOT_ARTIFACT_STORAGE_MODE=local
MARKET_COPILOT_LOCAL_ARTIFACT_ROOT=/Users/dev/Documents/market-copilot/.artifacts
```

For EC2/S3 deployment, switch to:

```bash
MARKET_COPILOT_ARTIFACT_STORAGE_MODE=s3
MARKET_COPILOT_S3_BUCKET=your_bucket_name
MARKET_COPILOT_S3_REGION=your_aws_region
```

5. Scheduled XML ingestion source is also configuration-driven:

```bash
MARKET_COPILOT_HOUSE_XML_SOURCE_URL=https://disclosures-clerk.house.gov/public_disc/financial-pdfs/2026FD.xml
```

## Local Commands

Run the fixture XML ingestion flow:

```bash
.venv/bin/python -m market_copilot.scripts.ingest_fixture_xml
```

The default fixture set contains only `2026` PTR samples.

Run the failure-path fixture flow:

```bash
.venv/bin/python -m market_copilot.scripts.ingest_failure_fixture_xml
```

Run one normalization cycle for the next queued job:

```bash
.venv/bin/python -m market_copilot.scripts.run_normalization_cycle
```

Run one scheduled-style ingestion flow and drain queued normalization jobs:

```bash
.venv/bin/python -m market_copilot.ingestion.main
```

For benchmark evaluation, run the normalization cycle repeatedly until it returns:

```bash
{'status': 'no_queued_jobs'}
```

Evaluation artifacts:

- benchmark rules: [`docs/congressional-normalization-eval-v1.md`](/Users/dev/Documents/market-copilot/docs/congressional-normalization-eval-v1.md)
- benchmark sample set: [`docs/congressional-normalization-eval-sample-set-v1.csv`](/Users/dev/Documents/market-copilot/docs/congressional-normalization-eval-sample-set-v1.csv)
- source readiness checklist: [`docs/congressional-2026-readiness-checklist.md`](/Users/dev/Documents/market-copilot/docs/congressional-2026-readiness-checklist.md)

Run the API locally:

```bash
.venv/bin/uvicorn market_copilot.api.app:app --reload
```

Run the lightweight backend acceptance tests:

```bash
python3 -m unittest discover -s tests
```

Create an initial application user:

```bash
.venv/bin/python -m market_copilot.scripts.create_user you@example.com your_password --profile admin
```

Current auth runtime behavior:

- backend login endpoint: `POST /auth/login`
- GraphQL profile authorization is intended to be driven by a trusted app session, not a caller-supplied profile header
- admin GraphQL queries must only be reachable through an authenticated admin session

## Current GraphQL Surface

Product-facing GraphQL queries:

- `congressionalFilings`
- `congressionalFiling`
- `congressionalTransactions`
- `tickerSignals`

Admin-only GraphQL queries:

- `adminIngestionRuns`
- `adminValidationResults`
- `adminTransactionAnomalies`

Current product query behavior:

- product-facing congressional queries are scoped to in-scope `2026+` trade activity
- future-dated transaction anomalies are excluded from user-facing query results
- those anomalies remain available through `adminTransactionAnomalies` for investigation instead of being silently discarded

Current signal behavior:

- `tickerSignals` is built from deterministic aggregation over structured transaction data
- it is intended for “popular buy ticker” ranking rather than narrative generation
