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
os.environ["ENVIRONMENT"] = "development"

from apps.api.config import settings
from apps.api.main import app
from apps.api.db import get_session

@pytest.fixture
def test_db():
    """Crée une DB SQLite en mémoire pour chaque test"""
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        yield session 


@pytest.fixture
def client(test_db):
    """Client HTTP pour tester les routes"""
    def override_get_session():
        yield test_db
    
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


@pytest.fixture
def user_token(client, registered_user, registered_user_data):
    return client.post(
        "/auth/login-json",
        json={"mail": registered_user_data["mail"], "password": registered_user_data["password"]}
    )

@pytest.fixture
def auth_headers(user_token):
    return {"Authorization": f"bearer {user_token.json()["access_token"]}"}

@pytest.fixture
def logged_user(client, auth_headers):
    return client.get(
        "/auth/me",
        headers=auth_headers
    )

@pytest.fixture
def new_recipe_data():
    return {
        "name": "Crêpes",
        "preparation_time": 10,
        "cooking_time": 20,
        "description": "Pâte à crêpes classique",
        "base_serving": 4,
        "tags": [
            {"new": True, "name": "dessert"},
            {"new": True, "name": "facile"},
        ],
        "ingredients": [
            {"new": True, "name": "farine", "quantity": 250, "unit": "g"},
            {"new": True, "name": "lait", "quantity": 50, "unit": "cl"},
            {"new": True, "name": "oeuf", "quantity": 4, "unit": "piece"},
        ],
        "instructions": [
            {"title": "Pâte", "details": "Mélanger la farine, les oeufs puis le lait."},
            {"title": "Cuisson", "details": "Cuire chaque crêpe une minute de chaque côté."},
        ],
    }

@pytest.fixture
def create_recipe(client, new_recipe_data, auth_headers):
    return client.post(
        "/recipe/me",
        json=new_recipe_data,
        headers=auth_headers
    )