import { TransactionFeedItem } from "@/lib/graphql";
import { formatAssetType, formatDisplayDate, formatOwnerType } from "@/lib/insights";
import styles from "./disclosure-list.module.css";

export function DisclosureList({
  transactions,
}: {
  transactions: TransactionFeedItem[];
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
        <article
          key={`${transaction.sourceRecordId}-${transaction.transactionIndex}`}
          className={styles.row}
        >
          <div className={styles.memberColumn}>
            <p className={styles.member}>{transaction.reportingPerson}</p>
            <p className={styles.meta}>{transaction.districtOrState ?? "Unknown district"}</p>
            {transaction.ownerType ? (
              <span className={styles.ownerPill}>{formatOwnerType(transaction.ownerType)}</span>
            ) : null}
          </div>

          <div className={styles.assetColumn}>
            <p className={styles.ticker}>{transaction.ticker ?? "No ticker"}</p>
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

        </article>
      ))}
    </div>
  );
}
