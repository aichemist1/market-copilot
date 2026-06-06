"use client";

import { useEffect, useState } from "react";
import { ProductShell } from "@/components/product-shell";
import {
  AdminTransactionAnomaly,
  AdminValidationResult,
  fetchAdminTransactionAnomalies,
  fetchAdminValidationResults,
} from "@/lib/graphql";
import { formatDisplayDate } from "@/lib/insights";
import styles from "./admin-review-page.module.css";

export function AdminReviewPage() {
  const [anomalies, setAnomalies] = useState<AdminTransactionAnomaly[]>([]);
  const [validations, setValidations] = useState<AdminValidationResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);

      try {
        const [nextAnomalies, nextValidations] = await Promise.all([
          fetchAdminTransactionAnomalies({ limit: 25 }),
          fetchAdminValidationResults({ status: "failed", limit: 25 }),
        ]);

        if (!cancelled) {
          setAnomalies(nextAnomalies);
          setValidations(nextValidations);
        }
      } catch (nextError) {
        if (!cancelled) {
          setError(nextError instanceof Error ? nextError.message : "Unable to load review queue");
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
      title="Review Queue"
      subtitle="Admin-only review surface for anomalies and failed validations that should not quietly leak into the product dataset."
      compactHero
    >
      <section className={styles.grid}>
        <article className={styles.card}>
          <div className={styles.cardHeader}>
            <div>
              <p className={styles.sectionLabel}>Transaction anomalies</p>
              <h2 className={styles.cardTitle}>Future-dated or suspicious trades that require source review.</h2>
            </div>
            <p className={styles.count}>{anomalies.length}</p>
          </div>

          {error ? <p className={styles.state}>{error}</p> : null}
          {loading ? <p className={styles.state}>Loading anomalies…</p> : null}
          {!loading && !error && anomalies.length === 0 ? (
            <p className={styles.state}>No transaction anomalies are currently queued.</p>
          ) : null}

          {!loading && !error && anomalies.length > 0 ? (
            <div className={styles.stack}>
              {anomalies.map((anomaly) => (
                <article
                  key={`${anomaly.sourceRecordId}-${anomaly.transactionIndex}-${anomaly.anomalyCode}`}
                  className={styles.row}
                >
                  <div className={styles.rowTop}>
                    <div>
                      <strong>{anomaly.reportingPerson}</strong>
                      <p className={styles.meta}>
                        {anomaly.ticker ?? "No ticker"} · {anomaly.transactionType} · {anomaly.amountRange ?? "Unknown amount"}
                      </p>
                    </div>
                    <span className={styles.badge}>{anomaly.anomalyCode}</span>
                  </div>
                  <p className={styles.message}>{anomaly.anomalyMessage}</p>
                  <div className={styles.rowBottom}>
                    <span>Trade: {formatDisplayDate(anomaly.transactionDate)}</span>
                    <span>Notify: {formatDisplayDate(anomaly.notificationDate)}</span>
                    <a href={anomaly.sourceDocumentUrl} rel="noreferrer" target="_blank">
                      Source filing
                    </a>
                  </div>
                </article>
              ))}
            </div>
          ) : null}
        </article>

        <article className={styles.card}>
          <div className={styles.cardHeader}>
            <div>
              <p className={styles.sectionLabel}>Failed validations</p>
              <h2 className={styles.cardTitle}>Recent normalization outputs that did not satisfy the publishable contract.</h2>
            </div>
            <p className={styles.count}>{validations.length}</p>
          </div>

          {error ? <p className={styles.state}>{error}</p> : null}
          {loading ? <p className={styles.state}>Loading validation failures…</p> : null}
          {!loading && !error && validations.length === 0 ? (
            <p className={styles.state}>No failed validation results are currently queued.</p>
          ) : null}

          {!loading && !error && validations.length > 0 ? (
            <div className={styles.stack}>
              {validations.map((result) => (
                <article key={`${result.sourceRecordId}-${result.validatedAt}`} className={styles.row}>
                  <div className={styles.rowTop}>
                    <div>
                      <strong>Source record {result.sourceRecordId}</strong>
                      <p className={styles.meta}>
                        {result.validationVersion} · {formatDisplayDate(result.validatedAt)}
                      </p>
                    </div>
                    <span className={styles.badge}>{result.status}</span>
                  </div>
                  <ul className={styles.errorList}>
                    {result.errors.slice(0, 3).map((entry) => (
                      <li key={`${entry.code}-${entry.path}`}>{entry.message}</li>
                    ))}
                  </ul>
                </article>
              ))}
            </div>
          ) : null}
        </article>
      </section>
    </ProductShell>
  );
}
