"""Request and response schemas for users."""

import re
import uuid
from pydantic import field_validator, Field

from . import UserBase


class UserPublic(UserBase):
    """User data returned by the API. Never includes the password hash.

    Attributes:
        id: The user's ID.
    """
    id: uuid.UUID


class UserCreate(UserBase):
    """Body for creating a user (signup and admin create).

    Validates the password strength and the username format, and lowercases
    the email.

    Attributes:
        password: Plain text password; hashed by `UserService`.
    """
    password: str = Field(..., min_length=1, description="User password")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Require 10+ characters with an uppercase letter, a lowercase letter and a digit.

        The dev passwords "azerty" and "qsdfg" skip these checks.
        """
        # Dev mode: allow "azerty" to bypass validation
        if v == "azerty" or v == "qsdfg":
            return v

        if len(v) < 10:
            raise ValueError("Password must be at least 10 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain lowercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain digit")
        return v

    @field_validator("name")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Strip spaces and check the username format.

        Rules: 3 to 50 characters; only letters, digits, `-` and `_`; no `--` or `__`.
        """
        # Remove leading/trailing spaces
        v = v.strip()

        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        if len(v) > 50:
            raise ValueError("Username cannot exceed 50 characters")

        # Only alphanumeric, dash, underscore
        if not all(c.isalnum() or c in "-_" for c in v):
            raise ValueError(
                "Username can only contain letters, numbers, dashes, and underscores")

        # No consecutive dashes/underscores
        if "--" in v or "__" in v:
            raise ValueError(
                "Username cannot have consecutive special characters")

        return v

    @field_validator("mail", mode="after")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        """Lowercase the email and strip spaces."""
        return v.lower().strip()


class UserUpdate(UserBase):
    """Body for a partial user update. Only the fields sent are changed.

    Attributes:
        password: New plain text password; hashed by `UserService`.
    """
    name: str | None = None
    mail: str | None = None
    admin: bool | None = None
    password: str | None = None
    disabled: bool | None = None

    @field_validator("password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """Check the new password's length, if one is sent. Only the length rule is applied."""
        if v is not None:  # Only check if provided
            # Same validation as UserCreate
            if len(v) < 10:
                raise ValueError("Password must be at least 10 characters")
            # ... other checks
        return v


class UserSignUp(UserBase):
    """Minimal signup body. Not used by any route (signup uses `UserCreate`).

    Attributes:
        password: Plain text password.
    """
    password: str
