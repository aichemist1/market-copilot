# Phase 1 Backend Design: Congressional Source

## 1. Purpose

This document translates the approved product and ingestion specs into a concrete backend design for Phase 1.

Phase 1 is focused on one source only:
- congressional disclosures

The goal of this phase is to build a reliable backend foundation that can:
- fetch congressional source data
- extract usable source content
- use an LLM to normalize that content into a structured congressional schema
- validate publishability
- store raw and structured records with provenance
- expose queryable structured data for internal product use

This document is implementation-oriented. It does not replace the broader product direction in [project-spec.md](/Users/dev/Documents/market-copilot/docs/project-spec.md) or the source-level ingestion requirements in [ingestion-design-congressional.md](/Users/dev/Documents/market-copilot/docs/ingestion-design-congressional.md).

---

## 2. Phase 1 Scope

### 2.1 In Scope
- House Clerk bulk XML ingestion
- PTR discovery and PDF download
- raw file storage
- typed PDF text extraction
- LLM-based normalization into congressional schema `v1`
- deterministic validation before publish
- structured storage in PostgreSQL
- admin inspection of failed or unpublished records
- GraphQL queries over published congressional data

### 2.2 Out of Scope
- Senate ingestion
- institutional, whale, or social sources
- recommendation logic
- scoring and ranking models
- broad end-user UI buildout
- near-real-time ingestion

---

## 3. Service Boundaries

Phase 1 should use two backend services plus shared infrastructure.

### 3.1 Ingestion Service

Responsibilities:
- fetch House Clerk XML
- detect new or updated PTR records
- download referenced PDFs
- store raw artifacts
- extract text from PDFs
- call the LLM normalization flow
- validate normalized results
- publish valid records
- track ingestion run status and errors

### 3.2 API Service

Responsibilities:
- authentication and authorization
- GraphQL product queries
- admin inspection queries
- profile-based domain access enforcement
- release-state enforcement

### 3.3 Shared Infrastructure

- PostgreSQL for structured data and operational metadata
- S3 for raw files and retained extraction artifacts
- `cron` for scheduled ingestion

---

## 4. Domain Model

Phase 1 should not force all future sources into one identical schema. Instead, it should establish:

- a shared operational model
- a congressional structured schema
- reusable patterns for future sources

### 4.1 Shared Concepts

These concepts should remain consistent across current and future domains where possible:
- `source_type`
- `source_record_id`
- `source_document_url`
- `publication_status`
- `normalization_version`
- `model_name`
- provenance references
- created/updated timestamps

### 4.2 Congressional Structured Concepts

Congressional schema `v1` should model the first source naturally rather than forcing it into a generic trading schema too early.

Key concepts:
- filing
- reporting person
- office metadata
- transaction rows
- source artifact references
- normalization result metadata

---

## 5. PostgreSQL Design

The database should separate operational tracking, source metadata, and published structured facts.

### 5.1 Core Tables

Recommended initial tables:
- `ingestion_runs`
- `source_documents`
- `congressional_filings`
- `congressional_transactions`
- `normalization_jobs`
- `validation_results`
- `users`
- `invite_codes`

### 5.2 `ingestion_runs`

Purpose:
- track each scheduled or manual ingestion execution

Suggested fields:
- `id`
- `source_type`
- `run_type`
- `status`
- `started_at`
- `completed_at`
- `files_discovered_count`
- `files_downloaded_count`
- `records_normalized_count`
- `records_published_count`
- `error_summary`
- `created_at`

### 5.3 `source_documents`

Purpose:
- store one row per raw source artifact or retained derivative

Suggested fields:
- `id`
- `source_type`
- `source_record_id`
- `document_type`
- `source_url`
- `storage_key`
- `checksum`
- `mime_type`
- `file_size_bytes`
- `extraction_status`
- `extracted_text_storage_key`
- `ingestion_run_id`
- `created_at`

Typical `document_type` values:
- `house_xml`
- `ptr_pdf`
- `extracted_text`

### 5.4 `congressional_filings`

Purpose:
- represent filing-level metadata for each congressional disclosure

