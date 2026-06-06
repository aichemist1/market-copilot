# Release Checklist Results: 2026-06-06

## Purpose

This document records the current release-check outcome for the MVP soft launch checklist.

It is a run result, not the checklist definition itself.

Checklist source:

- [release-checklist-mvp.md](/Users/dev/Documents/market-copilot/docs/release-checklist-mvp.md)

## 1. Current Summary

Current state:

- release-critical unauthenticated route protection is working
- authenticated role-based product checks passed for:
  - `basic`
  - `admin`

Current release recommendation:

- marked `passed` for invited-user soft launch

## 2. Verified in This Pass

### 2.1 Unauthenticated Route Protection

Verified against the running local frontend:

- `/` redirects to `/login`
- `/trade-explorer` redirects to `/login`
- `/research` redirects to `/login`
- `/signals` redirects to `/login`
- `/admin/review` redirects to `/login`

Observed redirect behavior:

- `/` -> `/login?next=%2F`
- `/trade-explorer` -> `/login?next=%2Ftrade-explorer`
- `/research` -> `/login?next=%2Fresearch`
- `/signals` -> `/login?next=%2Fsignals`
- `/admin/review` -> `/login?next=%2Fadmin%2Freview`

Conclusion:

- the new session gate is active for both user-facing and admin-only routes

## 3. Signed-In Checklist Outcome

### 3.1 Basic User Pass

Verified:

- sign in as `basic`
- dashboard loads
- trade explorer loads
- research opens from dashboard and trade explorer
- signals page loads
- `Review Queue` is not visible
- direct `/admin/review` access is blocked

### 3.2 Admin User Pass

Verified:

- sign in as `admin`
- released product pages still behave normally
- `Review Queue` is visible in the header
- `/admin/review` loads correctly
- anomalies and failed validations render

## 4. Release Decision

Current decision:

- the MVP release candidate passed the current role-based checklist
- the app is ready for invited-user soft launch
- continue using anomaly review and admin inspection during the first cohort rollout

Next operating plan:

- [invited-user-rollout-plan-mvp.md](/Users/dev/Documents/market-copilot/docs/invited-user-rollout-plan-mvp.md)
