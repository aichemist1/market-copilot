# Ingestion and Normalization Design

## 1. Purpose

This document defines the MVP ingestion and normalization design for congressional disclosures.

The immediate goal is to build a reliable backend pipeline that ingests congressional disclosures, extracts usable content from source files, uses an LLM to convert the input into a unified structured format, validates the result, and publishes it for backend querying.

---

## 2. MVP Source Strategy

### 2.1 First Source
Target the House first.

Primary source approach:
- use the House Clerk daily bulk XML files
- detect new Periodic Transaction Reports (PTRs)
- download target PDFs referenced by those records

### 2.2 Why Start Here
- clear public source
- daily cadence fits MVP freshness goal
- good foundation for schema design and publication flow
- lets us validate the end-to-end normalization approach before adding more sources

---

## 3. Input Types

The normalization pipeline must be able to handle:
- XML
- PDF
- extracted text
- later, social and other text-based inputs

The unified-format goal is the same across all input types:
- LLM converts source-specific input into a consistent structured schema

---

## 4. MVP Processing Flow

1. Fetch House Clerk daily bulk XML.
2. Detect new or updated PTR records.
3. Download associated PDFs.
4. Store raw XML and PDFs in S3.
5. Extract text from PDFs.
6. Normalize extracted content into structured schema using an LLM.
7. Validate normalized output.
8. Auto-publish validated records.
9. Expose published records through backend queries.

---

## 5. Extraction Strategy

### 5.1 XML Processing
- parse House bulk XML directly with Python
- extract report metadata and PDF references deterministically
- use XML as a trusted source for discovery and metadata capture

### 5.2 PDF Processing
- implement a Python-based parser
- preferred first tools: `pdfplumber` or `pypdf`
- focus first on typed digital forms

### 5.3 Edge Cases
Some House PDFs may be handwritten or poorly formatted.

Edge-case handling rule:
- route handwritten or low-quality PDFs to an OCR path
- OCR options may include `AWS Textract` or a lightweight open-source vision model
- normalize OCR output into the same structured schema

This OCR path should be exception-based, not the default flow.

---

## 6. Scheduling

### 6.1 MVP Scheduler
Use `cron` for daily ingestion.

Daily cron job responsibilities:
- fetch latest XML
- detect new PTRs
- download PDFs
- run extraction and normalization
- validate and auto-publish results

### 6.2 Why Cron
- simplest operational model
- low maintenance
- enough for daily congressional ingestion

---

## 7. Storage Design

### 7.1 S3
Use S3 for:
- raw XML files
- raw PDFs
- OCR artifacts if needed
- extracted text artifacts if retained

### 7.2 PostgreSQL
Use PostgreSQL for:
- normalized structured records
- publication state
- source metadata
- ingestion run tracking
- user/auth data

---

## 8. Unified Schema Direction

The first schema should be based on congressional trading data.

Suggested initial fields:
- `source_type`
- `source_record_id`
- `filing_type`
- `filing_date`
- `disclosure_date`
- `reporting_person`
- `office`
- `district_or_state`
- `issuer_name`
- `ticker`
- `asset_type`
- `transaction_type`
- `transaction_date`
- `amount_range`
- `source_document_url`
- `raw_text_reference`
- `normalization_version`
- `model_name`
- `publication_status`

Schema design rules:
- keep it simple for the first source
- preserve provenance
- allow nullable fields where PDFs are inconsistent
- store source metadata separately from normalized facts when useful

---

## 9. LLM Normalization

### 9.1 Goal
The LLM converts source input into the unified schema.

### 9.2 Input Options
Depending on the stage, the model may receive:
- extracted PDF text
- XML-derived metadata
- OCR output
- later, social/text inputs from other sources

### 9.3 Controls
- require structured output
- validate against schema before publish
- keep prompt and normalization version metadata
- use the cheapest acceptable model for MVP

---

## 10. Publication Model

- validated records auto-publish
- published records become queryable immediately
- no manual review gate in MVP unless a failure condition requires intervention

---

## 11. Service Shape

Preferred modular services:
- API service
- ingestion/normalization service
- frontend later

This keeps the repo modular while avoiding too many moving parts in the MVP runtime.

---

## 12. Logging

Basic logging is enough:
- cron run start/end
- fetched file counts
- extraction failures
- normalization failures
- publish results

---

## 13. Later Expansion

After congressional ingestion is stable:
- add Senate or other congressional sources if needed
- add SEC / institutional sources
- add social feeds
- add technical/fundamental sources

Do not expand until:
- schema is validated
- extraction is reliable
- published backend data looks correct

---

## 14. Recommended Build Order

1. Define congressional schema `v1`.
2. Build House Clerk XML fetch and PTR detection.
3. Download referenced PDFs and store them in S3.
4. Build typed-PDF extraction with `pdfplumber` or `pypdf`.
5. Add LLM normalization into unified schema.
6. Add validation and auto-publication.
7. Expose queryable backend data.
8. Add OCR exception path for handwritten forms.
