import { TradeExplorerPage } from "@/components/trade-explorer-page";

export default async function TradeExplorerRoute({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const resolved = await searchParams;

  return (
    <TradeExplorerPage
      initialFilters={{
        ticker: firstValue(resolved.ticker),
        reportingPerson: firstValue(resolved.reportingPerson),
        transactionType: firstValue(resolved.transactionType),
        assetType: firstValue(resolved.assetType),
        transactionDateFrom: firstValue(resolved.transactionDateFrom),
        transactionDateTo: firstValue(resolved.transactionDateTo),
      }}
    />
  );
}

function firstValue(value: string | string[] | undefined) {
  return Array.isArray(value) ? value[0] : value;
}
