export type TransactionFeedItem = {
  sourceRecordId: string;
  reportingPerson: string;
  districtOrState: string | null;
  sourceDocumentUrl: string;
  transactionIndex: number;
  issuerName: string;
  ticker: string | null;
  assetType: string | null;
  transactionType: string;
  transactionDate: string | null;
  notificationDate: string | null;
  amountRange: string | null;
  ownerType: string | null;
  subholding: string | null;
  capitalGainsOver200: boolean | null;
  commentary: string | null;
};

export type TickerSignal = {
  rank: number;
  ticker: string;
  issuerName: string | null;
  buyCount: number;
  sellCount: number;
  filerCount: number;
  latestTransactionDate: string | null;
  latestFilingDate: string | null;
};

export type DashboardMetrics = {
  disclosureCount: number;
  buyCount: number;
  sellCount: number;
  filerCount: number;
};

export type FilingTransaction = {
  transactionIndex: number;
  issuerName: string;
  ticker: string | null;
  assetType: string | null;
  transactionType: string;
  transactionDate: string | null;
  notificationDate: string | null;
  amountRange: string | null;
  ownerType: string | null;
  commentary: string | null;
};

export type CongressionalFilingRecord = {
  sourceRecordId: string;
  filingDate: string | null;
  filingType: string;
  reportingPerson: string;
  districtOrState: string | null;
  sourceDocumentUrl: string;
  transactions: FilingTransaction[];
};

export type TransactionQueryParams = {
  ticker?: string;
  reportingPerson?: string;
  transactionType?: string;
  assetType?: string;
  transactionDateFrom?: string;
  transactionDateTo?: string;
  limit?: number;
};

export type TickerSignalQueryParams = {
  assetType?: string;
  transactionDateFrom?: string;
  transactionDateTo?: string;
  limit?: number;
};

const transactionsQuery = `
  query TransactionFeed(
    $ticker: String
    $reportingPerson: String
    $transactionType: String
    $assetType: String
    $transactionDateFrom: String
    $transactionDateTo: String
    $limit: Int!
  ) {
    congressionalTransactions(
      ticker: $ticker
      reportingPerson: $reportingPerson
      transactionType: $transactionType
      assetType: $assetType
      transactionDateFrom: $transactionDateFrom
      transactionDateTo: $transactionDateTo
      limit: $limit
    ) {
      sourceRecordId
      reportingPerson
      districtOrState
      sourceDocumentUrl
      transactionIndex
      issuerName
      ticker
      assetType
      transactionType
      transactionDate
      notificationDate
      amountRange
      ownerType
      subholding
      capitalGainsOver200
      commentary
    }
  }
`;

const tickerSignalsQuery = `
  query TickerSignals(
    $assetType: String
    $transactionDateFrom: String
    $transactionDateTo: String
    $limit: Int!
  ) {
    tickerSignals(
      assetType: $assetType
      transactionDateFrom: $transactionDateFrom
      transactionDateTo: $transactionDateTo
      limit: $limit
    ) {
      rank
      ticker
      issuerName
      buyCount
      sellCount
      filerCount
      latestTransactionDate
      latestFilingDate
    }
  }
`;

const filingQuery = `
  query FilingDetail($sourceRecordId: String!) {
    congressionalFiling(sourceRecordId: $sourceRecordId) {
      sourceRecordId
      filingDate
      filingType
      reportingPerson
      districtOrState
      sourceDocumentUrl
      transactions {
        transactionIndex
        issuerName
        ticker
        assetType
        transactionType
        transactionDate
        notificationDate
        amountRange
        ownerType
        commentary
      }
    }
  }
`;

const dashboardMetricsQuery = `
  query DashboardMetrics(
    $transactionDateFrom: String
    $transactionDateTo: String
  ) {
    dashboardMetrics(
      transactionDateFrom: $transactionDateFrom
      transactionDateTo: $transactionDateTo
    ) {
      disclosureCount
      buyCount
      sellCount
      filerCount
    }
  }
`;

export async function fetchTransactions(
  params: TransactionQueryParams,
): Promise<TransactionFeedItem[]> {
  const response = await fetch("/api/graphql", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-user-profile": "basic",
    },
    body: JSON.stringify({
      query: transactionsQuery,
      variables: {
        ticker: params.ticker || null,
        reportingPerson: params.reportingPerson || null,
        transactionType: params.transactionType || null,
        assetType: params.assetType || null,
        transactionDateFrom: params.transactionDateFrom || null,
        transactionDateTo: params.transactionDateTo || null,
        limit: params.limit ?? 24,
      },
    }),
    cache: "no-store",
  });

  const payload = await response.json();

  if (!response.ok || payload.errors?.length) {
    const message = payload.errors?.[0]?.message ?? "GraphQL request failed";
    throw new Error(message);
  }

  return payload.data.congressionalTransactions ?? [];
}

export async function fetchTickerSignals(
  params: TickerSignalQueryParams,
): Promise<TickerSignal[]> {
  const response = await fetch("/api/graphql", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-user-profile": "basic",
    },
    body: JSON.stringify({
      query: tickerSignalsQuery,
      variables: {
        assetType: params.assetType || null,
        transactionDateFrom: params.transactionDateFrom || null,
        transactionDateTo: params.transactionDateTo || null,
        limit: params.limit ?? 25,
      },
    }),
    cache: "no-store",
  });

  const payload = await response.json();

  if (!response.ok || payload.errors?.length) {
    const message = payload.errors?.[0]?.message ?? "GraphQL request failed";
    throw new Error(message);
  }

  return payload.data.tickerSignals ?? [];
}

export async function fetchFiling(
  sourceRecordId: string,
): Promise<CongressionalFilingRecord | null> {
  const response = await fetch("/api/graphql", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-user-profile": "basic",
    },
    body: JSON.stringify({
      query: filingQuery,
      variables: {
        sourceRecordId,
      },
    }),
    cache: "no-store",
  });

  const payload = await response.json();

  if (!response.ok || payload.errors?.length) {
    const message = payload.errors?.[0]?.message ?? "GraphQL request failed";
    throw new Error(message);
  }

  return payload.data.congressionalFiling ?? null;
}

export async function fetchDashboardMetrics(params: {
  transactionDateFrom?: string;
  transactionDateTo?: string;
}): Promise<DashboardMetrics> {
  const response = await fetch("/api/graphql", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-user-profile": "basic",
    },
    body: JSON.stringify({
      query: dashboardMetricsQuery,
      variables: {
        transactionDateFrom: params.transactionDateFrom || null,
        transactionDateTo: params.transactionDateTo || null,
      },
    }),
    cache: "no-store",
  });

  const payload = await response.json();

  if (!response.ok || payload.errors?.length) {
    const message = payload.errors?.[0]?.message ?? "GraphQL request failed";
    throw new Error(message);
  }

  return payload.data.dashboardMetrics;
}
