"use client";

import { useEffect, useMemo, useState } from "react";
import { ProductShell } from "@/components/product-shell";
import { TransactionFeedItem, fetchTransactions } from "@/lib/graphql";
import { buildSignalGroups } from "@/lib/insights";
import styles from "./alerts-page.module.css";

export function AlertsPage() {
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
          transactionDateFrom: "2026-01-01",
          limit: 80,
        });

        if (!cancelled) {
          setTransactions(next);
        }
      } catch (nextError) {
        if (!cancelled) {
          setError(nextError instanceof Error ? nextError.message : "Unable to load alerts");
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

  const signals = useMemo(() => buildSignalGroups(transactions), [transactions]);
  const repeatedNames = useMemo(
    () => [...signals.buys, ...signals.sells].filter((item) => item.count > 1).slice(0, 3),
    [signals],
  );

  return (
    <ProductShell
      title="Alerts"
      subtitle="Alerts will become the fast-response layer of the product: unusual clusters, repeated buys, repeated sells, and sharper changes in disclosed activity."
    >
      <section className={styles.grid}>
        <article className={styles.card}>
          <p className={styles.sectionLabel}>Current posture</p>
          <h2 className={styles.cardTitle}>Alert surfacing is intentionally restrained until the logic is strong enough to trust.</h2>
          <p className={styles.cardText}>
            The page is ready to hold the alert engine, but the current focus is on reliable signals and a cleaner exploration workflow first.
          </p>
        </article>

        <article className={styles.card}>
          <p className={styles.sectionLabel}>Emerging names</p>
          <h2 className={styles.cardTitle}>Names that are appearing more than once in the current disclosure slice.</h2>

          {error ? <p className={styles.state}>{error}</p> : null}
          {loading ? <p className={styles.state}>Loading alert candidates…</p> : null}
          {!loading && !error && repeatedNames.length === 0 ? (
            <p className={styles.state}>No repeated names are standing out yet.</p>
          ) : null}

          {!loading && !error && repeatedNames.length > 0 ? (
            <div className={styles.alertList}>
              {repeatedNames.map((item) => (
                <div key={item.label} className={styles.alertRow}>
                  <strong>{item.label}</strong>
                  <span>{item.count} disclosures</span>
                </div>
              ))}
            </div>
          ) : null}
        </article>
      </section>
    </ProductShell>
  );
}
