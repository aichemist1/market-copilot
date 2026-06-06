import { TransactionFeedItem } from "@/lib/graphql";

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

function mapToSortedSignals(source: Map<string, number>) {
  return Array.from(source.entries())
    .map(([label, count]) => ({ label, count }))
    .sort((left, right) => right.count - left.count || left.label.localeCompare(right.label))
    .slice(0, 5);
}
