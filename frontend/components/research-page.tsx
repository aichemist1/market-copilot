"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { DisclosureList } from "@/components/disclosure-list";
import { ProductShell } from "@/components/product-shell";
import { CongressionalFilingRecord, TransactionFeedItem, fetchFiling, fetchTransactions } from "@/lib/graphql";
import { buildSummary, formatAssetType, formatDisplayDate } from "@/lib/insights";
import styles from "./research-page.module.css";

type ResearchParams = {
  from?: string;
  sourceRecordId?: string;
  ticker?: string;
  member?: string;
  tickerFilter?: string;
  reportingPersonFilter?: string;
  transactionTypeFilter?: string;
  assetTypeFilter?: string;
  transactionDateFromFilter?: string;
  transactionDateToFilter?: string;
};

export function ResearchPage({ params }: { params: ResearchParams }) {
  const from = params.from ?? "";
  const sourceRecordId = params.sourceRecordId ?? "";
  const ticker = params.ticker ?? "";
  const member = params.member ?? "";
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
  const filingTickerList = useMemo(() => buildFilingTickerList(filing), [filing]);
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
  const focusLabel = member || "Research";
  const focalTradeCount = filing?.transactions.length ?? 0;
  const focalSummary = buildFocalSummary({
    filing,
    member,
    ticker,
  });
  const tradeExplorerHref = buildTradeExplorerHref(params, { ticker, member });

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
            <Link className={styles.inlineLink} href={buildTickerExplorerHref(params, ticker)}>
              View {ticker} in Trade Explorer
            </Link>
          ) : null}
          {member ? (
            <Link className={styles.inlineLink} href={buildMemberExplorerHref(params, member)}>
              View {member} in Trade Explorer
            </Link>
          ) : null}
        </div>
      </div>

      <section className={styles.summaryRow}>
        <SummaryCard label="Focus" value={focusLabel} />
        <SummaryCard label="Filing trades" value={focalTradeCount.toString()} />
        <SummaryCard label="Other filer trades" value={sameMemberOtherTrades.length.toString()} />
        <SummaryCard label="Purchases" value={summary.purchases.toString()} />
      </section>

      <section className={styles.panel}>
        <div className={styles.sectionHeader}>
          <div>
            <p className={styles.sectionLabel}>Research focus</p>
            <h2 className={styles.sectionTitle}>{focusLabel}</h2>
            <p className={styles.sectionNote}>{focalSummary}</p>
            {filingTickerList.length > 0 ? (
              <div className={styles.tickerChipRow}>
                {filingTickerList.map((value) => (
                  <span key={value} className={styles.tickerChip}>
                    {value}
                  </span>
                ))}
              </div>
            ) : null}
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
              <div className={styles.cardGrid}>
                {filing.transactions.map((transaction) => (
                  <ResearchTradeCard
                    key={`${filing.sourceRecordId}-${transaction.transactionIndex}`}
                    filingDate={filing.filingDate}
                    filingId={filing.sourceRecordId}
                    issuerName={transaction.issuerName}
                    ticker={transaction.ticker}
                    amountRange={transaction.amountRange}
                    assetType={transaction.assetType}
                    tradeDate={transaction.transactionDate}
                    transactionType={transaction.transactionType}
                  />
                ))}
              </div>
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

  const filingTickers = Array.from(
    new Set(
      filing.transactions
        .map((transaction) => transaction.ticker)
        .filter((value): value is string => Boolean(value)),
    ),
  );
  const otherTickerCount = new Set(
    filing.transactions
      .map((transaction) => transaction.ticker)
      .filter((value): value is string => Boolean(value) && value !== ticker),
  ).size;

  if (ticker && filingTickers.length > 1) {
    return `${member} filed ${filing.transactions.length} trades in filing ${filing.sourceRecordId}. This filing includes ${filingTickers.join(", ")}.`;
  }

  if (ticker && filingTickers.length === 1) {
    return `${member} disclosed ${ticker} in filing ${filing.sourceRecordId}.`;
  }

  return `${member} disclosed ${filing.transactions.length} trade${filing.transactions.length === 1 ? "" : "s"} in filing ${filing.sourceRecordId}.`;
}

function buildFilingTickerList(filing: CongressionalFilingRecord | null) {
  if (!filing) {
    return [];
  }

  return Array.from(
    new Set(
      filing.transactions
        .map((transaction) => transaction.ticker)
        .filter((value): value is string => Boolean(value)),
    ),
  );
}

