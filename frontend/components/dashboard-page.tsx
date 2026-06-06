"use client";

import { useEffect, useMemo, useState } from "react";
import { DisclosureList } from "@/components/disclosure-list";
import { ProductShell } from "@/components/product-shell";
import { TransactionFeedItem, fetchTransactions } from "@/lib/graphql";
import { buildSummary } from "@/lib/insights";
import styles from "./dashboard-page.module.css";

export function DashboardPage() {
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
          limit: 10,
        });

        if (!cancelled) {
          setTransactions(next);
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
  }, []);

  const summary = useMemo(() => buildSummary(transactions), [transactions]);
  return (
    <ProductShell
      title="A clearer view of current market disclosures."
      subtitle="Use the dashboard to stay oriented, then move into Trade Explorer or Signals when you want a sharper answer."
    >
      <section className={styles.summaryRow}>
        <SummaryCard label="Recent disclosures" value={summary.total.toString()} />
        <SummaryCard label="Buy actions" value={summary.purchases.toString()} />
        <SummaryCard label="Sell actions" value={summary.sales.toString()} />
        <SummaryCard label="Active members" value={summary.members.toString()} />
      </section>

      <section className={styles.mainSection}>
        <div className={styles.sectionHeader}>
          <div>
            <p className={styles.sectionLabel}>Recent disclosures</p>
            <h2 className={styles.sectionTitle}>A list-first view of the latest reportable activity.</h2>
          </div>
        </div>

        {error ? <p className={styles.state}>{error}</p> : null}
        {loading ? <p className={styles.state}>Loading disclosures…</p> : null}
        {!loading && !error && transactions.length === 0 ? (
          <p className={styles.state}>No disclosures are available yet.</p>
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
