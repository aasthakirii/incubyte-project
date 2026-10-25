import os
import tempfile
import pytest
from fastapi.testclient import TestClient

# Set the database before importing the application modules.
db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
db_file.close()
os.environ["DATABASE_URL"] = f"sqlite:///{db_file.name}"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-that-is-long-enough"

from app.database import Base, engine
from app.main import app

@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture()
def user_token(client):
    client.post("/api/auth/register", json={"email": "user@example.com", "password": "password123"})
    response = client.post("/api/auth/login", json={"email": "user@example.com", "password": "password123"})
    return response.json()["access_token"]

@pytest.fixture()
def admin_token(client):
    from app.database import SessionLocal
    from app.models import User
    from app.security import hash_password
    with SessionLocal() as db:
        db.add(User(email="admin@example.com", password_hash=hash_password("password123"), is_admin=True))
        db.commit()
    response = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "password123"})
    return response.json()["access_token"]

@pytest.fixture()
def vehicle_id(client, admin_token):
    response = client.post(
        "/api/vehicles",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"make": "Toyota", "model": "Corolla", "category": "Sedan", "price": 22000, "quantity": 2},
    )
    return response.json()["id"]
