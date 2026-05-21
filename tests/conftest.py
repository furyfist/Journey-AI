import pytest
from unittest.mock import AsyncMock, MagicMock

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
    return AsyncMock()


@pytest.fixture
def client(mock_db, mock_http):
    """
    FastAPI test client with mocked app state so tests never hit real services.
    Extend this fixture in integration tests as needed.
    """
    app.state.db = mock_db
    app.state.http = mock_http
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
