import pytest
from fastapi.testclient import TestClient

from app import database
from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "gastos_teste.db"
    monkeypatch.setattr(database, "DB_PATH", str(db_path))

    with TestClient(app) as test_client:
        yield test_client
