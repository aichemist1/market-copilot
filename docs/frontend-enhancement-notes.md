# Frontend Enhancement Notes

## Purpose

This document captures UI and UX enhancement feedback that should inform future iterations of the product surface.

It is intentionally different from:

- [frontend-product-surface-mvp.md](/Users/dev/Documents/market-copilot/docs/frontend-product-surface-mvp.md), which describes the current implemented surface
- [congressional-signal-theses-mvp.md](/Users/dev/Documents/market-copilot/docs/congressional-signal-theses-mvp.md), which captures signal and analytics interpretation guidance

This file is for design refinement, interaction improvements, and page-level enhancement ideas.

## Research Page Enhancements

### Layout Direction

The current `Research` page is functionally correct, but there is a clear opportunity to make it more elegant and more informative.

Recommended enhancement direction:

- replace the current list/table-style focal filing presentation with a richer "baseball card" layout for each disclosed trade
- each card should make the trade feel like a self-contained research object, with:
  - filer identity
  - action
  - ticker
  - issuer name
  - amount range
  - trade date
  - asset type
  - filing reference
- the card treatment should feel more editorial and investigation-oriented than the current row treatment

### Content Framing Correction

When a focal filing contains more than one ticker, the research hero should not over-anchor to a single ticker in a way that obscures the broader filing context.

Example problem:

- `Hon. Tim Walberg disclosed FSSL in filing 20034660. This filing also includes 1 other ticker.`

This is technically accurate, but still too narrow if the filing also includes `UA`.

Recommended future treatment:

- the hero summary should emphasize the filing as a multi-trade research object when appropriate
- related tickers from the same filing should be surfaced prominently instead of being implied only through count language
- the page should help users understand both:
  - the focal ticker that brought them into `Research`
  - the full set of other disclosed names in the same filing

### Design Intent

The `Research` page should feel different from `Trade Explorer`.

- `Trade Explorer` should remain list-first and operational
- `Research` should feel richer, more contextual, and more analytical

That makes the page transition feel intentional:

- `Trade Explorer` = browse
- `Research` = investigate
