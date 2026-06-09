"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { ProductShell } from "@/components/product-shell";
import { SignalMetrics, TickerSignal, fetchSignalMetrics, fetchTickerSignals } from "@/lib/graphql";
import { formatDisplayDate } from "@/lib/insights";
import styles from "./signals-page.module.css";

const assetViews = [
  { label: "Stocks", value: "stock" },
  { label: "ETFs", value: "etf" },
] as const;

const dateWindows = [
  { label: "1 month", from: formatDateOffset(30), caption: "last 30 days" },
  { label: "3 months", from: formatDateOffset(90), caption: "last 90 days" },
  { label: "All", from: "2026-01-01", caption: "full 2026 scope" },
] as const;

const emptyMetrics: SignalMetrics = {
  activeTickerCount: 0,
  buyDisclosureCount: 0,
  distinctFilerCount: 0,
  latestFilingDate: null,
};

export function SignalsPage() {
  const [signals, setSignals] = useState<TickerSignal[]>([]);
  const [metrics, setMetrics] = useState<SignalMetrics>(emptyMetrics);
  const [assetType, setAssetType] = useState<(typeof assetViews)[number]["value"]>("stock");
  const [transactionDateFrom, setTransactionDateFrom] = useState(dateWindows[0].from);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);

      try {
        const [nextSignals, nextMetrics] = await Promise.all([
          fetchTickerSignals({
            assetType,
            transactionDateFrom,
            limit: 24,
          }),
          fetchSignalMetrics({
            assetType,
            transactionDateFrom,
          }),
        ]);

        if (!cancelled) {
          setSignals(nextSignals);
          setMetrics(nextMetrics);
        }
      } catch (nextError) {
        if (!cancelled) {
          setError(nextError instanceof Error ? nextError.message : "Unable to load signals");
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
  }, [assetType, transactionDateFrom]);

  const maxActivity = useMemo(() => {
    const counts = signals.flatMap((signal) => [signal.buyCount, signal.sellCount]);
    return Math.max(1, ...counts);
  }, [signals]);
  const dateWindowLabel =
    dateWindows.find((window) => window.from === transactionDateFrom)?.caption ?? "current window";

  return (
    <ProductShell
      title="Signals"
      subtitle="Most-bought tickers from official congressional disclosure records, ranked by conviction and filer participation."
      compactHero
    >
      <section className={styles.metricsStrip}>
        <SummaryMetric
          label="Active tickers"
          value={metrics.activeTickerCount}
          hint={dateWindowLabel}
          accent
        />
        <SummaryMetric
          label="Buy disclosures"
          value={metrics.buyDisclosureCount}
          hint={dateWindowLabel}
          accent
        />
        <SummaryMetric
          label="Distinct filers"
          value={metrics.distinctFilerCount}
          hint="across visible signals"
        />
        <SummaryMetric
          label="Latest filing"
          value={formatDisplayDate(metrics.latestFilingDate)}
          hint={buildRecencyText(metrics.latestFilingDate)}
        />
      </section>

      <section className={styles.panel}>
        <div className={styles.sectionHeader}>
          <div>
            <p className={styles.sectionLabel}>Popular buy tickers</p>
            <h2 className={styles.sectionTitle}>Signal cards ranked by buy pressure and filer breadth.</h2>
            <p className={styles.sectionNote}>
              Use the asset view and time window to narrow the field, then move straight into Research or Trade Explorer from the names that stand out.
            </p>
          </div>
          <div className={styles.controls}>
            <div className={styles.chips}>
              {assetViews.map((view) => (
                <button
                  key={view.value}
                  className={assetType === view.value ? styles.chipActive : styles.chip}
                  onClick={() => setAssetType(view.value)}
                  type="button"
                >
                  {view.label}
                </button>
              ))}
            </div>
            <div className={styles.chips}>
              {dateWindows.map((window) => (
                <button
                  key={window.label}
                  className={transactionDateFrom === window.from ? styles.chipActive : styles.chip}
                  onClick={() => setTransactionDateFrom(window.from)}
                  type="button"
                >
                  {window.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {error ? <p className={styles.state}>{error}</p> : null}
        {loading ? <p className={styles.state}>Loading signals…</p> : null}
        {!loading && !error && signals.length === 0 ? (
          <p className={styles.state}>
            No signals matched this view. Try a wider date range or switch asset types.
          </p>
        ) : null}

        {!loading && !error && signals.length > 0 ? (
          <div className={styles.cardGrid}>
            {signals.map((signal) => (
              <SignalCard
                key={signal.ticker}
                assetType={assetType}
                maxActivity={maxActivity}
                signal={signal}
                transactionDateFrom={transactionDateFrom}
              />
            ))}
          </div>
        ) : null}
      </section>
    </ProductShell>
  );
}

function SummaryMetric({
  label,
  value,
  hint,
  accent = false,
}: {
  label: string;
  value: number | string;
  hint: string;
  accent?: boolean;
}) {
  return (
    <article className={styles.metricCard}>
      <p className={styles.metricLabel}>{label}</p>
      <p className={styles.metricValue}>{value}</p>
      <p className={accent ? styles.metricHintAccent : styles.metricHint}>{hint}</p>
    </article>
  );
}

function SignalCard({
  assetType,
  maxActivity,
  signal,
  transactionDateFrom,
}: {
  assetType: string;
  maxActivity: number;
  signal: TickerSignal;
  transactionDateFrom: string;
}) {
  const buyWidth = Math.max(8, (signal.buyCount / maxActivity) * 100);
  const sellWidth = signal.sellCount > 0 ? Math.max(8, (signal.sellCount / maxActivity) * 100) : 0;
  const rankTone = signal.rank === 1 ? styles.rankHot : signal.rank === 2 ? styles.rankSilver : signal.rank === 3 ? styles.rankBronze : styles.rankNeutral;
  const cardTone = signal.rank === 1 ? styles.signalCardHot : styles.signalCard;

  return (
    <article className={cardTone}>
      <div className={styles.cardTop}>
        <div className={styles.identityRow}>
          <span className={`${styles.rankBadge} ${rankTone}`}>{signal.rank}</span>
          <div className={styles.identityText}>
            <h3 className={styles.tickerValue}>{signal.ticker}</h3>
            <p className={styles.issuerName}>{signal.issuerName ?? "Unknown issuer"}</p>
          </div>
        </div>
        {signal.rank === 1 ? <span className={styles.hotBadge}>Hot</span> : null}
      </div>

      <div className={styles.cardBody}>
        <SignalBarRow
          label="Buy"
          value={signal.buyCount}
          width={buyWidth}
          tone="buy"
        />
        <SignalBarRow
          label="Sell"
          value={signal.sellCount}
          width={sellWidth}
          tone="sell"
        />

        <div className={styles.metaGrid}>
          <div>
            <p className={styles.metaLabel}>Distinct filers</p>
            <p className={styles.metaValue}>{signal.filerCount}</p>
          </div>
          <div>
            <p className={styles.metaLabel}>Latest disclosure</p>
            <p className={styles.metaValue}>{formatDisplayDate(signal.latestFilingDate)}</p>
          </div>
        </div>
      </div>

      <div className={styles.cardActions}>
        <Link
          className={styles.actionButton}
          href={`/research?from=signals&ticker=${encodeURIComponent(signal.ticker)}&assetTypeFilter=${encodeURIComponent(assetType)}&transactionDateFromFilter=${encodeURIComponent(transactionDateFrom)}`}
        >
          Research
        </Link>
        <Link
          className={styles.actionButton}
          href={`/trade-explorer?ticker=${encodeURIComponent(signal.ticker)}&assetType=${assetType}&transactionDateFrom=${transactionDateFrom}`}
        >
          Explore
        </Link>
      </div>
    </article>
  );
}

function SignalBarRow({
  label,
  tone,
  value,
  width,
}: {
  label: string;
  tone: "buy" | "sell";
  value: number;
  width: number;
}) {
  return (
    <div className={styles.barRow}>
      <span className={tone === "buy" ? styles.buyLabel : styles.sellLabel}>{label}</span>
      <div className={styles.barTrack}>
        {value > 0 ? (
          <span
            className={tone === "buy" ? styles.buyBar : styles.sellBar}
            style={{ width: `${width}%` }}
          />
        ) : null}
      </div>
      <span className={styles.barValue}>{value}</span>
    </div>
  );
}

function buildRecencyText(value: string | null) {
  if (!value) {
    return "no filing date";
  }

  const latest = new Date(`${value}T00:00:00Z`);
  const now = new Date();
  const diffMs = now.getTime() - latest.getTime();
  const days = Math.max(0, Math.floor(diffMs / (1000 * 60 * 60 * 24)));
  return days === 0 ? "today" : `${days} day${days === 1 ? "" : "s"} ago`;
}

function formatDateOffset(days: number) {
  const value = new Date();
  value.setDate(value.getDate() - days);
  const year = value.getFullYear();
  const month = `${value.getMonth() + 1}`.padStart(2, "0");
  const day = `${value.getDate()}`.padStart(2, "0");
  return `${year}-${month}-${day}`;
}
