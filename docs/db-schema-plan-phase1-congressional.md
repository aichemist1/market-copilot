# Database Schema and Migration Plan: Phase 1 Congressional

## 1. Purpose

This document turns the Phase 1 backend design into an initial PostgreSQL schema plan and migration sequence.

It is the first technical artifact intended to drive implementation of:
- database tables
- constraints
- indexes
- migration ordering
- schema boundaries between operational data and normalized product data

This plan is based on:
- [project-spec.md](/Users/dev/Documents/market-copilot/docs/project-spec.md)
- [ingestion-design-congressional.md](/Users/dev/Documents/market-copilot/docs/ingestion-design-congressional.md)
- [backend-design-phase1-congressional.md](/Users/dev/Documents/market-copilot/docs/backend-design-phase1-congressional.md)
- [source-mapping-congressional-v1.md](/Users/dev/Documents/market-copilot/docs/source-mapping-congressional-v1.md)

---

## 2. Design Goals

The schema should:
- preserve source provenance
- separate source artifacts from normalized facts
- support deterministic validation and publication state
- support admin inspection without exposing internal states to normal users
- avoid overfitting all future sources into a single rigid table design
- remain simple enough for fast MVP implementation

---

## 3. Schema Strategy

Phase 1 should use a single PostgreSQL database with a small number of clear table groups:

- auth and access tables
- ingestion operations tables
- source artifact tables
- normalized congressional data tables
- normalization and validation tracking tables

This is a practical MVP structure that can later evolve into additional domain tables for institutional, whale, or social sources without rewriting the whole database.

---

## 4. Proposed Table Set

### 4.1 Auth and Access

- `users`
- `invite_codes`

### 4.2 Ingestion Operations

- `ingestion_runs`

### 4.3 Source Artifacts

- `source_documents`

### 4.4 Normalized Domain Data

- `congressional_filings`
- `congressional_transactions`

### 4.5 Normalization and Validation

- `normalization_jobs`
- `validation_results`

---

## 5. Table Definitions

The types below are planning-level PostgreSQL suggestions. Final SQL can be adjusted slightly during implementation.

### 5.1 `users`

Purpose:
- application users and role/profile assignment

Suggested columns:
- `id` `uuid` primary key
- `email` `text` not null unique
- `password_hash` `text` not null
- `profile` `text` not null
- `status` `text` not null default `'active'`
- `created_at` `timestamptz` not null default `now()`
- `updated_at` `timestamptz` not null default `now()`

Suggested checks:
- `profile` in `('basic', 'premium', 'admin')`
- `status` in `('active', 'disabled', 'pending_invite')`

Indexes:
- unique index on `email`

### 5.2 `invite_codes`

Purpose:
- invite-only registration support

Suggested columns:
- `id` `uuid` primary key
- `code` `text` not null unique
- `created_by_user_id` `uuid` null references `users(id)`
- `used_by_user_id` `uuid` null references `users(id)`
- `status` `text` not null default `'active'`
- `expires_at` `timestamptz` null
- `used_at` `timestamptz` null
- `created_at` `timestamptz` not null default `now()`

Suggested checks:
- `status` in `('active', 'used', 'expired', 'disabled')`

### 5.3 `ingestion_runs`

Purpose:
- one row per scheduled or manual ingestion execution

Suggested columns:
- `id` `uuid` primary key
- `source_type` `text` not null
- `run_type` `text` not null
- `status` `text` not null
- `started_at` `timestamptz` not null
- `completed_at` `timestamptz` null
- `files_discovered_count` `integer` not null default `0`
- `files_downloaded_count` `integer` not null default `0`
- `records_normalized_count` `integer` not null default `0`
- `records_published_count` `integer` not null default `0`
- `error_summary` `text` null
- `created_at` `timestamptz` not null default `now()`

Suggested checks:
- `source_type` in `('congressional_house_ptr')`
- `run_type` in `('scheduled', 'manual', 'recovery')`
- `status` in `('running', 'completed', 'completed_with_errors', 'failed')`

Indexes:
- index on `started_at desc`
- index on `(source_type, started_at desc)`

### 5.4 `source_documents`

