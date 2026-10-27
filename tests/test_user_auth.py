import os
import pytest
from jose import jwt
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

def test_signup(client):
    user_data = {
        "name": "testuser2",
        "mail": "test2@example.com",
        "password": "TestPassword123!",
    }

    # Act
    response = client.post("/auth/signup", json=user_data)
    data = response.json()

    # Assert
    assert response.status_code == 200, response.json()
    assert data["name"] == user_data["name"]
    assert data["mail"] == user_data["mail"]
    assert data["admin"] is False
    assert data["disabled"] is False
    assert data["id"]
    assert "password" not in data
    assert "hashed_password" not in data


def test_signup_cannot_create_admin(client):
    user_data = {
        "name": "testuser3",
        "mail": "test3@example.com",
        "password": "TestPassword123!",
        "admin": True
    }

    response = client.post("/auth/signup", json=user_data)
    data = response.json()

    assert response.status_code == 200, response.json()
    assert data["admin"] is False


@pytest.mark.parametrize("login", ["test@example.com", "testuser"])
@pytest.mark.usefixtures("registered_user")
def test_login(client, login): 
   
    response_login = client.post(
        "/auth/login-json",
        json={"mail": login, "password": "TestPassword123!"}
    )

    login_data = response_login.json()

    # response_me = client.post("/auth/me-json", login_data)

    assert response_login.status_code == 200, login_data

    
    payload = jwt.decode(login_data["access_token"], SECRET_KEY, algorithms=ALGORITHM)
    # print(payload)



@pytest.mark.parametrize("login, password", [
    ("testtest@example.com", "TestPassword123!"), 
    ("testtestuser", "TestPassword123!"),
    ("testuser", "TestPassword123")
])
@pytest.mark.usefixtures("registered_user")
def test_login_fail(client, login, password):

    response = client.post("/auth/login-json", json={"mail": login, "password": password})

    assert response.status_code == 401