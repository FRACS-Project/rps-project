"""User module: model, base schema and exceptions. Services and routers are imported directly to avoid circular imports."""

from .models import User, UserBase
from .exceptions import (
    DuplicateEmailError,
    DuplicateUsernameError,
    InvalidCredentialsError,
    UserNotFoundError,
    UserDisabledError
)

__all__ = [
    "User",
    "UserBase",
    "DuplicateEmailError",
    "DuplicateUsernameError",
    "InvalidCredentialsError",
    "UserNotFoundError",
    "UserDisabledError",
]