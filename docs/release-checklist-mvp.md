# Release Checklist: MVP Soft Launch

## Purpose

This checklist defines the minimum release gate for the first invited-user launch of Market Intelligence Copilot.

It assumes:

- the `2026+` congressional pipeline is running
- the first user-visible product surface is limited to:
  - `Dashboard`
  - `Trade Explorer`
  - `Research`
  - `Signals`
- admin-only review remains available through `/admin/review`

This is a release checklist, not a deployment checklist and not a backlog document.

## 1. Release Surface

### 1.1 User-Visible

- `Dashboard`
- `Trade Explorer`
- `Research`
- `Signals`

### 1.2 Admin-Only

- `Review Queue`
- admin anomaly inspection
- admin validation inspection
- ingestion and operational workflows

### 1.3 Not Yet Released

- `Alerts`
- `X Feed`

## 2. Basic User Checklist

Run this checklist with a real `basic` user account.

### 2.1 Sign-In

- user can sign in successfully
- user lands in the authenticated product shell
- sign-out works cleanly
- unauthenticated access to product pages redirects to `/login`

### 2.2 Dashboard

- dashboard loads without GraphQL errors
- summary counts render
- recent disclosures render
- grouped rows look intentional, not duplicated by accident
- `View full disclosure stream` opens `Trade Explorer`
- filer/ticker links open `Research`

### 2.3 Trade Explorer

- trade explorer loads without GraphQL errors
- filters work:
  - ticker
  - member name
  - action
  - asset type
  - date range
- empty-state messaging is clear when no trades match
- filer/ticker links open `Research`

### 2.4 Research

- research opens from dashboard and trade explorer
- focal filing section renders
- related activity sections render when applicable
- `Back to Trade Explorer` returns the user to filtered context when entered from explorer
- ticker/member explorer links feel continuous, not dead-end

### 2.5 Signals

- signals page loads without GraphQL errors
- stock and ETF views work
- date windows work
- `Research` and `Explore` actions navigate correctly

### 2.6 Access Restrictions

- basic user does not see `Review Queue` in the UI
- basic user cannot access `/admin/review` directly
- basic user does not see `Alerts` in the main nav

## 3. Admin User Checklist

Run this checklist with a real `admin` user account.

### 3.1 Sign-In

- admin can sign in successfully
- admin sees the same released product shell as basic users

### 3.2 Admin Entry Point

- admin sees `Review Queue` in the header
- `Review Queue` opens `/admin/review`

### 3.3 Review Queue

- transaction anomalies render
- failed validation results render
- source filing links open correctly
- the review surface is not mixed into the normal user nav

### 3.4 Product Pages

- dashboard, trade explorer, research, and signals still work for admin
- admin access does not change normal product behavior unexpectedly

## 4. Data Trust Checklist

Before invited-user release:

- no known future-dated trade rows are visible in user-facing pages
- anomaly queue is receiving suspicious rows for admin review
- recent dashboard and signals data looks directionally sane on spot check
- research page reflects focal filing context accurately for spot-checked examples

## 5. Operational Checklist

- backend service is healthy
- GraphQL responds successfully
- scheduled ingestion is running
- recent ingestion runs complete without unexplained failures
- recent validation failures are inspectable
- admin review route is reachable for admins

See also:

- [congressional-2026-readiness-checklist.md](/Users/dev/Documents/market-copilot/docs/congressional-2026-readiness-checklist.md)
- [operator-runbook-phase1-congressional.md](/Users/dev/Documents/market-copilot/docs/operator-runbook-phase1-congressional.md)

## 6. Soft Launch Recommendation

Recommended first release model:

1. create a very small admin set
2. create a very small invited `basic` user cohort
3. keep release surface limited to:
   - `Dashboard`
   - `Trade Explorer`
   - `Research`
   - `Signals`
4. keep `Alerts` and `X Feed` hidden
5. monitor anomalies and failed validations during early usage

## 7. Release Decision

The MVP is ready for invited-user soft launch only when:

- basic user checklist passes
- admin user checklist passes
- data trust checklist passes
- operational checklist passes

If any of those fail, hold the release and fix the failing area before expanding user access.
