# Congressional Normalization Evaluation v1

## Purpose

This document defines the first compact evaluation harness for congressional PTR normalization.

The goal is to measure data quality systematically without overfitting the pipeline to one PDF or building a heavyweight evaluation platform too early.

This evaluation set is the quality gate for the Phase 1 congressional source before broader source expansion or EC2 deployment hardening.

For MVP, this evaluation scope is limited to `2026` and forward congressional PTR data only. Historical pre-2026 disclosures are explicitly out of scope and must not drive ingestion or normalization work.

## Scope

This evaluation focuses on the Phase 1 normalization path:

- fetch or seed a known PTR source document
- extract text deterministically
- normalize via the LLM-backed adapter
- canonicalize source-specific values
- validate the normalized payload
- persist publishable structured records

This is not a model-benchmark exercise. It is a product data quality exercise.

## Initial Benchmark Set

The benchmark sample manifest lives in [congressional-normalization-eval-sample-set-v1.csv](/Users/dev/Documents/market-copilot/docs/congressional-normalization-eval-sample-set-v1.csv).

`v1` intentionally starts small:

- two current-year happy-path samples
- one additional current-year happy-path sample
- one current-year known failure-path sample

Before the first EC2 deployment milestone, expand this set to `5-10` real samples covering more row shapes and ownership/asset edge cases.

## Review Criteria

Review each sample against the source document using the same criteria every time.

### Filing-Level Accuracy

- `reporting_person`
- `reporting_status`
- `district_or_state`
- `filing_date`
- `filing_status`
- `source_document_url`

### Transaction-Level Accuracy

- transaction count matches the source
- `transaction_type` is correct
- `asset_type` is canonically correct for House codes
- `owner_type` is correct and not over-inferred
- `transaction_date` and `notification_date` are correct
- `amount_range` is correct
- `issuer_name` is clean and not polluted by extraction noise

### Provenance and Restraint

- `raw_text_reference` exists at filing and row level when possible
- ambiguous source text is not converted into false precision
- missing values remain null rather than being guessed

### System Outcome

- validation result is `passed` for publishable samples
- failure samples fail cleanly with a meaningful error
- no bad sample is silently published

## Evaluation Workflow

1. Queue one benchmark sample or sample set.
2. Run the normalization cycle until no queued jobs remain.
3. Inspect the stored normalization output artifact.
4. Compare the artifact against the source PDF text or source PDF.
5. Record the result in the sample manifest.
6. Only change the normalization layer when the issue repeats across samples or clearly reflects a stable source convention.

Do not add historical pre-2026 samples to this benchmark set.

## Decision Rule

Refine the normalization system only when at least one of these is true:

- the same issue appears in multiple samples
- the issue reflects a documented House convention such as asset or owner codes
- the issue causes false publication, bad validation, or misleading structured data

Do not refine the system just because one noisy PDF looks odd.

## Result Labels

Use these statuses in the sample manifest:

- `pending`
- `passed`
- `passed_with_notes`
- `failed_expected`
- `failed_unexpected`

## Exit Criteria For v1

The congressional normalization path is ready for the next maturity stage when:

- benchmark samples consistently produce publishable structured data for happy paths
- failure paths fail safely and transparently
- repeated issues have documented fixes or explicit deferrals
- quality is stable enough that additional effort is better spent on broader sample coverage than on single-sample tuning
