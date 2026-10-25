def test_register_and_login(client):
    registered = client.post("/api/auth/register", json={"email": "test@example.com", "password": "password123"})
    assert registered.status_code == 201
    assert registered.json()["email"] == "test@example.com"
    assert "password_hash" not in registered.json()

    logged_in = client.post("/api/auth/login", json={"email": "test@example.com", "password": "password123"})
    assert logged_in.status_code == 200
    assert logged_in.json()["token_type"] == "bearer"
    assert logged_in.json()["access_token"]

def test_duplicate_registration_is_rejected(client):
    payload = {"email": "same@example.com", "password": "password123"}
    assert client.post("/api/auth/register", json=payload).status_code == 201
    assert client.post("/api/auth/register", json=payload).status_code == 409

def test_bad_password_is_rejected(client):
    assert client.post("/api/auth/register", json={"email": "bad@example.com", "password": "short"}).status_code == 422
    assert client.post("/api/auth/login", json={"email": "missing@example.com", "password": "wrong"}).status_code == 401
