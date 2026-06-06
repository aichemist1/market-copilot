"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { DisclosureList } from "@/components/disclosure-list";
import { ProductShell } from "@/components/product-shell";
import { CongressionalFilingRecord, TransactionFeedItem, fetchFiling, fetchTransactions } from "@/lib/graphql";
import { buildSummary, formatDisplayDate } from "@/lib/insights";
import styles from "./research-page.module.css";

export function ResearchPage() {
  const searchParams = useSearchParams();
  const from = searchParams.get("from") ?? "";
  const sourceRecordId = searchParams.get("sourceRecordId") ?? "";
  const ticker = searchParams.get("ticker") ?? "";
  const member = searchParams.get("member") ?? "";
  const [filing, setFiling] = useState<CongressionalFilingRecord | null>(null);
  const [transactions, setTransactions] = useState<TransactionFeedItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);

      try {
        const [nextFiling, nextTransactions] = await Promise.all([
          sourceRecordId ? fetchFiling(sourceRecordId) : Promise.resolve(null),
          fetchTransactions({
            reportingPerson: member || undefined,
            transactionDateFrom: "2026-01-01",
            limit: 50,
          }),
        ]);

        if (!cancelled) {
          setFiling(nextFiling);
          setTransactions(nextTransactions);
        }
      } catch (nextError) {
        if (!cancelled) {
          setError(nextError instanceof Error ? nextError.message : "Unable to load research");
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
  }, [member, sourceRecordId, ticker]);

  const summary = useMemo(() => buildSummary(transactions), [transactions]);
  const sameMemberOtherTrades = useMemo(() => {
    return transactions.filter((transaction) => transaction.sourceRecordId !== sourceRecordId);
  }, [sourceRecordId, transactions]);
  const sameTickerByMember = useMemo(() => {
    if (!ticker) {
      return [];
    }

    return transactions.filter(
      (transaction) =>
        transaction.ticker === ticker && transaction.sourceRecordId !== sourceRecordId,
    );
  }, [sourceRecordId, ticker, transactions]);
  const descriptor = ticker ? `${member || "Member"} · ${ticker}` : member || "Research";
  const focalTradeCount = filing?.transactions.length ?? 0;
  const focalSummary = buildFocalSummary({
    filing,
    member,
    ticker,
  });
  const tradeExplorerHref = buildTradeExplorerHref(searchParams, { ticker, member });

  return (
    <ProductShell
      title="Research"
      subtitle="Start with the focal filing, then widen into related activity from the same filer or ticker."
    >
      <div className={styles.topActions}>
        {from === "trade-explorer" ? (
          <Link className={styles.backLink} href={tradeExplorerHref}>
            Back to Trade Explorer
          </Link>
        ) : null}
        <div className={styles.inlineActions}>
          {ticker ? (
            <Link className={styles.inlineLink} href={buildTickerExplorerHref(searchParams, ticker)}>
              View {ticker} in Trade Explorer
            </Link>
          ) : null}
          {member ? (
            <Link className={styles.inlineLink} href={buildMemberExplorerHref(searchParams, member)}>
              View {member} in Trade Explorer
            </Link>
          ) : null}
        </div>
      </div>

      <section className={styles.summaryRow}>
        <SummaryCard label="Focus" value={descriptor} />
        <SummaryCard label="Filing trades" value={focalTradeCount.toString()} />
        <SummaryCard label="Other filer trades" value={sameMemberOtherTrades.length.toString()} />
        <SummaryCard label="Purchases" value={summary.purchases.toString()} />
      </section>

      <section className={styles.panel}>
        <div className={styles.sectionHeader}>
          <div>
            <p className={styles.sectionLabel}>Research focus</p>
            <h2 className={styles.sectionTitle}>{descriptor}</h2>
            <p className={styles.sectionNote}>{focalSummary}</p>
          </div>
        </div>

        {error ? <p className={styles.state}>{error}</p> : null}
        {loading ? <p className={styles.state}>Loading research…</p> : null}
        {!loading && !error && !filing && transactions.length === 0 ? (
          <p className={styles.state}>No matching trades were found for this research view. Return to Trade Explorer and broaden the search.</p>
        ) : null}

        {!loading && !error && filing ? (
          <div className={styles.stack}>
            <section className={styles.subsection}>
              <div className={styles.subsectionHeader}>
                <div>
                  <p className={styles.subsectionLabel}>Focal filing</p>
                  <h3 className={styles.subsectionTitle}>
                    Filing {filing.sourceRecordId} · {formatDisplayDate(filing.filingDate)}
                  </h3>
                </div>
                <a
                  className={styles.sourceLink}
                  href={filing.sourceDocumentUrl}
                  rel="noreferrer"
                  target="_blank"
                >
                  Source filing
                </a>
              </div>
              <DisclosureList transactions={mapFilingTransactions(filing)} />
            </section>

            {sameTickerByMember.length > 0 ? (
              <section className={styles.subsection}>
                <div className={styles.subsectionHeader}>
                  <div>
                    <p className={styles.subsectionLabel}>Ticker view</p>
                    <h3 className={styles.subsectionTitle}>
                      Other {ticker} activity by {member}
                    </h3>
                  </div>
                </div>
                <DisclosureList transactions={sameTickerByMember} />
              </section>
            ) : null}

            {sameMemberOtherTrades.length > 0 ? (
              <section className={styles.subsection}>
                <div className={styles.subsectionHeader}>
                  <div>
                    <p className={styles.subsectionLabel}>Related activity</p>
                    <h3 className={styles.subsectionTitle}>Other recent trades by {member}</h3>
                  </div>
                </div>
                <DisclosureList transactions={sameMemberOtherTrades} />
              </section>
            ) : null}
          </div>
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

function mapFilingTransactions(filing: CongressionalFilingRecord): TransactionFeedItem[] {
  return filing.transactions.map((transaction) => ({
    sourceRecordId: filing.sourceRecordId,
    reportingPerson: filing.reportingPerson,
    districtOrState: filing.districtOrState,
    sourceDocumentUrl: filing.sourceDocumentUrl,
    transactionIndex: transaction.transactionIndex,
    issuerName: transaction.issuerName,
    ticker: transaction.ticker,
    assetType: transaction.assetType,
    transactionType: transaction.transactionType,
    transactionDate: transaction.transactionDate,
    notificationDate: transaction.notificationDate,
    amountRange: transaction.amountRange,
    ownerType: transaction.ownerType,
    subholding: null,
    capitalGainsOver200: null,
    commentary: transaction.commentary,
  }));
}

function buildFocalSummary({
  filing,
  member,
  ticker,
}: {
  filing: CongressionalFilingRecord | null;
  member: string;
  ticker: string;
}) {
  if (!filing) {
    return "Start with the filing-level context, then widen into the filer’s broader trading pattern.";
  }

  const otherTickerCount = new Set(
    filing.transactions
      .map((transaction) => transaction.ticker)
      .filter((value): value is string => Boolean(value) && value !== ticker),
  ).size;

  if (ticker) {
    return `${member} disclosed ${ticker} in filing ${filing.sourceRecordId}. This filing also includes ${otherTickerCount} other ticker${otherTickerCount === 1 ? "" : "s"}.`;
  }

  return `${member} disclosed ${filing.transactions.length} trade${filing.transactions.length === 1 ? "" : "s"} in filing ${filing.sourceRecordId}.`;
}

function buildTradeExplorerHref(
  searchParams: URLSearchParams,
  fallback: { ticker: string; member: string },
) {
  const params = new URLSearchParams();
  const tickerFilter = searchParams.get("tickerFilter") ?? fallback.ticker;
  const reportingPersonFilter = searchParams.get("reportingPersonFilter") ?? fallback.member;
  const transactionTypeFilter = searchParams.get("transactionTypeFilter") ?? "";
  const assetTypeFilter = searchParams.get("assetTypeFilter") ?? "";
  const transactionDateFromFilter = searchParams.get("transactionDateFromFilter") ?? "2026-01-01";
  const transactionDateToFilter = searchParams.get("transactionDateToFilter") ?? "";

  if (tickerFilter) params.set("ticker", tickerFilter);
  if (reportingPersonFilter) params.set("reportingPerson", reportingPersonFilter);
  if (transactionTypeFilter) params.set("transactionType", transactionTypeFilter);
  if (assetTypeFilter) params.set("assetType", assetTypeFilter);
  if (transactionDateFromFilter) params.set("transactionDateFrom", transactionDateFromFilter);
  if (transactionDateToFilter) params.set("transactionDateTo", transactionDateToFilter);

  const query = params.toString();
  return query ? `/trade-explorer?${query}` : "/trade-explorer";
}

function buildTickerExplorerHref(searchParams: URLSearchParams, ticker: string) {
  const params = new URLSearchParams();
  params.set("ticker", ticker);
  const transactionDateFromFilter = searchParams.get("transactionDateFromFilter") ?? "2026-01-01";
  const transactionDateToFilter = searchParams.get("transactionDateToFilter") ?? "";
  if (transactionDateFromFilter) params.set("transactionDateFrom", transactionDateFromFilter);
  if (transactionDateToFilter) params.set("transactionDateTo", transactionDateToFilter);
  return `/trade-explorer?${params.toString()}`;
}

function buildMemberExplorerHref(searchParams: URLSearchParams, member: string) {
  const params = new URLSearchParams();
  params.set("reportingPerson", member);
  const transactionDateFromFilter = searchParams.get("transactionDateFromFilter") ?? "2026-01-01";
  const transactionDateToFilter = searchParams.get("transactionDateToFilter") ?? "";
  if (transactionDateFromFilter) params.set("transactionDateFrom", transactionDateFromFilter);
  if (transactionDateToFilter) params.set("transactionDateTo", transactionDateToFilter);
  return `/trade-explorer?${params.toString()}`;
}
