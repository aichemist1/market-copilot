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

export type SignalMetrics = {
  activeTickerCount: number;
  buyDisclosureCount: number;
  distinctFilerCount: number;
  latestFilingDate: string | null;
};

export type ValidationMessage = {
  code: string;
  message: string;
  path: string;
};

export type AdminValidationResult = {
  sourceRecordId: string;
  status: string;
  validationVersion: string;
  errors: ValidationMessage[];
  warnings: ValidationMessage[];
  validatedAt: string;
};

export type AdminTransactionAnomaly = {
  sourceRecordId: string;
  reportingPerson: string;
  districtOrState: string | null;
  filingDate: string | null;
  transactionIndex: number;
  issuerName: string;
  ticker: string | null;
  transactionType: string;
  transactionDate: string | null;
  notificationDate: string | null;
  amountRange: string | null;
  sourceDocumentUrl: string;
  anomalyCode: string;
  anomalyMessage: string;
};

export type AdminInviteCode = {
  code: string;
  status: string;
  expires_at: string | null;
  used_at: string | null;
  created_at: string;
  created_by_email: string | null;
  used_by_email: string | null;
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

const signalMetricsQuery = `
  query SignalMetrics(
    $assetType: String
    $transactionDateFrom: String
    $transactionDateTo: String
  ) {
    signalMetrics(
      assetType: $assetType
      transactionDateFrom: $transactionDateFrom
      transactionDateTo: $transactionDateTo
    ) {
      activeTickerCount
      buyDisclosureCount
      distinctFilerCount
      latestFilingDate
    }
  }
`;

const adminValidationResultsQuery = `
  query AdminValidationResults($status: String, $limit: Int!) {
    adminValidationResults(status: $status, limit: $limit) {
      sourceRecordId
      status
      validationVersion
      validatedAt
      errors {
        code
        message
        path
      }
      warnings {
        code
        message
        path
      }
    }
  }
`;

const adminTransactionAnomaliesQuery = `
  query AdminTransactionAnomalies($limit: Int!) {
    adminTransactionAnomalies(limit: $limit) {
      sourceRecordId
      reportingPerson
      districtOrState
      filingDate
      transactionIndex
      issuerName
      ticker
      transactionType
      transactionDate
      notificationDate
      amountRange
      sourceDocumentUrl
      anomalyCode
      anomalyMessage
    }
  }
`;

async function postGraphQL<T>({
  query,
  variables,
}: {
  query: string;
  variables: Record<string, unknown>;
}): Promise<T> {
  const response = await fetch("/api/graphql", {
    method: "POST",
    headers: {
      "content-type": "application/json",
    },
    body: JSON.stringify({
      query,
      variables,
    }),
    cache: "no-store",
  });

  const payload = await response.json();

  if (!response.ok || payload.errors?.length) {
    const message = payload.errors?.[0]?.message ?? "GraphQL request failed";
    throw new Error(message);
  }

  return payload.data as T;
}

export async function fetchTransactions(
  params: TransactionQueryParams,
): Promise<TransactionFeedItem[]> {
  const data = await postGraphQL<{ congressionalTransactions: TransactionFeedItem[] }>({
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
  });

  return data.congressionalTransactions ?? [];
}

export async function fetchTickerSignals(
  params: TickerSignalQueryParams,
): Promise<TickerSignal[]> {
  const data = await postGraphQL<{ tickerSignals: TickerSignal[] }>({
    query: tickerSignalsQuery,
    variables: {
      assetType: params.assetType || null,
      transactionDateFrom: params.transactionDateFrom || null,
      transactionDateTo: params.transactionDateTo || null,
      limit: params.limit ?? 25,
    },
  });

  return data.tickerSignals ?? [];
}

export async function fetchFiling(
  sourceRecordId: string,
): Promise<CongressionalFilingRecord | null> {
  const data = await postGraphQL<{ congressionalFiling: CongressionalFilingRecord | null }>({
    query: filingQuery,
    variables: {
      sourceRecordId,
    },
  });

  return data.congressionalFiling ?? null;
}

export async function fetchDashboardMetrics(params: {
  transactionDateFrom?: string;
  transactionDateTo?: string;
}): Promise<DashboardMetrics> {
  const data = await postGraphQL<{ dashboardMetrics: DashboardMetrics }>({
    query: dashboardMetricsQuery,
    variables: {
      transactionDateFrom: params.transactionDateFrom || null,
      transactionDateTo: params.transactionDateTo || null,
    },
  });

  return data.dashboardMetrics;
}

export async function fetchSignalMetrics(params: {
  assetType?: string;
  transactionDateFrom?: string;
  transactionDateTo?: string;
}): Promise<SignalMetrics> {
  const data = await postGraphQL<{ signalMetrics: SignalMetrics }>({
    query: signalMetricsQuery,
    variables: {
      assetType: params.assetType || null,
      transactionDateFrom: params.transactionDateFrom || null,
      transactionDateTo: params.transactionDateTo || null,
    },
  });

  return data.signalMetrics;
}

export async function fetchAdminValidationResults(params: {
  status?: string;
  limit?: number;
}): Promise<AdminValidationResult[]> {
  const data = await postGraphQL<{ adminValidationResults: AdminValidationResult[] }>({
    query: adminValidationResultsQuery,
    variables: {
      status: params.status || null,
      limit: params.limit ?? 25,
    },
  });

  return data.adminValidationResults ?? [];
}

export async function fetchAdminTransactionAnomalies(params: {
  limit?: number;
}): Promise<AdminTransactionAnomaly[]> {
  const data = await postGraphQL<{ adminTransactionAnomalies: AdminTransactionAnomaly[] }>({
    query: adminTransactionAnomaliesQuery,
    variables: {
      limit: params.limit ?? 25,
    },
  });

  return data.adminTransactionAnomalies ?? [];
}

export async function fetchAdminInviteCodes(): Promise<AdminInviteCode[]> {
  const response = await fetch("/api/admin/invite-codes", {
    cache: "no-store",
  });
  const payload = (await response.json()) as {
    error?: string;
    inviteCodes?: AdminInviteCode[];
  };

  if (!response.ok) {
    throw new Error(payload.error ?? "Unable to load invite codes");
  }

  return payload.inviteCodes ?? [];
}

export async function createAdminInviteCode(params: {
  expiresDays?: number;
  code?: string;
}): Promise<AdminInviteCode> {
  const response = await fetch("/api/admin/invite-codes", {
    method: "POST",
    headers: {
      "content-type": "application/json",
    },
    body: JSON.stringify({
      expiresDays: params.expiresDays ?? 14,
      code: params.code ?? "",
    }),
  });
  const payload = (await response.json()) as {
    error?: string;
    inviteCode?: AdminInviteCode;
  };

  if (!response.ok || !payload.inviteCode) {
    throw new Error(payload.error ?? "Unable to create invite code");
  }

  return payload.inviteCode;
}
