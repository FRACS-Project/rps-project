##############################################################################################################
#
# Authentication and User Management Routes
#
# This module provides HTTP endpoints for user authentication and management.
# Routes handle HTTP request/response and delegate business logic to the service layer.
#
# Architecture:
#   - Routes: HTTP layer (request parsing, response formatting)
#   - Services: Business logic (validation, authentication, authorization)
#   - CRUD: Database operations (queries, inserts, updates, deletes)
#
# Routers:
#   - login_router: Authentication endpoints (login, token management)
#   - register_router: Public user registration (signup)
#
##############################################################################################################

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlmodel import Session

from . import (
    Token
)

from ..user.schemas import UserCreate, UserPublic
from ..user.services import UserService
from ..core import get_current_active_user
from ..db import get_session

##############################################################################################################
#
# Authentication router providing login endpoints and user info retrieval.
#
# This module handles user authentication through both form-based and JSON-based
# login methods, as well as endpoints to retrieve the current authenticated user's
# information. It supports the OAuth2 password flow with bearer token authentication.
#
##############################################################################################################

login_router = APIRouter(prefix="/auth", tags=["Auth"])


class LoginRequest(BaseModel):
    """Request body schema for JSON-based login.

    Attributes:
        mail (str): The user's email address or username.
        password (str): The user's password in plain text.
    """
    mail: str  # username ou email
    password: str


@login_router.post("/login-json", response_model=Token)
def login_json(
    request: LoginRequest,
    db: Session = Depends(get_session)
):
    """Authenticate user with JSON credentials and return access token.

    JSON-based authentication endpoint for programmatic API access.
    Validates credentials, checks account status, and generates JWT token.

    Args:
        request (LoginRequest): Login credentials (email and password).
        db (Session): Database session injected by FastAPI.

    Returns:
        Token: JWT access token and token type (bearer).

    Raises:
        InvalidCredentialsError (401): Invalid email or password.
        UserDisabledError (403): Account is disabled.
    """
    service = UserService(db)
    return service.authenticate_and_create_token(request.mail, request.password)


@login_router.get("/me-json", response_model=UserPublic)
def get_current_user_json(current_user: UserPublic = Depends(get_current_active_user)):
    """Retrieve the current user's information.

    This endpoint requires authentication and returns extended user information.

    Args:
        current_user (UserPublic): The authenticated user from token.

    Returns:
        UserPublic: The current user's data.
    """
    return current_user


@login_router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_session)
):
    """Authenticate user with form data and return access token.

    OAuth2 password flow authentication endpoint for browser-based login forms.
    Validates credentials, checks account status, and generates JWT token.

    Args:
        form_data (OAuth2PasswordRequestForm): OAuth2 form containing username and password.
        db (Session): Database session injected by FastAPI.

    Returns:
        Token: JWT access token and token type (bearer).

    Raises:
        InvalidCredentialsError (401): Invalid credentials.
        UserDisabledError (403): Account is disabled.
    """
    service = UserService(db)
    return service.authenticate_and_create_token(form_data.username, form_data.password)


@login_router.get("/me", response_model=UserPublic)
def get_current_user(current_user: UserPublic = Depends(get_current_active_user)):
    """Retrieve the current user's basic information.

    This endpoint requires authentication and returns basic user information.

    Args:
        current_user (UserPublic): The authenticated user from token.

    Returns:
        UserPublic: The current user's basic data.
    """
    return current_user


##############################################################################################################
#
# User registration router providing signup functionality.
#
# This module handles new user registration, including validation to ensure
# uniqueness of email addresses and usernames. It provides endpoints for
# creating new user accounts in the system.
#
##############################################################################################################


register_router = APIRouter(prefix="/auth", tags=["Auth"])


@register_router.post("/signup", response_model=UserPublic)
def signup(
    user: UserCreate,
    session: Session = Depends(get_session)
):
    """Register a new user account.

    This endpoint creates a new user account after validating that both the
    email address and username are not already in use. The password will be
    automatically hashed before storage.

    Args:
        user (UserCreate): The new user's registration data.
        session (Session): The database session dependency.

    Returns:
        UserPublic: The created user's public information.
    """
    service = UserService(session)
    return service.create_user(user)
