from fastapi.testclient import TestClient
from main import app    
client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code in [200, 201]
    assert response.json() == {"message": "Welcome to the Product Management API"}