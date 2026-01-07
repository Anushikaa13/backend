import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_headers(client):
    response = client.post("/token", data={"username": "anu", "password": "anu"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}