Suggested fields:
- `id`
- `source_type`
- `source_record_id`
- `filing_type`
- `reporting_status`
- `filing_date`
- `disclosure_date`
- `filing_status`
- `reporting_person`
- `office`
- `district_or_state`
- `source_document_id`
- `source_document_url`
- `publication_status`
- `domain_release_state`
- `normalization_version`
- `model_name`
- `published_at`
- `created_at`
- `updated_at`

Notes:
- `source_record_id` should be unique within `source_type`
- `domain_release_state` supports admin preview before broader release

### 5.5 `congressional_transactions`

Purpose:
- store transaction-level normalized rows associated with a filing

Suggested fields:
- `id`
- `filing_id`
- `transaction_index`
- `issuer_name`
- `ticker`
- `asset_type`
- `transaction_type`
- `transaction_date`
- `notification_date`
- `amount_range`
- `amount_range_min`
- `amount_range_max`
- `owner_type`
- `subholding`
- `capital_gains_over_200`
- `commentary`
- `raw_text_reference`
- `publication_status`
- `created_at`
- `updated_at`

Notes:
- one filing may contain multiple transactions
- `transaction_index` preserves row order from the normalized source

### 5.6 `normalization_jobs`

Purpose:
- retain LLM normalization inputs, outputs, and run metadata

Suggested fields:
- `id`
- `source_document_id`
- `source_type`
- `normalization_version`
- `model_name`
- `prompt_version`
- `status`
- `input_reference`
- `output_reference`
- `error_message`
- `started_at`
- `completed_at`
- `created_at`

### 5.7 `validation_results`

Purpose:
- record deterministic validation outcomes per filing or transaction batch

Suggested fields:
- `id`
- `source_type`
- `source_record_id`
- `entity_type`
- `entity_id`
- `validation_version`
- `status`
- `errors_json`
- `warnings_json`
- `validated_at`

---

## 6. Congressional Schema `v1`

The first normalized source schema should include a filing-level object plus transaction rows.

### 6.1 Filing-Level Fields

- `source_type`
- `source_record_id`
- `filing_type`
- `reporting_status`
- `filing_date`
- `disclosure_date`
- `filing_status`
- `reporting_person`
- `office`
- `district_or_state`
- `source_document_url`
- `normalization_version`
- `model_name`
- `publication_status`

### 6.2 Transaction-Level Fields

- `issuer_name`
- `ticker`
- `asset_type`
- `transaction_type`
- `transaction_date`
- `notification_date`
- `amount_range`
- `owner_type`
- `subholding`
- `capital_gains_over_200`
- `commentary`
- `raw_text_reference`

### 6.3 Schema Design Rules

- keep the first version close to the congressional source
- allow nullable values where source PDFs are inconsistent
- do not fabricate missing values
- preserve raw wording where useful for auditability
- support later enrichment without rewriting the original normalized output

---

## 7. Validation and Publishability Rules

Validation must be deterministic and must run after LLM normalization but before publication.

### 7.1 Required Filing-Level Checks

- `source_type` must be present
- `source_record_id` must be present
- `filing_type` must be present
- at least one date field must be present if available from source metadata
- `reporting_person` must be present if present in source
- `source_document_url` must be traceable to the raw artifact

### 7.2 Required Transaction-Level Checks

- every transaction row must include an `issuer_name` unless the source row is unusable
- `transaction_type` must map to an allowed enum
- `transaction_date` must be normalized when parseable
- `notification_date` must be normalized when parseable
- `amount_range` must map to an accepted canonical format when present

### 7.3 Enum and Format Rules

Normalize to controlled values where possible:
- `transaction_type`
- `asset_type`
- `owner_type`
- date formats
- amount range formats

### 7.4 Duplicate Rules

- do not re-create the same filing when `source_type` + `source_record_id` already exists
- do not duplicate transaction rows within a filing on reruns unless the source actually changed

### 7.5 Failure Handling

- invalid normalized results must not publish
- failed records must remain queryable to admins for inspection
- failures should capture structured validation errors, not only free-text logs
- reruns should be possible without manual cleanup of core data tables

### 7.6 Publication Rules

A filing can publish only when:
- source artifact exists
- normalization completed successfully
- validation passed
- at least one valid normalized transaction exists when the filing implies transaction content

