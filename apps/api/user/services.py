"""User service: account management and login.

Checks email/username uniqueness, hashes passwords, and issues JWT access
tokens on login.
"""

import uuid
from sqlmodel import Session

from . import (
    User,
    DuplicateEmailError,
    DuplicateUsernameError,
    InvalidCredentialsError,
    UserNotFoundError,
    UserDisabledError
)

from .schemas import UserCreate, UserUpdate
from .crud import UserCrud

from ..core import security


class UserService:
    """Business logic for user accounts and authentication."""
    # ── Constructor ─────────────────────────────────────────────────────────────────────────────────────────────────
    def __init__(self, db: Session):
        """Initialize with a database session.

        Args:
            db: Database session shared with the CRUD layer.
        """
        self.db = db
        self.crud = UserCrud(self.db)

    # ── Public: Queries ─────────────────────────────────────────────────────────────────────────────────────────────────
    def get_user(self, user_id: uuid.UUID) -> User:
        """Return a user by ID.

        Args:
            user_id: ID of the user.

        Returns:
            The user.

        Raises:
            UserNotFoundError: If no user has this ID.
        """
        
        user = self.crud.read_user(user_id)
        if not user:
            raise UserNotFoundError()

        return user
    
    def get_users(self, offset: int = 0, limit: int = 0) -> list[User]:
        """Return a page of users.

        Args:
            offset: Number of users to skip.
            limit: Maximum number of users to return.

        Returns:
            The users in this page.
        """
        
        return self.crud.read_users(offset, limit)
    
    # ── Public: Commands ─────────────────────────────────────────────────────────────────────────────────────────────────
    def create_user(self, user: UserCreate) -> User:
        """Create a user after checking uniqueness, and hash their password.

        Args:
            user: Signup or admin-create data.

        Returns:
            The created user.

        Raises:
            DuplicateEmailError: If the email is already used.
            DuplicateUsernameError: If the username is already taken.
        """
        
        # Check if email already exists
        if self.crud.get_user_by_email(user.mail):
            raise DuplicateEmailError()

        # Check if username already exists
        if self.crud.get_user_by_name(user.name):
            raise DuplicateUsernameError()

        # Hash the password
        hashed_password = security.hash_password(user.password)

        # Prepare data for CRUD layer
        user_data = {
            "name": user.name,
            "mail": user.mail,
            "admin": False,
            "hashed_password": hashed_password,
            "disabled": False
        }

        # Call CRUD to insert into database
        return self.crud.create_user(user_data)

    def update_user(self, user_id: uuid.UUID, user: UserUpdate) -> User:
        """Partially update a user. A new password is hashed before saving.

        Args:
            user_id: ID of the user.
            user: Fields to change; unset fields are left as they are.

        Returns:
            The updated user.

        Raises:
            UserNotFoundError: If no user has this ID.
        """
        
        db_user = self.crud.read_user(user_id)

        if not db_user:
            raise UserNotFoundError()
        
        # Only hash if password is being updated
        user_data = user.model_dump(exclude_unset=True)
        if "password" in user_data:
            user_data["hashed_password"] = security.hash_password(user_data.pop("password"))
    
        return self.crud.update_user(db_user, user_data)

    def delete_user(self, user_id: uuid.UUID) -> dict:
        """Delete a user and, through cascade, their recipes and images.

        Args:
            user_id: ID of the user.

        Returns:
            `{"ok": True}`.

        Raises:
            UserNotFoundError: If no user has this ID.
        """
        
        db_user = self.crud.read_user(user_id)

        if not db_user:
            raise UserNotFoundError()
        
        self.crud.delete_user(db_user)
        
        return {"ok": True}

    def authenticate_and_create_token(self, mail: str, password: str) -> dict:
        """Check the credentials and return a JWT access token.

        Args:
            mail: Email or username.
            password: Plain text password.

        Returns:
            `{"access_token": ..., "token_type": "bearer"}`. The token's `sub` is
            the user's email.

        Raises:
            InvalidCredentialsError: If the user does not exist or the password is wrong.
            UserDisabledError: If the account is disabled.
        """
        
        user = self.crud.get_user_by_email(mail)
        if not user:
            user = self.crud.get_user_by_name(mail)
            if not user:
                raise InvalidCredentialsError()
        
        if user.disabled:
            raise UserDisabledError()
        
        if not security.verify_password(password, user.hashed_password):
            raise InvalidCredentialsError()

        access_token = security.create_access_token({"sub": user.mail})
        return {"access_token": access_token, "token_type": "bearer"}