"""Database access for users. No validation; the service layer handles that."""

import uuid
from sqlmodel import Session, select

from . import User


class UserCrud:
    """Queries and writes for the user table. Each write commits immediately."""
    def __init__(self, db: Session):
        """Initialize with a database session.

        Args:
            db: Database session.
        """
        self.db = db

    def create_user(self, user: dict) -> User:
        """Insert a user and commit.

        Args:
            user: User fields, including `hashed_password`.

        Returns:
            The created user.
        """
        db_user = User.model_validate(user)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user


    def read_users(self, offset: int, limit: int) -> list[User]:
        """Return a page of users."""
        return self.db.exec(select(User).offset(offset).limit(limit)).all()


    def read_user(self, user_id: uuid.UUID) -> User | None:
        """Return the user with this ID, or None."""
        return self.db.get(User, user_id)


    def update_user(self, db_user: User, user: dict) -> User:
        """Apply the given fields to a user and commit.

        Args:
            db_user: User to update.
            user: Fields to change.

        Returns:
            The updated user.
        """
        db_user.sqlmodel_update(user)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user


    def delete_user(self, db_user: User) -> dict:
        """Delete a user and commit. Their recipes and images are deleted too."""
        self.db.delete(db_user)
        self.db.commit()
        return {"ok": True}


    def get_user_by_email(self, email: str) -> User | None:
        """Return the user with this email, or None."""
        query = select(User).where(User.mail == email)
        return self.db.exec(query).first()


    def get_user_by_name(self, username: str):
        """Return the user with this username, or None."""
        query = select(User).where(User.name == username)
        return self.db.exec(query).first()
