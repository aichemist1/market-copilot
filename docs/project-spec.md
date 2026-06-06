# Product Specification

## 1. Purpose

This specification defines the product vision, MVP scope, delivery phases, and target architecture for Market Intelligence Copilot.

The product goal is to help users make better stock and stock options buy/sell decisions by combining signals from congressional disclosures, institutional activity, whale buying, social feeds, and other market-relevant inputs into a usable intelligence workflow.

The product will be delivered in phases. The first phase follows a backend-first approach so ingestion quality, normalization, schema design, validation, and structured querying are reliable before a broader user-facing experience is built on top. This delivery sequence is intentional, but the product scope is broader than the backend alone.

Source-specific ingestion details live in [ingestion-design-congressional.md](/Users/dev/Documents/market-copilot/docs/ingestion-design-congressional.md).

---

## 2. Product Summary

### 2.1 Working Title
Market Intelligence Copilot

### 2.2 Vision
Build a production-grade GenAI application for investment research that can:
- ingest complex input formats such as PDF, XML, text, and social feeds
- use an LLM to convert those inputs into a unified structured format
- store raw and structured data for traceability
- support modular expansion to multiple data sources over time
- expose structured data through secure backend APIs
- support user-facing research workflows and recommendation-oriented product experiences
- evolve toward multi-source market intelligence for decision support across stocks and options

### 2.3 MVP Focus
The MVP will focus on one source only:
- congressional disclosures

The MVP objective is:
- ingest `2026` and forward congressional source data daily
- normalize it into a unified schema
- validate that structured output is publishable and trustworthy
- auto-publish validated data
- support structured querying from the backend

Historical pre-2026 congressional disclosures are out of scope for the MVP because they do not support the intended current and forward-looking investment workflow.

This MVP focus is a sequencing decision, not a statement that the product is limited to congressional workflows.

---

## 3. Delivery Principles

- product vision first, backend-first delivery phase
- modular multi-service design
- simplest viable production-grade setup
- low operational overhead
- daily freshness for congressional data
- LLM used for normalization into unified format
- schema and validation quality before broad UI buildout
- expand sources only after the first source is validated and stable

---

## 4. Scope

### 4.1 In Scope
- backend APIs for auth, data access, and admin operations
- daily ingestion for congressional data
- PDF and XML ingestion support
- LLM-based normalization into unified schema
- deterministic validation rules before publication
- raw and structured data storage
- auto-publication of validated data
- invite-only registration
- profile-based access restrictions by module/domain
- deployment on EC2 with S3 storage
- product foundations that allow later UI and multi-source expansion without reworking the core data model
- a first user-facing product shell with overview, exploration, research, and signal workflows over the published dataset

### 4.2 Out of Scope for MVP
- institutional, social, and technical-data ingestion
- broad frontend feature buildout
- advanced CI/CD automation
- extensive observability stack
- field-level or column-level data restrictions

The UI is not out of product scope. Broad UI development is simply deferred until the first source pipeline and structured dataset are stable.

### 4.3 Current Product Surface
The current MVP product surface is intentionally narrow and organized around user intent rather than raw source categories.

Implemented user-facing pages:
- `Dashboard`
- `Trade Explorer`
- `Research`
- `Signals`

Planned but still gated:
- `Alerts`
- `X Feed`

Admin-only capabilities remain separate from the main user navigation and are accessed through backend/admin flows rather than being embedded into the consumer product shell.

### 4.4 First Release Matrix

User-visible in the first release candidate:
- `Dashboard`
- `Trade Explorer`
- `Research`
- `Signals`

Admin-only:
- review queue and anomaly inspection
- backend admin GraphQL queries
- ingestion and operational tooling

Implemented but not yet released to users:
- `Alerts`
- `X Feed`

---

## 5. Access Model

### 5.1 User Profiles
- `basic`
  - congressional data access
- `premium`
  - congressional data in MVP
  - later expansion to institutional and premium domains
- `admin`
  - ingestion and operational access

### 5.2 Access Rules
- no field-level or column-level restrictions
- access is enforced at screen/module/domain level
- UI will hide restricted screens
- backend will enforce matching domain restrictions in GraphQL resolvers and service logic
- authenticated session state, not caller-provided profile hints, should be the trust source for release gating and admin-only surfaces

