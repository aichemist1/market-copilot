# Invited User Rollout Plan: MVP

## Purpose

This document defines the first invited-user rollout plan for Market Intelligence Copilot.

It assumes:

- the MVP release checklist passed
- the first release surface is limited to:
  - `Dashboard`
  - `Trade Explorer`
  - `Research`
  - `Signals`
- `Review Queue` remains admin-only
- `Alerts` and `X Feed` remain hidden

This is an operating plan for rollout, not a product roadmap.

## 1. Rollout Goal

The first rollout goal is not broad adoption.

It is to:

- validate that invited users can navigate the current product slice confidently
- confirm that live data remains trustworthy during normal usage
- keep anomaly review and operational monitoring tight while the first cohort uses the product

## 2. Cohort Shape

### 2.1 Admin Cohort

Recommended size:

- `1-2` admin users

Purpose:

- monitor anomalies
- inspect failed validations
- confirm daily ingestion health
- support invited users during the soft launch

### 2.2 Invited Basic Cohort

Recommended size:

- `3-5` invited `basic` users for the first wave

Purpose:

- validate the first user journey
- gather product feedback on:
  - dashboard usefulness
  - trade explorer clarity
  - research value
  - signals quality

Do not expand the cohort until the first wave is stable.

## 3. Invitation Model

The intended onboarding model is:

1. admin creates invite code
2. invite code is shared with the user
3. user registers through the UI with:
   - email
   - password
   - invite code
4. user lands in the authenticated product surface

Manual user creation is no longer the preferred onboarding path for normal invited users.

## 4. What Users See

### 3.1 First Release Surface

Visible to invited `basic` users:

- `Dashboard`
- `Trade Explorer`
- `Research`
- `Signals`

### 3.2 Admin-Only

Visible to `admin` users only:

- `Review Queue`
- anomaly inspection
- validation inspection
- operational runbook paths

### 3.3 Hidden for Now

Not visible in the soft launch:

- `Alerts`
- `X Feed`

## 5. Invitation Process

For each invited user:

1. create an invite code
2. share the invite code securely
3. confirm the user can register
4. confirm the user can sign in
5. confirm the user lands in the correct release surface

Suggested first-account sequence:

1. create admin accounts
2. verify admin review route
3. create first invite codes for `basic` users
4. verify one successful `basic` registration and sign-in before inviting more

## 6. Daily Monitoring During Soft Launch

During the first invited-user period, review these daily:

### 5.1 Product Health

- app login works
- dashboard loads
- trade explorer loads
- signals load

### 5.2 Data Trust

- recent user-facing disclosures look sane on spot check
- no future-dated trades appear in product pages
- signals still look directionally credible

### 5.3 Admin Review Queue

- transaction anomalies are visible to admins
- failed validations are visible to admins
- anomaly volume is not unexpectedly spiking

### 5.4 Ingestion Operations

- latest ingestion run completed
- normalization queue is not backing up unexpectedly
- validation failure rate is stable

See:

- [operator-runbook-phase1-congressional.md](/Users/dev/Documents/market-copilot/docs/operator-runbook-phase1-congressional.md)

## 7. Feedback Focus

Ask the first invited users about:

- whether `Dashboard` gives a clear sense of what matters
- whether `Trade Explorer` is usable without explanation
- whether `Research` answers “what else did this filer trade?”
- whether `Signals` feels useful and believable
- whether anything feels misleading, dead-end, or noisy

Do not expand scope during the first feedback cycle unless the issue is trust-breaking.

## 8. Hold Conditions

Pause or hold the rollout if any of these happen:

- future-dated or obviously incorrect trades appear in user-facing pages
- sign-in or access control breaks
- admin review route becomes accessible to non-admin users
- ingestion failures prevent fresh data from landing
- signal rankings look clearly wrong on repeated spot checks

## 9. Expand Conditions

Expand from the first cohort only when:

- invited users can sign in and use the product reliably
- no major trust-breaking data issues are found
- admin review remains manageable
- recent ingestion runs stay healthy

Recommended expansion path:

1. first `3-5` basic users
2. stabilize for several days
3. expand to the next small invited group

## 10. Current Recommendation

Current recommendation:

- proceed with a small invited-user soft launch
- keep the first cohort intentionally small
- use admin review and operational checks actively during the first usage window
