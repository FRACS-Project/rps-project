
def test_create_bookmark(client, create_recipe, auth_headers):

    recipe_id = create_recipe.json()["id"]
    response = client.post(
        "/bookmark/me",
        json={"recipe_id": recipe_id},
        headers=auth_headers
    )
    bookmark = client.get(
        f"/bookmark/me/{recipe_id}",
        headers=auth_headers
    )

    assert response.status_code == 200, response.json()
    assert response.json()["id"] ==  recipe_id, response.json()
    assert bookmark.status_code == 200, bookmark.json()
    assert bookmark.json() == create_recipe.json()


def test_create_bookmark_twice_409(client, create_recipe, auth_headers):
    recipe_id = create_recipe.json()["id"]
    
    client.post(
        "/bookmark/me",
        json={"recipe_id": recipe_id},
        headers=auth_headers
    )
    response = client.post(
        "/bookmark/me",
        json={"recipe_id": recipe_id},
        headers=auth_headers
    )

    assert response.status_code == 409, response.json()


def test_create_bookmark_no_recipe(client, auth_headers):
    recipe_id = "2d6ffb65-afac-45c0-885d-3ba980f33688"

    response = client.post(
        "/bookmark/me",
        json={"recipe_id": recipe_id},
        headers=auth_headers
    )

    assert response.status_code == 404, response.json()


def test_create_bookmark_no_recipe_id(client, auth_headers):

    response = client.post(
        "/bookmark/me",
        headers=auth_headers
    )

    assert response.status_code == 422, response.json()