### 5.3 Release Gating and Admin Preview
- domain access and domain release state are separate concerns
- a user profile may be eligible for a domain without that domain being generally released yet
- unreleased domains may remain visible to `admin` users for preview and validation
- non-admin users must not see unreleased domain data or screens
- release gating must be enforced in both the UI and backend authorization layer
- this model should support states such as `development`, `admin_preview`, `published`, and `disabled`

### 5.4 Registration
- invite-only registration
- user must provide a valid invite code during sign-up

---

## 6. Architecture Direction

### 6.1 Confirmed Product Technology Choices
- Frontend: `Next.js` + `React` + `TypeScript`
- Product API: `GraphQL`-first
- Backend services: `Python`
- Database: `PostgreSQL`
- Object storage: `S3`
- Compute: `EC2`
- Reverse proxy / middleware: `Nginx`
- Logging: basic structured application logs
- Scheduling: `cron`

### 6.2 Recommended Backend Implementation Stack
- API framework: `FastAPI`
- GraphQL layer: `Strawberry GraphQL`
- Data validation and contracts: `Pydantic`
- ORM and migrations: `SQLAlchemy` + `Alembic`
- PDF extraction: `pdfplumber` or `pypdf`
- OCR exception path: provider-agnostic OCR or vision extraction only if handwritten or low-quality PDFs require it

This stack keeps the codebase strongly typed, Python-native, and practical for a backend-first MVP without adding unnecessary operational weight. In this architecture, ingestion and base extraction remain deterministic, while the LLM is responsible for semantic normalization into the unified schema.

### 6.3 What We Are Intentionally Not Using in MVP
- no `Celery`
- no `Redis`
- no large observability stack
- no complex CI/CD automation

### 6.4 Why This Simpler Setup
- lower setup and maintenance overhead
- fewer moving parts to troubleshoot
- good fit for backend-first incremental delivery
- still leaves room to scale later by splitting services further

---

## 7. Deployment Model

### 7.1 MVP Deployment
Run the application on EC2 with S3 for object storage.

Recommended initial shape:
- one EC2 instance for app services
- `Nginx` as reverse proxy
- Python backend service(s)
- PostgreSQL
- `cron` for scheduled ingestion jobs
- S3 for raw files and processing artifacts

### 7.2 Simplified Release Approach
- keep deployment simple
- manual or script-based deployment is acceptable for MVP
- avoid investing in full CI/CD automation until the backend flow is stable

---

## 8. Security Requirements

### 8.1 Authentication
- email/password authentication
- passwords will be stored in the application database, not plain text
- password hashing is still required at the application layer
- for MVP, use the framework’s standard secure password hashing support
- invite code required during registration

### 8.2 Authorization
- enforce module/domain-level restrictions
- enforce resolver-level authorization for GraphQL
- keep admin operations restricted to admin users

### 8.3 Middleware
We do need middleware. For MVP:
- `Nginx` reverse proxy
- auth/session middleware
- request logging
- basic rate limiting
- GraphQL query protection such as depth or complexity limits

---

## 9. Data and Normalization Requirements

### 9.1 Input Types
The normalization layer must support inputs such as:
- PDF
- XML
- social media feed content
- plain text

### 9.2 Normalization Goal
The LLM should convert extracted source-specific content into a unified structured format. The LLM is part of the normalization layer, not the ingestion or file-fetching layer.

### 9.3 Validation and Publishability Requirements
- every normalized record must validate against the schema before publication
- required fields must be enforced where the source format supports them
- enums, dates, and amount ranges must be normalized into consistent representations
- source metadata and normalized facts must remain traceable to raw source files
- duplicate detection must prevent re-publishing the same filing or transaction unintentionally
- failed validations must be retained with error states for retry or review rather than silently dropped
- normalization versions must be tracked so output quality can be audited over time

The published dataset is the contract that later UI, recommendation logic, and downstream workflows will rely on.

### 9.4 Storage Pattern
- store raw source files and payloads in S3
- store structured normalized data in PostgreSQL
- retain provenance so every published record can be traced back to its source

### 9.5 Publication Model
- newly validated data should automatically publish
- the backend should query from the published structured dataset
- unpublished or failed records should remain available for operational inspection

Record publication status and domain release state are different controls. A record may be valid and published within an unreleased domain while remaining visible only to admins until that domain is launched for users.

---

## 10. API Direction

### 10.1 API Style
- GraphQL-first for product data access
- limited REST endpoints allowed for health checks or operational needs

GraphQL resolvers and service logic must enforce both user-profile access rules and domain release-state rules so unreleased modules remain admin-only until launch.