function buildTradeExplorerHref(
  paramsSource: ResearchParams,
  fallback: { ticker: string; member: string },
) {
  const queryParams = new URLSearchParams();
  const tickerFilter = paramsSource.tickerFilter ?? fallback.ticker;
  const reportingPersonFilter = paramsSource.reportingPersonFilter ?? fallback.member;
  const transactionTypeFilter = paramsSource.transactionTypeFilter ?? "";
  const assetTypeFilter = paramsSource.assetTypeFilter ?? "";
  const transactionDateFromFilter = paramsSource.transactionDateFromFilter ?? "2026-01-01";
  const transactionDateToFilter = paramsSource.transactionDateToFilter ?? "";

  if (tickerFilter) queryParams.set("ticker", tickerFilter);
  if (reportingPersonFilter) queryParams.set("reportingPerson", reportingPersonFilter);
  if (transactionTypeFilter) queryParams.set("transactionType", transactionTypeFilter);
  if (assetTypeFilter) queryParams.set("assetType", assetTypeFilter);
  if (transactionDateFromFilter) queryParams.set("transactionDateFrom", transactionDateFromFilter);
  if (transactionDateToFilter) queryParams.set("transactionDateTo", transactionDateToFilter);

  const query = queryParams.toString();
  return query ? `/trade-explorer?${query}` : "/trade-explorer";
}

function buildTickerExplorerHref(paramsSource: ResearchParams, ticker: string) {
  const params = new URLSearchParams();
  params.set("ticker", ticker);
  const transactionDateFromFilter = paramsSource.transactionDateFromFilter ?? "2026-01-01";
  const transactionDateToFilter = paramsSource.transactionDateToFilter ?? "";
  if (transactionDateFromFilter) params.set("transactionDateFrom", transactionDateFromFilter);
  if (transactionDateToFilter) params.set("transactionDateTo", transactionDateToFilter);
  return `/trade-explorer?${params.toString()}`;
}

function buildMemberExplorerHref(paramsSource: ResearchParams, member: string) {
  const params = new URLSearchParams();
  params.set("reportingPerson", member);
  const transactionDateFromFilter = paramsSource.transactionDateFromFilter ?? "2026-01-01";
  const transactionDateToFilter = paramsSource.transactionDateToFilter ?? "";
  if (transactionDateFromFilter) params.set("transactionDateFrom", transactionDateFromFilter);
  if (transactionDateToFilter) params.set("transactionDateTo", transactionDateToFilter);
  return `/trade-explorer?${params.toString()}`;
}

function ResearchTradeCard({
  transactionType,
  ticker,
  issuerName,
  amountRange,
  assetType,
  tradeDate,
  filingId,
  filingDate,
}: {
  transactionType: string;
  ticker: string | null;
  issuerName: string;
  amountRange: string | null;
  assetType: string | null;
  tradeDate: string | null;
  filingId: string;
  filingDate: string | null;
}) {
  const daysSinceTrade = buildDaysSinceTrade(tradeDate);

  return (
    <article className={styles.tradeCard}>
      <div className={styles.tradeCardTop}>
        <p className={styles.tradeCardKicker}>Focal trade</p>
        <span
          className={transactionType === "purchase" ? styles.actionBadgeBuy : styles.actionBadgeSell}
        >
          {transactionType}
        </span>
      </div>

      <div className={styles.tradeCardBody}>
        <div className={styles.tickerLine}>
          <span className={styles.tickerValue}>{ticker ?? "No ticker"}</span>
          <span className={styles.issuerInline}>{issuerName}</span>
        </div>
        <span className={styles.assetPill}>{assetType === "stock" ? "Equity" : formatAssetType(assetType)}</span>

        <div className={styles.metricGrid}>
          <MetricBlock label="Amount range" value={amountRange ?? "Undisclosed"} accent />
          <MetricBlock label="Trade date" value={formatDisplayDate(tradeDate)} />
          <MetricBlock label="Asset type" value={assetType === "stock" ? "Equity" : formatAssetType(assetType)} />
          <MetricBlock label="Days since trade" value={daysSinceTrade} />
        </div>
      </div>

      <div className={styles.tradeCardFooter}>
        <span>Filing</span>
        <span>
          {filingId} · {formatDisplayDate(filingDate)}
        </span>
      </div>
    </article>
  );
}

function MetricBlock({
  label,
  value,
  accent = false,
}: {
  label: string;
  value: string;
  accent?: boolean;
}) {
  return (
    <div className={styles.metricBlock}>
      <p className={styles.metricLabel}>{label}</p>
      <p className={accent ? styles.metricValueAccent : styles.metricValue}>{value}</p>
    </div>
  );
}

function buildDaysSinceTrade(value: string | null) {
  if (!value) {
    return "Unknown";
  }

  const tradeDate = new Date(`${value}T00:00:00Z`);
  const now = new Date();
  const diffMs = now.getTime() - tradeDate.getTime();
  const days = Math.max(0, Math.floor(diffMs / (1000 * 60 * 60 * 24)));
  return `${days} day${days === 1 ? "" : "s"}`;
}
