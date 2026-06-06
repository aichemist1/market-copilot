import Link from "next/link";
import { TransactionFeedItem } from "@/lib/graphql";
import { formatAssetType, formatDisplayDate } from "@/lib/insights";
import styles from "./disclosure-list.module.css";

export function DisclosureList({
  transactions,
  linkToResearch = false,
  researchContext,
}: {
  transactions: TransactionFeedItem[];
  linkToResearch?: boolean;
  researchContext?: Record<string, string>;
}) {
  return (
    <div className={styles.list}>
      <div className={styles.headerRow}>
        <span>Member</span>
        <span>Disclosure</span>
        <span>Action</span>
        <span>Amount</span>
        <span>Trade Date</span>
      </div>

      {transactions.map((transaction) => (
        <article key={`${transaction.sourceRecordId}-${transaction.transactionIndex}`} className={styles.row}>
          {(() => {
            const researchParams = new URLSearchParams({
              sourceRecordId: transaction.sourceRecordId,
              member: transaction.reportingPerson,
            });

            if (researchContext) {
              for (const [key, value] of Object.entries(researchContext)) {
                if (value) {
                  researchParams.set(key, value);
                }
              }
            }

            if (transaction.ticker) {
              researchParams.set("ticker", transaction.ticker);
            }

            const researchHref = `/research?${researchParams.toString()}`;
            const memberContent = linkToResearch ? (
              <Link className={styles.memberLink} href={researchHref}>
                {transaction.reportingPerson}
              </Link>
            ) : (
              <p className={styles.member}>{transaction.reportingPerson}</p>
            );
            const tickerContent = linkToResearch ? (
              <Link className={styles.tickerLink} href={researchHref}>
                {transaction.ticker ?? "No ticker"}
              </Link>
            ) : (
              <p className={styles.ticker}>{transaction.ticker ?? "No ticker"}</p>
            );

            return (
              <>
          <div className={styles.memberColumn}>
                {memberContent}
          </div>

          <div className={styles.assetColumn}>
                {tickerContent}
            <h3 className={styles.issuer}>{transaction.issuerName}</h3>
            <p className={styles.assetMeta}>{formatAssetType(transaction.assetType)}</p>
          </div>

          <div className={styles.centerColumn}>
            <span
              className={
                transaction.transactionType === "purchase" ? styles.badgeBuy : styles.badgeSell
              }
            >
              {transaction.transactionType}
            </span>
          </div>

          <div className={styles.centerColumn}>
            <p className={styles.amount}>{transaction.amountRange ?? "Undisclosed range"}</p>
          </div>

          <div className={styles.centerColumn}>
            <p className={styles.metaStrong}>{formatDisplayDate(transaction.transactionDate)}</p>
          </div>
              </>
            );
          })()}
        </article>
      ))}
    </div>
  );
}
