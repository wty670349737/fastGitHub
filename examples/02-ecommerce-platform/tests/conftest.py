"""pytest 公共配置：必须在导入 app 之前设置好环境变量。"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

TEST_DB = Path(tempfile.gettempdir()) / "pyshop_test.db"
if TEST_DB.exists():
    TEST_DB.unlink()

os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB.as_posix()}"
os.environ["SECRET_KEY"] = "test-secret-key-not-for-production"
os.environ["ADMIN_EMAIL"] = "admin@example.com"
os.environ["ADMIN_PASSWORD"] = "admin123"

from sqlmodel import SQLModel  # noqa: E402

from app.database import engine  # noqa: E402
from app.main import create_app  # noqa: E402


@pytest.fixture(autouse=True)
def reset_db():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    yield


@pytest.fixture
def client(reset_db):
    with TestClient(create_app()) as test_client:
        yield test_client
