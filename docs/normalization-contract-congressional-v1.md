# Normalization Contract: Congressional `v1`

## 1. Purpose

This document defines the expected structured output from the LLM normalization step for Phase 1 congressional PTR processing.

It sits between:
- extracted source content
- deterministic validation rules
- database persistence

The LLM's role is:
- understand extracted congressional disclosure content
- convert it into a structured congressional representation

The LLM's role is not:
- fetch source files
- decide publication status
- bypass validation
- invent missing facts

---

## 2. Contract Shape

The normalized output should contain:
- one filing object
- one or more transaction objects
- normalization metadata

Suggested top-level shape:

```json
{
  "filing": {
    "source_type": "congressional_house_ptr",
    "source_record_id": "20033330",
    "filing_type": "Periodic Transaction Report",
    "reporting_status": "Member",
    "filing_date": "2025-06-13",
    "disclosure_date": null,
    "filing_status": "New",
    "reporting_person": "Example Person",
    "office": null,
    "district_or_state": "CA45",
    "source_document_url": "https://...",
    "raw_text_reference": "s3://..."
  },
  "transactions": [
    {
      "transaction_index": 0,
      "issuer_name": "Apple Inc.",
      "ticker": "AAPL",
      "asset_type": "stock",
      "transaction_type": "purchase",
      "transaction_date": "2025-05-14",
      "notification_date": "2025-05-16",
      "amount_range": "$1,001-$15,000",
      "owner_type": "self",
      "subholding": null,
      "capital_gains_over_200": null,
      "commentary": null,
      "raw_text_reference": "row-1"
    }
  ],
  "normalization_metadata": {
    "normalization_version": "congressional_v1",
    "model_name": "TBD",
    "warnings": []
  }
}
```

---

## 3. Filing Object

### 3.1 Required Fields

- `source_type`
- `source_record_id`
- `filing_type`
- `reporting_person`
- `source_document_url`

### 3.2 Optional but Expected When Available

- `reporting_status`
- `filing_date`
- `disclosure_date`
- `filing_status`
- `office`
- `district_or_state`
- `raw_text_reference`

### 3.3 Rules

- do not fabricate fields missing from source content
- keep dates in ISO `YYYY-MM-DD` when parseable
- preserve the source-specific filing type wording when useful
- `source_type` should be the canonical internal value `congressional_house_ptr`

---

## 4. Transaction Objects

Each transaction object represents one source row from the PTR transaction table.

### 4.1 Required Fields

- `transaction_index`
- `issuer_name`
- `transaction_type`

### 4.2 Optional but Expected When Available

- `ticker`
- `asset_type`
- `transaction_date`
- `notification_date`
- `amount_range`
- `owner_type`
- `subholding`
- `capital_gains_over_200`
- `commentary`
- `raw_text_reference`

### 4.3 Rules

- preserve one normalized object per visible source row
- do not merge rows
- do not infer ticker unless source wording supports it
- normalize dates only when the extracted text is sufficiently clear
- preserve optional comments instead of dropping them

---

## 5. Canonical Value Expectations

These values are application-level normalization targets. Validation will enforce them.

### 5.1 `source_type`

Allowed Phase 1 value:
- `congressional_house_ptr`

### 5.2 `transaction_type`

Recommended canonical values:
- `purchase`
- `sale`
- `exchange`
- `other`
- `unknown`

Source values such as `P` and `S` should map into these canonical values.

### 5.3 `asset_type`

Recommended early canonical values:
- `stock`
- `government_security`
- `mutual_fund`
- `etf`
- `bond`
- `option`
- `other`
- `unknown`

This list can expand later without changing the contract shape.

### 5.4 `owner_type`

Recommended early canonical values:
- `self`
- `spouse`
- `dependent_child`
- `joint`
- `other`
- `unknown`

---

## 6. Nullability Rules

The LLM should return `null` when:
- a field is absent
- a field is unreadable
- a field is too ambiguous to normalize safely

The LLM should not:
- emit empty strings instead of `null`
- invent placeholder values
- guess a ticker or asset type from weak evidence

---

## 7. Raw Reference Rules

To preserve provenance, normalized objects should carry references back to extracted content where practical.

Recommended use:
- filing-level `raw_text_reference`
- transaction-level `raw_text_reference`

These references may be:
- extracted row IDs
- page/row hints
- offsets or structured extraction anchors

They do not need to be user-facing. Their purpose is auditability and debugging.

---

## 8. Validation Hand-Off

After normalization, deterministic validation should check:
- required fields
- allowed enums
- date formats
- amount-range formatting
- duplicate transaction indexing

The normalization contract should stay stable even if validation rules become stricter over time.

---

## 9. Intentional Non-Goals

This contract does not yet define:
- full enrichment logic for missing tickers
- recommendation features
- cross-source unified response formats
- final GraphQL response objects

It is strictly the LLM-to-backend handoff contract for Phase 1 congressional normalization.

---

## 10. Recommendation

This contract should be treated as the canonical Phase 1 normalization boundary.

The next implementation step should use it to define:
- application schemas
- validation models
- database persistence mappings
- prompt/output tests
