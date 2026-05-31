# Source Mapping: Congressional `v1`

## 1. Purpose

This document grounds the proposed congressional schema against real House disclosure source structure.

It is intentionally limited in scope:
- validate the high-level filing and transaction shape against real source evidence
- identify fields that are clearly source-backed today
- identify fields that remain provisional until live XML samples are inspected during implementation

This is a bridge artifact between:
- [ingestion-design-congressional.md](/Users/dev/Documents/market-copilot/docs/ingestion-design-congressional.md)
- [backend-design-phase1-congressional.md](/Users/dev/Documents/market-copilot/docs/backend-design-phase1-congressional.md)

---

## 2. Evidence Base

This mapping is grounded in a small, bounded sample of official House Clerk public disclosure materials:

- the official House Clerk financial disclosure download/search page
- real PTR PDF examples exposed from the official House Clerk disclosure site

This is enough to validate the basic filing and transaction model.

This is not yet enough to lock:
- exact annual download package structure
- exact XML element names
- exact XML metadata coverage for every filing year

Those details should be confirmed when we implement the XML fetch/parser layer.

---

## 3. What Is Confirmed by Real PTR Samples

Based on official PTR examples, the Phase 1 source clearly has:

### 3.1 Filing-Level Information

- filing identifier
- filer name
- filer status
- state/district
- filing status
- certification/signature section
- IPO yes/no question

### 3.2 Transaction-Level Information

Each PTR may contain one or more transaction rows with fields such as:
- owner
- asset
- transaction type
- date
- notification date
- amount
- capital gains indicator

### 3.3 Optional or Sometimes-Present Detail

Some PTRs also include:
- subholding / investment vehicle detail
- description
- comments
- partial sale notation
- asset-type or ticker-like hints embedded in asset text

This confirms that the Phase 1 normalized model should be:
- filing-centric
- transaction-row based
- tolerant of optional and inconsistent row-level details

---

## 4. Source-to-Normalized Mapping

### 4.1 Filing-Level Mapping

| Source evidence | Proposed normalized field | Confidence | Notes |
| --- | --- | --- | --- |
| Filing ID | `source_record_id` | High | Direct source identifier from PTR documents |
| Report type "Periodic Transaction Report" | `filing_type` | High | Stable for Phase 1 PTR workflow |
| Filer name | `reporting_person` | High | Directly present on PTR |
| Status | `reporting_status` | High | Example values include Member |
| State/District | `district_or_state` | High | Source combines these in one visible field in many PTRs |
| Filing status | `filing_status` | High | Example includes `New`; may later include amended flows |
| Source PDF URL | `source_document_url` | High | Deterministic from official file location |
| Certification date / digital signature date | `filing_date` | Medium | Source may contain a signature date, but exact filing-date semantics should be confirmed against XML metadata |
| Document year from path | `filing_year` | Medium | Useful operational metadata, but not necessarily the transaction reporting date |

### 4.2 Transaction-Level Mapping

| Source evidence | Proposed normalized field | Confidence | Notes |
| --- | --- | --- | --- |
| Owner | `owner_type` | High | Direct row field in PTR |
| Asset | `issuer_name` | Medium | Good primary normalized target, but asset text often includes multiple concepts |
| Asset text with ticker in parentheses | `ticker` | Medium | Often derivable, but not always present or clean |
| Asset type abbreviation such as `[ST]` or `[GS]` | `asset_type` | Medium | Directly source-backed, but exact enum mapping should be standardized separately |
| Transaction Type | `transaction_type` | High | Direct row field, often values such as `P` and `S` |
| Date | `transaction_date` | High | Direct row field |
| Notification Date | `notification_date` | High | Direct row field and worth preserving |
| Amount | `amount_range` | High | Direct row field; canonical ranges appear in PTR output |
| Cap. Gains > $200? | `capital_gains_over_200` | Medium | Present in PTR examples; useful but not mandatory for first MVP query set |
| Description | `commentary` or `description` | Medium | Optional text; preserve if present |
| Comments | `commentary` | Medium | Optional text; preserve raw wording when present |
| Subholding Of | `subholding` | Medium | Optional contextual field; should likely remain nullable |

---

## 5. Implications for Schema Design

### 5.1 What the Evidence Supports

The current backend design is directionally correct in these areas:

- separate filing and transaction tables
- one filing may have many transactions
- nullable transaction attributes are required
- provenance to source document must be preserved
- `transaction_type`, `amount_range`, and date normalization should be deterministic

### 5.2 What Should Be Adjusted or Clarified

The real PTR layout suggests a few additions or clarifications:

- `notification_date` should be included in the normalized transaction model
- `reporting_status` is source-backed and should be stored at filing level
- `filing_status` from the PTR should be preserved separately from internal `publication_status`
- `state` and `district` may later deserve separate parsed fields even if Phase 1 stores a combined `district_or_state`
- `subholding` and `capital_gains_over_200` are real source fields and should remain available even if not central to MVP queries

---

## 6. What Is Still Provisional

The following areas are still provisional until implementation inspects the annual House download package directly:

### 6.1 XML Discovery Structure

Still to confirm:
- exact XML root and element names
- exact metadata fields available in XML
- whether XML exposes filing date, amendment status, and direct PDF references in a consistent structure
- whether XML records are strictly one-per-filing

### 6.2 Source-Derived Metadata Priority

Still to confirm:
- whether `filing_date` should come from XML metadata, PDF metadata, signature date, or a separate ingest timestamp
- whether `disclosure_date` should be modeled distinctly for PTRs in Phase 1

### 6.3 Asset and Ticker Normalization

Still to confirm:
- how often ticker is directly present versus inferred
- whether ticker extraction should be part of MVP normalization or a later enrichment pass

---

## 7. Recommended Updates to the Phase 1 Design

Before finalizing the database schema, the Phase 1 backend design should treat the following as source-backed:

- filing-level:
  - `source_record_id`
  - `filing_type`
  - `reporting_person`
  - `reporting_status`
  - `district_or_state`
  - `filing_status`
  - `source_document_url`

- transaction-level:
  - `owner_type`
  - `issuer_name`
  - `transaction_type`
  - `transaction_date`
  - `notification_date`
  - `amount_range`
  - `asset_type`
  - `subholding`
  - `capital_gains_over_200`
  - optional `commentary`

The design should continue to treat the following as normalized or derived:

- `ticker`
- canonical enum values
- parsed amount min/max values
- internal publication and release-state fields

---

## 8. Recommendation

The schema is ready to move to the next step with one healthy constraint:

- proceed to the initial database schema and migration plan
- keep XML field names and a few metadata semantics marked as provisional until parser implementation validates them

This avoids over-delaying the build while still keeping the source-truth boundary honest.
