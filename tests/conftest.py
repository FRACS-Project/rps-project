# conftest.py
import pytest
import os
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlalchemy.pool import StaticPool

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "test-secret-key-not-for-production-0000"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"

from apps.api.main import app
from apps.api.db import get_session

@pytest.fixture
def test_db():
    """Crée une DB SQLite en mémoire pour chaque test"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )  # DB temporaire
    SQLModel.metadata.create_all(engine)          # Crée les tables
    
    with Session(engine) as session:
        yield session  # Donne la session au test
    
    # À la fin du test, tout est détruit (mémoire)


@pytest.fixture
def client(test_db):
    """Client HTTP pour tester les routes"""
    def override_get_session():
        yield test_db  # Remplace la vraie DB par la DB de test
    
    app.dependency_overrides[get_session] = override_get_session
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def registered_user_data():
    """Données utilisateur valides pour tests"""
    return {
        "name": "testuser",
        "mail": "test@example.com",
        "password": "TestPassword123!",
        "admin": False,
        "disabled": False
    }

@pytest.fixture
def mock_user_data():
    """Données utilisateur valides pour tests"""
    return {
        "name": "testuser2",
        "mail": "test2@example.com",
        "password": "TestPassword321!",
        "admin": False,
        "disabled": False
    }


@pytest.fixture
def registered_user(client, registered_user_data):
    return client.post("/auth/signup", json=registered_user_data).json()