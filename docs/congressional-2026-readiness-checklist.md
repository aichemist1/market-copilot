# Congressional 2026 Readiness Checklist

## Purpose

This checklist defines the minimum ongoing quality and operational readiness gate for the congressional Phase 1 source.

It is intentionally narrow:

- keep the `2026+` congressional dataset trustworthy
- prepare the current source pipeline for first EC2 deployment

This is not a general project management checklist. It is a source-readiness guardrail.

## 1. Ongoing 2026 Review Checklist

Use this checklist when reviewing new benchmark samples or spot-checking newly ingested 2026 congressional PTRs.

### 1.1 Filing-Level Review

- `source_record_id` matches the House filing ID
- `reporting_person` matches the filing header
- `reporting_status` is correct
- `district_or_state` is correct
- `filing_date` is correct
- `filing_status` is correct
- `source_document_url` points to the correct PTR PDF

### 1.2 Transaction-Level Review

- transaction count matches the source document
- `issuer_name` is clean and free of extraction junk
- `ticker` is correct when present in source text
- `asset_type` is canonically correct for House codes such as `[ST]`, `[GS]`, and `[CS]`
- `transaction_type` is correct, including `S (partial)` handling
- `transaction_date` is correct
- `notification_date` is correct
- `amount_range` is correct
- `owner_type` is correct when explicitly present
- `subholding` is not overused for unrelated fields

### 1.3 Provenance and Restraint

- `raw_text_reference` exists at filing and row level where supported
- ambiguous values remain null instead of being guessed
- comments and explanatory text are retained where useful
- no source noise is being published as structured fact

### 1.4 Operational Outcome

- validation result is `passed` for expected happy paths
- known bad inputs fail safely
- no failed normalization is silently published

## 2. Benchmark Gate

Before the first EC2 deployment milestone, the active benchmark set in [congressional-normalization-eval-sample-set-v1.csv](/Users/dev/Documents/market-copilot/docs/congressional-normalization-eval-sample-set-v1.csv) should remain in this state:

- all current-year happy-path samples are `passed` or `passed_with_notes`
- failure-path samples are `failed_expected`
- no current-year sample is `failed_unexpected`

If a current-year sample becomes `failed_unexpected`, fix or explicitly defer the issue before treating the source as deployment-ready.

## 3. EC2 Readiness Gate

The congressional Phase 1 source is ready for first EC2 deployment only when all of the following are true.

### 3.1 Data Pipeline

- the `2026+` benchmark set is green
- fixture and benchmark runs are repeatable locally
- normalization output artifacts are stored consistently
- validation and publication behavior is stable

### 3.2 Runtime Configuration

- environment variables are documented and complete
- OpenAI provider configuration is externalized
- database connection settings are externalized
- artifact storage root or S3 target is configurable

### 3.3 Database and Schema

- Alembic migrations apply cleanly from an empty database
- current schema supports the active congressional source scope
- failed jobs and validation results remain inspectable

### 3.4 Operational Controls

- cron command for daily ingestion is defined
- manual rerun path exists for recovery
- failure logs are easy to inspect
- admin queries can inspect ingestion runs and validation results

### 3.5 Deployment Simplicity

- one EC2 instance is sufficient for the first release
- `Nginx`, API service, ingestion service, PostgreSQL, and cron responsibilities are understood
- no extra infrastructure is added unless the current source proves it is necessary

## 4. Near-Term Build Order

The next work after this checklist should follow this order:

1. document exact EC2 runtime/deployment shape
2. define environment variables and secret handling clearly
3. add a small operator runbook for ingestion reruns and failure inspection
4. perform a first staging-style deployment on EC2

The EC2 runtime/deployment shape is defined in [ec2-deployment-design-phase1-congressional.md](/Users/dev/Documents/market-copilot/docs/ec2-deployment-design-phase1-congressional.md).

## 5. Out of Scope

This checklist does not expand scope to:

- pre-2026 congressional data
- Senate or other sources
- recommendation logic
- full product UI
- advanced observability or CI/CD
