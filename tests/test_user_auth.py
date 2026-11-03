import pytest
from jose import jwt
import datetime as dt
from apps.api.config import settings

def test_signup(client, mock_user_data):

    # Act
    response = client.post("/auth/signup", json=mock_user_data)

    # Assert
    assert response.status_code == 200, response.json()
    assert response.json()["name"] == mock_user_data["name"]
    assert response.json()["mail"] == mock_user_data["mail"]
    assert response.json()["admin"] is False
    assert response.json()["disabled"] is False
    assert response.json()["id"]
    assert "password" not in response.json()
    assert "hashed_password" not in response.json()


def test_signup_cannot_create_admin(client):
    user_data = {
        "name": "testuser3",
        "mail": "test3@example.com",
        "password": "TestPassword123!",
        "admin": True
    }

    response = client.post("/auth/signup", json=user_data)

    assert response.status_code == 200, response.json()
    assert response.json()["admin"] is False


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

    
    payload = jwt.decode(
        login_data["access_token"],
        settings.secret_key,
        algorithms=settings.algorithm
    )
    print(payload["exp"])
    dt.timedelta(minutes=30, seconds=5)



@pytest.mark.parametrize("login, password", [
    ("testtest@example.com", "TestPassword123!"), 
    ("testtestuser", "TestPassword123!"),
    ("testuser", "TestPassword123")
])
@pytest.mark.usefixtures("registered_user")
def test_login_fail(client, login, password):

    response = client.post("/auth/login-json", json={"mail": login, "password": password})

    assert response.status_code == 401, response.json()