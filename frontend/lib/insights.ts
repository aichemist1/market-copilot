import { TransactionFeedItem } from "@/lib/graphql";

export type DashboardDisclosureGroup = {
  key: string;
  primarySourceRecordId: string;
  reportingPerson: string;
  districtOrState: string | null;
  ticker: string | null;
  issuerName: string;
  assetType: string | null;
  transactionType: string;
  transactionDate: string | null;
  amountRangeLabel: string;
  lineItemCount: number;
  transactions: TransactionFeedItem[];
};

export function buildSummary(transactions: TransactionFeedItem[]) {
  return {
    total: transactions.length,
    purchases: transactions.filter((item) => item.transactionType === "purchase").length,
    sales: transactions.filter((item) => item.transactionType === "sale").length,
    members: new Set(transactions.map((item) => item.reportingPerson)).size,
  };
}

export function buildSignalGroups(transactions: TransactionFeedItem[]) {
  const buyMap = new Map<string, number>();
  const sellMap = new Map<string, number>();

  for (const transaction of transactions) {
    const key = transaction.ticker ?? transaction.issuerName;

    if (transaction.transactionType === "purchase") {
      buyMap.set(key, (buyMap.get(key) ?? 0) + 1);
    }

    if (transaction.transactionType === "sale") {
      sellMap.set(key, (sellMap.get(key) ?? 0) + 1);
    }
  }

  return {
    buys: mapToSortedSignals(buyMap),
    sells: mapToSortedSignals(sellMap),
  };
}

export function formatAssetType(value: string | null) {
  if (!value) {
    return "Unknown asset";
  }

  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export function formatOwnerType(value: string) {
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export function formatDisplayDate(value: string | null) {
  if (!value) {
    return "Unknown date";
  }

  return value;
}

export function buildDashboardDisclosureGroups(
  transactions: TransactionFeedItem[],
): DashboardDisclosureGroup[] {
  const groups = new Map<string, DashboardDisclosureGroup>();

  for (const transaction of transactions) {
    const key = [
      transaction.reportingPerson,
      transaction.ticker ?? transaction.issuerName,
      transaction.transactionType,
      transaction.transactionDate ?? "unknown-date",
    ].join("::");

    const existing = groups.get(key);
    if (!existing) {
      groups.set(key, {
        key,
        primarySourceRecordId: transaction.sourceRecordId,
        reportingPerson: transaction.reportingPerson,
        districtOrState: transaction.districtOrState,
        ticker: transaction.ticker,
        issuerName: transaction.issuerName,
        assetType: transaction.assetType,
        transactionType: transaction.transactionType,
        transactionDate: transaction.transactionDate,
        amountRangeLabel: transaction.amountRange ?? "Undisclosed range",
        lineItemCount: 1,
        transactions: [transaction],
      });
      continue;
    }

    existing.transactions.push(transaction);
    existing.lineItemCount += 1;
    existing.amountRangeLabel = buildAmountSummary(existing.transactions);
  }

  return Array.from(groups.values()).sort((left, right) => {
    const leftDate = left.transactionDate ?? "";
    const rightDate = right.transactionDate ?? "";
    return rightDate.localeCompare(leftDate);
  });
}

function buildAmountSummary(transactions: TransactionFeedItem[]) {
  const uniqueRanges = Array.from(
    new Set(transactions.map((transaction) => transaction.amountRange ?? "Undisclosed range")),
  );

  if (uniqueRanges.length === 1) {
    return uniqueRanges[0];
  }

  return `${transactions.length} disclosed trades`;
}

function mapToSortedSignals(source: Map<string, number>) {
  return Array.from(source.entries())
    .map(([label, count]) => ({ label, count }))
    .sort((left, right) => right.count - left.count || left.label.localeCompare(right.label))
    .slice(0, 5);
}
