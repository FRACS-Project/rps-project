##############################################################################################################
#
# User Service Layer - Business Logic and Validation
#
# This module contains the service layer for user management and authentication.
# Services handle all business logic, validation, and coordinate between routes and CRUD.
#
# Architecture:
#   - Receives requests from routes (HTTP layer)
#   - Validates business rules (duplicates, passwords, account status)
#   - Coordinates CRUD operations (database layer)
#   - Handles error conditions with domain-specific exceptions
#
# Key Responsibilities:
#   - User creation with duplicate checking and password hashing
#   - Authentication with credential validation and token generation
#   - Business rule enforcement (password strength, account status)
#
##############################################################################################################

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
    """Service layer for user management and authentication.

    Handles all business logic related to users including creation, authentication,
    validation, and authorization. Coordinates between HTTP routes and database CRUD.
    """
    # ── Constructor ─────────────────────────────────────────────────────────────────────────────────────────────────
    def __init__(self, db: Session):
        """Initialize UserService with database session.

        Args:
            db (Session): Database session for executing queries via CRUD layer.
        """
        self.db = db
        self.crud = UserCrud(self.db)

    # ── Public: Queries ─────────────────────────────────────────────────────────────────────────────────────────────────
    def get_user(self, user_id: uuid.UUID) -> User:
        """Retrieve a specific user by their ID.

        Args:
            user_id (uuid.UUID): The unique identifier of the user.

        Returns:
            User: The found user instance.

        Raises:
            UserNotFoundError: If the user was not found.
        """
        
        user = self.crud.read_user(user_id)
        if not user:
            raise UserNotFoundError()

        return user
    
    def get_users(self, offset: int = 0, limit: int = 0) -> list[User]:
        """Retrieve a paginated list of all users.

        Returns a list of users data, supporting pagination through offset and limit parameters.

        Args:
            offset (int): Number of users to skip (for pagination).
            limit (int): Maximum number of users to return.

        Returns:
            List[User]: List of users.
        """
        
        return self.crud.read_users(offset, limit)
    
    # ── Public: Commands ─────────────────────────────────────────────────────────────────────────────────────────────────
    def create_user(self, user: UserCreate) -> User:
        """Create a new user with validation and password hashing.

        Args:
            user (UserCreate): The user data to create.

        Returns:
            User: The newly created user.

        Raises:
            DuplicateEmailError: If email already exists.
            DuplicateUsernameError: If username already exists.
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
            "admin": user.admin,
            "hashed_password": hashed_password,
            "disabled": user.disabled
        }

        # Call CRUD to insert into database
        return self.crud.create_user(user_data)

    def update_user(self, user_id: uuid.UUID, user: UserUpdate) -> User:
        """Update an existing user's information.

        Args:
            user_id (uuid.UUID): The unique identifier of the user.
            user (UserUpdate): The new user data to apply.

        Returns:
            User: The updated user instance.

        Raises:
            UserNotFoundError: If the user was not found.
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
        """Delete a user.

        Args:
            user_id (uuid.UUID): The unique identifier of the user.

        Raises:
            UserNotFoundError: If the user was not found.
        """
        
        db_user = self.crud.read_user(user_id)

        if not db_user:
            raise UserNotFoundError()
        
        self.crud.delete_user(db_user)
        
        return {"ok": True}

    def authenticate_and_create_token(self, mail: str, password: str) -> dict:
        """Authenticate user credentials and generate access token.

        Validates user credentials, checks account status, and creates a JWT token
        for authenticated sessions.

        Args:
            mail (str): User's email address.
            password (str): User's plain text password.

        Returns:
            dict: Token response with access_token and token_type.

        Raises:
            InvalidCredentialsError: Invalid email or password.
            UserDisabledError: Account is disabled.
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