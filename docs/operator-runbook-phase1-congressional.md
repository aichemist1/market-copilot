# Operator Runbook: Phase 1 Congressional Source

## Purpose

This runbook defines the minimum manual operations path for the `2026+` congressional backend.

Use it for:

- health checks
- manual ingestion reruns
- normalization recovery
- failure inspection

This runbook assumes the first EC2 deployment shape described in [ec2-deployment-design-phase1-congressional.md](/Users/dev/Documents/market-copilot/docs/ec2-deployment-design-phase1-congressional.md).

## 1. Health Checks

### 1.1 API Health

Check the health endpoint:

```bash
curl -fsS http://127.0.0.1:8000/health
```

Expected result:

```json
{"status":"ok"}
```

### 1.2 API Service Status

```bash
sudo systemctl status market-copilot-api
```

### 1.3 Recent API Logs

```bash
sudo journalctl -u market-copilot-api -n 100 --no-pager
```

## 2. Manual Ingestion Rerun

Run one full scheduled-style ingestion flow manually:

```bash
cd /srv/market-copilot/backend
.venv/bin/python -m market_copilot.ingestion.main
```

Use this when:

- the cron run failed
- configuration changed
- you want a post-deployment smoke test

## 3. Manual Normalization Recovery

If ingestion already queued work and you want to drain normalization jobs manually:

```bash
cd /srv/market-copilot/backend
.venv/bin/python -m market_copilot.scripts.run_normalization_cycle
```

Run repeatedly until the result becomes:

```python
{'status': 'no_queued_jobs'}
```

## 4. Database Inspection

### 4.1 Most Recent Ingestion Runs

```bash
psql "$MARKET_COPILOT_DATABASE_URL" -c "select id, status, files_discovered_count, records_normalized_count, records_published_count, completed_at from ingestion_runs order by started_at desc limit 10;"
```

### 4.2 Most Recent Normalization Jobs

```bash
psql "$MARKET_COPILOT_DATABASE_URL" -c "select id, status, source_type, normalization_version, model_name, output_reference, error_message, created_at from normalization_jobs order by created_at desc limit 20;"
```

### 4.3 Most Recent Validation Results

```bash
psql "$MARKET_COPILOT_DATABASE_URL" -c "select source_record_id, status, validation_version, validated_at from validation_results order by validated_at desc limit 20;"
```

## 5. Failure Inspection Flow

If a scheduled run behaves unexpectedly, use this sequence:

1. inspect API service status
2. inspect recent API logs
3. inspect recent ingestion runs
4. inspect recent normalization jobs
5. inspect recent validation results
6. rerun ingestion manually only after the failure mode is understood

## 6. Artifact Inspection

If artifact storage mode is `local`, inspect artifacts under:

```bash
$MARKET_COPILOT_LOCAL_ARTIFACT_ROOT
```

If artifact storage mode is `s3`, inspect the configured bucket/prefix for:

- raw XML
- raw PTR PDFs
- extracted text
- normalization outputs

## 7. Post-Deployment Smoke Test

After a deployment:

1. confirm migrations ran successfully
2. confirm API health endpoint responds
3. run one manual scheduled-style ingestion flow
4. inspect the resulting ingestion run and normalization jobs
5. verify that no unexpected validation failures were introduced

## 8. Scope Guardrail

Do not use this runbook to backfill or investigate pre-2026 congressional data for MVP.

The active operational source scope is `2026+` only.
