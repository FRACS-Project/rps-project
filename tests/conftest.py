# conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from back.auth import crud
from back.main import app
from back.db.database import get_session

@pytest.fixture
def test_db():
    """Crée une DB SQLite en mémoire pour chaque test"""
    engine = create_engine("sqlite:///:memory:")  # DB temporaire
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
    return TestClient(app)

@pytest.fixture
def mock_user_data():
    """Données utilisateur valides pour tests"""
    return {
        "name": "testuser",
        "mail": "test@example.com",
        "password": "TestPassword123",
        "admin": False,
        "disabled": False
    }