Purpose:
- raw and derived artifacts tied to source records

Suggested columns:
- `id` `uuid` primary key
- `source_type` `text` not null
- `source_record_id` `text` null
- `document_type` `text` not null
- `source_url` `text` null
- `storage_key` `text` not null
- `checksum` `text` null
- `mime_type` `text` null
- `file_size_bytes` `bigint` null
- `extraction_status` `text` not null default `'not_started'`
- `extracted_text_storage_key` `text` null
- `ingestion_run_id` `uuid` null references `ingestion_runs(id)`
- `created_at` `timestamptz` not null default `now()`

Suggested checks:
- `source_type` in `('congressional_house_ptr')`
- `document_type` in `('house_xml', 'ptr_pdf', 'extracted_text', 'normalization_input', 'normalization_output')`
- `extraction_status` in `('not_started', 'completed', 'failed', 'skipped')`

Indexes:
- index on `(source_type, source_record_id)`
- unique index on `storage_key`
- index on `ingestion_run_id`

### 5.5 `congressional_filings`

Purpose:
- filing-level normalized congressional disclosure records

Suggested columns:
- `id` `uuid` primary key
- `source_type` `text` not null
- `source_record_id` `text` not null
- `filing_type` `text` not null
- `reporting_status` `text` null
- `filing_date` `date` null
- `disclosure_date` `date` null
- `filing_status` `text` null
- `reporting_person` `text` not null
- `office` `text` null
- `district_or_state` `text` null
- `source_document_id` `uuid` null references `source_documents(id)`
- `source_document_url` `text` not null
- `publication_status` `text` not null default `'published'`
- `domain_release_state` `text` not null default `'published'`
- `normalization_version` `text` not null
- `model_name` `text` not null
- `published_at` `timestamptz` null
- `created_at` `timestamptz` not null default `now()`
- `updated_at` `timestamptz` not null default `now()`

Suggested checks:
- `source_type` in `('congressional_house_ptr')`
- `publication_status` in `('draft', 'published', 'failed_validation', 'archived')`
- `domain_release_state` in `('development', 'admin_preview', 'published', 'disabled')`

Indexes:
- unique index on `(source_type, source_record_id)`
- index on `reporting_person`
- index on `filing_date desc`
- index on `publication_status`
- index on `domain_release_state`

### 5.6 `congressional_transactions`

Purpose:
- normalized transaction rows under a filing

Suggested columns:
- `id` `uuid` primary key
- `filing_id` `uuid` not null references `congressional_filings(id)` on delete cascade
- `transaction_index` `integer` not null
- `issuer_name` `text` not null
- `ticker` `text` null
- `asset_type` `text` null
- `transaction_type` `text` not null
- `transaction_date` `date` null
- `notification_date` `date` null
- `amount_range` `text` null
- `amount_range_min` `numeric(18,2)` null
- `amount_range_max` `numeric(18,2)` null
- `owner_type` `text` null
- `subholding` `text` null
- `capital_gains_over_200` `boolean` null
- `commentary` `text` null
- `raw_text_reference` `text` null
- `publication_status` `text` not null default `'published'`
- `created_at` `timestamptz` not null default `now()`
- `updated_at` `timestamptz` not null default `now()`

Suggested checks:
- `transaction_index >= 0`
- `publication_status` in `('draft', 'published', 'failed_validation', 'archived')`

Indexes:
- unique index on `(filing_id, transaction_index)`
- index on `ticker`
- index on `issuer_name`
- index on `transaction_date desc`
- index on `transaction_type`

### 5.7 `normalization_jobs`

Purpose:
- one row per LLM normalization execution

Suggested columns:
- `id` `uuid` primary key
- `source_document_id` `uuid` not null references `source_documents(id)`
- `source_type` `text` not null
- `normalization_version` `text` not null
- `model_name` `text` not null
- `prompt_version` `text` not null
- `status` `text` not null
- `input_reference` `text` null
- `output_reference` `text` null
- `error_message` `text` null
- `started_at` `timestamptz` not null
- `completed_at` `timestamptz` null
- `created_at` `timestamptz` not null default `now()`

