from __future__ import annotations

from datetime import date

from fastapi import Depends, Request
import strawberry
from strawberry.fastapi import GraphQLRouter
from graphql import GraphQLError

from market_copilot.api.graphql.context import GraphQLContext
from market_copilot.api.graphql.mappers import (
    map_filing,
    map_ingestion_run,
    map_transaction_feed_item,
    map_validation_result,
)
from market_copilot.api.graphql.resolvers import (
    get_dashboard_metrics,
    get_congressional_filing_by_source_record_id,
    list_congressional_filings,
    list_congressional_transactions,
    list_recent_ingestion_runs,
    list_transaction_anomalies,
    list_recent_validation_results,
    list_ticker_signals,
)
from market_copilot.api.graphql.types import (
    AdminTransactionAnomalyType,
    CongressionalFilingType,
    CongressionalTransactionFeedItemType,
    DashboardMetricsType,
    IngestionRunType,
    TickerSignalType,
    ValidationResultType,
)
from market_copilot.api.dependencies import get_db_session


def _require_admin(context: GraphQLContext) -> None:
    if context.user_profile != "admin":
        raise GraphQLError("admin access required")


@strawberry.type
class Query:
    @strawberry.field
    def dashboard_metrics(
        self,
        info: strawberry.Info[GraphQLContext, None],
        transaction_date_from: str | None = None,
        transaction_date_to: str | None = None,
    ) -> DashboardMetricsType:
        parsed_date_from = date.fromisoformat(transaction_date_from) if transaction_date_from else None
        parsed_date_to = date.fromisoformat(transaction_date_to) if transaction_date_to else None
        metrics = get_dashboard_metrics(
            info.context.db,
            transaction_date_from=parsed_date_from,
            transaction_date_to=parsed_date_to,
        )
        return DashboardMetricsType(**metrics)

    @strawberry.field
    def congressional_filings(
        self,
        info: strawberry.Info[GraphQLContext, None],
        ticker: str | None = None,
        reporting_person: str | None = None,
        limit: int = 50,
    ) -> list[CongressionalFilingType]:
        filings = list_congressional_filings(
            info.context.db,
            ticker=ticker,
            reporting_person=reporting_person,
            limit=limit,
        )
        return [map_filing(filing) for filing in filings]

    @strawberry.field
    def congressional_transactions(
        self,
        info: strawberry.Info[GraphQLContext, None],
        ticker: str | None = None,
        reporting_person: str | None = None,
        transaction_type: str | None = None,
        asset_type: str | None = None,
        transaction_date_from: str | None = None,
        transaction_date_to: str | None = None,
        limit: int = 50,
    ) -> list[CongressionalTransactionFeedItemType]:
        parsed_date_from = date.fromisoformat(transaction_date_from) if transaction_date_from else None
        parsed_date_to = date.fromisoformat(transaction_date_to) if transaction_date_to else None
        transactions = list_congressional_transactions(
            info.context.db,
            ticker=ticker,
            reporting_person=reporting_person,
            transaction_type=transaction_type,
            asset_type=asset_type,
            transaction_date_from=parsed_date_from,
            transaction_date_to=parsed_date_to,
            limit=limit,
        )
        return [map_transaction_feed_item(transaction) for transaction in transactions]

    @strawberry.field
    def ticker_signals(
        self,
        info: strawberry.Info[GraphQLContext, None],
        asset_type: str | None = None,
        transaction_date_from: str | None = None,
        transaction_date_to: str | None = None,
        limit: int = 25,
    ) -> list[TickerSignalType]:
        parsed_date_from = date.fromisoformat(transaction_date_from) if transaction_date_from else None
        parsed_date_to = date.fromisoformat(transaction_date_to) if transaction_date_to else None
        signals = list_ticker_signals(
            info.context.db,
            asset_type=asset_type,
            transaction_date_from=parsed_date_from,
            transaction_date_to=parsed_date_to,
            limit=limit,
        )
        return [TickerSignalType(**signal) for signal in signals]

    @strawberry.field
    def congressional_filing(
        self,
        info: strawberry.Info[GraphQLContext, None],
        source_record_id: str,
    ) -> CongressionalFilingType | None:
        filing = get_congressional_filing_by_source_record_id(
            info.context.db,
            source_record_id=source_record_id,
        )
        if filing is None:
            return None
        return map_filing(filing)

    @strawberry.field
    def admin_ingestion_runs(
        self,
        info: strawberry.Info[GraphQLContext, None],
        limit: int = 20,
    ) -> list[IngestionRunType]:
        _require_admin(info.context)
        runs = list_recent_ingestion_runs(info.context.db, limit=limit)
        return [map_ingestion_run(run) for run in runs]

    @strawberry.field
    def admin_validation_results(
        self,
        info: strawberry.Info[GraphQLContext, None],
        status: str | None = None,
        limit: int = 50,
    ) -> list[ValidationResultType]:
        _require_admin(info.context)
        results = list_recent_validation_results(
            info.context.db,
            status=status,
            limit=limit,
        )
        return [map_validation_result(result) for result in results]

    @strawberry.field
    def admin_transaction_anomalies(
        self,
        info: strawberry.Info[GraphQLContext, None],
        limit: int = 50,
    ) -> list[AdminTransactionAnomalyType]:
        _require_admin(info.context)
        anomalies = list_transaction_anomalies(info.context.db, limit=limit)
        return [AdminTransactionAnomalyType(**anomaly) for anomaly in anomalies]


schema = strawberry.Schema(query=Query)


async def build_context(
    request: Request,
    db=Depends(get_db_session),
) -> GraphQLContext:
    user_profile = request.headers.get("x-user-profile", "admin")
    return GraphQLContext(db=db, user_profile=user_profile)


graphql_router = GraphQLRouter(schema, context_getter=build_context)
