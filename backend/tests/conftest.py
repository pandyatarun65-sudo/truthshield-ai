import os
import sys
import tempfile
from pathlib import Path

_tmp = tempfile.mkdtemp()
os.environ.update(DATABASE_URL=f"sqlite:///{_tmp}/test.db", UPLOAD_DIR=f"{_tmp}/uploads", RATE_LIMIT_ENABLED="false",
                  SEED_ON_STARTUP="true", DEMO_MODE="true", JWT_SECRET="test-secret")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:  # runs startup: create tables + demo seed
        yield c


def login(client, email, password):
    r = client.post("/api/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture(scope="session")
def admin_h(client):
    return login(client, "admin@truthshield.demo", "Admin@12345")


@pytest.fixture(scope="session")
def user_h(client):
    r = client.post("/api/auth/register", json={"username": "tester", "email": "tester@truthshield.demo", "password": "Tester@1234"})
    assert r.status_code == 201, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}
