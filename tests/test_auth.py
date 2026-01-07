def test_login_invalid_user(client):
    response = client.post("/token", data={"username": "nonexistent", "password": "wrongpass"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}