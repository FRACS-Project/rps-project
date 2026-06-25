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
#   - user_router: Admin-only user management (CRUD operations)
#   - login_router: Authentication endpoints (login, token management)
#   - register_router: Public user registration (signup)
#
##############################################################################################################


import uuid
from typing import List
from fastapi import APIRouter, Depends
from sqlmodel import Session

from .schemas import (
    UserCreate,
    UserPublic,
    UserUpdate
)

from .services import UserService
from ..core import get_current_admin_user, get_current_active_user
from ..db import get_session
from ..utils import (
    LimitQuery,
    OffsetQuery,
    DEFAULT_OFFSET,
    DEFAULT_LIMIT
)


user_router = APIRouter(
    prefix="/users",
    tags=["User"],
    # dependencies=[Depends(get_current_admin_user)]
)


@user_router.post("/", response_model=UserPublic)
def create_user(
    *,
    user: UserCreate,
    session: Session = Depends(get_session)
):
    """Create a new user account (Admin only).

    Admin endpoint for creating user accounts with full control over privileges.
    Validates email and username uniqueness, hashes password, and persists to database.

    Args:
        user (UserCreate): User data including name, email, password, and optional admin/disabled flags.
        session (Session): Database session injected by FastAPI.

    Returns:
        UserPublic: Created user's public information (excludes password).

    Raises:
        DuplicateEmailError (409): Email already exists.
        DuplicateUsernameError (409): Username already taken.
    """
    service = UserService(session)
    return service.create_user(user)


@user_router.get("/", response_model=List[UserPublic])
def get_users(
    *,
    offset: OffsetQuery = DEFAULT_OFFSET,
    limit: LimitQuery = DEFAULT_LIMIT,
    session: Session = Depends(get_session)
):
    """Retrieve a paginated list of all users.

    This endpoint returns a list of users data, supporting pagination through offset and limit parameters.

    Args:
        offset (OffsetQuery): Number of users to skip (for pagination).
        limit (LimitQuery): Maximum number of users to return.
        session (Session): The database session dependency.

    Returns:
        List[UserPublic]: List of users.
    """
    service = UserService(session)
    return service.get_users(offset, limit)


@user_router.get("/{user_id}", response_model=UserPublic)
def get_user(
    *,
    user_id: uuid.UUID,
    session: Session = Depends(get_session)
):
    """Retrieve a specific user by their ID.

    This endpoint returns detailed information about a single user.

    Args:
        user_id (UUID): The unique identifier of the user to retrieve.
        session (Session): The database session dependency.

    Returns:
        UserPublic: The user's information.

    Raises:
        HTTPException: If the user is not found (404 Not Found).
    """
    service = UserService(session)
    return service.get_user(user_id)


@user_router.patch("/{user_id}", response_model=UserPublic)
def update_user(
    *,
    user_id: uuid.UUID,
    user: UserUpdate,
    session: Session = Depends(get_session)
):
    """Update a specific user's information.

    This endpoint allows partial updates to a user's data, only modifying
    the fields that are provided in the update request.

    Args:
        user_id (UUID): The unique identifier of the user to update.
        user (UserUpdate): The fields to update and their new values.
        session (Session): The database session dependency.

    Returns:
        UserPublic: The updated user's public information.

    Raises:
        HTTPException: If the user is not found (404 Not Found).
    """
    service = UserService(session)
    return service.update_user(user_id, user)


@user_router.delete("/{user_id}")
def delete_user(
    *,
    user_id: uuid.UUID,
    session: Session = Depends(get_session)
):
    """Delete a user account.

    This endpoint permanently removes a user account and all associated data.
    This operation cannot be undone.

    Args:
        user_id (UUID): The unique identifier of the user to delete.
        session (Session): The database session dependency.

    Returns:
        dict: A confirmation message that the deletion was successful.

    Raises:
        HTTPException: If the user is not found (404 Not Found).
    """
    service = UserService(session)
    return service.delete_user(user_id)
