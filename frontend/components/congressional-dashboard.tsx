"use client";

import { useEffect, useMemo, useState } from "react";
import { DashboardPayload, fetchDashboardData, IngestionRun, TransactionFeedItem, UserProfile } from "@/lib/graphql";
import styles from "./congressional-dashboard.module.css";

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

export function CongressionalDashboard() {
  const [profile, setProfile] = useState<UserProfile>("basic");
  const [filters, setFilters] = useState<Filters>(defaultFilters);
  const [data, setData] = useState<DashboardPayload>({ transactions: [], ingestionRuns: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);

      try {
        const next = await fetchDashboardData({
          profile,
          ...filters,
          limit: 24,
        });
        if (!cancelled) {
          setData(next);
        }
      } catch (nextError) {
        if (!cancelled) {
          setError(nextError instanceof Error ? nextError.message : "Unable to load dashboard");
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
  }, [profile, filters]);

  const summary = useMemo(() => buildSummary(data.transactions), [data.transactions]);
  const activePreset = useMemo(() => resolveActivePreset(filters), [filters]);
  const adminOverview = useMemo(() => buildAdminOverview(data.ingestionRuns), [data.ingestionRuns]);

  return (
    <main className={styles.page}>
      <section className={styles.shell}>
        <header className={styles.topbar}>
          <div>
            <p className={styles.eyebrow}>Market Intelligence Copilot</p>
            <h1 className={styles.title}>Congressional activity, shaped for decision-making.</h1>
          </div>
          <div className={styles.topbarMeta}>
            <span className={styles.livePill}>Live congressional feed</span>
            <div className={styles.profileSwitch}>
              <button
                className={profile === "basic" ? styles.profileActive : styles.profileButton}
                onClick={() => setProfile("basic")}
                type="button"
              >
                Consumer View
              </button>
              <button
                className={profile === "admin" ? styles.profileActive : styles.profileButton}
                onClick={() => setProfile("admin")}
                type="button"
              >
                Admin View
              </button>
            </div>
          </div>
        </header>

        <section className={styles.hero}>
          <div className={styles.heroCopy}>
            <p className={styles.subtitle}>
              Start from a high-signal feed of recent congressional transactions, then tighten by
              ticker, member, or date window. The admin view keeps one eye on pipeline health
              without turning the product surface into an operations console.
            </p>
            <div className={styles.heroNotes}>
              <div className={styles.noteCard}>
                <p className={styles.noteLabel}>Product scope</p>
                <p className={styles.noteValue}>Only transactions dated 2026 and forward appear here.</p>
              </div>
              <div className={styles.noteCard}>
                <p className={styles.noteLabel}>Default posture</p>
                <p className={styles.noteValue}>Recent flow first, source filing always one click away.</p>
              </div>
            </div>
          </div>
          <nav className={styles.heroNav} aria-label="Primary product areas">
            <p className={styles.panelEyebrow}>Navigation</p>
            <a className={styles.heroNavActive} href="#congressional-feed">
              Congressional Feed
            </a>
            <span className={styles.heroNavMuted}>Member Detail</span>
            <span className={styles.heroNavMuted}>Institutional Flow</span>
            <span className={styles.heroNavMuted}>Whale Activity</span>
          </nav>
        </section>

        <section className={styles.summaryRow}>
          <SummaryCard label="Visible transactions" value={summary.total.toString()} tone="neutral" />
          <SummaryCard label="Buy signals" value={summary.purchases.toString()} tone="accent" />
          <SummaryCard label="Sell signals" value={summary.sales.toString()} tone="warn" />
          <SummaryCard label="Tracked members" value={summary.members.toString()} tone="neutral" />
        </section>

        <section className={styles.layout}>
          <div className={styles.feedPanel} id="congressional-feed">
            <header className={styles.panelHeader}>
              <div>
                <p className={styles.panelEyebrow}>Transaction Feed</p>
                <h2 className={styles.panelTitle}>Recent congressional transactions</h2>
              </div>
              <p className={styles.panelContext}>
                {profile === "admin"
                  ? "Admin view keeps the feed intact while surfacing pipeline momentum on the side."
                  : "Consumer view stays focused on what just happened and why it may matter."}
              </p>
            </header>

            <FilterBar
              activePreset={activePreset}
              filters={filters}
              onChange={setFilters}
            />

            {error ? <p className={styles.error}>{error}</p> : null}
            {loading ? <p className={styles.state}>Loading transaction feed…</p> : null}
            {!loading && !error && data.transactions.length === 0 ? (
              <p className={styles.state}>No in-scope transactions matched the current filters.</p>
            ) : null}

            <div className={styles.feedList}>
              {data.transactions.map((transaction) => (
                <TransactionCard
                  key={`${transaction.sourceRecordId}-${transaction.transactionIndex}`}
                  transaction={transaction}
                />
              ))}
            </div>
          </div>

          <aside className={styles.sidePanel}>
            <section className={styles.sideCard}>
              <p className={styles.panelEyebrow}>Signal framing</p>
              <div className={styles.signalStack}>
                <div className={styles.signalRow}>
                  <span className={styles.signalLabel}>Active window</span>
                  <strong>{activePreset}</strong>
                </div>
                <div className={styles.signalRow}>
                  <span className={styles.signalLabel}>Default scope</span>
                  <strong>2026+</strong>
                </div>
                <div className={styles.signalRow}>
                  <span className={styles.signalLabel}>Feed posture</span>
                  <strong>{summary.purchases >= summary.sales ? "Buy-heavy" : "Sell-heavy"}</strong>
                </div>
              </div>
            </section>

            <section className={styles.sideCard}>
              <p className={styles.panelEyebrow}>Consumer perspective</p>
              <p className={styles.sideText}>
                Start from a clean feed, filter by ticker or member, and open source filings when a
                trade deserves deeper review.
              </p>
            </section>

            <section className={styles.sideCard}>
              <p className={styles.panelEyebrow}>Admin pulse</p>
              {profile === "admin" ? (
                <>
                  <div className={styles.adminGrid}>
                    <div className={styles.adminMetric}>
                      <span className={styles.signalLabel}>Latest run</span>
                      <strong>{adminOverview.latestStatus}</strong>
                    </div>
                    <div className={styles.adminMetric}>
                      <span className={styles.signalLabel}>Published</span>
                      <strong>{adminOverview.latestPublished}</strong>
                    </div>
                  </div>
                  <AdminRuns runs={data.ingestionRuns} />
                </>
              ) : (
                <p className={styles.sideText}>
                  Switch to Admin View to inspect recent ingestion runs and pipeline health.
                </p>
              )}
            </section>
          </aside>
        </section>
      </section>
    </main>
  );
}

function buildSummary(transactions: TransactionFeedItem[]) {
  return {
    total: transactions.length,
    purchases: transactions.filter((item) => item.transactionType === "purchase").length,
    sales: transactions.filter((item) => item.transactionType === "sale").length,
    members: new Set(transactions.map((item) => item.reportingPerson)).size,
  };
}

function SummaryCard({
  label,
  value,
  tone,
}: {
  label: string;
  value: string;
  tone: "neutral" | "accent" | "warn";
}) {
  const className =
    tone === "accent"
      ? styles.summaryAccent
      : tone === "warn"
        ? styles.summaryWarn
        : styles.summaryNeutral;

  return (
    <article className={className}>
      <p className={styles.summaryLabel}>{label}</p>
      <p className={styles.summaryValue}>{value}</p>
    </article>
  );
}

function FilterBar({
  activePreset,
  filters,
  onChange,
}: {
  activePreset: string;
  filters: Filters;
  onChange: (next: Filters) => void;
}) {
  return (
    <>
      <div className={styles.rangeRow}>
        <span className={styles.rangeLabel}>Quick ranges</span>
        <div className={styles.rangeChips}>
          {rangePresets.map((preset) => {
            const isActive = activePreset === preset.label;
            return (
              <button
                key={preset.label}
                className={isActive ? styles.rangeChipActive : styles.rangeChip}
                onClick={() => onChange(applyRangePreset(filters, preset.days))}
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
          onChange={(event) => onChange({ ...filters, ticker: event.target.value.toUpperCase() })}
        />
        <input
          className={styles.input}
          placeholder="Member name"
          value={filters.reportingPerson}
          onChange={(event) => onChange({ ...filters, reportingPerson: event.target.value })}
        />
        <select
          className={styles.select}
          value={filters.transactionType}
          onChange={(event) => onChange({ ...filters, transactionType: event.target.value })}
        >
          <option value="">All actions</option>
          <option value="purchase">Purchases</option>
          <option value="sale">Sales</option>
        </select>
        <select
          className={styles.select}
          value={filters.assetType}
          onChange={(event) => onChange({ ...filters, assetType: event.target.value })}
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
          onChange={(event) => onChange({ ...filters, transactionDateFrom: event.target.value })}
        />
        <input
          className={styles.input}
          type="date"
          value={filters.transactionDateTo}
          onChange={(event) => onChange({ ...filters, transactionDateTo: event.target.value })}
        />
      </div>
    </>
  );
}

function TransactionCard({ transaction }: { transaction: TransactionFeedItem }) {
  return (
    <article className={styles.transactionCard}>
      <div className={styles.transactionGrid}>
        <div className={styles.transactionIdentity}>
          <div className={styles.memberRow}>
            <p className={styles.member}>{transaction.reportingPerson}</p>
            {transaction.ownerType ? <span className={styles.ownerPill}>{formatOwnerType(transaction.ownerType)}</span> : null}
          </div>
          <p className={styles.meta}>
            {transaction.districtOrState ?? "Unknown district"} · Filing {transaction.sourceRecordId}
          </p>
        </div>

        <div className={styles.transactionAsset}>
          <h3 className={styles.issuer}>{transaction.issuerName}</h3>
          <p className={styles.meta}>
            {transaction.ticker ?? "No ticker"} · {formatAssetType(transaction.assetType)}
          </p>
        </div>

        <div className={styles.transactionFacts}>
          <span
            className={
              transaction.transactionType === "purchase" ? styles.badgeBuy : styles.badgeSell
            }
          >
            {transaction.transactionType}
          </span>
          <p className={styles.amount}>{transaction.amountRange ?? "Undisclosed range"}</p>
          <p className={styles.meta}>{transaction.transactionDate ?? "Unknown date"}</p>
        </div>

        <div className={styles.transactionAction}>
          <a
            className={styles.sourceLink}
            href={transaction.sourceDocumentUrl}
            target="_blank"
            rel="noreferrer"
          >
            Open source filing
          </a>
        </div>
      </div>
    </article>
  );
}

function AdminRuns({ runs }: { runs: IngestionRun[] }) {
  if (runs.length === 0) {
    return <p className={styles.sideText}>No ingestion runs available yet.</p>;
  }

  return (
    <div className={styles.runList}>
      {runs.map((run) => (
        <article key={run.id} className={styles.runCard}>
          <div className={styles.runTop}>
            <strong>{run.status}</strong>
            <span>{new Date(run.startedAt).toLocaleString()}</span>
          </div>
          <p className={styles.runMeta}>
            discovered {run.filesDiscoveredCount} · normalized {run.recordsNormalizedCount} ·
            published {run.recordsPublishedCount}
          </p>
          {run.errorSummary ? <p className={styles.runError}>{run.errorSummary}</p> : null}
        </article>
      ))}
    </div>
  );
}

function buildAdminOverview(runs: IngestionRun[]) {
  const latest = runs[0];

  return {
    latestStatus: latest?.status ?? "No runs",
    latestPublished: latest ? latest.recordsPublishedCount.toString() : "0",
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

function formatOwnerType(value: string) {
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function formatAssetType(value: string | null) {
  if (!value) {
    return "Unknown asset";
  }

  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}
