import pytest

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
    assert data["admin"] is True


@pytest.mark.parametrize("login", ["test@example.com", "testuser"])
@pytest.mark.usefixtures("registered_user")
def test_login(client, login): 
   
    response = client.post("/auth/login-json", json={"mail": login, "password": "TestPassword123!"})
    data = response.json()

    print(data)

    assert response.status_code == 200, response.json()


@pytest.mark.parametrize("login, password", [
    ("testtest@example.com", "TestPassword123!"), 
    ("testtestuser", "TestPassword123!"),
    ("testuser", "TestPassword123")
])
@pytest.mark.usefixtures("registered_user")
def test_login_fail(client, login, password):

    response = client.post("/auth/login-json", json={"mail": login, "password": password})

    assert response.status_code == 401