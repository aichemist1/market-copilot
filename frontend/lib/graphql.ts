export type UserProfile = "basic" | "admin";

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

export type IngestionRun = {
  id: string;
  status: string;
  startedAt: string;
  completedAt: string | null;
  filesDiscoveredCount: number;
  recordsNormalizedCount: number;
  recordsPublishedCount: number;
  errorSummary: string | null;
};

export type DashboardPayload = {
  transactions: TransactionFeedItem[];
  ingestionRuns: IngestionRun[];
};

type DashboardParams = {
  profile: UserProfile;
  ticker?: string;
  reportingPerson?: string;
  transactionType?: string;
  assetType?: string;
  transactionDateFrom?: string;
  transactionDateTo?: string;
  limit?: number;
};

const dashboardQuery = `
  query DashboardData(
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
    adminIngestionRuns(limit: 6) {
      id
      status
      startedAt
      completedAt
      filesDiscoveredCount
      recordsNormalizedCount
      recordsPublishedCount
      errorSummary
    }
  }
`;

const consumerQuery = `
  query DashboardData(
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

export async function fetchDashboardData(params: DashboardParams): Promise<DashboardPayload> {
  const response = await fetch("/api/graphql", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-user-profile": params.profile,
    },
    body: JSON.stringify({
      query: params.profile === "admin" ? dashboardQuery : consumerQuery,
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
  });

  const payload = await response.json();

  if (!response.ok || payload.errors?.length) {
    const message = payload.errors?.[0]?.message ?? "GraphQL request failed";
    throw new Error(message);
  }

  return {
    transactions: payload.data.congressionalTransactions ?? [],
    ingestionRuns: payload.data.adminIngestionRuns ?? [],
  };
}
