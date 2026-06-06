import Link from "next/link";
import { DashboardDisclosureGroup, formatAssetType, formatDisplayDate } from "@/lib/insights";
import styles from "./dashboard-disclosure-list.module.css";

export function DashboardDisclosureList({
  groups,
}: {
  groups: DashboardDisclosureGroup[];
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

      {groups.map((group) => {
        const researchParams = new URLSearchParams({
          sourceRecordId: group.primarySourceRecordId,
          member: group.reportingPerson,
        });

        if (group.ticker) {
          researchParams.set("ticker", group.ticker);
        }

        const researchHref = `/research?${researchParams.toString()}`;

        return (
          <article key={group.key} className={styles.row}>
            <div className={styles.memberColumn}>
              <Link className={styles.memberLink} href={researchHref}>
                {group.reportingPerson}
              </Link>
            </div>

            <div className={styles.assetColumn}>
              <Link className={styles.tickerLink} href={researchHref}>
                {group.ticker ?? "No ticker"}
              </Link>
              <h3 className={styles.issuer}>{group.issuerName}</h3>
              <p className={styles.assetMeta}>
                {formatAssetType(group.assetType)}
                {group.lineItemCount > 1 ? ` · ${group.lineItemCount} trades` : ""}
              </p>
            </div>

            <div className={styles.centerColumn}>
              <span
                className={
                  group.transactionType === "purchase" ? styles.badgeBuy : styles.badgeSell
                }
              >
                {group.transactionType}
              </span>
            </div>

            <div className={styles.centerColumn}>
              <p className={styles.amount}>{group.amountRangeLabel}</p>
            </div>

            <div className={styles.centerColumn}>
              <p className={styles.metaStrong}>{formatDisplayDate(group.transactionDate)}</p>
            </div>
          </article>
        );
      })}
    </div>
  );
}
