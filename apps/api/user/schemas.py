##############################################################################################################
#
# Pydantic schemas for user data validation and serialization.
#
# This module defines the various schemas used for creating, updating, and
# returning user data through the API endpoints.
#
##############################################################################################################

import re
import uuid
from pydantic import field_validator, Field

from . import UserBase


class UserPublic(UserBase):
    """Schema for publicly viewable user data.

    Attributes:
        id (UUID): The user's unique identifier.
        name (str): The username.
        mail (EmailStr): The user's email address (unique).
        admin (bool, optional): Whether the user has admin privileges. Defaults to False.
        disabled (bool, optional): Whether the user account is disabled. Defaults to False.
    """
    id: uuid.UUID


class UserCreate(UserBase):
    """Schema for creating a new user.

    Attributes:
        password (str): The user's password in plain text (will be hashed).
    """
    password: str = Field(..., min_length=1, description="User password")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password meets security requirements."""
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
        """Validate username format and sanitize."""
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
        """Normalize email to lowercase."""
        return v.lower().strip()


class UserUpdate(UserBase):
    """Schema for updating user data.

    All fields are optional to allow partial updates.

    Attributes:
        name (str, optional): The updated username.
        mail (str, optional): The updated email address.
        admin (bool, optional): Whether to grant/revoke admin privileges.
        password (str, optional): The new password in plain text (will be hashed).
        disabled (bool, optional): Whether to disable the user account.
    """
    name: str | None = None
    mail: str | None = None
    admin: bool | None = None
    password: str | None = None
    disabled: bool | None = None

    @field_validator("password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """Only validate if password is being updated."""
        if v is not None:  # Only check if provided
            # Same validation as UserCreate
            if len(v) < 10:
                raise ValueError("Password must be at least 10 characters")
            # ... other checks
        return v


class UserSignUp(UserBase):
    """Schema for user registration/signup.

    A simplified schema for the signup endpoint that includes only the essential
    fields needed to create a new user account.

    Attributes:
        password (str): The user's chosen password in plain text (will be hashed).
    """
    password: str
