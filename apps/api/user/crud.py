##############################################################################################################
#
# CRUD operations for managing users in the application.
#
# This module provides pure database operations for user entities.
# All business logic, validation, and error handling is in the service layer.
#
##############################################################################################################

import uuid
from sqlmodel import Session, select

from . import User


class UserCrud:
    def __init__(self, db: Session):
        """Initialize UserCrud with database session.

        Args:
            db (Session): Database session for executing queries via CRUD layer.
        """
        self.db = db

    def create_user(self, user: dict) -> User:
        """Create a new user in the database.

        Args:
            user (dict): The user data dict to create.

        Returns:
            User: The newly created user instance.
        """
        db_user = User.model_validate(user)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user


    def read_users(self, offset: int, limit: int) -> list[User]:
        """Retrieve a paginated list of users.

        Args:
            offset (int): Number of records to skip.
            limit (int): Maximum number of records to return.

        Returns:
            list[User]: A list of user instances.
        """
        return self.db.exec(select(User).offset(offset).limit(limit)).all()


    def read_user(self, user_id: uuid.UUID) -> User | None:
        """Retrieve a specific user by their ID.

        Args:
            user_id (uuid.UUID): The unique identifier of the user.

        Returns:
            User | None: The found user instance or None if not found.
        """
        return self.db.get(User, user_id)


    def update_user(self, db_user: User, user: dict) -> User:
        """Update an existing user's information.

        Args:
            db_user (User): The existing user instance to update.
            user (dict): The user data dict to apply.

        Returns:
            User: The updated user instance.
        """
        db_user.sqlmodel_update(user)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user


    def delete_user(self, db_user: User) -> dict:
        """Delete a user from the database.

        Args:
            db_user (User): The user instance to delete.
        
        Returns:
            dict: Confirmation message.
        """
        self.db.delete(db_user)
        self.db.commit()
        return {"ok": True}


    def get_user_by_email(self, email: str) -> User | None:
        """Retrieve a user by their email address.

        Args:
            email (str): The email address to search for.

        Returns:
            User | None: The found user instance or None if not found.
        """
        query = select(User).where(User.mail == email)
        return self.db.exec(query).first()


    def get_user_by_name(self, username: str):
        """Retrieve a user by their username.

        Args:
            username (str): The username to search for.

        Returns:
            User | None: The found user instance or None if not found.
        """
        query = select(User).where(User.name == username)
        return self.db.exec(query).first()
