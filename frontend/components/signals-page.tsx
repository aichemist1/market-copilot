"use client";

import { useEffect, useState } from "react";
import { ProductShell } from "@/components/product-shell";
import { TickerSignal, fetchTickerSignals } from "@/lib/graphql";
import styles from "./signals-page.module.css";

export function SignalsPage() {
  const [signals, setSignals] = useState<TickerSignal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);

      try {
        const next = await fetchTickerSignals({
          transactionDateFrom: "2026-01-01",
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
  }, []);

  return (
    <ProductShell
      title="Signals"
      subtitle="Most-bought stock and ETF tickers from current official disclosure activity. Built from deterministic aggregates so the ranking stays consistent, transparent, and scalable."
    >
      <section className={styles.panel}>
        <div className={styles.sectionHeader}>
          <div>
            <p className={styles.sectionLabel}>Popular buy tickers</p>
            <h2 className={styles.sectionTitle}>Ranked by recent buy disclosures across distinct filers.</h2>
          </div>
        </div>

        {error ? <p className={styles.state}>{error}</p> : null}
        {loading ? <p className={styles.state}>Loading signals…</p> : null}
        {!loading && !error && signals.length === 0 ? (
          <p className={styles.state}>No ticker signals are available yet.</p>
        ) : null}

        {!loading && !error && signals.length > 0 ? (
          <div className={styles.table}>
            <div className={styles.tableHeader}>
              <span>Rank</span>
              <span>Ticker</span>
              <span>Issuer</span>
              <span>Buy Records</span>
              <span>Sell Records</span>
              <span>Filers</span>
              <span>Latest Filing Date</span>
            </div>

            {signals.map((signal) => (
              <article key={signal.ticker} className={styles.tableRow}>
                <strong>{signal.rank}</strong>
                <strong>{signal.ticker}</strong>
                <span>{signal.issuerName ?? "Unknown issuer"}</span>
                <span>{signal.buyCount}</span>
                <span>{signal.sellCount}</span>
                <span>{signal.filerCount}</span>
                <span>{signal.latestFilingDate ?? "Unknown"}</span>
              </article>
            ))}
          </div>
        ) : null}
      </section>
    </ProductShell>
  );
}