---

## 8. Ingestion Workflow

### 8.1 Scheduled Flow

1. `cron` starts an ingestion run.
2. Fetch the latest House Clerk XML source.
3. Parse XML and identify new or updated PTR entries.
4. Create or update source-document rows for discovered artifacts.
5. Download referenced PDFs.
6. Extract usable text from PDFs.
7. Create normalization jobs for extracted content.
8. Call the LLM to convert extracted content into congressional schema `v1`.
9. Run deterministic validation.
10. Upsert filing and transaction records.
11. Mark valid records as published.
12. Retain failures for admin review.
13. Finalize the ingestion run with counts and status.

### 8.2 Manual/Admin Flow

Admins should be able to:
- rerun a failed normalization
- inspect unpublished records
- inspect validation errors
- inspect raw artifact references

---

## 9. Storage Layout

### 9.1 S3 Layout

Suggested storage layout:
- `raw/congressional/house/xml/YYYY/MM/DD/...`
- `raw/congressional/house/pdfs/YYYY/MM/DD/...`
- `derived/congressional/extracted-text/YYYY/MM/DD/...`
- `derived/congressional/normalization-inputs/YYYY/MM/DD/...`
- `derived/congressional/normalization-outputs/YYYY/MM/DD/...`

### 9.2 Storage Principles

- raw source files should be immutable
- derived artifacts should be versionable
- database rows should reference storage keys, not embed large raw payloads

---

## 10. API and Query Model

Phase 1 does not need the full product API. It needs stable queries that prove the dataset is useful and governable.

### 10.1 Product Queries

Recommended initial GraphQL query areas:
- list congressional filings
- list congressional transactions
- filter by ticker
- filter by reporting person
- filter by filing date or transaction date
- filter by publication status for admin use

### 10.2 Admin Queries

Admins should be able to query:
- unpublished filings
- failed validations
- recent ingestion runs
- source document references
- normalization job status

### 10.3 Access and Release Enforcement

API behavior must enforce:
- user profile access rules
- domain release state rules
- publication status rules

For Phase 1:
- congressional domain may be `published`
- future domains may remain `admin_preview`

---

## 11. Release and Visibility Model

Phase 1 should implement the same release model described in the product spec.

### 11.1 Domain-Level States

Recommended states:
- `development`
- `admin_preview`
- `published`
- `disabled`

### 11.2 How It Applies in Phase 1

- congressional data can be fully published for allowed users
- future domains can be stored and previewed without being user-visible
- admin users may inspect unreleased domain data through protected API and UI paths

---

## 12. Operational Model

### 12.1 Scheduling

- daily `cron` job for production ingestion
- manual trigger path for local testing and admin recovery

### 12.2 Logging

Log at minimum:
- ingestion run start/end
- discovered source counts
- download failures
- extraction failures
- normalization failures
- validation failures
- publication counts

### 12.3 Recovery

The system should support:
- rerunning a single ingestion date
- rerunning normalization for one filing
- rerunning validation without re-downloading all artifacts when unnecessary

---

## 13. Open Decisions

These items should be resolved during implementation:

- exact GraphQL framework choice if `Strawberry` is not finalized
- final enum sets for `transaction_type`, `asset_type`, and `owner_type`
- how much normalized input/output to retain in S3 versus PostgreSQL
- exact admin inspection queries for the first API milestone
- whether extracted text should always be retained or only for failures and audits

---

## 14. Recommended Build Order

1. Finalize congressional schema `v1` and enum values.
2. Design PostgreSQL tables and create initial migrations.
3. Scaffold ingestion and API services.
4. Implement House Clerk XML fetch and PTR detection.
5. Implement PDF download and raw storage.
6. Implement typed PDF text extraction.
7. Implement LLM normalization contracts and job tracking.
8. Implement deterministic validation and publication rules.
9. Add initial GraphQL queries for published and admin-only views.
10. Run end-to-end testing on a small House data sample.

---

## 15. Immediate Next Artifact

After this document, the next concrete artifact should be:
- initial database schema and migration plan

That step will turn this design into executable backend work.
