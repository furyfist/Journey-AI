from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def mock_db():
    """Reusable mock for the Supabase AsyncClient."""
    db = MagicMock()
    db.table.return_value.select.return_value.limit.return_value.execute = AsyncMock(
        return_value=MagicMock(data=[])
    )
    return db


@pytest.fixture
def mock_http():
    """Reusable mock for the shared httpx.AsyncClient."""
    client = AsyncMock()
    client.aclose = AsyncMock()
    return client


@pytest.fixture
def client(mock_db, mock_http):
    """
    FastAPI test client. Patches lifespan startup so no real DB/HTTP connections
    are made — every test suite can run without credentials.
    """
    with (
        patch("app.main.create_db_client", AsyncMock(return_value=mock_db)),
        patch("app.main.build_async_client", return_value=mock_http),
    ):
        with TestClient(app, raise_server_exceptions=True) as c:
            yield c
