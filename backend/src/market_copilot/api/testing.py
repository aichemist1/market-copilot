from __future__ import annotations

from fastapi.testclient import TestClient

from market_copilot.api.app import app


def build_test_client() -> TestClient:
    return TestClient(app)
