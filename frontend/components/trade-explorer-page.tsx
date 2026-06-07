"use client";

import { useEffect, useMemo, useState } from "react";
import { DisclosureList } from "@/components/disclosure-list";
import { ProductShell } from "@/components/product-shell";
import { TransactionFeedItem, fetchTransactions } from "@/lib/graphql";
import styles from "./trade-explorer-page.module.css";

type Filters = {
  ticker: string;
  reportingPerson: string;
  transactionType: string;
  assetType: string;
  transactionDateFrom: string;
  transactionDateTo: string;
};

const defaultFilters: Filters = {
  ticker: "",
  reportingPerson: "",
  transactionType: "",
  assetType: "",
  transactionDateFrom: "2026-01-01",
  transactionDateTo: "",
};

type TradeExplorerInitialFilters = Partial<Filters>;

const rangePresets = [
  { label: "Today", days: 0 },
  { label: "1 week", days: 7 },
  { label: "1 month", days: 30 },
  { label: "3 months", days: 90 },
  { label: "All", days: null },
] as const;

export function TradeExplorerPage({
  initialFilters,
}: {
  initialFilters?: TradeExplorerInitialFilters;
}) {
  const [filters, setFilters] = useState<Filters>(() => filtersFromObject(initialFilters));
  const [transactions, setTransactions] = useState<TransactionFeedItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);

      try {
        const next = await fetchTransactions({
          ...filters,
          limit: 40,
        });

        if (!cancelled) {
          setTransactions(next);
        }
      } catch (nextError) {
        if (!cancelled) {
          setError(nextError instanceof Error ? nextError.message : "Unable to load explorer");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [filters]);

  const activePreset = useMemo(() => resolveActivePreset(filters), [filters]);
  const researchContext = useMemo(
    () => buildResearchContext(filters),
    [filters],
  );

  return (
    <ProductShell
      title="Trade Explorer"
      subtitle="Browse what congressional filers bought and sold, narrow the stream quickly, and open Research when a trade deserves a closer look."
      compactHero
    >
      <section className={styles.panel}>
        <div className={styles.rangeRow}>
          <div>
            <p className={styles.sectionLabel}>Explorer filters</p>
            <h2 className={styles.sectionTitle}>Filter the stream without losing the trade signal.</h2>
            <p className={styles.sectionNote}>
              Use ticker, filer, action, asset type, and trade date to isolate the activity you want to investigate next.
            </p>
          </div>
          <div className={styles.rangeChips}>
            {rangePresets.map((preset) => {
              const isActive = activePreset === preset.label;

              return (
                <button
                  key={preset.label}
                  className={isActive ? styles.rangeChipActive : styles.rangeChip}
                  onClick={() => setFilters(applyRangePreset(filters, preset.days))}
                  type="button"
                >
                  {preset.label}
                </button>
              );
            })}
          </div>
        </div>

        {!loading && !error ? (
          <p className={styles.resultMeta}>{transactions.length} visible trades in the current filtered view.</p>
        ) : null}

        <div className={styles.filters}>
          <input
            className={styles.input}
            placeholder="Ticker"
            value={filters.ticker}
            onChange={(event) => setFilters({ ...filters, ticker: event.target.value.toUpperCase() })}
          />
          <input
            className={styles.input}
            placeholder="Member name"
            value={filters.reportingPerson}
            onChange={(event) => setFilters({ ...filters, reportingPerson: event.target.value })}
          />
          <select
            className={styles.select}
            value={filters.transactionType}
            onChange={(event) => setFilters({ ...filters, transactionType: event.target.value })}
          >
            <option value="">All actions</option>
            <option value="purchase">Purchases</option>
            <option value="sale">Sales</option>
          </select>
          <select
            className={styles.select}
            value={filters.assetType}
            onChange={(event) => setFilters({ ...filters, assetType: event.target.value })}
          >
            <option value="">All assets</option>
            <option value="stock">Stock</option>
            <option value="option">Option</option>
            <option value="bond">Bond</option>
            <option value="government_security">Government security</option>
            <option value="other">Other</option>
          </select>
          <input
            className={styles.input}
            type="date"
            value={filters.transactionDateFrom}
            onChange={(event) => setFilters({ ...filters, transactionDateFrom: event.target.value })}
          />
          <input
            className={styles.input}
            type="date"
            value={filters.transactionDateTo}
            onChange={(event) => setFilters({ ...filters, transactionDateTo: event.target.value })}
          />
        </div>

        {error ? <p className={styles.state}>{error}</p> : null}
        {loading ? <p className={styles.state}>Loading trade explorer…</p> : null}
        {!loading && !error && transactions.length === 0 ? (
          <p className={styles.state}>No trades matched the current filters. Widen the dates or remove a filter to keep exploring.</p>
        ) : null}

        {!loading && !error && transactions.length > 0 ? (
          <DisclosureList
            transactions={transactions}
            linkToResearch
            researchContext={researchContext}
          />
        ) : null}
      </section>
    </ProductShell>
  );
}

function buildResearchContext(filters: Filters) {
  return {
    from: "trade-explorer",
    reportingPersonFilter: filters.reportingPerson,
    tickerFilter: filters.ticker,
    transactionTypeFilter: filters.transactionType,
    assetTypeFilter: filters.assetType,
    transactionDateFromFilter: filters.transactionDateFrom,
    transactionDateToFilter: filters.transactionDateTo,
  };
}

function filtersFromObject(source?: TradeExplorerInitialFilters): Filters {
  return {
    ticker: source?.ticker ?? defaultFilters.ticker,
    reportingPerson: source?.reportingPerson ?? defaultFilters.reportingPerson,
    transactionType: source?.transactionType ?? defaultFilters.transactionType,
    assetType: source?.assetType ?? defaultFilters.assetType,
    transactionDateFrom: source?.transactionDateFrom ?? defaultFilters.transactionDateFrom,
    transactionDateTo: source?.transactionDateTo ?? defaultFilters.transactionDateTo,
  };
}

function applyRangePreset(filters: Filters, days: number | null): Filters {
  if (days === null) {
    return {
      ...filters,
      transactionDateFrom: "2026-01-01",
      transactionDateTo: "",
    };
  }

  const endDate = new Date();
  const startDate = new Date();
  startDate.setDate(endDate.getDate() - days);

  return {
    ...filters,
    transactionDateFrom: formatDateForInput(startDate),
    transactionDateTo: formatDateForInput(endDate),
  };
}

function resolveActivePreset(filters: Filters) {
  for (const preset of rangePresets) {
    const next = applyRangePreset(defaultFilters, preset.days);
    if (
      next.transactionDateFrom === filters.transactionDateFrom &&
      next.transactionDateTo === filters.transactionDateTo
    ) {
      return preset.label;
    }
  }

  return "Custom";
}

function formatDateForInput(value: Date) {
  const year = value.getFullYear();
  const month = `${value.getMonth() + 1}`.padStart(2, "0");
  const day = `${value.getDate()}`.padStart(2, "0");

  return `${year}-${month}-${day}`;
}
