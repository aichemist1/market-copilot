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