### 10.2 MVP Query Goal
The first backend milestone is:
- ingest data
- normalize it
- validate it deterministically
- store it in structured form
- query it reliably

Once this foundation is stable, the UI and higher-level intelligence workflows can be built on top without reworking the core pipeline.

### 10.3 Product Interaction Model
The current interaction model is:

- `Dashboard`
  - grouped overview of recent disclosures
  - overview rows may collapse multiple related line items into one cleaner signal row
- `Trade Explorer`
  - raw disclosure stream with user-facing filters
- `Research`
  - drill-in page reached from dashboard/explorer interactions
  - focal filing first, then related activity by the same filer or ticker
- `Signals`
  - deterministic ticker ranking from structured transaction data
- `Alerts`
  - reserved for future alert logic and fast-response workflows

The product should expose source-derived intelligence without forcing users to think in terms of internal ingestion domains or backend source names.

---

## 11. Source Strategy

### 11.1 MVP Source Priority
Start with:
- congressional disclosures

### 11.2 Later Sources
Later phases may add:
- institutional / SEC sources
- whale and unusual activity sources
- social feeds
- technical and fundamentals providers

Provider selection for those later sources is still open.

### 11.3 Freshness Targets
- congressional data: daily
- later sources such as social or market feeds: near real-time where needed

---

## 12. Scheduled Jobs and Skills

### 12.1 Ingestion Scheduling
Use `cron` jobs for MVP ingestion.

This is preferred because it is simpler than introducing a task queue stack too early.

### 12.2 Agent Skills
Keep agent skills for:
- deployment automation later
- additional operational workflows later

### 12.3 MVP Scheduling Model
- daily cron job for congressional ingestion
- backend service performs fetch, parse, normalize, validate, and publish

---

## 13. Logging and Operations

### 13.1 Logging
Basic logging is enough for MVP:
- ingestion run logs
- normalization errors
- API errors
- auth events

### 13.2 Operational Goal
- minimize complexity
- keep services modular
- avoid unnecessary tooling
- stay aligned with production-grade goals

---

## 14. Environments

For MVP, keep the environment model simple:
- EC2 for compute
- S3 for object storage
- PostgreSQL for structured data

Local development can still be used for engineering, but the target runtime model is EC2 + S3.

---

## 15. Repository Structure

Use a modular multi-service repository structure.

Preferred structure:
- separate backend API service
- separate ingestion/normalization service
- separate frontend application
- shared schema/contracts package if needed

This keeps the system modular without overcomplicating the first release.

---

## 16. Incremental Plan

### Phase 1: Data Foundation
- define congressional schema `v1`
- build source ingestion flow
- parse source files
- normalize with LLM
- define deterministic validation rules
- store structured output
- support structured querying

### Phase 2: Validation and Publication
- validate data quality
- auto-publish validated records
- confirm freshness and daily runs

### Phase 3: Product Experience
- add UI after backend outputs and schema are stable
- wire UI to GraphQL backend
- apply module-level access restrictions in UI
- support admin preview of unreleased domains before general release
- begin user-facing research workflows on top of the structured dataset

### Phase 4: Source Expansion
- add additional domains only after congressional flow is reliable

---

## 17. MVP Acceptance Criteria

- invite-only users can register and sign in
- passwords are stored securely using application-layer hashing
- congressional data is ingested daily
- PDF and XML inputs can be normalized into a unified schema
- deterministic validation rules block invalid records from publication
- validated data auto-publishes
- structured data can be queried reliably from the backend
- unreleased domains remain admin-only until their release state changes
- the application runs on EC2 and uses S3 for object storage
- the architecture stays modular and ready for later source expansion and product UI buildout

---

## 18. Open Decisions Resolved

- API approach: `GraphQL`-first
- frontend choice: `Next.js` + `React`
- access model: module/domain-level, not field-level
- storage: `S3`
- scheduler: `cron`
- MVP source: congressional disclosures
- registration: invite-only
- publication: automatic after validation
- development order: backend-first foundation, then UI and broader product workflows
- unreleased domains: admin preview before user launch

---

## 19. Immediate Next Steps

1. Define the first congressional schema, validation rules, and publication view.
2. Build the congressional ingestion pipeline.
3. Validate structured output quality and failure handling.
4. Add stable GraphQL queries over the structured dataset.
5. Begin the first user-facing workflows after backend data quality is confirmed.
