from fastapi import FastAPI

from market_copilot.api.auth import router as auth_router
from market_copilot.api.graphql.schema import graphql_router

app = FastAPI(title="Market Copilot API", version="0.1.0")
app.include_router(auth_router)
app.include_router(graphql_router, prefix="/graphql")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
