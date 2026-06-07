# Frontend Product Surface MVP

## Purpose

This document captures the current user-facing MVP surface for Market Intelligence Copilot.

It focuses only on product behavior and UI features that are intentionally part of the current build.
It does not document troubleshooting history, deployment issues, or unfinished ideas.

## 1. Navigation

Current first-release top-level product navigation:

- `Dashboard`
- `Trade Explorer`
- `Research`
- `Signals`

Reserved for later gated release:

- `Alerts`
- `X Feed`

Admin-only and intentionally out of the main user nav:

- `Invite Codes` at `/admin/invites`
- `Review Queue` at `/admin/review`

These tabs are product concepts, not source-system names. The UI should stay organized around user intent rather than exposing internal ingestion categories such as congressional, institutional, whale, or other source labels as primary navigation.

## 2. Dashboard

Purpose:

- provide a concise overview of recent reportable activity
- surface current disclosures as a cleaner signal list rather than a raw filing reader
- act as the first entry point into deeper research

Current behavior:

- dashboard rows are grouped signal rows rather than a full raw transaction table
- grouping collapses repeated same-member, same-ticker, same-action, same-day activity into one cleaner row
- grouped rows emphasize:
  - filer
  - ticker
  - action
  - amount summary
  - trade date
- grouped rows link into `Research`

Important note:

- the dashboard is intentionally not a full dataset view
- it is a curated overview slice over the latest in-scope published data

## 3. Trade Explorer

Purpose:

- provide the raw, filterable disclosure stream
- let users explore activity directly without losing product clarity

Current filters:

- ticker
- member name
- action
- asset type
- date range
- date presets such as:
  - today
  - 1 week
  - 1 month
  - 3 months
  - all

Current row emphasis:

- member
- ticker
- company
- action
- amount range
- trade date

Trade Explorer shows line-item disclosure data rather than grouped dashboard summaries.

## 4. Research

Purpose:

- provide the investigation path that the dashboard and trade explorer resolve into
- help a user understand the focal disclosure in context

Current behavior:

- dashboard row clicks open `Research`
- research is anchored around the focal filing
- the page then shows:
  - the focal filing trades
  - other recent trades by the same filer
  - other recent activity in the same ticker by that filer when applicable

This page exists to answer questions such as:

- what else did this filer trade?
- what was disclosed in the filing that generated the dashboard signal?
- is this ticker part of a broader pattern from the same filer?

## 5. Signals

Purpose:

- provide a deterministic recommendation-oriented ranking layer
- surface popular buy tickers from official disclosure activity

Current behavior:

- shows ranked ticker rows built from structured transaction data
- intended to highlight:
  - buy record count
  - sell record count
  - distinct filer count
  - latest filing date

Signals are built from deterministic aggregation rather than another LLM pass.

## 6. Alerts

Purpose:

- reserve the future fast-response layer of the product
- eventually surface unusual clusters, repeated buys, repeated sells, and other actionable alert conditions

Current state:

- alerts remain intentionally restrained until the signal logic is strong enough to trust
- the page exists in the codebase, but it is not part of the first user-visible navigation set

## 7. Product Scope Rules Reflected in the UI

The current UI is designed around these product boundaries:

- only `2026+` trade activity belongs in the user-facing MVP dataset
- user-facing pages should show trustworthy structured data, not raw filing prose by default
- source PDFs and deeper source context are secondary, not primary UI actions
- grouped overview pages and raw exploration pages should stay distinct:
  - dashboard = grouped overview
  - trade explorer = raw filtered stream
  - research = contextual drill-in

## 8. Interaction Principles

The current frontend follows these interaction principles:

- show the signal first
- keep legal/source detail secondary
- make traversal obvious
- reduce repeated visual noise
- preserve room for future source expansion without changing the top-level product concepts

## 9. Admin Review Workflow

The current admin review workflow is intentionally narrow and operational:

- future-dated or otherwise suspicious transaction anomalies remain out of user-facing product views
- those rows remain visible to admins through the `Review Queue`
- failed validation outputs remain inspectable in the same admin review surface
- invited-user onboarding is managed through the admin `Invite Codes` page rather than CLI-only operations

Current admin review route:

- `/admin/invites`
- `/admin/review`

## 10. First Release Matrix

User-visible in the first release candidate:

- `Dashboard`
- `Trade Explorer`
- `Research`
- `Signals`

Admin-only:

- `Invite Codes`
- `Review Queue`
- backend admin anomaly and validation queries
- ingestion and operational tooling

Implemented but not released to users yet:

- `Alerts`
- `X Feed`

## 11. Access and Session Model

Current first-release access behavior:

- the visible product surface requires sign-in
- `Dashboard`, `Trade Explorer`, `Research`, and `Signals` are authenticated user pages
- `Invite Codes` and `Review Queue` remain admin-only operational surfaces
- `Review Queue` remains admin-only and must not be reachable by basic users through direct URL entry
- `Alerts` remains implemented but gated out of the first user release

The intended trust boundary is:

- frontend session cookie establishes user identity and profile
- frontend GraphQL proxy derives profile from that trusted session
- backend admin queries authorize from the trusted session-derived profile rather than a user-supplied UI toggle or caller-controlled profile hint

## 12. Release Readiness

The operational release gate for this product surface lives in:

- [release-checklist-mvp.md](/Users/dev/Documents/market-copilot/docs/release-checklist-mvp.md)
