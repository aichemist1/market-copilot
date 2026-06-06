"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ProductShell } from "@/components/product-shell";
import { TickerSignal, fetchTickerSignals } from "@/lib/graphql";
import styles from "./signals-page.module.css";

const assetViews = [
  { label: "Stocks", value: "stock" },
  { label: "ETFs", value: "etf" },
] as const;

const dateWindows = [
  { label: "1 month", from: formatDateOffset(30) },
  { label: "3 months", from: formatDateOffset(90) },
  { label: "All", from: "2026-01-01" },
] as const;

export function SignalsPage() {
  const [signals, setSignals] = useState<TickerSignal[]>([]);
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
        const next = await fetchTickerSignals({
          assetType,
          transactionDateFrom,
          limit: 25,
        });

        if (!cancelled) {
          setSignals(next);
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

  return (
    <ProductShell
      title="Signals"
      subtitle="Popular buy signals ranked from recent congressional disclosure activity, with asset views and time windows that keep the list focused."
      compactHero
    >
      <section className={styles.panel}>
        <div className={styles.sectionHeader}>
          <div>
            <p className={styles.sectionLabel}>Popular buy tickers</p>
            <h2 className={styles.sectionTitle}>Ranked by recent buy disclosures across distinct filers.</h2>
            <p className={styles.sectionNote}>
              Use the asset view and date window to focus the ranking, then move into Research or Trade Explorer from the names that stand out.
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
          <p className={styles.state}>No signals matched this view. Try a wider date range or switch asset types.</p>
        ) : null}

        {!loading && !error && signals.length > 0 ? (
          <div className={styles.table}>
            <div className={styles.tableHeader}>
              <span>Rank</span>
              <span>Ticker</span>
              <span>Signal</span>
              <span>Buy Records</span>
              <span>Sell Records</span>
              <span>Filers</span>
              <span>Latest</span>
              <span>Actions</span>
            </div>

            {signals.map((signal) => (
              <article key={signal.ticker} className={styles.tableRow}>
                <strong className={styles.rank}>{signal.rank}</strong>
                <div className={styles.tickerCell}>
                  <strong className={styles.ticker}>{signal.ticker}</strong>
                  <span className={styles.issuer}>{signal.issuerName ?? "Unknown issuer"}</span>
                </div>
                <span className={styles.signalText}>
                  {signal.buyCount} buy{signal.buyCount === 1 ? "" : "s"} across {signal.filerCount} filer
                  {signal.filerCount === 1 ? "" : "s"}
                </span>
                <span>{signal.buyCount}</span>
                <span>{signal.sellCount}</span>
                <span>{signal.filerCount}</span>
                <span>{signal.latestFilingDate ?? "Unknown"}</span>
                <div className={styles.actions}>
                  <Link className={styles.actionLink} href={`/research?ticker=${encodeURIComponent(signal.ticker)}`}>
                    Research
                  </Link>
                  <Link
                    className={styles.actionLink}
                    href={`/trade-explorer?ticker=${encodeURIComponent(signal.ticker)}&assetType=${assetType}&transactionDateFrom=${transactionDateFrom}`}
                  >
                    Explore
                  </Link>
                </div>
              </article>
            ))}
          </div>
        ) : null}
      </section>
    </ProductShell>
  );
}

function formatDateOffset(days: number) {
  const value = new Date();
  value.setDate(value.getDate() - days);
  const year = value.getFullYear();
  const month = `${value.getMonth() + 1}`.padStart(2, "0");
  const day = `${value.getDate()}`.padStart(2, "0");
  return `${year}-${month}-${day}`;
}