Suggested checks:
- `source_type` in `('congressional_house_ptr')`
- `status` in `('queued', 'running', 'completed', 'failed')`

Indexes:
- index on `source_document_id`
- index on `(status, started_at desc)`

### 5.8 `validation_results`

Purpose:
- structured validation outcomes for filings or transaction batches

Suggested columns:
- `id` `uuid` primary key
- `source_type` `text` not null
- `source_record_id` `text` not null
- `entity_type` `text` not null
- `entity_id` `uuid` null
- `validation_version` `text` not null
- `status` `text` not null
- `errors_json` `jsonb` not null default `'[]'::jsonb`
- `warnings_json` `jsonb` not null default `'[]'::jsonb`
- `validated_at` `timestamptz` not null

Suggested checks:
- `source_type` in `('congressional_house_ptr')`
- `entity_type` in `('filing', 'transaction_batch')`
- `status` in `('passed', 'failed', 'passed_with_warnings')`

Indexes:
- index on `(source_record_id, validated_at desc)`
- index on `status`

---

## 6. Relationship Model

The intended relationship flow is:

- one `ingestion_run` may create many `source_documents`
- one source filing may have one or more `source_documents`
- one PTR filing maps to one `congressional_filings` row
- one filing maps to many `congressional_transactions`
- one source document may have one or more `normalization_jobs`
- one filing or batch may have one or more `validation_results`

This keeps the system auditable without over-normalizing everything too early.

---

## 7. Enum Strategy

For MVP, use PostgreSQL `text` columns with check constraints rather than database enum types.

Why:
- easier migration changes early in the project
- less friction while source semantics are still settling
- simpler for schema iteration during Phase 1

Once values are stable, enum-like behavior can continue via:
- application constants
- validation rules
- database check constraints

This is the right tradeoff for a backend-first MVP.

---

## 8. Migration Sequence

The migration plan should be incremental and safe for iteration.

### Migration 001: Base Auth Tables

Create:
- `users`
- `invite_codes`

### Migration 002: Ingestion Operations

Create:
- `ingestion_runs`

### Migration 003: Source Artifact Storage

Create:
- `source_documents`

### Migration 004: Filing-Level Congressional Data

Create:
- `congressional_filings`

### Migration 005: Transaction-Level Congressional Data

Create:
- `congressional_transactions`

### Migration 006: Normalization Tracking

Create:
- `normalization_jobs`

### Migration 007: Validation Tracking

Create:
- `validation_results`

### Migration 008: Performance and Query Indexes

Add:
- secondary indexes after query patterns are confirmed in early development

---

## 9. Constraints and Implementation Notes

### 9.1 Uniqueness

The most important uniqueness rules at this stage are:
- `users.email`
- `invite_codes.code`
- `source_documents.storage_key`
- `congressional_filings (source_type, source_record_id)`
- `congressional_transactions (filing_id, transaction_index)`

### 9.2 Cascade Behavior

Recommended:
- deleting a filing should cascade to transactions
- source documents should generally not cascade-delete filings automatically
- ingestion runs should remain as historical audit rows

### 9.3 JSON Usage

Use `jsonb` only where structure is naturally variable:
- validation errors
- validation warnings

Avoid overusing `jsonb` for core product facts that need stable querying.

---

## 10. What Is Still Intentionally Deferred

This schema plan intentionally does not finalize:
- exact XML element-to-column parser mapping
- ticker enrichment rules
- cross-source shared entity tables
- recommendation, scoring, or alerting tables
- audit history tables beyond basic operational tracking

Those can be layered in later without weakening the Phase 1 foundation.

---

## 11. Recommended Implementation Follow-Up

After approving this schema plan, the next work items should be:

1. create repo scaffolding for backend services
2. choose the Python ORM/migration implementation path
3. implement the first migration set
4. define application-level schema constants and validation enums
5. wire the ingestion pipeline to these tables

---

## 12. Recommendation

This schema plan is production-appropriate for the MVP because it:
- preserves provenance
- supports staged rollout and admin preview
- keeps operational and product data separated
- avoids premature abstraction across all future sources
- leaves room for source expansion without rewriting Phase 1 foundations

It is also intentionally simple enough to implement quickly.
