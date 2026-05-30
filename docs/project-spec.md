# Product Specification

## 1. Purpose

This specification defines the MVP and target architecture for an investment intelligence application that ingests source data, uses an LLM to convert it into a unified format, stores the structured output, and exposes it through queryable backend APIs.

This project will follow a backend-first approach. The initial focus is accurate ingestion, normalization, schema design, and structured querying. The UI will follow after the backend data model and output quality are validated.

Source-specific ingestion details live in [ingestion-design.md](/Users/dev/Documents/ToBeNamed/docs/ingestion-design.md).

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
- later power a user-facing UI for research workflows

### 2.3 MVP Focus
The MVP will focus on one source only:
- congressional disclosures

The MVP objective is:
- ingest congressional source data daily
- normalize it into a unified schema
- auto-publish validated data
- support structured querying from the backend

---

## 3. Delivery Principles

- backend first
- modular multi-service design
- simplest viable production-grade setup
- low operational overhead
- daily freshness for congressional data
- LLM used for normalization into unified format
- expand sources only after the first source is validated and stable

---

## 4. Scope

### 4.1 In Scope
- backend APIs for auth, data access, and admin operations
- daily ingestion for congressional data
- PDF and XML ingestion support
- LLM-based normalization into unified schema
- raw and structured data storage
- auto-publication of validated data
- invite-only registration
- profile-based access restrictions by module/domain
- deployment on EC2 with S3 storage

### 4.2 Out of Scope for MVP
- institutional, social, and technical-data ingestion
- broad frontend feature buildout
- advanced CI/CD automation
- extensive observability stack
- field-level or column-level data restrictions

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

### 5.3 Registration
- invite-only registration
- user must provide a valid invite code during sign-up

---

## 6. Architecture Direction

### 6.1 Confirmed Technology Choices
- Frontend: `Next.js` + `React` + `TypeScript`
- Product API: `GraphQL`-first
- Backend services: `Python`
- Database: `PostgreSQL`
- Object storage: `S3`
- Compute: `EC2`
- Reverse proxy / middleware: `Nginx`
- Logging: basic structured application logs
- Scheduling: `cron`

### 6.2 What We Are Intentionally Not Using in MVP
- no `Celery`
- no `Redis`
- no large observability stack
- no complex CI/CD automation

### 6.3 Why This Simpler Setup
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
The LLM should convert source-specific input into a unified structured format.

### 9.3 Storage Pattern
- store raw source files and payloads in S3
- store structured normalized data in PostgreSQL
- retain provenance so every published record can be traced back to its source

### 9.4 Publication Model
- newly validated data should automatically publish
- the backend should query from the published structured dataset

---

## 10. API Direction

### 10.1 API Style
- GraphQL-first for product data access
- limited REST endpoints allowed for health checks or operational needs

### 10.2 MVP Query Goal
The first backend milestone is:
- ingest data
- normalize it
- store it in structured form
- query it reliably

Once this is stable, the UI can be added on top.

---

## 11. Source Strategy

### 11.1 MVP Source Priority
Start with:
- congressional disclosures

### 11.2 Later Sources
Later phases may add:
- institutional / SEC sources
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
- separate frontend later
- shared schema/contracts package if needed

This keeps the system modular without overcomplicating the first release.

---

## 16. Incremental Plan

### Phase 1: Backend Foundation
- define congressional schema `v1`
- build source ingestion flow
- parse source files
- normalize with LLM
- store structured output
- support structured querying

### Phase 2: Validation and Publication
- validate data quality
- auto-publish validated records
- confirm freshness and daily runs

### Phase 3: Frontend
- add UI after backend outputs and schema are stable
- wire UI to GraphQL backend
- apply module-level access restrictions in UI

### Phase 4: Source Expansion
- add additional domains only after congressional flow is reliable

---

## 17. MVP Acceptance Criteria

- invite-only users can register and sign in
- passwords are stored securely using application-layer hashing
- congressional data is ingested daily
- PDF and XML inputs can be normalized into a unified schema
- validated data auto-publishes
- structured data can be queried reliably from the backend
- the application runs on EC2 and uses S3 for object storage
- the architecture stays modular and ready for later source expansion

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
- development order: backend first, UI second

---

## 19. Immediate Next Steps

1. Define the first congressional schema and publication view.
2. Build the congressional ingestion pipeline.
3. Validate structured output quality.
4. Add stable GraphQL queries over the structured dataset.
5. Add the UI only after backend data quality is confirmed.
