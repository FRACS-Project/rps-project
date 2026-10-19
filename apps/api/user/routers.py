"""User management endpoints under `/users`.

Meant for admins, but the admin dependency on the router is currently
commented out, so these routes are not protected.
"""

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
    """Create a user account, including the `admin` and `disabled` flags.

    Raises:
        DuplicateEmailError: 409 if the email is already used.
        DuplicateUsernameError: 409 if the username is already taken.
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
    """List users, paginated with `offset` and `limit`."""
    service = UserService(session)
    return service.get_users(offset, limit)


@user_router.get("/{user_id}", response_model=UserPublic)
def get_user(
    *,
    user_id: uuid.UUID,
    session: Session = Depends(get_session)
):
    """Get a user by ID.

    Raises:
        UserNotFoundError: 404 if no user has this ID.
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
    """Partially update a user. Only the fields sent are changed.

    Raises:
        UserNotFoundError: 404 if no user has this ID.
    """
    service = UserService(session)
    return service.update_user(user_id, user)


@user_router.delete("/{user_id}")
def delete_user(
    *,
    user_id: uuid.UUID,
    session: Session = Depends(get_session)
):
    """Delete a user and all their recipes and images. Cannot be undone.

    Raises:
        UserNotFoundError: 404 if no user has this ID.
    """
    service = UserService(session)
    return service.delete_user(user_id)
