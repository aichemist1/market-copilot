"use client";

import { useEffect, useMemo, useState } from "react";
import { DisclosureList } from "@/components/disclosure-list";
import { ProductShell } from "@/components/product-shell";
import { TransactionFeedItem, fetchTransactions } from "@/lib/graphql";
import { buildSummary } from "@/lib/insights";
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

const rangePresets = [
  { label: "Today", days: 0 },
  { label: "1 week", days: 7 },
  { label: "1 month", days: 30 },
  { label: "3 months", days: 90 },
  { label: "All", days: null },
] as const;

export function TradeExplorerPage() {
  const [filters, setFilters] = useState<Filters>(defaultFilters);
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

  const summary = useMemo(() => buildSummary(transactions), [transactions]);
  const activePreset = useMemo(() => resolveActivePreset(filters), [filters]);

  return (
    <ProductShell
      title="Trade Explorer"
      subtitle="Explore the disclosure stream with a cleaner list-first workflow. Filter what matters and move directly into the underlying filing when you need source detail."
    >
      <section className={styles.summaryRow}>
        <SummaryCard label="Visible trades" value={summary.total.toString()} />
        <SummaryCard label="Purchases" value={summary.purchases.toString()} />
        <SummaryCard label="Sales" value={summary.sales.toString()} />
        <SummaryCard label="Members" value={summary.members.toString()} />
      </section>

      <section className={styles.panel}>
        <div className={styles.rangeRow}>
          <div>
            <p className={styles.sectionLabel}>Explorer filters</p>
            <h2 className={styles.sectionTitle}>Filter the disclosure stream without leaving the list view.</h2>
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
          <p className={styles.state}>No in-scope disclosures matched the current filters.</p>
        ) : null}

        {!loading && !error && transactions.length > 0 ? (
          <DisclosureList transactions={transactions} />
        ) : null}
      </section>
    </ProductShell>
  );
}

function SummaryCard({ label, value }: { label: string; value: string }) {
  return (
    <article className={styles.summaryCard}>
      <p className={styles.summaryLabel}>{label}</p>
      <p className={styles.summaryValue}>{value}</p>
    </article>
  );
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
