# Congressional Signal Theses For MVP

## Purpose

This document captures how congressional disclosure data should be interpreted and applied inside Market Intelligence Copilot.

It is not a source-ingestion document and not a UI specification. It is a product-strategy note for how the structured congressional dataset can evolve into differentiated research, signal, and recommendation features.

## Core Framing

Congressional disclosure data is valuable, but it must be used in the right time horizon.

Because disclosures can lag underlying transactions by as much as 45 days, this dataset should not be treated as a short-term trading feed, day-trading edge, or front-running mechanism. The correct framing is:

- long-horizon conviction signal
- macroeconomic and regulatory signal
- directional sector and capital-allocation signal
- idea-generation input for deeper research

The value comes less from immediate price reaction and more from what the trades imply about:

- regulatory awareness
- budget and spending visibility
- committee-domain knowledge
- longer-term sector positioning

## Important Caution

One statement should be treated as a working thesis, not a hard product fact until we validate it rigorously:

- "Historically, members of Congress beat the S&P 500 significantly over a multi-year horizon."

This may directionally support the product vision, but it should not be presented to users as a proven product truth unless we back it with robust historical analysis and methodology. Different studies can produce different conclusions depending on:

- time range
- transaction filtering
- lag handling
- benchmark choice
- handling of spouses, partial disclosures, and missing data

So the product should treat congressional data as potentially high-value intelligence, while remaining careful about making blanket outperformance claims without evidence.

## Product Interpretation Model

The product should interpret congressional disclosures as structural intelligence rather than immediate execution signals.

The practical meaning is:

- `Dashboard` should surface notable activity, not promise immediate tradability
- `Trade Explorer` should help users inspect patterns and concentration
- `Research` should contextualize the filing, filer, and related activity
- `Signals` should rank conviction, clustering, and sustained directional behavior

Over time, the product should learn to answer:

- Is this a one-off personal portfolio adjustment?
- Is this a repeated conviction pattern?
- Is this part of a committee-linked domain signal?
- Is political capital rotating toward or away from a sector?

## Signal Thesis 1: Cluster Buying

### Thesis

If one politician buys a stock, that may be noise or a routine portfolio adjustment. If multiple politicians buy the same stock within a defined window, especially from different geographies or overlapping oversight domains, that becomes a higher-conviction signal.

### Why It Matters

Cluster buying suggests the market may not yet fully reflect a longer-term policy, regulatory, contract, subsidy, or spending tailwind.

This is especially relevant when:

- several filers buy the same name within 30 days
- filers come from different states or districts
- filers share committee relevance
- purchases are net-positive rather than mixed with offsetting sales

### Product Use

This should become a first-class signal type in the product.

Possible future output:

- cluster-buy ticker alerts
- ranked cluster-buy tables in `Signals`
- cluster-buy annotations in `Research`
- time-window views such as 7-day, 30-day, and 90-day clusters

### Future Product Logic

Potential ranking inputs:

- number of distinct filers
- committee overlap strength
- net buys versus sells
- size-tier intensity
- recency of the cluster

## Signal Thesis 2: Committee Assignment Context

### Thesis

Committee assignments provide domain context for interpreting trades. Members often have deeper exposure to industry conditions, budgets, policy priorities, and supply-chain realities within their committees.

Examples of especially relevant committee categories:

- Armed Services
- Energy and Commerce
- Appropriations
- House Financial Services

### Why It Matters

A trade from a member within a relevant oversight domain may carry more informational weight than the same trade from a filer with no obvious domain linkage.

This should be interpreted as longer-term domain-aware conviction, not short-term timing.

Examples:

- defense and aerospace names tied to Armed Services
- energy, utilities, or climate-linked names tied to Energy and Commerce
- banks, exchanges, fintech, insurers, or asset managers tied to Financial Services

### Product Use

Committee alignment should become a ranking and filtering dimension.

Possible future output:

- committee-context badges in `Research`
- committee-linked scoring inside `Signals`
- filters such as "show buys from relevant oversight members"

### Dependency

This will require a committee-membership reference dataset and a mapping layer between:

- filers
- committees
- sectors or industries

## Signal Thesis 3: Asymmetric Conviction By Size

### Thesis

Broad transaction size bands still carry useful information. A small disclosed purchase may be ignorable noise, while a large disclosed purchase can represent unusually high conviction.

### Why It Matters

The reporting lag does not erase the information value of a large, concentrated, domain-relevant purchase by a senior or well-positioned member.

The product should distinguish between:

- low-signal micro-sized activity
- medium-conviction positioning
- very large asymmetric bets

### Product Use

This should evolve into a `Conviction Score`.

Possible scoring inputs:

- amount-range tier
- purchase versus sale
- repeated buys by the same filer
- committee relevance
- cluster participation
- whether the trade is in a stock, ETF, or other asset class

### Practical Product Behavior

This could support:

- conviction-ranked signal tables
- high-conviction filters in `Trade Explorer`
- conviction callouts in `Research`

## Signal Thesis 4: Broad Political Sector Rotation

### Thesis

Aggregated congressional transaction data can reveal sector rotation when viewed over longer rolling windows such as 90 days.

### Why It Matters

Even if individual names are noisy, aggregated directional flow can reveal where political capital is moving before the broader market narrative fully catches up.

Examples of rotation patterns that may matter:

- out of consumer staples
- into infrastructure
- into domestic manufacturing
- into specialized materials
- into defense, energy, or semiconductor themes

### Product Use

This should eventually become a sector-allocation and thematic-intelligence layer.

Possible future output:

- sector rotation summaries on `Dashboard`
- rolling 30-day / 90-day / 180-day flow views
- theme-level signal panels
- net capital flow trend visualizations

### Product Interpretation

This signal is best used for:

- longer-term portfolio allocation ideas
- sector watchlist building
- thematic research prioritization

It is not primarily for short-term trade execution.

## Product Implications

These theses imply that the product should evolve toward three intelligence modes:

### 1. Discovery

Users discover notable filings, tickers, and directional patterns.

Primary surfaces:

- `Dashboard`
- `Trade Explorer`

### 2. Investigation

Users investigate the full context behind a name, filer, or cluster.

Primary surface:

- `Research`

### 3. Prioritization

Users prioritize what matters based on conviction, clustering, committee relevance, and rotation.

Primary surface:

- `Signals`

## Recommended Future Signal Features

Based on these theses, the next meaningful signal features later should likely include:

- cluster-buy detection
- conviction scoring
- committee-aware relevance scoring
- sector rotation summaries
- multi-window signal ranking
- alerts for unusual repeated buys or cluster formation

## What Not To Overclaim

The product should avoid implying:

- that congressional data is a short-term trading edge by itself
- that every congressional trade is informed or predictive
- that every large trade is necessarily alpha
- that historical outperformance is already proven without internal validation

The better product stance is:

- this is a differentiated long-horizon intelligence source
- it becomes more useful when aggregated, contextualized, and scored
- its value comes from pattern detection and domain-aware interpretation, not just raw filings

## Working Product Principle

Congressional disclosure data should be treated as delayed but still powerful structural intelligence.

The product should win by converting:

- lagged raw disclosures

into:

- conviction-aware
- cluster-aware
- committee-aware
- sector-aware

research and signal workflows.
