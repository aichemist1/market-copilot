"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { DashboardDisclosureList } from "@/components/dashboard-disclosure-list";
import { ProductShell } from "@/components/product-shell";
import {
  DashboardMetrics,
  TransactionFeedItem,
  fetchDashboardMetrics,
  fetchTransactions,
} from "@/lib/graphql";
import { buildDashboardDisclosureGroups } from "@/lib/insights";
import styles from "./dashboard-page.module.css";

export function DashboardPage() {
  const [transactions, setTransactions] = useState<TransactionFeedItem[]>([]);
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);

      try {
        const [nextTransactions, nextMetrics] = await Promise.all([
          fetchTransactions({
            transactionDateFrom: "2026-01-01",
            limit: 10,
          }),
          fetchDashboardMetrics({
            transactionDateFrom: "2026-01-01",
          }),
        ]);

        if (!cancelled) {
          setTransactions(nextTransactions);
          setMetrics(nextMetrics);
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

  const groupedDisclosures = useMemo(
    () => buildDashboardDisclosureGroups(transactions),
    [transactions],
  );
  return (
    <ProductShell
      title="A clearer view of current market disclosures."
      subtitle="Use the dashboard to stay oriented, then move into Trade Explorer or Signals when you want a sharper answer."
    >
      <section className={styles.summaryRow}>
        <SummaryCard label="Published disclosures" value={(metrics?.disclosureCount ?? 0).toString()} />
        <SummaryCard label="Buy actions" value={(metrics?.buyCount ?? 0).toString()} />
        <SummaryCard label="Sell actions" value={(metrics?.sellCount ?? 0).toString()} />
        <SummaryCard label="Active members" value={(metrics?.filerCount ?? 0).toString()} />
      </section>

      <section className={styles.mainSection}>
        <div className={styles.sectionHeader}>
          <div>
            <p className={styles.sectionLabel}>Recent disclosures</p>
            <p className={styles.sectionNote}>
              Recent disclosed trades grouped into cleaner signal rows before you drill into research.
            </p>
          </div>
          <Link className={styles.sectionLink} href="/trade-explorer">
            View full disclosure stream
          </Link>
        </div>

        {error ? <p className={styles.state}>{error}</p> : null}
        {loading ? <p className={styles.state}>Loading disclosures…</p> : null}
        {!loading && !error && transactions.length === 0 ? (
          <p className={styles.state}>No disclosures are available yet.</p>
        ) : null}

        {!loading && !error && groupedDisclosures.length > 0 ? (
          <>
            <p className={styles.sampleNote}>
              Showing {groupedDisclosures.length} grouped disclosures from the latest 10 in-scope trades.
            </p>
            <DashboardDisclosureList groups={groupedDisclosures} />
          </>
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
