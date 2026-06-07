import { ResearchPage } from "@/components/research-page";

export default async function ResearchRoute({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const resolved = await searchParams;

  return (
    <ResearchPage
      params={{
        from: firstValue(resolved.from),
        sourceRecordId: firstValue(resolved.sourceRecordId),
        ticker: firstValue(resolved.ticker),
        member: firstValue(resolved.member),
        tickerFilter: firstValue(resolved.tickerFilter),
        reportingPersonFilter: firstValue(resolved.reportingPersonFilter),
        transactionTypeFilter: firstValue(resolved.transactionTypeFilter),
        assetTypeFilter: firstValue(resolved.assetTypeFilter),
        transactionDateFromFilter: firstValue(resolved.transactionDateFromFilter),
        transactionDateToFilter: firstValue(resolved.transactionDateToFilter),
      }}
    />
  );
}

function firstValue(value: string | string[] | undefined) {
  return Array.isArray(value) ? value[0] : value;
}
