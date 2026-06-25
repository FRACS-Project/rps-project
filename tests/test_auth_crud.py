from back.auth import crud


def test_create_user(test_db):
    """Test que create_user insère bien en DB"""
    # Arrange - Préparer les données
    user_data = {
        "name": "test",
        "mail": "test@test.com",
        "hashed_password": "hashed123",
        "admin": False,
        "disabled": False
    }
    
    # Act - Exécuter la fonction
    user = crud.create_user(test_db, user_data)
    
    # Assert - Vérifier le résultat
    assert user.id is not None         # ID généré
    assert user.name == "test"
    assert user.mail == "test@test.com"


def test_get_user_by_email_found(test_db):
    """Test que get_user_by_email trouve un user existant"""
    # Arrange
    user_data = {
        "name": "test",
        "mail": "test@test.com",
        "hashed_password": "hashed123",
        "admin": False,
        "disabled": False
    }
    crud.create_user(test_db, user_data)
    
    # Act
    found = crud.get_user_by_email(test_db, "test@test.com")
    
    # Assert
    assert found is not None
    assert found.mail == "test@test.com"


def test_get_user_by_email_not_found(test_db):
    """Test que get_user_by_email retourne None si pas trouvé"""
    # Act
    found = crud.get_user_by_email(test_db, "nonexistent@test.com")
    
    # Assert
    assert found is None  # Pas d'exception, juste None ✅